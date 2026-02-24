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

    IMPORTANT:
    - train_pattern.py saves the *underlying sklearn model* (RandomForestClassifier) via joblib.
    - planner_service.py loads that same sklearn model directly with joblib.load(...)
      and calls predict / predict_proba on it.
    """

    model: Any | None = None

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced",
            )

    def train(self, X: Any, y: Any) -> None:
        if self.model is None:
            raise RuntimeError("PatternClassifier: Model is not initialized.")
        self.model.fit(X, y)

    def predict(self, X: Any) -> Any:
        if self.model is None:
            raise RuntimeError("PatternClassifier: Model is not loaded/initialized.")
        return self.model.predict(X)

    def predict_proba(self, X: Any) -> Any:
        if self.model is None:
            raise RuntimeError("PatternClassifier: Model is not loaded/initialized.")
        if not hasattr(self.model, "predict_proba"):
            raise RuntimeError(
                "PatternClassifier: Underlying model lacks predict_proba()."
            )
        return self.model.predict_proba(X)

    def save(self, path: str | Path) -> None:
        if self.model is None:
            raise RuntimeError(
                "PatternClassifier: Nothing to save. Model is not initialized."
            )
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        # Save the underlying sklearn model (this matches planner_service.py behavior)
        joblib.dump(self.model, p)

    def load(self, path: str | Path) -> None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"PatternClassifier: Model file not found: {p}")
        self.model = joblib.load(p)

    @classmethod
    def from_file(cls, path: str | Path) -> PatternClassifier:
        inst = cls(model=None)
        inst.load(path)
        return inst
