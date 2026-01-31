from __future__ import annotations

from typing import Any

from pydantic import BaseModel

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
    components: list[ComponentSpec]

    # LLMs sometimes return deployment as a string OR as a dict/object
    deployment: str | dict[str, Any] = ""

    scaling: str = ""
    security: list[str] = []

    # Be tolerant of extra keys the LLM may include
    if ConfigDict is not None:
        model_config = ConfigDict(extra="allow")
    else:

        class Config:
            extra = "allow"
