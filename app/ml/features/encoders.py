# app/ml/features/encoders.py

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


@dataclass
class FeatureEncoder:
    """
    Encodes project fields into numeric features.

    - Categorical: domain, scale, budget -> OneHotEncoder
    - Numeric: users, compliance_count -> passthrough (with imputation)

    MUST match:
      ["domain", "scale", "budget", "users", "compliance_count"]
    """

    transformer: ColumnTransformer | None = None
    categorical_cols: list[str] = field(
        default_factory=lambda: ["domain", "scale", "budget"]
    )
    numeric_cols: list[str] = field(
        default_factory=lambda: ["users", "compliance_count"]
    )

    def fit(self, X: pd.DataFrame) -> FeatureEncoder:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("FeatureEncoder.fit expects a pandas DataFrame.")

        missing = [
            c for c in (self.categorical_cols + self.numeric_cols) if c not in X.columns
        ]
        if missing:
            raise ValueError(f"FeatureEncoder.fit: missing expected columns: {missing}")

        cat_pipe = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "ohe",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,  # sklearn >= 1.2
                    ),
                ),
            ]
        )

        num_pipe = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
            ]
        )

        self.transformer = ColumnTransformer(
            transformers=[
                ("cat", cat_pipe, self.categorical_cols),
                ("num", num_pipe, self.numeric_cols),
            ],
            remainder="drop",
            verbose_feature_names_out=False,
        )

        self.transformer.fit(X)
        return self

    def transform(self, X: pd.DataFrame):
        if self.transformer is None:
            raise RuntimeError("FeatureEncoder not fitted. Call fit() first.")
        if not isinstance(X, pd.DataFrame):
            raise TypeError("FeatureEncoder.transform expects a pandas DataFrame.")
        return self.transformer.transform(X)

    def fit_transform(self, X: pd.DataFrame):
        return self.fit(X).transform(X)
