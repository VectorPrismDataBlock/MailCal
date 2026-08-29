from datetime import date
from src.task_models import StructuredTask, TaskStructuringResult

def validate_structured_task(
    task: StructuredTask,
    source_commitment: object,
    source_text: str,
) -> list[str]:
    """
    Validate one structured task against its source commitment and message.
    """

    errors: list[str] = []

    if not task.title.strip():
        errors.append("Task title is empty")

    if not task.completion_criteria.strip():
        errors.append("Task completion criteria is empty")

    if not task.source_item_id.strip():
        errors.append("Task source_item_id is empty")

    if task.source_item_id != source_commitment.source_item_id:
        errors.append(
            "Task source_item_id does not match the source commitment"
        )

    if task.source_commitment_title != source_commitment.title:
        errors.append(
            "Task source_commitment_title does not match the source commitment"
        )

    if not task.evidence.strip():
        errors.append("Task evidence is empty")
    elif task.evidence not in source_text:
        errors.append(
            "Task evidence was not found verbatim in source text"
        )

    if task.evidence != source_commitment.evidence:
        errors.append(
            "Task evidence does not match the source commitment evidence"
        )

    if task.deadline != source_commitment.deadline:
        errors.append(
            "Task deadline does not match the source commitment deadline"
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
    source_commitments: list[object],
    source_text: str,
) -> list[str]:
    """
    Validate task-structuring status contracts and task provenance.

    The source commitments are expected to be validated Commitment objects.
    """

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

    if result.status == "tasks_found":
        if len(result.tasks) != len(source_commitments):
            errors.append(
                "Task count does not match source commitment count"
            )

        for task, source_commitment in zip(
            result.tasks,
            source_commitments,
        ):
            errors.extend(
                validate_structured_task(
                    task=task,
                    source_commitment=source_commitment,
                    source_text=source_text,
                )
            )

    return errors
