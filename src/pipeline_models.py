from typing import Literal

from pydantic import BaseModel, Field
from src.classification_models import ClassificationResult
from src.models import CommitmentExtraction

Route = Literal[
    "extract_commitments",
    "request_clarification",
    "skip_extraction",
]

class MessageItem(BaseModel):
    """
    One supported work-related input message.

    The current pipeline accepts one message at a time and performs no
    consequential external action.
    """

    item_id: str
    source: str
    content: str
    created_at: str | None = None

class PipelineState(BaseModel):
    """
    Structured record of one message moving through the current pipeline.

    This model is intentionally state-only. It does not classify, extract,
    validate, route, or perform external actions.
    """

    message: MessageItem

    classification: ClassificationResult | None = None
    classification_errors: list[str] = Field(default_factory=list)

    route: Route | None = None

    extraction: CommitmentExtraction | None = None
    extraction_errors: list[str] = Field(default_factory=list)

    pipeline_warnings: list[str] = Field(default_factory=list)

    clarification_required: bool = False
    clarification_question: str | None = None
