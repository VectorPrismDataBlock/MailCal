from typing import Literal

from pydantic import BaseModel, Field


Classification = Literal[
    "action_required",
    "information_only",
    "decision_required",
    "waiting_on_someone",
    "reference_material",
    "potential_project",
    "noise",
    "needs_clarification",
]


class ClassificationResult(BaseModel):
    item_id: str
    classification: Classification
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
