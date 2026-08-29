# src/models.py

from typing import Literal

from pydantic import BaseModel, Field


class Commitment(BaseModel):
    title: str
    owner: str | None = None
    deadline: str | None = None
    deadline_phrase: str | None = None
    source_item_id: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)
    ambiguity: str | None = None


class CommitmentExtraction(BaseModel):
    status: Literal["commitments_found", "none_found", "needs_clarification"]
    commitments: list[Commitment] = Field(default_factory=list)
    clarification_question: str | None = None
