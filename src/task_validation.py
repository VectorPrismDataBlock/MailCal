from datetime import date
from src.task_models import StructuredTask, TaskStructuringResult

def validate_structured_task(
    task: StructuredTask,
    source_item_id: str,
    source_text: str,
) -> list[str]:
    errors: list[str] = []

    if not task.title.strip():
        errors.append("Task title is empty")

    if not task.completion_criteria.strip():
        errors.append("Task completion criteria is empty")

    if not task.source_item_id.strip():
        errors.append("Task source_item_id is empty")

    if task.source_item_id != source_item_id:
        errors.append(
            "Task source_item_id does not match the input item ID"
        )

    if not task.source_commitment_title.strip():
        errors.append("Task source commitment title is empty")

    if not task.evidence.strip():
        errors.append("Task evidence is empty")
    elif task.evidence not in source_text:
        errors.append(
            "Task evidence was not found verbatim in source text"
        )

    if task.deadline is not None:
        try:
            date.fromisoformat(task.deadline)
        except (TypeError, ValueError):
            errors.append("Task deadline must use YYYY-MM-DD format")

    if task.ambiguity is not None and not task.ambiguity.strip():
        errors.append("Task ambiguity cannot be empty")

    if not 0.0 <= task.confidence <= 1.0:
        errors.append(
            "Task confidence must be between 0.0 and 1.0"
        )

    return errors

def validate_task_structuring(
    result: TaskStructuringResult,
    source_item_id: str,
    source_text: str,
) -> list[str]:
    errors: list[str] = []

    if result.status == "none_found":
        if result.tasks:
            errors.append(
                "Status is none_found but tasks were returned"
            )

        if result.clarification_question:
            errors.append(
                "Status is none_found but a clarification question "
                "was returned"
            )

    elif result.status == "tasks_found":
        if not result.tasks:
            errors.append(
                "Status is tasks_found but no tasks were returned"
            )

        if result.clarification_question:
            errors.append(
                "Status is tasks_found but a clarification question "
                "was returned"
            )

    elif result.status == "needs_clarification":
        if result.tasks:
            errors.append(
                "Status is needs_clarification but tasks were returned"
            )

        if not result.clarification_question:
            errors.append(
                "Status is needs_clarification but no clarification "
                "question was returned"
            )

    for task in result.tasks:
        errors.extend(
            validate_structured_task(
                task=task,
                source_item_id=source_item_id,
                source_text=source_text,
            )
        )

    return errors
