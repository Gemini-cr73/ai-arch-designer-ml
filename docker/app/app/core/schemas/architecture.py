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
    # ✅ NEW (Milestone 6 ML metrics)
    pattern_label: str | None = Field(
        None, description="Predicted architecture pattern label"
    )
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Model confidence score (0..1)"
    )

    # Existing fields
    pattern: str
    services: list[ServiceComponent]
    data_flows: list[DataFlow]
    storage: list[str]
    risks: list[str]
