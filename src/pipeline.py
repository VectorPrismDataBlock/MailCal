from collections.abc import Callable
from openai import OpenAI

from src.classification import classify_message
from src.classification_models import ClassificationResult
from src.classification_validation import validate_classification
from src.extraction import (
    extract_commitments,
    resolve_extraction_deadlines,
)
from src.models import CommitmentExtraction
from src.pipeline_models import MessageItem, PipelineState
from src.routing import Route, route_after_classification
from src.validation import validate_extraction

ClassificationFunction = Callable[
    [OpenAI, str, str],
    ClassificationResult,
]

ExtractionFunction = Callable[
    [OpenAI, str, str, str | None],
    CommitmentExtraction,
]

DeadlineResolutionFunction = Callable[
    [CommitmentExtraction, str | None],
    CommitmentExtraction,
]

ClassificationValidationFunction = Callable[
    [ClassificationResult, str],
    list[str],
]

ExtractionValidationFunction = Callable[
    [CommitmentExtraction, str, str],
    list[str],
]

RoutingFunction = Callable[
    [ClassificationResult],
    Route,
]

def run_pipeline(
    client: OpenAI,
    message: MessageItem,
    classify: ClassificationFunction = classify_message,
    validate_classification_result: ClassificationValidationFunction = (
        validate_classification
    ),
    route: RoutingFunction = route_after_classification,
    extract: ExtractionFunction = extract_commitments,
    resolve_deadlines: DeadlineResolutionFunction = (
        resolve_extraction_deadlines
    ),
    validate_extraction_result: ExtractionValidationFunction = (
        validate_extraction
    ),
) -> PipelineState:
    """
    Run the current Daily Operations pipeline for one message.

    Pipeline stages:

    Message
    -> classification
    -> classification validation
    -> routing
    -> commitment extraction when appropriate
    -> relative deadline resolution
    -> extraction validation
    -> structured PipelineState

    The function performs no consequential external action. It may call the
    supplied classification and extraction functions, which are model-backed
    by default. Tests can inject deterministic fake functions instead.
    """

    state = PipelineState(message=message)

    classification = classify(
        client,
        message.item_id,
        message.content,
    )

    state.classification = classification

    classification_errors = validate_classification_result(
        classification,
        message.item_id,
    )

    state.classification_errors = classification_errors

    if classification_errors:
        state.pipeline_warnings.append(
            "Classification contract validation failed; extraction was skipped."
        )
        return state

    pipeline_route = route(classification)
    state.route = pipeline_route

    if pipeline_route == "skip_extraction":
        return state

    extraction = extract(
        client,
        message.item_id,
        message.content,
        message.created_at,
    )

    resolved_extraction = resolve_deadlines(
        extraction,
        message.created_at,
    )

    state.extraction = resolved_extraction

    extraction_errors = validate_extraction_result(
        resolved_extraction,
        message.item_id,
        message.content,
    )

    state.extraction_errors = extraction_errors

    if pipeline_route == "request_clarification":
        _handle_clarification_route(state)

    if pipeline_route == "extract_commitments":
        _handle_commitment_extraction_route(state)

    return state

def _handle_clarification_route(state: PipelineState) -> None:
    """
    Apply deterministic checks and state updates for clarification routing.
    """

    if state.extraction is None:
        state.pipeline_warnings.append(
            "Clarification route did not produce an extraction result."
        )
        return

    if state.extraction.status != "needs_clarification":
        state.pipeline_warnings.append(
            "Classification found ownership ambiguity, but extraction did not "
            "return needs_clarification."
        )
        return

    state.clarification_required = True
    state.clarification_question = (
        state.extraction.clarification_question
    )

def _handle_commitment_extraction_route(state: PipelineState) -> None:
    """
    Apply deterministic disagreement warnings for commitment extraction routing.
    """

    if state.extraction is None:
        state.pipeline_warnings.append(
            "Commitment extraction route did not produce an extraction result."
        )
        return

    if state.extraction.status == "none_found":
        state.pipeline_warnings.append(
            "Classification routed this message to extraction, but extraction "
            "found no user commitment."
        )

    if state.extraction.status == "needs_clarification":
        state.pipeline_warnings.append(
            "Classification marked this message actionable, but extraction "
            "found ownership ambiguity."
        )
