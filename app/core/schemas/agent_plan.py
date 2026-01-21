from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ComponentSpec(BaseModel):
    name: str
    role: str
    technologies: list[str]


class AgentArchitecturePlan(BaseModel):
    components: list[ComponentSpec]

    # ✅ FIX: LLM may return deployment as a string OR as an object
    deployment: str | dict[str, Any]

    scaling: str
    security: list[str]

    class Config:
        extra = "allow"  # tolerate extra keys the LLM might include
