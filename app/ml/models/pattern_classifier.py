# app/ml/models/pattern_classifier.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
from sklearn.ensemble import RandomForestClassifier


@dataclass
class PatternClassifier:
    """
    Wrapper around a scikit-learn classifier for architecture pattern prediction.

    Training:
      - defaults to RandomForestClassifier and supports train()

    Inference:
      - load() a persisted model (.joblib) into self.model
    """

    model: Any | None = None

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = RandomForestClassifier(
                n_estimators=200,
                random_state=42,
                n_jobs=-1,
            )

    def train(self, X: Any, y: Any) -> None:
        if self.model is None:
            raise RuntimeError("Model is not initialized.")
        self.model.fit(X, y)

    def predict(self, X: Any) -> Any:
        if self.model is None:
            raise RuntimeError("Model is not loaded/initialized.")
        return self.model.predict(X)

    def predict_proba(self, X: Any) -> Any:
        if self.model is None:
            raise RuntimeError("Model is not loaded/initialized.")
        if not hasattr(self.model, "predict_proba"):
            raise RuntimeError("Underlying model does not support predict_proba().")
        return self.model.predict_proba(X)

    def save(self, path: str | Path) -> None:
        if self.model is None:
            raise RuntimeError("Nothing to save. Model is not loaded/initialized.")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, p)

    def load(self, path: str | Path) -> None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Model file not found: {p}")
        self.model = joblib.load(p)

    @classmethod
    def from_file(cls, path: str | Path) -> PatternClassifier:
        inst = cls(model=None)
        inst.load(path)
        return inst
