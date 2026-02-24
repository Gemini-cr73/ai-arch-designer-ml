# app/core/schemas/inputs.py

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Scale = Literal["prototype", "startup", "enterprise"]
Budget = Literal["low", "medium", "high"]


class ProjectIdeaInput(BaseModel):
    name: str = Field(..., examples=["AI Resume Screener"])
    description: str = Field(..., examples=["Ranks resumes using ML."])
    domain: str = Field(..., examples=["HR Tech"])
    scale: Scale = Field(..., examples=["prototype"])

    expected_users: int | None = Field(
        None, examples=[5000], description="Estimated number of users"
    )

    compliance: list[str] = Field(
        default_factory=list,
        examples=[["GDPR"]],
        description="List of compliance requirements",
    )

    budget: Budget | None = Field(
        None, examples=["medium"], description="Project budget level"
    )

    # --- Normalizers ---
    @field_validator("name", "description", "domain", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
        return v

    @field_validator("expected_users")
    @classmethod
    def validate_users(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            return 1
        return v
