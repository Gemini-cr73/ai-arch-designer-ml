from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.core.schemas.agent_plan import AgentArchitecturePlan


class DiagramRequest(BaseModel):
    plan: AgentArchitecturePlan = Field(
        ..., description="Agent-produced architecture plan"
    )

    diagram_type: Literal["flow", "component"] = Field(
        default="flow",
        description="Mermaid diagram type: 'flow' (LR) or 'component' (TB).",
    )

    title: str | None = Field(default=None, description="Optional diagram title")

    # Pydantic v2 only. (Do NOT add `class Config:` in the same model.)
    model_config = {
        "json_schema_extra": {
            "example": {
                "diagram_type": "flow",
                "title": "AI Resume Screener – Architecture",
                "plan": {
                    "components": [
                        {
                            "name": "API Gateway",
                            "role": "Request routing / auth",
                            "technologies": ["FastAPI"],
                        },
                        {
                            "name": "ML Service",
                            "role": "Inference + scoring",
                            "technologies": ["Python", "scikit-learn"],
                        },
                    ],
                    "deployment": "Azure App Service",
                    "scaling": "Horizontal scale-out",
                    "security": ["JWT auth", "Input validation"],
                },
            }
        }
    }


class DiagramResponse(BaseModel):
    diagram_type: Literal["flow", "component"] = Field(
        ..., description="Diagram type used."
    )
    mermaid: str = Field(..., description="Mermaid diagram source text.")
