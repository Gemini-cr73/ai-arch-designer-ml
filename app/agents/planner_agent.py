from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from app.agents.prompts.planner_prompt import SYSTEM_PROMPT, build_user_prompt
from app.core.schemas.agent_plan import AgentArchitecturePlan
from app.services.llm.groq_client import GroqClient

_CODEBLOCK_JSON_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


class PlannerAgent:
    def __init__(self, client: GroqClient) -> None:
        self.client = client

    def plan(self, idea: dict[str, Any]) -> AgentArchitecturePlan:
        user_prompt = build_user_prompt(idea)
        raw = self.client.chat(system=SYSTEM_PROMPT, user=user_prompt)

        json_text = self._extract_json(raw)
        json_text = self._remove_trailing_commas(json_text)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            snippet = json_text[:1200]
            raise ValueError(
                f"Invalid JSON from model: {e}\n\n--- Extracted JSON (trimmed) ---\n{snippet}"
            )

        try:
            if hasattr(AgentArchitecturePlan, "model_validate"):
                return AgentArchitecturePlan.model_validate(data)  # pydantic v2
            return AgentArchitecturePlan(**data)  # pydantic v1 fallback
        except ValidationError as e:
            raise ValueError(
                f"JSON did not match AgentArchitecturePlan schema:\n{e}\n\nData:\n{data}"
            )

    def _extract_json(self, raw: str) -> str:
        text = (raw or "").strip()
        if not text:
            raise ValueError("Model returned empty response.")

        # 1) Prefer fenced JSON
        m = _CODEBLOCK_JSON_RE.search(text)
        if m:
            return m.group(1).strip()

        # 2) Otherwise extract first balanced JSON object
        first = text.find("{")
        if first == -1:
            raise ValueError(f"Model did not return a JSON object. Raw output:\n{raw}")

        depth = 0
        in_string = False
        escape = False

        for i in range(first, len(text)):
            ch = text[i]

            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[first : i + 1].strip()

        raise ValueError(
            "Could not find a complete balanced JSON object in the model output.\n"
            f"Raw output:\n{raw}"
        )

    def _remove_trailing_commas(self, s: str) -> str:
        s = re.sub(r",\s*}", "}", s)
        s = re.sub(r",\s*]", "]", s)
        return s
