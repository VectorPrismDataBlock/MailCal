from src.models import Commitment
from src.task_models import StructuredTask, TaskStructuringResult
from src.task_structuring_validation import (
    validate_structured_task,
    validate_task_structuring,
)


def make_commitment() -> Commitment:
    return Commitment(
        title="Review the proposal",
        owner="user",
        deadline="2026-08-21",
        deadline_phrase="August 21, 2026",
        source_item_id="email-001",
        evidence="Please review the proposal by August 21, 2026.",
        confidence=0.95,
        ambiguity=None,
    )


def make_task() -> StructuredTask:
    return StructuredTask(
        title="Review the proposal",
        completion_criteria=(
            "Review the proposal and record any required changes."
        ),
        estimated_effort="30_to_60_minutes",
        dependencies=[],
        required_context=[],
        deadline="2026-08-21",
        source_item_id="email-001",
        source_commitment_title="Review the proposal",
        evidence="Please review the proposal by August 21, 2026.",
        confidence=0.95,
        ambiguity=None,
    )


def test_valid_structured_task_passes_validation():
    commitment = make_commitment()
    task = make_task()

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == []


def test_task_title_must_not_be_empty():
    commitment = make_commitment()
    task = make_task()
    task.title = "   "

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == ["Task title is empty"]


def test_completion_criteria_must_not_be_empty():
    commitment = make_commitment()
    task = make_task()
    task.completion_criteria = ""

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == ["Task completion criteria is empty"]


def test_task_source_commitment_title_must_match():
    commitment = make_commitment()
    task = make_task()
    task.source_commitment_title = "Unrelated task"

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task source_commitment_title does not match the source commitment"
    ]


def test_task_evidence_must_match_source_commitment():
    commitment = make_commitment()
    task = make_task()
    task.evidence = "Review the proposal."

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task evidence was not found verbatim in source text",
        "Task evidence does not match the source commitment evidence",
    ]


def test_task_deadline_must_match_source_commitment():
    commitment = make_commitment()
    task = make_task()
    task.deadline = "2026-08-22"

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task deadline does not match the source commitment deadline"
    ]


def test_task_deadline_must_use_iso_format():
    commitment = make_commitment()
    task = make_task()
    task.deadline = "August 21, 2026"

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task deadline does not match the source commitment deadline",
        "Task deadline must use YYYY-MM-DD format",
    ]


def test_tasks_found_requires_one_task_per_commitment():
    commitment = make_commitment()

    result = TaskStructuringResult(
        status="tasks_found",
        tasks=[],
        clarification_question=None,
    )

    errors = validate_task_structuring(
        result=result,
        source_commitments=[commitment],
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Status is tasks_found but no tasks were returned",
        "Task count does not match source commitment count",
    ]


def test_tasks_found_rejects_extra_tasks():
    commitment = make_commitment()

    result = TaskStructuringResult(
        status="tasks_found",
        tasks=[make_task(), make_task()],
        clarification_question=None,
    )

    errors = validate_task_structuring(
        result=result,
        source_commitments=[commitment],
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task count does not match source commitment count"
    ]


def test_none_found_must_not_return_tasks():
    result = TaskStructuringResult(
        status="none_found",
        tasks=[make_task()],
        clarification_question=None,
    )

    errors = validate_task_structuring(
        result=result,
        source_commitments=[],
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
        source_commitments=[],
        source_text="Please review the proposal.",
    )

    assert errors == [
        (
            "Status is needs_clarification but no clarification "
            "question was returned"
        )
    ]


def test_needs_clarification_must_not_return_tasks():
    result = TaskStructuringResult(
        status="needs_clarification",
        tasks=[make_task()],
        clarification_question="Please clarify the task.",
    )

    errors = validate_task_structuring(
        result=result,
        source_commitments=[make_commitment()],
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Status is needs_clarification but tasks were returned"
    ]


def test_tasks_found_must_not_return_clarification_question():
    result = TaskStructuringResult(
        status="tasks_found",
        tasks=[make_task()],
        clarification_question="Please clarify the task.",
    )

    errors = validate_task_structuring(
        result=result,
        source_commitments=[make_commitment()],
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Status is tasks_found but a clarification question was returned"
    ]


def test_none_found_must_not_return_clarification_question():
    result = TaskStructuringResult(
        status="none_found",
        tasks=[],
        clarification_question="Please clarify the task.",
    )

    errors = validate_task_structuring(
        result=result,
        source_commitments=[],
        source_text="No actionable commitment exists.",
    )

    assert errors == [
        (
            "Status is none_found but a clarification question "
            "was returned"
        )
    ]


def test_task_confidence_must_be_within_range():
    commitment = make_commitment()
    task = make_task()
    task.confidence = 1.5

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task confidence must be between 0.0 and 1.0"
    ]


def test_empty_task_ambiguity_is_invalid():
    commitment = make_commitment()
    task = make_task()
    task.ambiguity = "   "

    errors = validate_structured_task(
        task=task,
        source_commitment=commitment,
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == [
        "Task ambiguity cannot be empty"
    ]


def test_valid_task_result_matches_commitment():
    commitment = make_commitment()
    task = make_task()

    result = TaskStructuringResult(
        status="tasks_found",
        tasks=[task],
        clarification_question=None,
    )

    errors = validate_task_structuring(
        result=result,
        source_commitments=[commitment],
        source_text="Please review the proposal by August 21, 2026.",
    )

    assert errors == []
