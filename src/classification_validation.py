from src.classification_models import ClassificationResult

ALLOWED_CLASSIFICATIONS = {
    "action_required",
    "information_only",
    "decision_required",
    "waiting_on_someone",
    "reference_material",
    "potential_project",
    "noise",
    "needs_clarification",
}

def validate_classification(
    result: ClassificationResult,
    expected_item_id: str,
) -> list[str]:
    """
    Validate objective properties of a classification result.

    This does not judge whether the model chose the semantically correct
    category. It checks structural and contract-level requirements.
    """
    errors: list[str] = []

    if result.item_id != expected_item_id:
        errors.append(
            "Classification item_id does not match the input item ID"
        )

    if result.classification not in ALLOWED_CLASSIFICATIONS:
        errors.append(
            f"Unsupported classification: {result.classification}"
        )

    if not result.reason.strip():
        errors.append("Classification reason is empty")

    if not 0.0 <= result.confidence <= 1.0:
        errors.append("Classification confidence must be between 0.0 and 1.0")

    return errors