# app/core_schemas/architecture.py

from pydantic import BaseModel, Field


class ServiceComponent(BaseModel):
    name: str
    responsibility: str
    technologies: list[str]


class DataFlow(BaseModel):
    source: str
    destination: str
    description: str


class ArchitecturePlan(BaseModel):
    # Core plan output
    pattern: str = Field(
        ..., description="Primary architecture pattern (e.g., monolith, microservices)"
    )
    services: list[ServiceComponent]
    data_flows: list[DataFlow]
    storage: list[str]
    risks: list[str]

    # ✅ ML metadata (Milestone 6)
    pattern_label: str | None = Field(
        None, description="Predicted architecture pattern label"
    )
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Model confidence score (0..1)"
    )
