from __future__ import annotations

from typing import Any

SYSTEM_PROMPT = """You are an expert software architect.
Return ONLY valid JSON. No markdown. No backticks. No extra text.

You must produce an AgentArchitecturePlan JSON with fields:
{
  "components": [{"name": "...", "role": "...", "technologies": ["..."]}],
  "deployment": "...",
  "scaling": "...",
  "security": ["..."]
}

Rules:
- components must be 3–6 items
- technologies must be concrete (e.g., FastAPI, Streamlit, PostgreSQL, Docker, Azure App Service)
- security must include 3–6 actionable items
"""


def build_user_prompt(project: dict[str, Any]) -> str:
    name = project.get("name", "").strip()
    desc = project.get("description", "").strip()
    domain = project.get("domain", "").strip()
    scale = project.get("scale", "").strip()
    users = project.get("expected_users", None)
    compliance = project.get("compliance", [])
    budget = project.get("budget", None)

    return f"""Design an agentic architecture plan for this project.

Project:
- name: {name}
- description: {desc}
- domain: {domain}
- scale: {scale}
- expected_users: {users}
- compliance: {compliance}
- budget: {budget}

Return ONLY JSON matching the schema exactly.
"""
