# app/core/schemas/agent_plan.py

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

try:
    # Pydantic v2
    from pydantic import ConfigDict
except Exception:  # pragma: no cover
    ConfigDict = None  # type: ignore


class ComponentSpec(BaseModel):
    name: str
    role: str
    technologies: list[str]


class AgentArchitecturePlan(BaseModel):
    components: list[ComponentSpec] = Field(default_factory=list)

    # LLMs sometimes return deployment as a string OR as a dict/object
    deployment: str | dict[str, Any] = ""

    scaling: str = ""
    security: list[str] = Field(default_factory=list)

    # Be tolerant of extra keys the LLM may include
    if ConfigDict is not None:
        model_config = ConfigDict(extra="allow")
    else:

        class Config:
            extra = "allow"
