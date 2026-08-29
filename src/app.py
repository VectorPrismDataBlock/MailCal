import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

from src.calendar_client import (
    create_calendar_event,
    get_busy_slots,
)
from src.gmail_client import list_recent_messages
from src.integrations_models import (
    CalendarEventRequest,
    CalendarEventResponse,
    GmailMessage,
    TaskView,
)
from src.pipeline import run_pipeline
from src.pipeline_models import MessageItem, PipelineState
from src.priority import score_task_priority
from src.task_structuring import structure_commitments_as_tasks
from src.task_structuring_validation import (
    validate_task_structuring,
)


load_dotenv()

app = FastAPI(title="Daily Operations Assistant")

WEB_FILE = (
    Path(__file__).resolve().parent
    / "web"
    / "index.html"
)

_messages: dict[str, GmailMessage] = {}
_states: dict[str, PipelineState] = {}
_tasks: dict[str, list[TaskView]] = {}


class ProcessResponse(BaseModel):
    state: PipelineState
    tasks: list[TaskView]
    task_errors: list[str]


def _openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    return OpenAI(api_key=key)


@app.get("/")
def home():
    return FileResponse(WEB_FILE)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.get("/api/messages")
def messages():
    try:
        loaded = list_recent_messages()
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc

    _messages.clear()
    _messages.update(
        {message.item_id: message for message in loaded}
    )

    return loaded


@app.post("/api/process/{item_id}", response_model=ProcessResponse)
def process(item_id: str):
    source = _messages.get(item_id)

    if source is None:
        raise HTTPException(
            404,
            "Load Gmail first or message was not found",
        )

    message = MessageItem(
        item_id=source.item_id,
        source=source.source,
        content=source.content,
        created_at=source.created_at,
    )

    try:
        state = run_pipeline(
            client=_openai_client(),
            message=message,
        )
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc

    _states[item_id] = state
    tasks = []
    task_errors = []

    extraction = state.extraction

    if (
        extraction
        and extraction.status == "commitments_found"
        and not state.extraction_errors
    ):
        try:
            result = structure_commitments_as_tasks(
                client=_openai_client(),
                commitments=extraction.commitments,
            )

            task_errors = validate_task_structuring(
                result=result,
                source_commitments=extraction.commitments,
                source_text=message.content,
            )

            if not task_errors:
                for task in result.tasks:
                    priority, reason = score_task_priority(task)

                    tasks.append(
                        TaskView(
                            item_id=task.source_item_id,
                            title=task.title,
                            completion_criteria=(
                                task.completion_criteria
                            ),
                            deadline=task.deadline,
                            priority=priority,
                            priority_reason=reason,
                            estimated_effort=(
                                task.estimated_effort
                            ),
                            evidence=task.evidence,
                            source_commitment_title=(
                                task.source_commitment_title
                            ),
                            ambiguity=task.ambiguity,
                        )
                    )

                _tasks[item_id] = tasks

        except Exception as exc:
            task_errors = [str(exc)]

    return ProcessResponse(
        state=state,
        tasks=tasks,
        task_errors=task_errors,
    )


@app.get("/api/tasks")
def tasks():
    return [
        task
        for item_tasks in _tasks.values()
        for task in item_tasks
    ]


@app.get("/api/calendar/busy")
def calendar_busy(
    start: str,
    end: str,
    calendar_id: str = "primary",
):
    try:
        return get_busy_slots(start, end, calendar_id)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@app.post(
    "/api/calendar/events",
    response_model=CalendarEventResponse,
)
def calendar_event(request: CalendarEventRequest):
    try:
        return create_calendar_event(request)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
