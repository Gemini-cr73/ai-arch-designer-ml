from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.schemas.agent_plan import AgentArchitecturePlan
from app.core.schemas.inputs import ProjectIdeaInput


class ScaffoldRequest(BaseModel):
    """
    Milestone 4 request:
    - Either provide a plan directly OR provide an idea and let the API generate the plan first.
    """

    idea: ProjectIdeaInput | None = Field(
        default=None, description="Optional: project idea input (will call agent-plan)"
    )
    plan: AgentArchitecturePlan | None = Field(
        default=None, description="Optional: existing agent architecture plan"
    )

    project_slug: str = Field(
        default="generated_project",
        description="Repo folder name / slug (letters, numbers, underscores).",
    )

    include_docker: bool = Field(
        default=True, description="Include Dockerfile + compose"
    )
    include_github_actions: bool = Field(
        default=False, description="Include CI skeleton"
    )


class RepoFile(BaseModel):
    path: str = Field(..., description="Relative file path in the repo")
    content: str = Field(..., description="File content (text)")


class ScaffoldResponse(BaseModel):
    project_slug: str
    tree: list[str] = Field(..., description="Simple tree listing (paths)")
    files: dict[str, str] = Field(..., description="Map: path -> file contents")
    plan: AgentArchitecturePlan = Field(
        ..., description="The plan used to generate scaffold"
    )
