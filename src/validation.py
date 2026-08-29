from datetime import date
from src.models import Commitment, CommitmentExtraction

RELATIVE_DEADLINE_PHRASES = {
    "today",
    "tomorrow",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}

def is_relative_deadline_phrase(deadline_phrase: str | None) -> bool:
    """
    Return True when a deadline phrase is relative or context-dependent.
    """

    if not deadline_phrase:
        return False

    phrase = deadline_phrase.lower().strip()

    return (
        phrase in RELATIVE_DEADLINE_PHRASES
        or phrase.startswith("next ")
        or phrase.startswith("this ")
        or phrase.startswith("end of ")
        or "week" in phrase
        or "month" in phrase
        or "meeting" in phrase
    )

def validate_commitment(
    commitment: Commitment,
    source_text: str,
) -> list[str]:
    """
    Validate objective commitment-level contract requirements.
    """

    errors: list[str] = []

    if not commitment.title.strip():
        errors.append("Missing commitment title")

    if commitment.owner != "user":
        errors.append(
            "Commitment owner must be 'user' in a user-only extraction"
        )

    if not commitment.evidence.strip():
        errors.append("Missing commitment evidence")

    elif commitment.evidence not in source_text:
        errors.append(
            "Evidence was not found verbatim in source text"
        )

    if commitment.deadline_phrase is not None:
        if not commitment.deadline_phrase.strip():
            errors.append("Deadline phrase cannot be empty")

        elif commitment.deadline_phrase not in source_text:
            errors.append(
                "Deadline phrase was not found verbatim in source text"
            )

    if commitment.deadline is not None:
        try:
            date.fromisoformat(commitment.deadline)
        except (TypeError, ValueError):
            errors.append("Deadline must use YYYY-MM-DD format")

        if commitment.deadline_phrase is None:
            errors.append(
                "Deadline is present but deadline_phrase is missing"
            )

    if (
        commitment.deadline is None
        and is_relative_deadline_phrase(commitment.deadline_phrase)
        and not commitment.ambiguity
    ):
        errors.append(
            "An unresolved relative deadline requires an ambiguity statement"
        )

    if (
        commitment.deadline is None
        and commitment.deadline_phrase is None
        and commitment.ambiguity is not None
    ):
        errors.append(
            "Ambiguity is present but no deadline phrase exists"
        )

    if not 0.0 <= commitment.confidence <= 1.0:
        errors.append(
            "Commitment confidence must be between 0.0 and 1.0"
        )

    return errors

def validate_extraction(
    extraction: CommitmentExtraction,
    source_item_id: str,
    source_text: str,
) -> list[str]:
    """
    Validate extraction-level and commitment-level contract requirements.
    """

    errors: list[str] = []

    if extraction.status == "none_found":
        if extraction.commitments:
            errors.append(
                "Status is none_found but commitments were returned"
            )

        if extraction.clarification_question:
            errors.append(
                "Status is none_found but a clarification question was returned"
            )

    if extraction.status == "commitments_found":
        if not extraction.commitments:
            errors.append(
                "Status is commitments_found but no commitments were returned"
            )

        if extraction.clarification_question:
            errors.append(
                "Status is commitments_found but a clarification question was returned"
            )

    if extraction.status == "needs_clarification":
        if extraction.commitments:
            errors.append(
                "Status is needs_clarification but commitments were returned"
            )

        if not extraction.clarification_question:
            errors.append(
                "Status is needs_clarification but no clarification question "
                "was returned"
            )

    for commitment in extraction.commitments:
        if commitment.source_item_id != source_item_id:
            errors.append(
                "Commitment source_item_id does not match the input item ID"
            )

        errors.extend(
            validate_commitment(
                commitment=commitment,
                source_text=source_text,
            )
        )

    return errors
