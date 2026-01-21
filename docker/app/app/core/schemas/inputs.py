from pydantic import BaseModel, Field


class ProjectIdeaInput(BaseModel):
    name: str = Field(..., example="AI Resume Screener")  # required
    description: str = Field(..., example="Ranks resumes using ML.")  # required
    domain: str = Field(..., example="HR Tech")  # required
    scale: str = Field(..., example="prototype | startup | enterprise")  #  required
    expected_users: int | None = Field(None, example=5000)  # optional
    compliance: list[str] | None = Field(
        default_factory=list, example=["GDPR"]
    )  # optional
    budget: str | None = Field(None, example="low | medium | high")  # optional
