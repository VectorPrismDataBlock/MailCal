from openai import OpenAI

from src.classification_models import ClassificationResult
from src.models import Commitment, CommitmentExtraction
from src.pipeline import run_pipeline
from src.pipeline_models import MessageItem


def make_client() -> OpenAI:
    """
    Create a client object only to satisfy the run_pipeline interface.

    The injected fake functions below do not make API calls.
    """

    return OpenAI(api_key="test-key")


def test_pipeline_skips_extraction_for_information_only_message():
    message = MessageItem(
        item_id="email-001",
        source="email",
        content="FYI: The product team moved the release date.",
    )

    extraction_was_called = False

    def fake_classify(
        client: OpenAI,
        item_id: str,
        content: str,
    ) -> ClassificationResult:
        return ClassificationResult(
            item_id=item_id,
            classification="information_only",
            confidence=0.95,
            reason="The message is informational and does not request action.",
        )

    def fake_extract(
        client: OpenAI,
        item_id: str,
        content: str,
        created_at: str | None,
    ) -> CommitmentExtraction:
        nonlocal extraction_was_called

        extraction_was_called = True

        return CommitmentExtraction(
            status="none_found",
            commitments=[],
            clarification_question=None,
        )

    state = run_pipeline(
        client=make_client(),
        message=message,
        classify=fake_classify,
        extract=fake_extract,
    )

    assert state.classification is not None
    assert state.classification.classification == "information_only"
    assert state.classification_errors == []
    assert state.route == "skip_extraction"
    assert state.extraction is None
    assert state.extraction_errors == []
    assert state.pipeline_warnings == []
    assert state.clarification_required is False
    assert state.clarification_question is None
    assert extraction_was_called is False


def test_pipeline_extracts_and_resolves_weekday_deadline():
    message = MessageItem(
        item_id="email-002",
        source="email",
        content="Please send the revised timeline by Friday.",
        created_at="2026-08-19",
    )

    def fake_classify(
        client: OpenAI,
        item_id: str,
        content: str,
    ) -> ClassificationResult:
        return ClassificationResult(
            item_id=item_id,
            classification="action_required",
            confidence=0.95,
            reason="The message directly asks the user to send a timeline.",
        )

    def fake_extract(
        client: OpenAI,
        item_id: str,
        content: str,
        created_at: str | None,
    ) -> CommitmentExtraction:
        commitment = Commitment(
            title="Send the revised timeline",
            owner="user",
            deadline=None,
            deadline_phrase="Friday",
            source_item_id=item_id,
            evidence="Please send the revised timeline by Friday.",
            confidence=0.95,
            ambiguity=None,
        )

        return CommitmentExtraction(
            status="commitments_found",
            commitments=[commitment],
            clarification_question=None,
        )

    state = run_pipeline(
        client=make_client(),
        message=message,
        classify=fake_classify,
        extract=fake_extract,
    )

    assert state.classification is not None
    assert state.classification.classification == "action_required"
    assert state.classification_errors == []
    assert state.route == "extract_commitments"

    assert state.extraction is not None
    assert state.extraction.status == "commitments_found"
    assert len(state.extraction.commitments) == 1

    commitment = state.extraction.commitments[0]

    assert commitment.title == "Send the revised timeline"
    assert commitment.owner == "user"
    assert commitment.deadline_phrase == "Friday"
    assert commitment.deadline == "2026-08-21"
    assert commitment.ambiguity is None

    assert state.extraction_errors == []
    assert state.pipeline_warnings == []
    assert state.clarification_required is False
    assert state.clarification_question is None


def test_pipeline_marks_clarification_required_for_named_person_request():
    message = MessageItem(
        item_id="email-003",
        source="email",
        content="Taylor, could you send the approved invoice to accounting?",
    )

    def fake_classify(
        client: OpenAI,
        item_id: str,
        content: str,
    ) -> ClassificationResult:
        return ClassificationResult(
            item_id=item_id,
            classification="needs_clarification",
            confidence=0.95,
            reason=(
                "The request is directed to Taylor, and the system does not "
                "know whether Taylor is the user."
            ),
        )

    def fake_extract(
        client: OpenAI,
        item_id: str,
        content: str,
        created_at: str | None,
    ) -> CommitmentExtraction:
        return CommitmentExtraction(
            status="needs_clarification",
            commitments=[],
            clarification_question=(
                "Are you Taylor, the person addressed in this message?"
            ),
        )

    state = run_pipeline(
        client=make_client(),
        message=message,
        classify=fake_classify,
        extract=fake_extract,
    )

    assert state.classification is not None
    assert state.classification.classification == "needs_clarification"
    assert state.classification_errors == []
    assert state.route == "request_clarification"

    assert state.extraction is not None
    assert state.extraction.status == "needs_clarification"
    assert state.extraction.commitments == []
    assert state.extraction.clarification_question == (
        "Are you Taylor, the person addressed in this message?"
    )

    assert state.extraction_errors == []
    assert state.pipeline_warnings == []
    assert state.clarification_required is True
    assert state.clarification_question == (
        "Are you Taylor, the person addressed in this message?"
    )


def test_pipeline_stops_when_classification_contract_validation_fails():
    message = MessageItem(
        item_id="email-004",
        source="email",
        content="Please send the revised timeline.",
    )

    extraction_was_called = False

    def fake_classify(
        client: OpenAI,
        item_id: str,
        content: str,
    ) -> ClassificationResult:
        return ClassificationResult(
            item_id="wrong-item-id",
            classification="action_required",
            confidence=0.95,
            reason="The message asks the user to send a timeline.",
        )

    def fake_extract(
        client: OpenAI,
        item_id: str,
        content: str,
        created_at: str | None,
    ) -> CommitmentExtraction:
        nonlocal extraction_was_called

        extraction_was_called = True

        return CommitmentExtraction(
            status="none_found",
            commitments=[],
            clarification_question=None,
        )

    state = run_pipeline(
        client=make_client(),
        message=message,
        classify=fake_classify,
        extract=fake_extract,
    )

    assert state.classification is not None
    assert state.classification.item_id == "wrong-item-id"
    assert state.classification_errors == [
        "Classification item_id does not match the input item ID"
    ]

    assert state.route is None
    assert state.extraction is None
    assert state.extraction_errors == []
    assert state.pipeline_warnings == [
        "Classification contract validation failed; extraction was skipped."
    ]

    assert state.clarification_required is False
    assert state.clarification_question is None
    assert extraction_was_called is False


def test_pipeline_warns_when_actionable_classification_finds_no_commitment():
    message = MessageItem(
        item_id="email-005",
        source="email",
        content="Please send the revised timeline.",
    )

    def fake_classify(
        client: OpenAI,
        item_id: str,
        content: str,
    ) -> ClassificationResult:
        return ClassificationResult(
            item_id=item_id,
            classification="action_required",
            confidence=0.95,
            reason="The message directly asks the user to send a timeline.",
        )

    def fake_extract(
        client: OpenAI,
        item_id: str,
        content: str,
        created_at: str | None,
    ) -> CommitmentExtraction:
        return CommitmentExtraction(
            status="none_found",
            commitments=[],
            clarification_question=None,
        )

    state = run_pipeline(
        client=make_client(),
        message=message,
        classify=fake_classify,
        extract=fake_extract,
    )

    assert state.classification is not None
    assert state.classification.classification == "action_required"
    assert state.classification_errors == []
    assert state.route == "extract_commitments"

    assert state.extraction is not None
    assert state.extraction.status == "none_found"
    assert state.extraction_errors == []

    assert state.pipeline_warnings == [
        "Classification routed this message to extraction, but extraction "
        "found no user commitment."
    ]

    assert state.clarification_required is False
    assert state.clarification_question is None


def test_pipeline_warns_when_actionable_classification_finds_ownership_ambiguity():
    message = MessageItem(
        item_id="email-006",
        source="email",
        content="Please send the revised timeline.",
    )

    def fake_classify(
        client: OpenAI,
        item_id: str,
        content: str,
    ) -> ClassificationResult:
        return ClassificationResult(
            item_id=item_id,
            classification="action_required",
            confidence=0.95,
            reason="The message appears to ask the user to send a timeline.",
        )

    def fake_extract(
        client: OpenAI,
        item_id: str,
        content: str,
        created_at: str | None,
    ) -> CommitmentExtraction:
        return CommitmentExtraction(
            status="needs_clarification",
            commitments=[],
            clarification_question=(
                "Is the request actually assigned to you?"
            ),
        )

    state = run_pipeline(
        client=make_client(),
        message=message,
        classify=fake_classify,
        extract=fake_extract,
    )

    assert state.classification is not None
    assert state.classification.classification == "action_required"
    assert state.classification_errors == []
    assert state.route == "extract_commitments"

    assert state.extraction is not None
    assert state.extraction.status == "needs_clarification"
    assert state.extraction_errors == []

    assert state.pipeline_warnings == [
        "Classification marked this message actionable, but extraction "
        "found ownership ambiguity."
    ]

    assert state.clarification_required is False
    assert state.clarification_question is None


def test_pipeline_warns_when_clarification_route_does_not_return_clarification():
    message = MessageItem(
        item_id="email-007",
        source="email",
        content="Taylor, could you send the approved invoice to accounting?",
    )

    def fake_classify(
        client: OpenAI,
        item_id: str,
        content: str,
    ) -> ClassificationResult:
        return ClassificationResult(
            item_id=item_id,
            classification="needs_clarification",
            confidence=0.95,
            reason=(
                "The request is addressed to Taylor, whose identity relative "
                "to the user is unknown."
            ),
        )

    def fake_extract(
        client: OpenAI,
        item_id: str,
        content: str,
        created_at: str | None,
    ) -> CommitmentExtraction:
        return CommitmentExtraction(
            status="none_found",
            commitments=[],
            clarification_question=None,
        )

    state = run_pipeline(
        client=make_client(),
        message=message,
        classify=fake_classify,
        extract=fake_extract,
    )

    assert state.classification is not None
    assert state.classification.classification == "needs_clarification"
    assert state.classification_errors == []
    assert state.route == "request_clarification"

    assert state.extraction is not None
    assert state.extraction.status == "none_found"
    assert state.extraction_errors == []

    assert state.pipeline_warnings == [
        "Classification found ownership ambiguity, but extraction did not "
        "return needs_clarification."
    ]

    assert state.clarification_required is False
    assert state.clarification_question is None
