from src.priority import score_task_priority
from src.task_models import StructuredTask


def test_deadlined_action_task_scores_five():
    task = StructuredTask(
        title="Send the final budget",
        completion_criteria="Send the final budget to Priya.",
        deadline="2026-08-28",
        source_item_id="email-006",
        source_commitment_title="Send the final budget",
        evidence=(
            "I will send the final budget to Priya by August 28, 2026."
        ),
        confidence=1.0,
    )

    priority, reason = score_task_priority(task)

    assert priority == 5
    assert "has a deadline" in reason
    assert "concrete action" in reason
