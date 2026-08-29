from src.task_models import StructuredTask, TaskStructuringResult
from src.task_validation import (
    validate_structured_task,
    validate_task_structuring,
)

def make_task() -> StructuredTask:
    return StructuredTask(
        title="Review the proposal",
        completion_criteria=(
            "Review the proposal and record any required changes."
        ),
        estimated_effort="30_to_60_minutes",
        dependencies=[],
        required_context=["Proposal document"],
        deadline="2026-08-21",
        source_item_id="email-001",
        source_commitment_title="Review the proposal",
        evidence="Please review the proposal by August 21, 2026.",
        confidence=0.95,
        ambiguity=None,
    )

def test_valid_structured_task_passes_validation():
    task = make_task()

    errors = validate_structured_task(
        task=task,
        source_item_id="email-001",
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == []

def test_task_evidence_must_be_verbatim():
    task = make_task()
    task.evidence = "Review the proposal."

    errors = validate_structured_task(
        task=task,
        source_item_id="email-001",
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task evidence was not found verbatim in source text"
    ]

def test_task_source_item_id_must_match():
    task = make_task()
    task.source_item_id = "email-wrong"

    errors = validate_structured_task(
        task=task,
        source_item_id="email-001",
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task source_item_id does not match the input item ID"
    ]

def test_tasks_found_requires_at_least_one_task():
    result = TaskStructuringResult(
        status="tasks_found",
        tasks=[],
        clarification_question=None,
    )

    errors = validate_task_structuring(
        result=result,
        source_item_id="email-001",
        source_text="Please review the proposal.",
    )

    assert errors == [
        "Status is tasks_found but no tasks were returned"
    ]

def test_none_found_must_not_return_tasks():
    result = TaskStructuringResult(
        status="none_found",
        tasks=[make_task()],
        clarification_question=None,
    )

    errors = validate_task_structuring(
        result=result,
        source_item_id="email-001",
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Status is none_found but tasks were returned"
    ]

def test_needs_clarification_requires_question_and_no_tasks():
    result = TaskStructuringResult(
        status="needs_clarification",
        tasks=[],
        clarification_question=None,
    )

    errors = validate_task_structuring(
        result=result,
        source_item_id="email-001",
        source_text="Please review the proposal.",
    )

    assert errors == [
        (
            "Status is needs_clarification but no clarification "
            "question was returned"
        )
    ]
