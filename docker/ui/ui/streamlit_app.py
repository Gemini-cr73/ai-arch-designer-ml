import base64
import json
import os
import re
from typing import Any

import requests
import streamlit as st


# -----------------------------
# Config
# -----------------------------
def get_api_base_url() -> str:
    # 1) Try Streamlit secrets IF available (won't crash if secrets.toml is missing)
    try:
        if "API_BASE_URL" in st.secrets:
            return str(st.secrets["API_BASE_URL"]).rstrip("/")
    except Exception:
        pass

    # 2) Fall back to env var
    env_url = os.getenv("API_BASE_URL")
    if env_url:
        return env_url.rstrip("/")

    # 3) Default local API
    return "http://localhost:8000"


API_BASE_URL = get_api_base_url()

# ✅ Endpoints from your Swagger
PREVIEW_ENDPOINT = f"{API_BASE_URL}/architect/preview"
AGENT_PLAN_ENDPOINT = f"{API_BASE_URL}/architect/agent-plan"
DIAGRAM_ENDPOINT = f"{API_BASE_URL}/architect/diagram-from-idea"
SCAFFOLD_ENDPOINT = f"{API_BASE_URL}/architect/scaffold"
ZIP_ENDPOINT = f"{API_BASE_URL}/architect/scaffold/zip"

DEFAULT_TIMEOUT = 60  # seconds


# -----------------------------
# Helpers
# -----------------------------
def safe_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def mermaid_ink_url(mermaid_code: str) -> str:
    """
    Render Mermaid via mermaid.ink as SVG using base64.
    """
    raw = mermaid_code.encode("utf-8")
    b64 = base64.b64encode(raw).decode("ascii")
    return f"https://mermaid.ink/svg/{b64}"


def api_post_json_simple(
    url: str, payload: dict[str, Any]
) -> tuple[int, dict[str, Any], str]:
    """
    Returns (status_code, json_data_or_empty, raw_text)
    """
    r = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    try:
        return r.status_code, r.json(), r.text
    except Exception:
        return r.status_code, {}, r.text


def api_post_zip(
    url: str, payload: dict[str, Any]
) -> tuple[int, bytes, dict[str, str], str]:
    """
    Returns (status_code, zip_bytes, headers, error_text_if_any)
    """
    r = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    if r.status_code != 200:
        return r.status_code, b"", dict(r.headers), r.text
    return r.status_code, r.content, dict(r.headers), ""


def guess_zip_filename(headers: dict[str, str]) -> str:
    cd = headers.get("content-disposition", "") or headers.get(
        "Content-Disposition", ""
    )
    m = re.search(r'filename="?([^"]+)"?', cd, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    return "generated_project.zip"


def get_first_str(d: dict[str, Any], keys: list[str]) -> str | None:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def extract_mermaid(diagram_response: dict[str, Any]) -> str | None:
    """
    diagram-from-idea returns DiagramPipelineResponse with a 'mermaid' field.
    """
    return get_first_str(diagram_response, ["mermaid"])


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="AI Architecture Designer", page_icon="🧠", layout="wide")

st.title("🧠 AI Architecture Designer")
st.caption(
    "Turn project ideas into architecture plans, diagrams, and downloadable repo scaffolds."
)

with st.sidebar:
    st.subheader("🔌 API Connection")
    st.write("FastAPI backend base URL:")
    st.code(API_BASE_URL, language="text")

    st.divider()
    st.subheader("⚙️ Defaults")
    default_language = st.selectbox(
        "Preferred language", ["Python", "JavaScript/TypeScript", "Java", "Go"], index=0
    )
    default_cloud = st.selectbox(
        "Cloud target", ["Azure", "AWS", "GCP", "Local/On-Prem"], index=0
    )
    default_scale = st.select_slider(
        "Scale", options=["Prototype", "MVP", "Production"], value="MVP"
    )

    # ✅ Milestone 6 UI improvement: Diagram type selector (actually wired to API)
    diagram_type = st.selectbox(
        "Diagram type",
        ["flow", "system", "data_pipeline", "deployment"],
        index=0,
        help="This value is sent to /architect/diagram-from-idea as diagram_type.",
    )

    st.divider()
    st.subheader("🧩 Scaffold Options")
    include_docker = st.checkbox("Include Docker", value=True)
    include_github_actions = st.checkbox("Include GitHub Actions", value=True)

st.divider()

col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("1) Describe your project")
    idea = st.text_area(
        "Project idea",
        height=150,
        placeholder="Example: A web app that helps students track study habits and predicts burnout risk using ML.",
    )

    st.subheader("2) Constraints & preferences")
    project_name = st.text_input(
        "Project name (optional)", placeholder="e.g., StudyPulse"
    )
    domain = st.text_input(
        "Domain (optional)", placeholder="e.g., healthcare, fintech, education"
    )
    notes = st.text_area(
        "Extra notes (optional)",
        height=100,
        placeholder="Any must-haves, integrations, compliance needs...",
    )

    generate_btn = st.button(
        "✨ Generate Architecture", type="primary", use_container_width=True
    )

with col2:
    st.subheader("Status")
    status_box = st.empty()
    status_box.info("Ready. Enter an idea and click **Generate Architecture**.")

    st.subheader("Outputs")
    st.write("- Preview (ML) + Metrics")
    st.write("- Agent Plan (LLM)")
    st.write("- Mermaid diagram")
    st.write("- Scaffold + ZIP download")

# -----------------------------
# Session state
# -----------------------------
if "latest_preview" not in st.session_state:
    st.session_state.latest_preview = None  # /preview output
if "latest_plan" not in st.session_state:
    st.session_state.latest_plan = None  # /agent-plan output
if "latest_mermaid" not in st.session_state:
    st.session_state.latest_mermaid = None  # /diagram-from-idea mermaid string
if "latest_scaffold" not in st.session_state:
    st.session_state.latest_scaffold = None
if "latest_zip_bytes" not in st.session_state:
    st.session_state.latest_zip_bytes = None
if "latest_zip_name" not in st.session_state:
    st.session_state.latest_zip_name = None


# -----------------------------
# Payload builders (MATCH your ProjectIdeaInput)
# -----------------------------
def build_idea_payload() -> dict[str, Any]:
    resolved_name = (
        project_name.strip()
        if project_name and project_name.strip()
        else "Generated Project"
    )

    scale_map = {"Prototype": "prototype", "MVP": "startup", "Production": "enterprise"}
    resolved_scale = scale_map.get(default_scale, "startup")

    resolved_domain = domain.strip() if domain and domain.strip() else "General"

    # Your UI doesn't collect compliance/budget yet; safe defaults.
    compliance = (
        ["GDPR"] if resolved_domain.lower() in {"healthcare", "fintech"} else ["GDPR"]
    )
    budget = "medium"

    # Optionally blend notes into description (helps the planner)
    description = idea.strip()
    if notes and notes.strip():
        description = f"{description}\n\nNotes:\n{notes.strip()}"

    return {
        "name": resolved_name,
        "description": description,
        "domain": resolved_domain,
        "scale": resolved_scale,
        "expected_users": 5000,
        "compliance": compliance,
        "budget": budget,
    }


# -----------------------------
# Generate flow
# -----------------------------
if generate_btn:
    if not idea or not idea.strip():
        status_box.error("Please enter a project idea first.")
        st.stop()

    idea_payload = build_idea_payload()

    # 0) Preview (ML)
    status_box.info("Calling /architect/preview (ML) ...")
    pv_status, pv_data, pv_raw = api_post_json_simple(PREVIEW_ENDPOINT, idea_payload)
    if pv_status != 200:
        status_box.warning(f"Preview failed ({pv_status}). Continuing to LLM plan...")
        st.error("Preview error response:")
        st.code(pv_raw, language="text")
        st.session_state.latest_preview = None
    else:
        st.session_state.latest_preview = pv_data

    # 1) Agent Plan (LLM)
    status_box.info("Calling /architect/agent-plan ...")
    plan_status, plan_data, plan_raw = api_post_json_simple(
        AGENT_PLAN_ENDPOINT, idea_payload
    )
    if plan_status != 200:
        status_box.error(f"Agent plan failed ({plan_status}).")
        st.error("Agent plan error response:")
        st.code(plan_raw, language="text")
        st.stop()

    st.session_state.latest_plan = plan_data
    status_box.success("Agent plan generated ✅")

    # 2) Diagram (✅ diagram_type is now wired to dropdown)
    status_box.info("Calling /architect/diagram-from-idea ...")
    diagram_req = {
        "idea": idea_payload,
        "diagram_type": diagram_type,  # ✅ FIX: no longer hardcoded
        "title": idea_payload["name"],
    }

    # Optional debug: confirm what is being sent
    with st.expander("Debug: diagram request payload"):
        st.json(diagram_req)

    d_status, d_data, d_raw = api_post_json_simple(DIAGRAM_ENDPOINT, diagram_req)
    if d_status == 200:
        st.session_state.latest_mermaid = extract_mermaid(d_data)
    else:
        st.session_state.latest_mermaid = None
        with st.expander("Diagram endpoint error response"):
            st.code(d_raw, language="text")

    # 3) Scaffold
    status_box.info("Calling /architect/scaffold ...")
    scaffold_req = {
        "idea": idea_payload,
        "plan": plan_data,
        "project_slug": "generated_project",
        "include_docker": include_docker,
        "include_github_actions": include_github_actions,
    }
    sc_status, sc_data, sc_raw = api_post_json_simple(SCAFFOLD_ENDPOINT, scaffold_req)

    if sc_status != 200:
        status_box.warning(f"Scaffold failed ({sc_status}), but plan succeeded.")
        st.error("Scaffold error response:")
        st.code(sc_raw, language="text")
        st.session_state.latest_scaffold = None
    else:
        st.session_state.latest_scaffold = sc_data

    # 4) ZIP
    status_box.info("Calling /architect/scaffold/zip ...")
    zip_status, zip_bytes, zip_headers, zip_err = api_post_zip(
        ZIP_ENDPOINT, scaffold_req
    )

    if zip_status != 200:
        status_box.warning(f"ZIP failed ({zip_status}).")
        st.error("ZIP error response:")
        st.code(zip_err, language="text")
        st.session_state.latest_zip_bytes = None
        st.session_state.latest_zip_name = None
    else:
        zip_name = guess_zip_filename(zip_headers)
        st.session_state.latest_zip_bytes = zip_bytes
        st.session_state.latest_zip_name = zip_name
        status_box.success("✅ Done — ZIP ready for download")


# -----------------------------
# Display results
# -----------------------------
st.divider()

# Preview + Agent Plan side-by-side
top_left, top_right = st.columns([1, 1], gap="large")

with top_left:
    st.subheader("✅ Preview (ML) — ArchitecturePlan + Metrics")
    if st.session_state.latest_preview:
        # Show metrics if present (Milestone 6)
        pl = st.session_state.latest_preview.get("pattern_label")
        conf = st.session_state.latest_preview.get("confidence")
        if pl:
            st.markdown(f"**Predicted Pattern Label:** `{pl}`")
        if conf is not None:
            st.markdown(f"**Confidence:** `{conf}`")
        st.code(safe_json(st.session_state.latest_preview), language="json")
    else:
        st.info("No ML preview yet (or it failed).")

with top_right:
    st.subheader("🧠 Agent Plan (LLM) — AgentArchitecturePlan")
    if st.session_state.latest_plan:
        st.code(safe_json(st.session_state.latest_plan), language="json")
    else:
        st.info("No plan yet.")

st.divider()

# Diagram preview
st.subheader("🗺️ Diagram Preview (Mermaid)")
if st.session_state.latest_mermaid:
    st.caption("Rendered via mermaid.ink (SVG).")
    svg_url = mermaid_ink_url(st.session_state.latest_mermaid)
    st.components.v1.iframe(svg_url, height=520, scrolling=True)

    with st.expander("Show Mermaid code"):
        st.code(st.session_state.latest_mermaid, language="text")
else:
    st.info("No mermaid diagram yet (or diagram endpoint returned no mermaid).")

st.divider()

# Scaffold + ZIP download
c1, c2 = st.columns([1, 1], gap="large")

with c1:
    st.subheader("🌳 Scaffold Tree")
    scaffold = st.session_state.latest_scaffold
    if scaffold and "tree" in scaffold:
        st.code(safe_json(scaffold["tree"]), language="json")
    else:
        st.info("No scaffold tree available yet.")

with c2:
    st.subheader("⬇️ Download ZIP")
    if st.session_state.latest_zip_bytes and st.session_state.latest_zip_name:
        st.download_button(
            label=f"Download {st.session_state.latest_zip_name}",
            data=st.session_state.latest_zip_bytes,
            file_name=st.session_state.latest_zip_name,
            mime="application/zip",
            use_container_width=True,
        )
        st.caption("ZIP comes from /architect/scaffold/zip.")
    else:
        st.info("Generate an architecture to enable ZIP download.")
