from src.classification_models import ClassificationResult
from src.models import Commitment, CommitmentExtraction
from src.pipeline_models import MessageItem, PipelineState

def test_pipeline_state_has_safe_defaults():
    message = MessageItem(
        item_id="email-001",
        source="email",
        content="Please send the revised timeline.",
    )

    state = PipelineState(message=message)

    assert state.message.item_id == "email-001"
    assert state.classification is None
    assert state.classification_errors == []
    assert state.route is None
    assert state.extraction is None
    assert state.extraction_errors == []
    assert state.pipeline_warnings == []
    assert state.clarification_required is False
    assert state.clarification_question is None

def test_pipeline_state_records_completed_commitment_path():
    message = MessageItem(
        item_id="email-002",
        source="email",
        content="Please send the revised timeline by Friday.",
        created_at="2026-08-19",
    )

    classification = ClassificationResult(
        item_id="email-002",
        classification="action_required",
        confidence=0.95,
        reason="The message directly asks the user to send a timeline.",
    )

    commitment = Commitment(
        title="Send the revised timeline",
        owner="user",
        deadline="2026-08-21",
        deadline_phrase="Friday",
        source_item_id="email-002",
        evidence="Please send the revised timeline by Friday.",
        confidence=0.95,
        ambiguity=None,
    )

    extraction = CommitmentExtraction(
        status="commitments_found",
        commitments=[commitment],
        clarification_question=None,
    )

    state = PipelineState(
        message=message,
        classification=classification,
        route="extract_commitments",
        extraction=extraction,
    )

    assert state.classification.classification == "action_required"
    assert state.route == "extract_commitments"
    assert state.extraction is not None
    assert state.extraction.status == "commitments_found"
    assert len(state.extraction.commitments) == 1
    assert state.extraction.commitments[0].deadline == "2026-08-21"

def test_pipeline_state_records_clarification_path():
    message = MessageItem(
        item_id="email-003",
        source="email",
        content="Taylor, could you send the approved invoice?",
    )

    classification = ClassificationResult(
        item_id="email-003",
        classification="needs_clarification",
        confidence=0.95,
        reason=(
            "The message assigns work to Taylor, but the system does not know "
            "whether Taylor is the user."
        ),
    )

    extraction = CommitmentExtraction(
        status="needs_clarification",
        commitments=[],
        clarification_question="Are you Taylor, the person addressed here?",
    )

    state = PipelineState(
        message=message,
        classification=classification,
        route="request_clarification",
        extraction=extraction,
        clarification_required=True,
        clarification_question=extraction.clarification_question,
    )

    assert state.route == "request_clarification"
    assert state.clarification_required is True
    assert state.clarification_question == (
        "Are you Taylor, the person addressed here?"
    )
    assert state.extraction is not None
    assert state.extraction.status == "needs_clarification"
    assert state.extraction.commitments == []
