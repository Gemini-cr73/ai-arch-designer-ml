from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.agents.planner_agent import PlannerAgent
from app.core.schemas.agent_plan import AgentArchitecturePlan
from app.core.schemas.architecture import ArchitecturePlan
from app.core.schemas.inputs import ProjectIdeaInput
from app.core.schemas.pipeline import DiagramPipelineRequest, DiagramPipelineResponse
from app.core.schemas.scaffold import ScaffoldRequest, ScaffoldResponse
from app.services.diagrams.mermaid_builder import build_mermaid
from app.services.llm.ollama_client import OllamaClient
from app.services.planner.planner_service import ArchitecturePlanner
from app.services.scaffold.scaffold_generator import generate_repo_scaffold
from app.services.scaffold.zip_export import build_scaffold_zip_bytes

router = APIRouter(prefix="/architect", tags=["Architecture"])

# Milestone 1: ML-based pattern inference -> ArchitecturePlan
planner = ArchitecturePlanner()

# Milestone 2/3/4: Ollama-based planner agent (lazy init)
_AGENT: PlannerAgent | None = None


def _as_dict(model_obj: Any) -> dict[str, Any]:
    """Pydantic v2 (model_dump) and v1 (dict) compatibility."""
    if model_obj is None:
        return {}
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump(mode="json")
    return model_obj.dict()


def _is_ollama_down(msg: str) -> bool:
    msg = (msg or "").lower()
    return any(
        s in msg
        for s in [
            "connection",
            "refused",
            "timed out",
            "timeout",
            "localhost:11434",
            "failed to establish a new connection",
            "max retries exceeded",
        ]
    )


def _get_agent() -> PlannerAgent:
    global _AGENT
    if _AGENT is None:
        ollama = OllamaClient(base_url="http://localhost:11434", model="llama3.1:8b")
        _AGENT = PlannerAgent(client=ollama)
    return _AGENT


def _resolve_plan_from_scaffold_payload(
    payload: ScaffoldRequest,
) -> AgentArchitecturePlan:
    """
    Resolve plan from scaffold payload:
    - If payload.plan provided, use it
    - Else if payload.idea provided, call agent.plan()
    - Else 422
    """
    agent = _get_agent()

    if payload.plan is not None:
        return payload.plan
    if payload.idea is not None:
        return agent.plan(_as_dict(payload.idea))

    raise HTTPException(
        status_code=422,
        detail="Provide either 'plan' or 'idea' in the request body.",
    )


@router.post("/preview", response_model=ArchitecturePlan)
def preview_architecture(idea: ProjectIdeaInput) -> ArchitecturePlan:
    """Milestone 1: ML model + encoder -> ArchitecturePlan."""
    try:
        return planner.plan(_as_dict(idea))
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-plan", response_model=AgentArchitecturePlan)
def agent_plan(idea: ProjectIdeaInput) -> AgentArchitecturePlan:
    """Milestone 2: Ollama -> structured AgentArchitecturePlan."""
    try:
        agent = _get_agent()
        return agent.plan(_as_dict(idea))
    except Exception as e:
        if _is_ollama_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Ollama is not reachable. Start Ollama and confirm it is accessible at "
                    "http://localhost:11434 (and the model tag exists)."
                ),
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagram-from-idea", response_model=DiagramPipelineResponse)
def diagram_from_idea(payload: DiagramPipelineRequest) -> DiagramPipelineResponse:
    """Milestone 3: idea -> agent-plan -> mermaid."""
    try:
        agent = _get_agent()

        plan = agent.plan(_as_dict(payload.idea))
        mermaid = build_mermaid(
            plan=plan,
            diagram_type=payload.diagram_type,
            title=payload.title,
        )

        return DiagramPipelineResponse(
            diagram_type=payload.diagram_type,
            title=payload.title,
            mermaid=mermaid,
            plan=plan,
            render_url=None,
        )

    except Exception as e:
        if _is_ollama_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Ollama is not reachable. Start Ollama and confirm it is accessible at "
                    "http://localhost:11434 (and the model tag exists)."
                ),
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scaffold", response_model=ScaffoldResponse)
def scaffold_repo(payload: ScaffoldRequest) -> ScaffoldResponse:
    """Milestone 4: plan or idea -> repo tree + file contents."""
    try:
        plan = _resolve_plan_from_scaffold_payload(payload)

        tree, files = generate_repo_scaffold(
            plan=plan,
            project_slug=payload.project_slug,
            include_docker=payload.include_docker,
            include_github_actions=payload.include_github_actions,
        )

        return ScaffoldResponse(
            project_slug=payload.project_slug,
            tree=tree,
            files=files,
            plan=plan,
        )

    except Exception as e:
        if _is_ollama_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Ollama is not reachable. Start Ollama and confirm it is accessible at "
                    "http://localhost:11434 (and the model tag exists)."
                ),
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scaffold/zip", response_class=Response)
def scaffold_repo_zip(payload: ScaffoldRequest) -> Response:
    """Milestone 4.1: downloadable zip containing the generated scaffold repo."""
    try:
        plan = _resolve_plan_from_scaffold_payload(payload)

        _tree, files = generate_repo_scaffold(
            plan=plan,
            project_slug=payload.project_slug,
            include_docker=payload.include_docker,
            include_github_actions=payload.include_github_actions,
        )

        zip_bytes = build_scaffold_zip_bytes(files)
        filename = f"{payload.project_slug or 'generated_project'}.zip"

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        if _is_ollama_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Ollama is not reachable. Start Ollama and confirm it is accessible at "
                    "http://localhost:11434 (and the model tag exists)."
                ),
            )
        raise HTTPException(status_code=500, detail=str(e))
