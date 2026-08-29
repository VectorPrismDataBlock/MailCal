# src/dates.py
from datetime import date, timedelta

WEEKDAY_NAMES = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

def resolve_relative_deadline(
    deadline_phrase: str | None,
    reference_date: str | None,
) -> str | None:
    """
    Resolve an exact weekday deadline using a supplied reference date.

    Returns an ISO date string or None when resolution is not possible.

    This intentionally supports only exact weekday phrases such as "Friday".
    Ambiguous phrases such as "next Friday" are left unresolved.
    """

    if not deadline_phrase or not reference_date:
        return None

    try:
        base_date = date.fromisoformat(reference_date)
    except (TypeError, ValueError):
        return None

    phrase = deadline_phrase.lower().strip()

    if phrase not in WEEKDAY_NAMES:
        return None

    target_weekday = WEEKDAY_NAMES[phrase]
    days_ahead = (target_weekday - base_date.weekday()) % 7
    resolved_date = base_date + timedelta(days=days_ahead)

    return resolved_date.isoformat()
