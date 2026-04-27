# ui/streamlit_app.py

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any, Literal

import requests
import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# Page config (must be first)
# -----------------------------
st.set_page_config(
    page_title="AI Architecture Designer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_TIMEOUT = 60


# -----------------------------
# Config helpers
# -----------------------------
def _get_secret(key: str) -> str | None:
    try:
        if key in st.secrets:
            v = str(st.secrets[key]).strip()
            return v or None
    except Exception:
        return None
    return None


def _default_api_base_url() -> str:
    v = os.getenv("API_BASE_URL") or _get_secret("API_BASE_URL")
    return (v or "http://127.0.0.1:8000").rstrip("/")


# Allow override via UI
st.session_state.setdefault("api_base_url", _default_api_base_url())


# -----------------------------
# UI helpers
# -----------------------------
def render_logo(width: int = 56) -> None:
    logo_path = (
        os.getenv("LOGO_PATH") or _get_secret("LOGO_PATH") or "ui/assets/logo.png"
    )
    p = Path(logo_path)
    if p.exists():
        st.image(str(p), width=width)
    else:
        st.markdown("### 🧠")


def render_mermaid_interactive(mermaid_code: str, height: int = 520) -> None:
    if not mermaid_code or not mermaid_code.strip():
        st.info("No Mermaid diagram to render yet.")
        return

    safe_code = html.escape(mermaid_code.strip())

    html_doc = f"""
    <div class="mermaid">
    {safe_code}
    </div>

    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
      mermaid.initialize({{
        startOnLoad: true,
        theme: "dark",
        securityLevel: "loose"
      }});
    </script>
    """

    components.html(html_doc, height=height, scrolling=True)


# -----------------------------
# API helpers
# -----------------------------
def call_api(
    method: Literal["GET", "POST"],
    path: str,
    payload: dict | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict | None:
    base = (st.session_state.get("api_base_url") or "").rstrip("/")
    url = f"{base}{path}"

    try:
        if method == "POST":
            r = requests.post(url, json=payload, timeout=timeout)
        else:
            r = requests.get(url, timeout=timeout)

        if not r.ok:
            st.error(f"API error {r.status_code} — {method} {path}")
            try:
                st.code(r.json(), language="json")
            except Exception:
                st.code(r.text)
            return None

        return r.json()

    except requests.RequestException as e:
        st.error(f"Network/API call failed for {method} {path}: {e}")
        return None


def pretty_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


# -----------------------------
# Session State
# -----------------------------
st.session_state.setdefault("dataset_key", "nasa_promise")
st.session_state.setdefault("features_config", {"mode": "default"})
st.session_state.setdefault("latest_train_eval", None)
st.session_state.setdefault("latest_diagnostics", None)
st.session_state.setdefault("latest_llm_explain", None)

st.session_state.setdefault("latest_arch_preview", None)
st.session_state.setdefault("latest_agent_plan", None)
st.session_state.setdefault("latest_diagram", None)
st.session_state.setdefault("latest_scaffold", None)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.subheader("🔌 API Connection")

    st.session_state["api_base_url"] = st.text_input(
        "API Base URL",
        value=st.session_state["api_base_url"],
        help="Example: http://127.0.0.1:8001",
    ).rstrip("/")

    health = (
        call_api("GET", "/health") if st.session_state.get("api_base_url") else None
    )

    if health:
        st.success("API: connected ✅")
    else:
        st.warning("API: not reachable ❌")

    with st.expander("Health check (raw)", expanded=False):
        st.code(pretty_json(health) if health else "No response")

    st.divider()

    st.subheader("🧭 Workflow")
    step = st.radio(
        "Go to",
        [
            "Dataset",
            "Feature Engineering",
            "Train & Evaluate",
            "Compare Models",
            "Architecture (Optional)",
            "Export & Save Results",
        ],
        index=2,
    )

    st.divider()

    st.subheader("⚙️ Defaults")
    st.caption("These control training + evaluation runs.")
    test_size = st.slider("Test size", 0.1, 0.4, 0.2, 0.05)
    random_state = st.number_input(
        "Random state", min_value=0, max_value=9999, value=42, step=1
    )

    st.divider()

    st.subheader("🧪 Algorithms")
    st.write("✅ Logistic Regression (baseline)")
    st.write("✅ Random Forest")
    st.write("✅ SVM")

    st.divider()

    st.subheader("🤖 LLM (optional, post-ML only)")
    enable_llm = st.checkbox("Enable post-ML explanation", value=False)
    st.caption("Only affects /ml/explain. Not required for ML training/eval.")


# -----------------------------
# Header
# -----------------------------
left, right = st.columns([0.08, 0.92])

with left:
    render_logo()

with right:
    st.markdown("# AI Architecture Designer")
    st.caption("ML-first decision support. LLM is optional and post-ML only.")


# -----------------------------
# Dataset Step
# -----------------------------
if step == "Dataset":
    st.header("Step 1 — Dataset")
    st.caption("Select one dataset. Each dataset is trained/evaluated independently.")

    dataset_label_to_key = {
        "NASA PROMISE Dataset": "nasa_promise",
        "Google Cluster Dataset": "google_cluster",
        "NASA Benchmark Dataset": "nasa_benchmark",
    }

    selected_label = st.selectbox(
        "Dataset",
        list(dataset_label_to_key.keys()),
        index=list(dataset_label_to_key.values()).index(st.session_state.dataset_key),
    )

    st.session_state.dataset_key = dataset_label_to_key[selected_label]

    st.success("Dataset selected. Next: Feature Engineering → Train & Evaluate.")
    st.info("Comparisons are within this dataset only.")


# -----------------------------
# Feature Engineering Step
# -----------------------------
elif step == "Feature Engineering":
    st.header("Step 2 — Feature Engineering")
    st.caption("Start with defaults; add dataset-specific options later.")

    mode = st.selectbox("Feature mode", ["default", "standardize_numeric"], index=0)
    st.session_state.features_config = {"mode": mode}

    st.success("Feature configuration saved for the next training run.")


# -----------------------------
# Train & Evaluate Step
# -----------------------------
elif step == "Train & Evaluate":
    st.header("Step 3 — Train & Evaluate Models")
    st.caption(
        "Compare supervised algorithms using the selected dataset and engineered features."
    )

    dataset_key = st.session_state.dataset_key

    key_to_label = {
        "nasa_promise": "NASA PROMISE Dataset",
        "google_cluster": "Google Cluster Dataset",
        "nasa_benchmark": "NASA Benchmark Dataset",
    }

    st.selectbox(
        "Dataset:",
        [key_to_label.get(dataset_key, dataset_key)],
        index=0,
        disabled=True,
    )

    colA, colB = st.columns([0.7, 0.3])

    with colA:
        st.write("")

    with colB:
        retrain = st.button("Retrain Models", use_container_width=True)

    if retrain:
        payload = {
            "dataset": dataset_key,
            "features": st.session_state.features_config,
            "split": {
                "test_size": float(test_size),
                "random_state": int(random_state),
            },
            "algorithms": ["logreg", "rf", "svm"],
        }

        result = call_api("POST", "/ml/train-eval", payload)
        st.session_state.latest_train_eval = result

        if result and result.get("run_id"):
            diag = call_api("POST", "/ml/diagnostics", {"run_id": result["run_id"]})
            st.session_state.latest_diagnostics = diag

    res = st.session_state.latest_train_eval

    if not res:
        st.info(
            "Click **Retrain Models** to compute LR/RF/SVM metrics and populate the cards."
        )
        st.stop()

    metrics: dict[str, dict[str, float]] = res.get("metrics") or {}
    best_key: str = res.get("best_model") or ""

    bm = metrics.get(best_key, {})

    bm_name = {
        "logreg": "Logistic Regression",
        "rf": "Random Forest",
        "svm": "SVM",
    }.get(best_key, "—")

    top1, top2 = st.columns([0.6, 0.4], gap="large")

    with top2:
        st.markdown("#### Best Model")
        st.markdown(f"**{bm_name}**")
        st.write(
            f"Accuracy: {bm.get('accuracy', 0.0):.1%}"
            if "accuracy" in bm
            else "Accuracy: —"
        )
        st.write(f"F1 Score: {bm.get('f1', 0.0):.1%}" if "f1" in bm else "F1 Score: —")
        st.write(
            f"ROC AUC: {bm.get('roc_auc', 0.0):.1%}"
            if "roc_auc" in bm
            else "ROC AUC: —"
        )
        st.caption(f"(Trained on {key_to_label.get(dataset_key, dataset_key)})")

    with top1:
        st.markdown("#### Model Comparison")

        c1, c2, c3 = st.columns(3)

        def card(title: str, m: dict[str, float]) -> None:
            st.markdown(f"**{title}**")
            st.write(
                f"Accuracy: {m.get('accuracy', 0.0):.1%}"
                if "accuracy" in m
                else "Accuracy: —"
            )
            st.write(
                f"F1 Score: {m.get('f1', 0.0):.1%}" if "f1" in m else "F1 Score: —"
            )
            st.write(
                f"ROC AUC: {m.get('roc_auc', 0.0):.1%}"
                if "roc_auc" in m
                else "ROC AUC: —"
            )

        with c1:
            card("Logistic Regression", metrics.get("logreg", {}))

        with c2:
            card("Random Forest", metrics.get("rf", {}))

        with c3:
            card("SVM", metrics.get("svm", {}))

    st.markdown("---")

    with st.expander("View Diagnostics", expanded=False):
        diag = st.session_state.latest_diagnostics

        if not diag:
            st.info("No diagnostics yet. Retrain models to compute diagnostics.")
        else:
            st.subheader("Diagnostics")
            st.caption(
                "Confusion matrices, ROC curves, and feature importance where applicable."
            )
            st.code(pretty_json(diag), language="json")

    if enable_llm:
        st.markdown("---")
        st.subheader("Post-ML Explanation (Optional)")
        st.caption("This is separate from architecture generation.")

        if st.button("Explain these results (LLM)", use_container_width=True):
            run_id = res.get("run_id")
            st.session_state.latest_llm_explain = call_api(
                "POST", "/ml/explain", {"run_id": run_id}
            )

        if st.session_state.latest_llm_explain:
            st.write(
                st.session_state.latest_llm_explain.get("text", "No explanation text.")
            )


# -----------------------------
# Compare Models Step
# -----------------------------
elif step == "Compare Models":
    st.header("Step 4 — Compare Models")
    st.caption("Richer comparison view will go here.")

    res = st.session_state.latest_train_eval

    if not res:
        st.info(
            "No training run yet. Go to **Train & Evaluate** and click Retrain Models."
        )
    else:
        st.code(pretty_json(res), language="json")


# -----------------------------
# Architecture Step
# -----------------------------
elif step == "Architecture (Optional)":
    st.header("Architecture (Optional)")
    st.caption(
        "Generates architecture outputs from a project idea. "
        "Mermaid generation uses the LLM agent, so GROQ_API_KEY must be set in the API environment."
    )

    st.subheader("Project idea")

    project_name = st.text_input("Name", "NASA Defect Prediction Classifier")
    project_domain = st.text_input("Domain", "ml", help="Required by backend schema.")

    scale_label_to_value = {
        "Prototype (small)": "prototype",
        "Startup (medium)": "startup",
        "Enterprise (large)": "enterprise",
    }

    scale_labels = list(scale_label_to_value.keys())
    project_scale_label = st.selectbox("Scale", scale_labels, index=1)
    project_scale = scale_label_to_value[project_scale_label]

    project_desc = st.text_area(
        "Description",
        "Build a supervised ML system that predicts whether a NASA software module is defective. "
        "Compare Logistic Regression (baseline), Random Forest, and SVM; report Accuracy, F1, ROC AUC; include confusion matrix.",
        height=120,
    )

    project_notes = st.text_area("Notes (optional)", "", height=80)

    col1, col2, col3 = st.columns([0.34, 0.33, 0.33])

    with col1:
        btn_preview = st.button(
            "Architecture Preview (ML-based)", use_container_width=True
        )

    with col2:
        btn_agent = st.button("LLM Agent Plan (Groq)", use_container_width=True)

    with col3:
        btn_diagram = st.button("Generate Mermaid Diagram", use_container_width=True)

    idea_payload = {
        "name": (project_name or "").strip(),
        "domain": (project_domain or "").strip(),
        "scale": (project_scale or "").strip(),
        "description": (project_desc or "").strip(),
        "notes": (project_notes or "").strip(),
    }

    if (btn_preview or btn_agent or btn_diagram) and (
        not idea_payload["name"] or not idea_payload["domain"]
    ):
        st.error("Name and Domain are required.")
        st.stop()

    if btn_preview:
        st.session_state.latest_arch_preview = call_api(
            "POST", "/architect/preview", idea_payload
        )

    if btn_agent:
        st.session_state.latest_agent_plan = call_api(
            "POST", "/architect/agent-plan", idea_payload
        )

    if btn_diagram:
        diagram_payload = {
            "diagram_type": "flow",
            "title": idea_payload["name"] or "Architecture Diagram",
            "idea": idea_payload,
        }

        st.session_state.latest_diagram = call_api(
            "POST", "/architect/diagram-from-idea", diagram_payload
        )

    st.markdown("---")

    with st.expander("Architecture Preview (ML-based)", expanded=True):
        if st.session_state.latest_arch_preview:
            st.code(pretty_json(st.session_state.latest_arch_preview), language="json")
        else:
            st.caption("No preview yet.")

    with st.expander("LLM Agent Plan (Groq)", expanded=False):
        if st.session_state.latest_agent_plan:
            st.code(pretty_json(st.session_state.latest_agent_plan), language="json")
        else:
            st.caption("No agent plan yet.")

    with st.expander("Mermaid Diagram (Interactive)", expanded=True):
        diagram = st.session_state.latest_diagram or {}
        mermaid = diagram.get("mermaid") if isinstance(diagram, dict) else None

        if mermaid:
            render_mermaid_interactive(mermaid, height=560)

            with st.expander("Mermaid source", expanded=False):
                st.code(mermaid, language="text")
        else:
            st.caption(
                "No Mermaid diagram yet. Click **Generate Mermaid Diagram** above."
            )


# -----------------------------
# Export Step
# -----------------------------
elif step == "Export & Save Results":
    st.header("Export & Save Results")
    st.caption("Export metrics + artifacts for reporting and reproducibility.")

    res = st.session_state.latest_train_eval
    diag = st.session_state.latest_diagnostics

    if not res:
        st.info("Nothing to export yet. Run Train & Evaluate first.")
        st.stop()

    st.subheader("Latest Run (JSON)")
    st.code(pretty_json(res), language="json")

    if diag:
        st.subheader("Latest Diagnostics (JSON)")
        st.code(pretty_json(diag), language="json")

    st.info("Next: add an API endpoint to download a results bundle as a ZIP.")
