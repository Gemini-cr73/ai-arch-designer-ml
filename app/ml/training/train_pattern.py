# app/ml/training/train_pattern.py

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from app.ml.features.encoders import FeatureEncoder
from app.ml.models.pattern_classifier import PatternClassifier

# Paths relative to project root
DATA = Path("data/processed/training.csv")
MODEL_OUT = Path("artifacts/models/pattern_model.joblib")
ENCODER_OUT = Path("artifacts/models/pattern_encoder.joblib")


def main() -> None:
    if not DATA.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA.resolve()}\n"
            "Run: python -m app.ml.datasets.build_dataset"
        )

    df = pd.read_csv(DATA)

    feature_cols = ["domain", "scale", "budget", "users", "compliance_count"]
    target_col = "pattern"

    missing = [c for c in feature_cols + [target_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in training.csv: {missing}")

    # Make sure numeric fields are numeric (robustness)
    df["users"] = pd.to_numeric(df["users"], errors="coerce").fillna(100).astype(int)
    df["compliance_count"] = (
        pd.to_numeric(df["compliance_count"], errors="coerce").fillna(0).astype(int)
    )

    X = df[feature_cols]
    y = df[target_col].astype(str)

    # Split BEFORE fitting encoder to avoid leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y if y.nunique() > 1 else None,
    )

    encoder = FeatureEncoder()
    X_train_enc = encoder.fit_transform(X_train)
    X_test_enc = encoder.transform(X_test)

    model = PatternClassifier()
    model.train(X_train_enc, y_train)

    preds = model.predict(X_test_enc)

    print("\n✅ Pattern Classifier Evaluation")
    print("Accuracy:", round(accuracy_score(y_test, preds), 4))
    print("\nClassification Report:\n", classification_report(y_test, preds))
    print("Confusion Matrix:\n", confusion_matrix(y_test, preds))

    # Save model + encoder (needed for inference later)
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    ENCODER_OUT.parent.mkdir(parents=True, exist_ok=True)

    model.save(str(MODEL_OUT))
    joblib.dump(encoder, ENCODER_OUT)

    print(f"\n✅ Saved model:   {MODEL_OUT.resolve()}")
    print(f"✅ Saved encoder: {ENCODER_OUT.resolve()}")


if __name__ == "__main__":
    main()
