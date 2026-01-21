import base64
import json
import os
import re
from typing import Any

import requests
import streamlit as st

# =========================================================
# Page Config (MUST be first Streamlit call)
# =========================================================
st.set_page_config(
    page_title="AI Architecture Designer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# Sidebar Toggle (Hide / Show Controls)
# =========================================================
if "sidebar_hidden" not in st.session_state:
    st.session_state.sidebar_hidden = False


def _toggle_sidebar():
    st.session_state.sidebar_hidden = not st.session_state.sidebar_hidden


top_left, _ = st.columns([1, 9])
with top_left:
    st.button(
        "☰ Controls" if st.session_state.sidebar_hidden else "✖ Hide",
        on_click=_toggle_sidebar,
        use_container_width=True,
    )

if st.session_state.sidebar_hidden:
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] { display: none !important; }
          [data-testid="stAppViewContainer"] .main .block-container {
              padding-left: 2rem;
              padding-right: 2rem;
              max-width: 100% !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Config
# =========================================================
def _get_secret(key: str) -> str | None:
    try:
        if key in st.secrets:
            v = str(st.secrets[key]).strip()
            return v or None
    except Exception:
        return None
    return None


def get_api_public_url() -> str:
    """
    What Streamlit should DISPLAY in the sidebar for users to copy/paste.
    - Prefer API_PUBLIC_URL if set (compose sets this to http://localhost:8000)
    """
    v = os.getenv("API_PUBLIC_URL") or _get_secret("API_PUBLIC_URL")
    if v:
        return v.rstrip("/")
    # fallback: show internal if that's all we have
    v2 = os.getenv("API_BASE_URL") or _get_secret("API_BASE_URL")
    return (v2 or "http://localhost:8000").rstrip("/")


def get_api_internal_url() -> str:
    """
    What Streamlit should CALL server-side.
    - In docker-compose, this must be http://api:8000 (service name)
    """
    v = os.getenv("API_BASE_URL") or _get_secret("API_BASE_URL")
    return (v or "http://localhost:8000").rstrip("/")


API_PUBLIC_URL = get_api_public_url()
API_INTERNAL_URL = get_api_internal_url()

# Endpoints MUST use the INTERNAL URL (container -> container calls)
PREVIEW_ENDPOINT = f"{API_INTERNAL_URL}/architect/preview"
AGENT_PLAN_ENDPOINT = f"{API_INTERNAL_URL}/architect/agent-plan"
DIAGRAM_ENDPOINT = f"{API_INTERNAL_URL}/architect/diagram-from-idea"
SCAFFOLD_ENDPOINT = f"{API_INTERNAL_URL}/architect/scaffold"
ZIP_ENDPOINT = f"{API_INTERNAL_URL}/architect/scaffold/zip"

DEFAULT_TIMEOUT = 60


# =========================================================
# API Helper (better errors)
# =========================================================
def call_api(method: str, url: str, payload: dict | None = None, timeout: int = 60):
    try:
        if method.upper() == "POST":
            r = requests.post(url, json=payload, timeout=timeout)
        else:
            r = requests.get(url, timeout=timeout)

        if not r.ok:
            st.error(f"API Error ({r.status_code}) — {url}")
            try:
                st.code(r.json(), language="json")
            except Exception:
                st.code(r.text)
            return None

        return r.json()

    except requests.RequestException as e:
        st.error(f"Network/API call failed: {e}")
        return None


# =========================================================
# Helpers
# =========================================================
def safe_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def mermaid_ink_url(mermaid_code: str) -> str:
    raw = mermaid_code.encode("utf-8")
    b64 = base64.b64encode(raw).decode("ascii")
    return f"https://mermaid.ink/svg/{b64}"


def api_post_zip(url: str, payload: dict[str, Any]):
    r = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    if r.status_code != 200:
        return None, r.text
    return r, None


def guess_zip_filename(headers: dict[str, str]) -> str:
    cd = headers.get("content-disposition", "") or headers.get(
        "Content-Disposition", ""
    )
    m = re.search(r'filename="?([^"]+)"?', cd, flags=re.IGNORECASE)
    return m.group(1) if m else "generated_project.zip"


def extract_mermaid(d: dict[str, Any]) -> str | None:
    v = d.get("mermaid")
    return v if isinstance(v, str) and v.strip() else None


# =========================================================
# UI
# =========================================================
st.title("🧠 AI Architecture Designer")
st.caption("Turn project ideas into architecture plans, diagrams, and repo scaffolds.")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.subheader("🔌 API Connection")
    # SHOW the public URL (what user can open/copy)
    st.code(API_PUBLIC_URL)

    # Optional: show internal URL for debugging
    with st.expander("Debug (internal URL)", expanded=False):
        st.code(API_INTERNAL_URL)

    st.divider()
    st.subheader("⚙️ Defaults")

    default_language = st.selectbox(
        "Preferred language", ["Python", "JavaScript/TypeScript", "Java", "Go"], index=0
    )
    default_cloud = st.selectbox(
        "Cloud target", ["Azure", "AWS", "GCP", "Local"], index=0
    )
    default_scale = st.select_slider(
        "Scale", options=["Prototype", "MVP", "Production"], value="MVP"
    )

    # ✅ Friendly UI labels → safe backend enum
    ui_label = st.selectbox(
        "Diagram type", ["Flow", "Component", "Deployment"], index=0
    )

    DIAGRAM_TYPE_MAP = {
        "Flow": "flow",
        "Component": "component",
        "Deployment": "flow",  # safe fallback until backend supports deployment
    }
    diagram_type = DIAGRAM_TYPE_MAP.get(ui_label, "flow")

    st.divider()
    st.subheader("🧩 Scaffold Options")
    include_docker = st.checkbox("Include Docker", value=True)
    include_github_actions = st.checkbox("Include GitHub Actions", value=True)

# ---------------- Main Layout ----------------
col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("1) Describe your project")
    idea = st.text_area(
        "Project idea",
        height=150,
        placeholder="Example: A web app that predicts churn using ML and dashboards.",
    )

    st.subheader("2) Constraints & preferences")
    project_name = st.text_input("Project name (optional)")
    domain = st.text_input("Domain (optional)")
    notes = st.text_area("Extra notes (optional)", height=100)

    generate_btn = st.button(
        "✨ Generate Architecture", type="primary", use_container_width=True
    )

with col2:
    st.subheader("Status")
    status_box = st.empty()
    status_box.info("Ready.")

    st.subheader("Outputs")
    st.write("- ML Preview + Metrics")
    st.write("- LLM Agent Plan")
    st.write("- Mermaid Diagram")
    st.write("- Scaffold ZIP")


# =========================================================
# Session State
# =========================================================
for k in [
    "latest_preview",
    "latest_plan",
    "latest_mermaid",
    "latest_scaffold",
    "latest_zip_bytes",
    "latest_zip_name",
]:
    st.session_state.setdefault(k, None)


# =========================================================
# Payload Builder
# =========================================================
def build_idea_payload() -> dict[str, Any]:
    name = project_name.strip() if project_name else "Generated Project"
    scale_map = {"Prototype": "prototype", "MVP": "startup", "Production": "enterprise"}
    resolved_scale = scale_map.get(default_scale, "startup")
    resolved_domain = domain.strip() if domain else "General"

    description = idea.strip()
    if notes:
        description += f"\n\nNotes:\n{notes.strip()}"

    return {
        "name": name,
        "description": description,
        "domain": resolved_domain,
        "scale": resolved_scale,
        "expected_users": 5000,
        "compliance": ["GDPR"],
        "budget": "medium",
    }


# =========================================================
# Generate Flow
# =========================================================
if generate_btn:
    if not idea.strip():
        status_box.error("Please enter a project idea.")
        st.stop()

    idea_payload = build_idea_payload()

    status_box.info("ML Preview...")
    st.session_state.latest_preview = call_api("POST", PREVIEW_ENDPOINT, idea_payload)

    status_box.info("LLM Agent Plan...")
    plan = call_api("POST", AGENT_PLAN_ENDPOINT, idea_payload)
    if not plan:
        status_box.error("Agent plan failed.")
        st.stop()
    st.session_state.latest_plan = plan

    status_box.info("Diagram...")
    diagram_req = {
        "idea": idea_payload,
        "diagram_type": diagram_type,
        "title": idea_payload["name"],
    }
    diagram = call_api("POST", DIAGRAM_ENDPOINT, diagram_req)
    st.session_state.latest_mermaid = extract_mermaid(diagram) if diagram else None

    status_box.info("Scaffold...")
    scaffold_req = {
        "idea": idea_payload,
        "plan": plan,
        "project_slug": "generated_project",
        "include_docker": include_docker,
        "include_github_actions": include_github_actions,
    }
    st.session_state.latest_scaffold = call_api("POST", SCAFFOLD_ENDPOINT, scaffold_req)

    status_box.info("ZIP...")
    zip_resp, zip_err = api_post_zip(ZIP_ENDPOINT, scaffold_req)
    if zip_resp:
        st.session_state.latest_zip_bytes = zip_resp.content
        st.session_state.latest_zip_name = guess_zip_filename(zip_resp.headers)
        status_box.success("✅ Done")
    else:
        st.error(zip_err)


# =========================================================
# Display Results
# =========================================================
st.divider()

l, r = st.columns(2)

with l:
    st.subheader("Preview (ML)")
    if st.session_state.latest_preview:
        st.code(safe_json(st.session_state.latest_preview), language="json")
    else:
        st.info("No preview yet.")

with r:
    st.subheader("Agent Plan (LLM)")
    if st.session_state.latest_plan:
        st.code(safe_json(st.session_state.latest_plan), language="json")
    else:
        st.info("No plan yet.")

st.divider()

st.subheader("Mermaid Diagram")
if st.session_state.latest_mermaid:
    st.components.v1.iframe(
        mermaid_ink_url(st.session_state.latest_mermaid), height=520, scrolling=True
    )
else:
    st.info("No diagram yet.")

st.divider()

l2, r2 = st.columns(2)

with l2:
    st.subheader("Scaffold Tree")
    if st.session_state.latest_scaffold and "tree" in st.session_state.latest_scaffold:
        st.code(safe_json(st.session_state.latest_scaffold["tree"]), language="json")
    else:
        st.info("No scaffold yet.")

with r2:
    st.subheader("Download ZIP")
    if st.session_state.latest_zip_bytes:
        st.download_button(
            "Download Project ZIP",
            data=st.session_state.latest_zip_bytes,
            file_name=st.session_state.latest_zip_name or "project.zip",
            mime="application/zip",
            use_container_width=True,
        )
    else:
        st.info("Generate architecture first.")
