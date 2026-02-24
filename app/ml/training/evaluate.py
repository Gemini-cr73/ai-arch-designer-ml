# app/ml/training/evaluate.py

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC


def _infer_column_types(
    df: pd.DataFrame, target_col: str
) -> tuple[list[str], list[str]]:
    """Infer numeric vs categorical feature columns (excluding target)."""
    feature_cols = [c for c in df.columns if c != target_col]

    numeric_cols: list[str] = []
    categorical_cols: list[str] = []

    for c in feature_cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            numeric_cols.append(c)
        else:
            categorical_cols.append(c)

    return numeric_cols, categorical_cols


def _build_preprocessor(
    numeric_cols: list[str], categorical_cols: list[str]
) -> ColumnTransformer:
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def _safe_multiclass_roc_auc(
    y_true: np.ndarray,
    y_score: np.ndarray,
    labels: list[Any],
) -> float | None:
    """
    Compute ROC-AUC:
    - Binary: standard roc_auc_score
    - Multiclass: ovo macro (requires score matrix)
    Returns None if not computable.
    """
    try:
        if len(labels) <= 1:
            return None
        if len(labels) == 2:
            # y_score should be probability of positive class or decision function
            return float(roc_auc_score(y_true, y_score))
        # Multiclass
        return float(roc_auc_score(y_true, y_score, multi_class="ovo", average="macro"))
    except Exception:
        return None


def _evaluate_model(
    name: str,
    model: Any,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    preprocessor: ColumnTransformer,
) -> dict[str, Any]:
    clf = Pipeline(steps=[("prep", preprocessor), ("model", model)])

    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)

    labels = sorted(list(pd.unique(y_train)))
    y_true = np.array(y_test)

    metrics: dict[str, Any] = {
        "model": name,
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision_macro": float(
            precision_score(y_test, preds, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_test, preds, average="macro", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_test, preds, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, preds, labels=labels).tolist(),
        "labels": labels,
    }

    # ROC-AUC (optional)
    # - For LR/RF we can use predict_proba
    # - For SVM we can enable probability=True and use predict_proba
    roc_auc = None
    try:
        if hasattr(clf.named_steps["model"], "predict_proba"):
            proba = clf.predict_proba(X_test)
            if len(labels) == 2:
                roc_auc = _safe_multiclass_roc_auc(y_true, proba[:, 1], labels)
            else:
                roc_auc = _safe_multiclass_roc_auc(y_true, proba, labels)
    except Exception:
        roc_auc = None

    metrics["roc_auc"] = roc_auc
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate LR (baseline), RF, and SVM on ONE dataset (no merging)."
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to dataset CSV (one dataset at a time).",
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Target column name for supervised learning.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.20,
        help="Test split fraction (default 0.20).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default 42).",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="artifacts/metrics",
        help="Output directory for metrics JSON/CSV (default artifacts/metrics).",
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path.resolve()}")

    df = pd.read_csv(data_path)
    if args.target not in df.columns:
        raise ValueError(
            f"Target column '{args.target}' not found. Columns: {list(df.columns)}"
        )

    # Drop rows with missing target
    df = df.dropna(subset=[args.target])

    X = df.drop(columns=[args.target])
    y = df[args.target]

    # Stratify only if it makes sense
    stratify = y if y.nunique() > 1 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=stratify,
    )

    numeric_cols, categorical_cols = _infer_column_types(df, target_col=args.target)
    preprocessor = _build_preprocessor(numeric_cols, categorical_cols)

    # Models (Professor requirement)
    models = [
        (
            "Logistic Regression (baseline)",
            LogisticRegression(
                max_iter=2000,
                n_jobs=None,
                class_weight="balanced",
            ),
        ),
        (
            "Random Forest",
            RandomForestClassifier(
                n_estimators=300,
                random_state=args.seed,
                class_weight="balanced",
            ),
        ),
        (
            "SVM",
            SVC(
                kernel="rbf",
                probability=True,  # enables predict_proba for ROC-AUC
                class_weight="balanced",
                random_state=args.seed,
            ),
        ),
    ]

    results: list[dict[str, Any]] = []
    for name, model in models:
        res = _evaluate_model(
            name=name,
            model=model,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            preprocessor=preprocessor,
        )
        results.append(res)

    # Choose best by F1 macro
    best = max(results, key=lambda r: r.get("f1_macro", 0.0))

    # Output
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    dataset_tag = data_path.stem
    json_path = outdir / f"eval_{dataset_tag}.json"
    csv_path = outdir / f"eval_{dataset_tag}.csv"

    payload = {
        "dataset": str(data_path),
        "target": args.target,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "best_model": best["model"],
        "results": results,
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Flat CSV for quick viewing
    flat_rows = []
    for r in results:
        flat_rows.append(
            {
                "model": r["model"],
                "accuracy": r["accuracy"],
                "precision_macro": r["precision_macro"],
                "recall_macro": r["recall_macro"],
                "f1_macro": r["f1_macro"],
                "roc_auc": r["roc_auc"],
            }
        )
    pd.DataFrame(flat_rows).to_csv(csv_path, index=False)

    print("\n✅ Evaluation complete")
    print(f"Dataset: {data_path}")
    print(f"Target:  {args.target}")
    print(f"Saved:   {json_path}")
    print(f"Saved:   {csv_path}")
    print(f"Best:    {best['model']} (F1_macro={best['f1_macro']:.4f})")


if __name__ == "__main__":
    main()
