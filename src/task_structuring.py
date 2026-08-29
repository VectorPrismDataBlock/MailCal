from openai import OpenAI
from src.models import Commitment
from src.task_models import TaskStructuringResult

TASK_STRUCTURING_INSTRUCTIONS = """
You convert validated user commitments into structured tasks.

You receive one or more commitments that have already passed deterministic
commitment validation.

The current system is decision support only. Do not perform or propose any
external action.

For each commitment, create exactly one structured task unless the commitment
cannot be safely structured.

Task requirements:

1. The task title must be concise and verb-led.
2. The task must describe the same work as the source commitment.
3. Completion criteria must explain what must be true for the task to be
   considered complete.
4. Preserve the commitment deadline exactly.
5. Preserve the source item ID exactly.
6. Preserve the source evidence exactly.
7. Preserve the original commitment title in source_commitment_title.
8. Do not invent dependencies.
9. Do not invent required context.
10. Use empty lists when dependencies or required context are not supported by
    the source commitment.
11. Use "unknown" for estimated_effort unless the message provides enough
    information for a cautious estimate.
12. Preserve meaningful uncertainty in ambiguity.
13. Confidence must be between 0.0 and 1.0.

Task status rules:

- tasks_found:
  Return one or more structured tasks.

- none_found:
  Return this only when no valid task can be created from the supplied
  commitments.

- needs_clarification:
  Return this when the commitment contains unresolved ambiguity that prevents
  safe task structuring.
  Return no tasks and include a clarification question.

Evidence rules:

- evidence must be copied exactly from the commitment.
- Do not rewrite, summarize, or normalize evidence.

Deadline rules:

- Copy the commitment deadline exactly.
- Do not calculate or change dates.
- If the commitment deadline is null, the task deadline must also be null.

Return structured output matching the supplied schema.
"""

def structure_commitments_as_tasks(
    client: OpenAI,
    commitments: list[Commitment],
) -> TaskStructuringResult:
    """
    Convert validated commitments into structured tasks.

    This function performs no external action and does not validate the model
    output. Validation is handled separately.
    """

    commitment_text = "\n\n".join(
        [
            (
                f"Commitment {index}:\n"
                f"Title: {commitment.title}\n"
                f"Owner: {commitment.owner}\n"
                f"Deadline: {commitment.deadline}\n"
                f"Deadline phrase: {commitment.deadline_phrase}\n"
                f"Source item ID: {commitment.source_item_id}\n"
                f"Evidence: {commitment.evidence}\n"
                f"Confidence: {commitment.confidence}\n"
                f"Ambiguity: {commitment.ambiguity}"
            )
            for index, commitment in enumerate(commitments, start=1)
        ]
    )

    response = client.responses.parse(
        model="gpt-5-mini",
        instructions=TASK_STRUCTURING_INSTRUCTIONS,
        input=(
            "Validated commitments:\n\n"
            f"{commitment_text}"
        ),
        text_format=TaskStructuringResult,
    )

    return response.output_parsed
