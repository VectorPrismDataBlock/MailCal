from typing import Literal
from src.classification_models import ClassificationResult

Route = Literal[
    "extract_commitments",
    "request_clarification",
    "skip_extraction",
]

def route_after_classification(
    classification: ClassificationResult,
) -> Route:
    """
    Route a message after classification.

    Clarification cases are handled separately so the system does not create
    user-owned commitments when ownership is uncertain.
    """
    if classification.classification == "needs_clarification":
        return "request_clarification"

    if classification.classification in {
        "action_required",
        "decision_required",
    }:
        return "extract_commitments"

    return "skip_extraction"
