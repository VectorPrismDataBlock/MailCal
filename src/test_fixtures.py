from src.classification_models import ClassificationResult
from src.models import Commitment, CommitmentExtraction


CLASSIFICATION_FIXTURES = {
    "email-001": ClassificationResult(
        item_id="email-001",
        classification="action_required",
        confidence=1.0,
        reason="The message directly asks the user to review the proposal and send comments.",
    ),
    "email-002": ClassificationResult(
        item_id="email-002",
        classification="information_only",
        confidence=1.0,
        reason="The message provides an update and does not request user action.",
    ),
    "email-003": ClassificationResult(
        item_id="email-003",
        classification="action_required",
        confidence=1.0,
        reason="The message directly asks the user to review the contract and report back.",
    ),
    "email-004": ClassificationResult(
        item_id="email-004",
        classification="needs_clarification",
        confidence=1.0,
        reason="Work is assigned to named people, but the user's identity is unknown.",
    ),
    "email-005": ClassificationResult(
        item_id="email-005",
        classification="action_required",
        confidence=1.0,
        reason="The message directly requests two concrete user actions.",
    ),
    "email-006": ClassificationResult(
        item_id="email-006",
        classification="action_required",
        confidence=1.0,
        reason="The message contains a first-person promise by the user.",
    ),
    "email-007": ClassificationResult(
        item_id="email-007",
        classification="information_only",
        confidence=1.0,
        reason="The message is only a suggestion and does not create an obligation.",
    ),
    "email-008": ClassificationResult(
        item_id="email-008",
        classification="action_required",
        confidence=1.0,
        reason="The message directly asks the user to send a timeline.",
    ),
    "email-009": ClassificationResult(
        item_id="email-009",
        classification="action_required",
        confidence=1.0,
        reason="The message directly asks the user to send a timeline.",
    ),
    "email-010": ClassificationResult(
        item_id="email-010",
        classification="decision_required",
        confidence=1.0,
        reason="The message asks the user to decide whether to renew a contract.",
    ),
    "email-011": ClassificationResult(
        item_id="email-011",
        classification="waiting_on_someone",
        confidence=1.0,
        reason="Progress depends on Morgan's response.",
    ),
    "email-012": ClassificationResult(
        item_id="email-012",
        classification="reference_material",
        confidence=1.0,
        reason="The message provides background material without immediate action.",
    ),
    "email-013": ClassificationResult(
        item_id="email-013",
        classification="potential_project",
        confidence=1.0,
        reason="The message suggests a broader future initiative.",
    ),
    "email-014": ClassificationResult(
        item_id="email-014",
        classification="noise",
        confidence=1.0,
        reason="The message is unrelated promotional content.",
    ),
    "email-015": ClassificationResult(
        item_id="email-015",
        classification="needs_clarification",
        confidence=1.0,
        reason="Work is assigned to Taylor, but the user's identity is unknown.",
    ),
}


def _commitment(
    *,
    item_id: str,
    title: str,
    deadline: str | None,
    deadline_phrase: str | None,
    evidence: str,
    ambiguity: str | None = None,
) -> Commitment:
    return Commitment(
        title=title,
        owner="user",
        deadline=deadline,
        deadline_phrase=deadline_phrase,
        source_item_id=item_id,
        evidence=evidence,
        confidence=1.0,
        ambiguity=ambiguity,
    )


EXTRACTION_FIXTURES = {
    "email-001": CommitmentExtraction(
        status="commitments_found",
        commitments=[
            _commitment(
                item_id="email-001",
                title="Review the proposal and send comments",
                deadline="2026-08-21",
                deadline_phrase="August 21, 2026",
                evidence=(
                    "can you review the proposal and send me your comments "
                    "by August 21, 2026?"
                ),
            )
        ],
    ),
    "email-003": CommitmentExtraction(
        status="commitments_found",
        commitments=[
            _commitment(
                item_id="email-003",
                title="Review the draft contract and report on payment terms",
                deadline=None,
                deadline_phrase=None,
                evidence=(
                    "Could you look over the draft contract and let me know "
                    "whether the payment terms seem reasonable?"
                ),
            )
        ],
    ),
    "email-004": CommitmentExtraction(
        status="needs_clarification",
        commitments=[],
        clarification_question=(
            "Are you Alex or Jordan, the person addressed in this message?"
        ),
    ),
    "email-005": CommitmentExtraction(
        status="commitments_found",
        commitments=[
            _commitment(
                item_id="email-005",
                title="Review customer feedback",
                deadline="2026-08-22",
                deadline_phrase="August 22, 2026",
                evidence=(
                    "Could you review the customer feedback by August 22, 2026"
                ),
            ),
            _commitment(
                item_id="email-005",
                title="Send the revised onboarding checklist",
                deadline="2026-08-25",
                deadline_phrase="August 25, 2026",
                evidence=(
                    "send the revised onboarding checklist by August 25, 2026"
                ),
            ),
        ],
    ),
    "email-006": CommitmentExtraction(
        status="commitments_found",
        commitments=[
            _commitment(
                item_id="email-006",
                title="Send the final budget to Priya",
                deadline="2026-08-28",
                deadline_phrase="August 28, 2026",
                evidence=(
                    "I will send the final budget to Priya by August 28, 2026."
                ),
            )
        ],
    ),
    "email-008": CommitmentExtraction(
        status="commitments_found",
        commitments=[
            _commitment(
                item_id="email-008",
                title="Send the revised timeline",
                deadline=None,
                deadline_phrase="Friday",
                evidence="Please send the revised timeline by Friday.",
                ambiguity=(
                    "The exact date for Friday cannot be resolved without "
                    "a reference date."
                ),
            )
        ],
    ),
    "email-009": CommitmentExtraction(
        status="commitments_found",
        commitments=[
            _commitment(
                item_id="email-009",
                title="Send the revised timeline",
                deadline=None,
                deadline_phrase="Friday",
                evidence="Please send the revised timeline by Friday.",
            )
        ],
    ),
    "email-010": CommitmentExtraction(
        status="commitments_found",
        commitments=[
            _commitment(
                item_id="email-010",
                title="Decide whether to renew the Northstar contract",
                deadline="2026-08-26",
                deadline_phrase="August 26, 2026",
                evidence=(
                    "Please decide whether we should renew the contract with "
                    "Northstar before the vendor meeting on August 26, 2026."
                ),
            )
        ],
    ),
    "email-015": CommitmentExtraction(
        status="needs_clarification",
        commitments=[],
        clarification_question=(
            "Are you Taylor, the person addressed in this message?"
        ),
    ),
}
