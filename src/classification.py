from openai import OpenAI
from src.classification_models import ClassificationResult

CLASSIFICATION_INSTRUCTIONS = """
You classify exactly one work-related message.

The current system does not know the user's name.

Choose exactly one classification:

- action_required:
  The unnamed user is clearly expected to perform a concrete action.

- information_only:
  The message provides information but does not require the unnamed user to act.

- decision_required:
  The unnamed user must make, approve, reject, or communicate a decision.

- waiting_on_someone:
  Progress depends on another person providing information or taking action.

- reference_material:
  The message is useful background material but does not create current work.

- potential_project:
  The message suggests a larger effort or project rather than one current task.

- noise:
  The message is irrelevant, spam, or not useful for work operations.

- needs_clarification:
  It is unclear whether the user is responsible, including when work is
  addressed or assigned to a named person.

Rules:

1. Use action_required when the message directly asks the unnamed user to
   perform a concrete action.

   Examples:
   - "Can you review the proposal by Friday?"
   - "Could you look over the draft contract and let me know whether the
     payment terms seem reasonable?"
   - "Please send the revised timeline."

2. Use action_required when the message contains a first-person promise by
   the user to perform an action.

   Examples:
   - "I will send the final budget tomorrow."
   - "I'll review the contract."
   - "I promise to prepare the slides."

3. Use decision_required when the unnamed user must choose, approve, reject,
   or communicate a decision.

   Example:
   - "Please decide whether we should renew the contract."

4. A suggestion is not action_required unless the user is directly asked or
   clearly obligated to act.

   Example:
   - "It might be helpful to review the competitor analysis."
   - classification: information_only

5. The system does not know the user's name. If work is directly addressed,
   assigned, or requested from any named person, use needs_clarification.
   This applies even when there is only one named recipient.

   Examples:
   - "Alex, please send the budget."
   - "Taylor, could you send the approved invoice to accounting?"
   - "Jordan, can you confirm once it has been sent?"

   These messages are needs_clarification because the system cannot assume
   that Alex, Taylor, or Jordan is the user.

6. Use waiting_on_someone when the message says progress depends on another
   person's response or action and does not directly request current work from
   the user.

7. Use reference_material for attachments, reports, or background documents
   without an immediate request.

8. Use potential_project for proposed broad initiatives rather than a specific,
   current operational action.

9. Do not invent user responsibilities.

10. Return a short explanation directly supported by the message.

11. Return confidence between 0.0 and 1.0.

Return structured output matching the supplied schema.
"""

def classify_message(
    client: OpenAI,
    item_id: str,
    content: str,
) -> ClassificationResult:
    """
    Classify one message using structured model output.

    This function performs no external action and does not perform semantic
    validation. Contract validation is handled separately.
    """

    response = client.responses.parse(
        model="gpt-5-mini",
        instructions=CLASSIFICATION_INSTRUCTIONS,
        input=(
            f"Source item ID: {item_id}\n\n"
            f"Message:\n{content}"
        ),
        text_format=ClassificationResult,
    )

    return response.output_parsed
