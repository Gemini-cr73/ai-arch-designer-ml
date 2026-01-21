from __future__ import annotations

from app.core.schemas.agent_plan import AgentArchitecturePlan
from app.services.diagrams.mermaid_builder import build_mermaid


class DiagramService:
    def to_mermaid(
        self,
        plan: AgentArchitecturePlan,
        diagram_type: str = "flow",
        title: str | None = None,
    ) -> str:
        return build_mermaid(plan=plan, diagram_type=diagram_type, title=title)
