from __future__ import annotations

import os
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

# ✅ IMPORTANT: Azure deployment must NOT depend on Ollama.
# We use Groq (hosted LLM) only.
from app.services.llm.groq_client import GroqClient
from app.services.planner.planner_service import ArchitecturePlanner
from app.services.scaffold.scaffold_generator import generate_repo_scaffold
from app.services.scaffold.zip_export import build_scaffold_zip_bytes

router = APIRouter(prefix="/architect", tags=["Architecture"])

# Milestone 1: ML-based pattern inference -> ArchitecturePlan
planner = ArchitecturePlanner()

# Milestone 2/3/4: LLM-based planner agent (lazy init)
_AGENT: PlannerAgent | None = None


def _as_dict(model_obj: Any) -> dict[str, Any]:
    """Pydantic v2 (model_dump) and v1 (dict) compatibility."""
    if model_obj is None:
        return {}
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump(mode="json")
    return model_obj.dict()


def _get_env(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    if val is None or str(val).strip() == "":
        return default
    return val


def _llm_provider() -> str:
    # Accept: LLM_PROVIDER (values like "groq", "ollama", etc.)
    return (_get_env("LLM_PROVIDER", "groq") or "groq").strip().lower()


def _is_provider_down(msg: str) -> bool:
    msg = (msg or "").lower()
    return any(
        s in msg
        for s in [
            "connection",
            "refused",
            "timed out",
            "timeout",
            "failed to establish a new connection",
            "max retries exceeded",
            "service unavailable",
            "502",
            "503",
            "504",
            "unauthorized",
            "forbidden",
            "api key",
            "invalid_api_key",
            "authentication",
            "permission",
            "rate limit",
            "quota",
        ]
    )


def _get_agent() -> PlannerAgent:
    """
    Build the PlannerAgent using the configured provider.

    ✅ Default: Groq (hosted) for Azure.
    ❌ Ollama is intentionally unsupported in Azure.
    """
    global _AGENT
    if _AGENT is not None:
        return _AGENT

    provider = _llm_provider()
    if provider != "groq":
        raise HTTPException(
            status_code=500,
            detail=(
                f"Invalid LLM_PROVIDER='{provider}'. Azure deployment must use Groq. "
                "Set LLM_PROVIDER=groq in Azure App Settings."
            ),
        )

    groq_api_key = _get_env("GROQ_API_KEY")
    groq_model = _get_env("GROQ_MODEL", "llama-3.1-8b-instant")

    if not groq_api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "GROQ_API_KEY is missing in environment variables. "
                "Add GROQ_API_KEY in Azure App Settings and restart the Web App."
            ),
        )

    client = GroqClient(api_key=groq_api_key, model=groq_model)
    _AGENT = PlannerAgent(client=client)
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
    if payload.plan is not None:
        return payload.plan

    if payload.idea is not None:
        agent = _get_agent()
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
    """Milestone 2: Groq -> structured AgentArchitecturePlan."""
    try:
        agent = _get_agent()
        return agent.plan(_as_dict(idea))
    except HTTPException:
        raise
    except Exception as e:
        if _is_provider_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "LLM provider is not reachable or not authorized. "
                    "Verify GROQ_API_KEY and GROQ_MODEL in Azure App Settings."
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

    except HTTPException:
        raise
    except Exception as e:
        if _is_provider_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "LLM provider is not reachable or not authorized. "
                    "Verify GROQ_API_KEY and GROQ_MODEL in Azure App Settings."
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

    except HTTPException:
        raise
    except Exception as e:
        if _is_provider_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "LLM provider is not reachable or not authorized. "
                    "Verify GROQ_API_KEY and GROQ_MODEL in Azure App Settings."
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
            include_github_actions=payload.include_docker,
        )

        zip_bytes = build_scaffold_zip_bytes(files)
        filename = f"{payload.project_slug or 'generated_project'}.zip"

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        if _is_provider_down(str(e)):
            raise HTTPException(
                status_code=503,
                detail=(
                    "LLM provider is not reachable or not authorized. "
                    "Verify GROQ_API_KEY and GROQ_MODEL in Azure App Settings."
                ),
            )
        raise HTTPException(status_code=500, detail=str(e))
