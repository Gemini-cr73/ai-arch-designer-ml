from __future__ import annotations

from typing import Literal

from app.core.schemas.agent_plan import AgentArchitecturePlan


def build_mermaid(
    plan: AgentArchitecturePlan,
    diagram_type: Literal["flow", "component"] = "flow",
    title: str | None = None,
) -> str:
    if diagram_type == "component":
        return _component_diagram(plan, title=title)
    return _flow_diagram(plan, title=title)


def _sanitize_id(s: str) -> str:
    # Mermaid node IDs: safest is letters/numbers/underscore only
    out = []
    for ch in s or "":
        out.append(ch if ch.isalnum() else "_")
    cleaned = "".join(out).strip("_")
    return cleaned or "node"


def _escape_label(s: str) -> str:
    # Mermaid labels are quoted. Escape quotes.
    return (s or "").replace('"', '\\"')


def _make_unique_ids(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    ids: list[str] = []
    for n in names:
        base = _sanitize_id(n)
        count = seen.get(base, 0) + 1
        seen[base] = count
        ids.append(base if count == 1 else f"{base}_{count}")
    return ids


def _component_diagram(plan: AgentArchitecturePlan, title: str | None = None) -> str:
    lines: list[str] = ["flowchart TB"]
    if title:
        lines.append(f"%% {_escape_label(title)}")

    comps = list(plan.components or [])
    if not comps:
        return "flowchart TB\nA[No components]\n"

    names = [c.name for c in comps]
    node_ids = _make_unique_ids(names)

    # Build name->id mapping in order
    name_to_id: dict[str, str] = {}
    for idx, c in enumerate(comps):
        name_to_id[c.name] = node_ids[idx]

    # Nodes
    for idx, c in enumerate(comps):
        nid = node_ids[idx]
        tech = ", ".join(c.technologies or [])
        label_parts = [c.name]
        if getattr(c, "role", None):
            label_parts.append(c.role)
        if tech:
            label_parts.append(f"[{tech}]")
        label = _escape_label("\\n".join(label_parts))
        lines.append(f'{nid}["{label}"]')

    # Simple sequential edges
    for i in range(len(node_ids) - 1):
        lines.append(f"{node_ids[i]} --> {node_ids[i + 1]}")

    return "\n".join(lines) + "\n"


def _flow_diagram(plan: AgentArchitecturePlan, title: str | None = None) -> str:
    """
    Heuristic flow:
    - Pick an entry node (gateway/api/ui)
    - Connect entry -> others
    """
    lines: list[str] = ["flowchart LR"]
    if title:
        lines.append(f"%% {_escape_label(title)}")

    comps = list(plan.components or [])
    if not comps:
        return "flowchart LR\nA[No components]\n"

    def score_entry(name: str) -> int:
        n = (name or "").lower()
        score = 0
        if "gateway" in n or "api" in n:
            score += 3
        if "ui" in n or "frontend" in n or "client" in n:
            score += 2
        return score

    entry = max(comps, key=lambda c: score_entry(c.name))

    names = [c.name for c in comps]
    node_ids = _make_unique_ids(names)

    name_to_id: dict[str, str] = {}
    for i, name in enumerate(names):
        name_to_id[name] = node_ids[i]

    entry_id = name_to_id.get(entry.name, _sanitize_id(entry.name))

    # Nodes
    for c in comps:
        nid = name_to_id.get(c.name, _sanitize_id(c.name))
        lines.append(f'{nid}["{_escape_label(c.name)}"]')

    # Edges: entry -> others
    for c in comps:
        if c.name == entry.name:
            continue
        lines.append(f"{entry_id} --> {name_to_id.get(c.name, _sanitize_id(c.name))}")

    return "\n".join(lines) + "\n"
