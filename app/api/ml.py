# app/api/ml.py

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/train-eval")
def train_eval(payload: dict[str, Any]) -> dict[str, Any]:
    """
    TEMP scaffold so Streamlit stops 404'ing.
    Replace internals with your real ML pipeline (LR/RF/SVM) next.
    """
    dataset = payload.get("dataset", "nasa_promise")
    run_id = str(uuid4())

    metrics = {
        "logreg": {"accuracy": 0.705, "f1": 0.593, "roc_auc": 0.755},
        "rf": {"accuracy": 0.859, "f1": 0.791, "roc_auc": 0.911},
        "svm": {"accuracy": 0.833, "f1": 0.749, "roc_auc": 0.887},
    }

    return {
        "run_id": run_id,
        "dataset": dataset,
        "best_model": "rf",
        "metrics": metrics,
    }


@router.post("/diagnostics")
def diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    """
    TEMP scaffold. Later this should return:
    - confusion matrices for each model
    - ROC curve arrays (optional)
    - feature importance for RF (optional)
    """
    run_id = payload.get("run_id")

    return {
        "run_id": run_id,
        "confusion_matrices": {
            "logreg": {"tn": 50, "fp": 10, "fn": 12, "tp": 28},
            "rf": {"tn": 54, "fp": 6, "fn": 8, "tp": 32},
            "svm": {"tn": 53, "fp": 7, "fn": 9, "tp": 31},
        },
    }


@router.post("/explain")
def explain(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Optional post-ML LLM explanation endpoint.
    Keep it optional; return stub text for now.
    """
    run_id = payload.get("run_id")
    return {
        "run_id": run_id,
        "text": "Post-ML explanation is currently stubbed. Next step: summarize LR/RF/SVM tradeoffs and why RF is best on this dataset.",
    }
