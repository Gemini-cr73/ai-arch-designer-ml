# app/services/scaffold/templates.py

from __future__ import annotations

import json
from datetime import datetime
from textwrap import dedent

from app.core.schemas.agent_plan import AgentArchitecturePlan


def _safe_title(plan: AgentArchitecturePlan) -> str:
    comps = getattr(plan, "components", None) or []
    first = comps[0] if comps else None
    name = getattr(first, "name", None) if first else None
    name = (name or "").strip()
    return f"{name} Project" if name else "Generated Project"


def _md_bullets(items: list[str] | None, empty: str) -> str:
    items = items or []
    return "\n".join(f"- {x}" for x in items) if items else f"- {empty}"


def _format_deployment(deployment: object) -> str:
    """
    deployment may be a string OR a dict (LLM variance).
    Render it safely as readable markdown.
    """
    if deployment is None or deployment == "":
        return "(not specified)"

    if isinstance(deployment, str):
        d = deployment.strip()
        return d if d else "(not specified)"

    # dict / other JSON-like
    try:
        return (
            "```json\n" + json.dumps(deployment, indent=2, ensure_ascii=False) + "\n```"
        )
    except Exception:
        return str(deployment)


def render_readme(plan: AgentArchitecturePlan, project_slug: str) -> str:
    title = _safe_title(plan)

    components = getattr(plan, "components", None) or []
    comp_lines: list[str] = []
    for c in components:
        name = getattr(c, "name", "") or "Component"
        role = getattr(c, "role", "") or ""
        tech_list = getattr(c, "technologies", None) or []
        tech = f" (Tech: {', '.join(tech_list)})" if tech_list else ""
        comp_lines.append(f"- **{name}**: {role}{tech}".rstrip())

    bullets = "\n".join(comp_lines) if comp_lines else "- (No components provided)"

    deployment_val = getattr(plan, "deployment", None)
    deployment = _format_deployment(deployment_val)

    scaling = (getattr(plan, "scaling", None) or "").strip() or "(not specified)"
    security = _md_bullets(getattr(plan, "security", None), "None provided")

    body = f"""
    # {project_slug}

    {title}

    ## Overview
    This repository scaffold was generated from an **ML-first architecture workflow**:
    - **ML preview** predicts an architecture pattern and returns metrics/metadata.
    - **LLM agent plan** is **optional** and used only to generate a structured plan for scaffolding/diagrams.

    ## Architecture Components (from Agent Plan)
    {bullets}

    ## Deployment
    {deployment}

    ## Scaling
    {scaling}

    ## Security Notes
    {security}

    ## Run Locally
    ```bash
    python -m venv .venv
    # Windows PowerShell:
    # .venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```

    ## API Docs
    - Swagger: http://127.0.0.1:8000/docs

    Generated on {datetime.utcnow().isoformat()}Z
    """

    return dedent(body).strip() + "\n"


def render_main_py() -> str:
    return (
        dedent(
            """
            from __future__ import annotations

            from fastapi import FastAPI

            app = FastAPI(title="Generated API", version="0.1.0")


            @app.get("/health")
            def health():
                return {"status": "ok"}
            """
        ).strip()
        + "\n"
    )


def render_requirements_txt() -> str:
    return (
        dedent(
            """
            fastapi>=0.110
            uvicorn[standard]>=0.27
            pydantic>=2.0
            """
        ).strip()
        + "\n"
    )


def render_gitignore() -> str:
    return (
        dedent(
            """
            .venv/
            __pycache__/
            *.pyc
            .DS_Store
            .env
            """
        ).strip()
        + "\n"
    )


def render_env_example() -> str:
    return (
        dedent(
            """
            # Example environment variables
            APP_ENV=local
            """
        ).strip()
        + "\n"
    )


def render_dockerfile() -> str:
    return (
        dedent(
            """
            FROM python:3.12-slim

            WORKDIR /app
            COPY requirements.txt /app/requirements.txt
            RUN pip install --no-cache-dir -r /app/requirements.txt

            COPY app /app/app

            EXPOSE 8000
            CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
            """
        ).strip()
        + "\n"
    )


def render_docker_compose() -> str:
    return (
        dedent(
            """
            services:
              api:
                build: .
                ports:
                  - "8000:8000"
            """
        ).strip()
        + "\n"
    )
