from typing import Literal
from pydantic import BaseModel, Field

class StructuredTask(BaseModel):
    title: str
    completion_criteria: str
    estimated_effort: Literal[
        "unknown",
        "less_than_15_minutes",
        "15_to_30_minutes",
        "30_to_60_minutes",
        "1_to_2_hours",
        "more_than_2_hours",
    ] = "unknown"
    dependencies: list[str] = Field(default_factory=list)
    required_context: list[str] = Field(default_factory=list)
    deadline: str | None = None
    source_item_id: str
    source_commitment_title: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)
    ambiguity: str | None = None


class TaskStructuringResult(BaseModel):
    status: Literal[
        "tasks_found",
        "none_found",
        "needs_clarification",
    ]
    tasks: list[StructuredTask] = Field(default_factory=list)
    clarification_question: str | None = None
