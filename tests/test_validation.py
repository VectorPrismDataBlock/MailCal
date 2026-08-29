from src.models import Commitment
from src.validation import validate_commitment
from src.dates import resolve_relative_deadline

def test_valid_commitment_passes_validation():
    source_text = (
        "Hi, can you review the proposal and send me your comments "
        "by August 21, 2026?"
    )

    commitment = Commitment(
        title="Review the proposal and send comments",
        owner="user",
        deadline="2026-08-21",
        deadline_phrase="August 21, 2026",
        source_item_id="email-001",
        evidence=(
            "can you review the proposal and send me your comments "
            "by August 21, 2026?"
        ),
        confidence=0.95,
        ambiguity=None,
    )

    errors = validate_commitment(
        commitment=commitment,
        source_text=source_text,
    )

    assert errors == []


def test_relative_deadline_phrase_is_allowed():
    commitment = Commitment(
        title="Send the revised timeline",
        owner="user",
        deadline=None,
        deadline_phrase="Friday",
        source_item_id="email-009",
        evidence="Please send the revised timeline by Friday.",
        confidence=0.95,
        ambiguity=(
            "The exact date for Friday will be resolved separately."
        ),
    )

    assert commitment.deadline is None
    assert commitment.deadline_phrase == "Friday"

def test_friday_resolves_from_reference_date():
    resolved = resolve_relative_deadline(
        deadline_phrase="Friday",
        reference_date="2026-08-19",
    )

    assert resolved == "2026-08-21"

def test_weekday_deadline_resolves_from_reference_date():
    result = resolve_relative_deadline(
        deadline_phrase="Friday",
        reference_date="2026-08-19",
    )

    assert result == "2026-08-21"


def test_same_weekday_resolves_to_reference_date():
    result = resolve_relative_deadline(
        deadline_phrase="Friday",
        reference_date="2026-08-21",
    )

    assert result == "2026-08-21"


def test_missing_reference_date_returns_none():
    result = resolve_relative_deadline(
        deadline_phrase="Friday",
        reference_date=None,
    )

    assert result is None
