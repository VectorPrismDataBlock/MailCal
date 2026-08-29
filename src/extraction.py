from openai import OpenAI
from src.dates import resolve_relative_deadline
from src.models import CommitmentExtraction
from src.validation import is_relative_deadline_phrase

EXTRACTION_INSTRUCTIONS = """
You extract user commitments from exactly one work-related message.

The current system does not know the user's name.

A commitment exists only when at least one of the following is true:

1. The message directly asks the user, as an unnamed recipient, to do a
   concrete action.
2. The message contains a clear obligation assigned to the unnamed user.
3. The message is a first-person statement written by the user that clearly
   promises a future action.

Direct requests to the unnamed user include phrasing such as:
- "Can you..."
- "Could you..."
- "Would you..."
- "Will you..."
- "Please..."
- "I need you to..."
- "Can you let me know..."
- "Could you look over..."
- "Please decide..."

Examples that MUST produce commitments_found:
- "Can you review the proposal?"
- "Could you look over the draft contract and let me know whether the payment
  terms seem reasonable?"
- "Please send the updated budget."
- "Please decide whether we should renew the contract."
- "I will prepare the slides."

Named-person ownership rule:

If the message directly addresses, assigns work to, or requests work from a
named person, the user's identity is unknown. You MUST return
needs_clarification, even if there is only one named recipient.

Examples that MUST return needs_clarification:
- "Alex, please send the budget."
- "Taylor, could you send the approved invoice to accounting?"
- "Jordan, can you confirm once it has been sent?"
- "Alex, please send the budget. Jordan, can you confirm once it has been sent?"

For needs_clarification:
- status must be "needs_clarification";
- commitments must be an empty list;
- clarification_question must ask whether the named person is the user;
- do not extract any commitment.

Do not create a commitment from:
- FYI updates,
- general information,
- suggestions without a direct request,
- vague ideas,
- reference material,
- work explicitly assigned to another named person,
- messages where named-person ownership is uncertain.

Examples that MUST return none_found:
- "FYI: The release date has moved."
- "It might be helpful to review the competitor analysis."
- "Attached is the market research report for background."
- "We should consider creating a customer onboarding program."
- "We are waiting for Morgan to confirm the final pricing."

Never invent a deadline.

Deadline rules:
- deadline_phrase must contain only the exact date or time expression.
- Do not include surrounding words such as "by", "before", or "on".
- Do not include trailing punctuation.
- deadline_phrase must be an exact verbatim substring of the message.
- Use YYYY-MM-DD in deadline only when the date is explicit and exact.
- For relative deadlines such as "Friday", "tomorrow", "next week", or
  "before the meeting", set deadline to null.
- Do not perform date arithmetic yourself.
- If a relative deadline cannot yet be resolved, explain the limitation in
  ambiguity.
- If no deadline exists, set both deadline and deadline_phrase to null.

Deadline examples:
- "by August 21, 2026" means:
  deadline_phrase = "August 21, 2026"
  deadline = "2026-08-21"

- "Please send it by Friday." means:
  deadline_phrase = "Friday"
  deadline = null

- "before tomorrow's meeting" means:
  deadline_phrase = "tomorrow"
  deadline = null

For each extracted commitment:
- title must be concise and verb-led;
- owner must be "user";
- evidence must be an exact verbatim substring from the message;
- source_item_id must exactly equal the supplied item ID;
- confidence must be between 0.0 and 1.0;
- ambiguity must be null when there is no meaningful uncertainty.

Task granularity rules:
- Combine tightly connected actions into one commitment when they serve one
  outcome and share one deadline.
- Separate independent deliverables when they have distinct outcomes or
  different deadlines.

Status rules:
- commitments_found: one or more user commitments were extracted.
- none_found: no user commitment exists.
- needs_clarification: ownership is genuinely unclear because a named person
  was assigned or directly asked to do work.

Return structured output matching the supplied schema.
"""

def extract_commitments(
    client: OpenAI,
    item_id: str,
    content: str,
    created_at: str | None = None,
) -> CommitmentExtraction:
    """
    Extract commitments assigned to the user from one input message.

    This function performs no external action and does not validate output.
    """

    response = client.responses.parse(
        model="gpt-5-mini",
        instructions=EXTRACTION_INSTRUCTIONS,
        input=(
            f"Source item ID: {item_id}\n"
            f"Message date: {created_at or 'not supplied'}\n\n"
            f"Message:\n{content}"
        ),
        text_format=CommitmentExtraction,
    )

    return response.output_parsed

def unresolved_relative_deadline_ambiguity(
    deadline_phrase: str,
    reference_date: str | None,
) -> str:
    """
    Return a deterministic explanation for a relative deadline that remains
    unresolved after the supported date-resolution step.
    """

    if not reference_date:
        return (
            f"The exact date for {deadline_phrase} cannot be resolved "
            "without a reference date."
        )

    return (
        f"The relative deadline phrase '{deadline_phrase}' cannot be resolved "
        "by the current deterministic date-resolution policy."
    )

def resolve_extraction_deadlines(
    extraction: CommitmentExtraction,
    created_at: str | None,
) -> CommitmentExtraction:
    """
    Return a copy of the extraction with supported relative deadlines resolved.

    Exact weekday names are resolved only when a valid reference date is
    available. If a relative deadline remains unresolved, this function
    deterministically ensures that an ambiguity explanation exists.
    """

    resolved_extraction = extraction.model_copy(deep=True)

    for commitment in resolved_extraction.commitments:
        if commitment.deadline is not None:
            continue

        if commitment.deadline_phrase is None:
            continue

        resolved_deadline = resolve_relative_deadline(
            deadline_phrase=commitment.deadline_phrase,
            reference_date=created_at,
        )

        if resolved_deadline is not None:
            commitment.deadline = resolved_deadline
            commitment.ambiguity = None
            continue

        if (
            is_relative_deadline_phrase(commitment.deadline_phrase)
            and not commitment.ambiguity
        ):
            commitment.ambiguity = unresolved_relative_deadline_ambiguity(
                deadline_phrase=commitment.deadline_phrase,
                reference_date=created_at,
            )

    return resolved_extraction
