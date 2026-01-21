from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.core.schemas.architecture import ArchitecturePlan, DataFlow, ServiceComponent


class ArchitecturePlanner:
    """
    Loads trained ML artifacts and uses them to predict an architecture pattern,
    then converts that pattern into a concrete ArchitecturePlan response.
    Also returns Milestone 6 ML metrics: pattern_label + confidence (0..1).
    """

    def __init__(
        self,
        model_path: str = "artifacts/models/pattern_model.joblib",
        encoder_path: str = "artifacts/models/pattern_encoder.joblib",
    ) -> None:
        self.model_path = Path(model_path)
        self.encoder_path = Path(encoder_path)
        self._model = None
        self._encoder = None

    def _load_artifacts(self) -> None:
        if self._model is not None and self._encoder is not None:
            return

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found: {self.model_path}. "
                "Run: python -m app.ml.training.train_pattern"
            )

        if not self.encoder_path.exists():
            raise FileNotFoundError(
                f"Encoder artifact not found: {self.encoder_path}. "
                "Run: python -m app.ml.training.train_pattern"
            )

        self._model = joblib.load(self.model_path)
        self._encoder = joblib.load(self.encoder_path)

    def plan(self, idea: dict[str, Any]) -> ArchitecturePlan:
        """
        idea: dict version of ProjectIdeaInput.
        Returns: ArchitecturePlan (Pydantic model) incl. ML metrics.
        """
        self._load_artifacts()

        # These MUST match training feature columns exactly
        raw_users = idea.get("expected_users", 100)
        try:
            users = int(raw_users) if raw_users not in (None, "") else 100
        except Exception:
            users = 100
        if users < 1:
            users = 1

        compliance = idea.get("compliance") or []
        if not isinstance(compliance, list):
            compliance = []
        compliance_count = len(compliance)

        X = pd.DataFrame(
            [
                {
                    "domain": (idea.get("domain") or "other"),
                    "scale": (idea.get("scale") or "prototype"),
                    "budget": (idea.get("budget") or "low"),
                    "users": users,
                    "compliance_count": compliance_count,
                }
            ]
        )

        X_enc = self._encoder.transform(X)

        # ---- Prediction + confidence (Milestone 6) ----
        pred = self._model.predict(X_enc)[0]
        pattern_label = str(pred)

        confidence: float | None = None
        if hasattr(self._model, "predict_proba"):
            try:
                proba = self._model.predict_proba(X_enc)
                if proba is not None and len(proba) > 0:
                    confidence = float(max(proba[0]))
            except Exception:
                confidence = None

        # Build the plan with your existing mapping
        plan = self._pattern_to_plan(pattern_label, idea)

        # Inject ML metrics
        plan.pattern_label = pattern_label
        plan.confidence = confidence

        return plan

    def _pattern_to_plan(self, pattern: str, idea: dict[str, Any]) -> ArchitecturePlan:
        domain = (idea.get("domain") or "other").strip()
        scale = (idea.get("scale") or "prototype").strip()
        budget = (idea.get("budget") or "low").strip()

        base_risks: list[str] = [
            "Requirements drift",
            "Operational overhead",
            "Security misconfiguration",
        ]

        if pattern == "monolith":
            services = [
                ServiceComponent(
                    name="app",
                    responsibility="Single deployable API + business logic + ML calls",
                    technologies=["FastAPI", "Python", "SQLite"],
                )
            ]
            flows = [
                DataFlow(
                    source="client",
                    destination="app",
                    description="Submit project idea + constraints",
                ),
                DataFlow(
                    source="app",
                    destination="storage",
                    description="Persist runs, artifacts, feedback",
                ),
            ]
            storage = ["SQLite"]
            risks = base_risks + ["Scaling limits under high concurrency"]

        elif pattern == "microservices":
            services = [
                ServiceComponent(
                    name="api",
                    responsibility="Request routing, validation, orchestration",
                    technologies=["FastAPI"],
                ),
                ServiceComponent(
                    name="ml-service",
                    responsibility="Pattern inference + recommendations",
                    technologies=["Python", "scikit-learn"],
                ),
                ServiceComponent(
                    name="artifact-store",
                    responsibility="Store models, outputs, generated scaffolds",
                    technologies=["Local FS (dev)", "Blob Storage (prod)"],
                ),
            ]
            flows = [
                DataFlow(
                    source="client",
                    destination="api",
                    description="Submit project idea + constraints",
                ),
                DataFlow(
                    source="api",
                    destination="ml-service",
                    description="Predict architecture pattern",
                ),
                DataFlow(
                    source="api",
                    destination="artifact-store",
                    description="Save generated plans + diagrams",
                ),
            ]
            storage = ["SQLite", "Object Storage"]
            risks = base_risks + ["Service-to-service latency", "Deployment complexity"]

        elif pattern == "event-driven":
            services = [
                ServiceComponent(
                    name="api",
                    responsibility="Accept requests and publish events",
                    technologies=["FastAPI"],
                ),
                ServiceComponent(
                    name="worker",
                    responsibility="Async generation: diagrams, scaffolds, evaluations",
                    technologies=["Python", "Celery/RQ (later)"],
                ),
                ServiceComponent(
                    name="queue",
                    responsibility="Buffer work and decouple components",
                    technologies=["Redis (dev)", "Azure Service Bus (prod)"],
                ),
            ]
            flows = [
                DataFlow(
                    source="client",
                    destination="api",
                    description="Submit project idea",
                ),
                DataFlow(
                    source="api",
                    destination="queue",
                    description="Publish 'plan_requested' event",
                ),
                DataFlow(
                    source="queue",
                    destination="worker",
                    description="Worker consumes and generates outputs",
                ),
            ]
            storage = ["SQLite", "Object Storage"]
            risks = base_risks + ["Event ordering/retries", "Observability needed"]

        elif pattern == "serverless":
            services = [
                ServiceComponent(
                    name="api-functions",
                    responsibility="Stateless endpoints for plan/diagram/scaffold generation",
                    technologies=["Azure Functions (later)", "FastAPI (dev)"],
                ),
                ServiceComponent(
                    name="storage",
                    responsibility="Persist artifacts and outputs",
                    technologies=["Blob Storage"],
                ),
            ]
            flows = [
                DataFlow(
                    source="client",
                    destination="api-functions",
                    description="Submit project idea",
                ),
                DataFlow(
                    source="api-functions",
                    destination="storage",
                    description="Store outputs and artifacts",
                ),
            ]
            storage = ["Object Storage"]
            risks = base_risks + [
                "Cold starts",
                "Vendor lock-in",
                "Debugging complexity",
            ]

        else:
            services = [
                ServiceComponent(
                    name="api",
                    responsibility="Plan + generate outputs",
                    technologies=["FastAPI", "Python"],
                )
            ]
            flows = [
                DataFlow(
                    source="client",
                    destination="api",
                    description="Submit project idea",
                )
            ]
            storage = ["SQLite"]
            risks = base_risks + ["Unrecognized pattern fallback"]

        risks.append(f"Context: domain={domain}, scale={scale}, budget={budget}")

        return ArchitecturePlan(
            pattern=pattern,  # keep existing behavior
            pattern_label=None,  # injected later in plan()
            confidence=None,  # injected later in plan()
            services=services,
            data_flows=flows,
            storage=storage,
            risks=risks,
        )
