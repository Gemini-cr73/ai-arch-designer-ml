from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


@dataclass
class FeatureEncoder:
    """
    Encodes categorical project fields (domain, scale, budget) into numeric features.

    Compatible with scikit-learn >= 1.2 (uses sparse_output).
    """
    transformer: ColumnTransformer | None = None

    def fit(self, X: pd.DataFrame) -> "FeatureEncoder":
        categorical_cols = list(X.columns)

        ohe = OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False,   # ✅ new API (replaces sparse=...)
        )

        self.transformer = ColumnTransformer(
            transformers=[("cat", ohe, categorical_cols)],
            remainder="drop",
        )

        self.transformer.fit(X)
        return self

    def transform(self, X: pd.DataFrame):
        if self.transformer is None:
            raise RuntimeError("FeatureEncoder not fitted. Call fit() first.")
        return self.transformer.transform(X)

    def fit_transform(self, X: pd.DataFrame):
        return self.fit(X).transform(X)
