# app/ml/datasets/schema.py

from __future__ import annotations

from pydantic import BaseModel, Field


class ArchitectureTrainingSample(BaseModel):
    domain: str
    scale: str
    budget: str
    users: int = Field(..., ge=1)
    compliance_count: int = Field(..., ge=0)

    pattern: str

    # Stored as CSV string in training.csv (e.g., "api,db,queue")
    components: str = ""

    risk_score: float = Field(..., ge=0.0, le=0.99)
