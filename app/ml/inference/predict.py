from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd


MODEL_PATH = Path("artifacts/models/pattern_model.joblib")
ENCODER_PATH = Path("artifacts/models/pattern_encoder.joblib")


class PatternPredictor:
    def __init__(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Missing model at {MODEL_PATH}. Train it with: python -m app.ml.training.train_pattern"
            )
        if not ENCODER_PATH.exists():
            raise FileNotFoundError(
                f"Missing encoder at {ENCODER_PATH}. Train it with: python -m app.ml.training.train_pattern"
            )

        self.model = joblib.load(MODEL_PATH)
        self.encoder = joblib.load(ENCODER_PATH)

    def predict(self, features: Dict[str, Any]) -> str:
        # Keep exactly the same feature columns used in training
        X = pd.DataFrame(
            [{
                "domain": features.get("domain", "unknown"),
                "scale": features.get("scale", "prototype"),
                "budget": features.get("budget", "low"),
            }]
        )

        X_enc = self.encoder.transform(X)
        pred = self.model.predict(X_enc)[0]
        return str(pred)
