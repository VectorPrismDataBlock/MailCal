from pydantic import BaseModel, Field


class GmailMessage(BaseModel):
    item_id: str
    thread_id: str | None = None
    source: str = "gmail"
    sender: str = ""
    recipients: str = ""
    subject: str = ""
    content: str
    created_at: str | None = None
    web_url: str | None = None


class CalendarEventRequest(BaseModel):
    task_title: str
    description: str = ""
    start: str
    end: str
    timezone: str = "America/New_York"
    calendar_id: str = "primary"


class CalendarEventResponse(BaseModel):
    event_id: str
    html_link: str | None = None
    summary: str
    start: str
    end: str


class AvailabilitySlot(BaseModel):
    start: str
    end: str


class TaskView(BaseModel):
    item_id: str
    title: str
    completion_criteria: str
    deadline: str | None = None
    priority: int = Field(ge=1, le=5)
    priority_reason: str
    estimated_effort: str
    evidence: str
    source_commitment_title: str
    ambiguity: str | None = None
