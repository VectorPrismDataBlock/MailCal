from src.task_models import StructuredTask


def score_task_priority(task: StructuredTask) -> tuple[int, str]:
    score = 3
    reasons = []

    if task.deadline:
        score += 1
        reasons.append("has a deadline")

    action_words = (
        "decide",
        "approve",
        "review",
        "send",
        "confirm",
    )

    text = (
        f"{task.title} "
        f"{task.completion_criteria}"
    ).lower()

    if any(word in text for word in action_words):
        score += 1
        reasons.append("contains a concrete action")

    if task.ambiguity:
        score -= 1
        reasons.append("contains unresolved ambiguity")

    return max(1, min(5, score)), (
        "; ".join(reasons) or "default task priority"
    )
