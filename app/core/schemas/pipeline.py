from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.core.schemas.agent_plan import AgentArchitecturePlan
from app.core.schemas.inputs import ProjectIdeaInput


class DiagramPipelineRequest(BaseModel):
    idea: ProjectIdeaInput = Field(..., description="High-level project idea input")
    diagram_type: Literal["flow", "component"] = Field(
        default="flow",
        description="Mermaid diagram type: 'flow' (LR) or 'component' (TB).",
    )
    title: str | None = Field(default=None, description="Optional diagram title")


class DiagramPipelineResponse(BaseModel):
    diagram_type: Literal["flow", "component"] = Field(
        ..., description="Diagram type used."
    )
    title: str | None = Field(default=None, description="Diagram title used (if any).")
    mermaid: str = Field(..., description="Mermaid diagram source text.")
    plan: AgentArchitecturePlan = Field(
        ..., description="Structured plan produced by the agent."
    )

    # Optional for later (Mermaid rendering service / endpoint)
    render_url: str | None = Field(
        default=None,
        description="Optional URL to a rendered diagram image (future).",
    )
