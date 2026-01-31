# app/ml/inference/predict.py

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


def _resolve_artifact_paths() -> tuple[Path, Path]:
    """
    Resolve model + encoder paths robustly in Docker/Azure.

    Expected inside container:
      /app/artifacts/models/pattern_model.joblib
      /app/artifacts/models/pattern_encoder.joblib
    """
    # 1) Best: explicit container root (we will set APP_ROOT=/app in Azure)
    app_root = os.getenv("APP_ROOT")
    if app_root:
        root = Path(app_root).resolve()
    else:
        # 2) Infer from file location:
        # /app/app/ml/inference/predict.py -> parents[3] == /app
        try:
            root = Path(__file__).resolve().parents[3]
        except Exception:
            # 3) Fallback
            root = Path.cwd().resolve()

    model_path = root / "artifacts" / "models" / "pattern_model.joblib"
    encoder_path = root / "artifacts" / "models" / "pattern_encoder.joblib"
    return model_path, encoder_path


MODEL_PATH, ENCODER_PATH = _resolve_artifact_paths()


class PatternPredictor:
    def __init__(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Missing model artifact.\n"
                f"Expected at: {MODEL_PATH}\n"
                f"CWD: {Path.cwd()}\n"
                f"APP_ROOT: {os.getenv('APP_ROOT')}\n"
                "Train it with: python -m app.ml.training.train_pattern"
            )
        if not ENCODER_PATH.exists():
            raise FileNotFoundError(
                "Missing encoder artifact.\n"
                f"Expected at: {ENCODER_PATH}\n"
                f"CWD: {Path.cwd()}\n"
                f"APP_ROOT: {os.getenv('APP_ROOT')}\n"
                "Train it with: python -m app.ml.training.train_pattern"
            )

        self.model = joblib.load(MODEL_PATH)
        self.encoder = joblib.load(ENCODER_PATH)

    def predict(self, features: dict[str, Any]) -> str:
        X = pd.DataFrame(
            [
                {
                    "domain": features.get("domain", "unknown"),
                    "scale": features.get("scale", "prototype"),
                    "budget": features.get("budget", "low"),
                }
            ]
        )

        X_enc = self.encoder.transform(X)
        pred = self.model.predict(X_enc)[0]
        return str(pred)
