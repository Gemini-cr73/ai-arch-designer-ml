# app/services/llm/groq_client.py

from __future__ import annotations

from groq import Groq


class GroqClient:
    """
    Minimal Groq client wrapper that matches the interface used by PlannerAgent:

      chat(system: str, user: str, timeout: int = 60) -> str

    Notes:
    - `timeout` is kept only for compatibility. Groq SDK does not expose
      a requests-style timeout parameter directly.
    """

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant") -> None:
        api_key = (api_key or "").strip()
        if not api_key:
            raise ValueError("GroqClient: api_key is missing or empty.")

        model = (model or "llama-3.1-8b-instant").strip()
        if not model:
            raise ValueError("GroqClient: model name is empty.")

        self.client = Groq(api_key=api_key)
        self.model = model

    def chat(
        self,
        system: str,
        user: str,
        timeout: int = 60,
        max_tokens: int | None = None,
        temperature: float = 0.2,
    ) -> str:
        system = (system or "").strip()
        user = (user or "").strip()

        if not user:
            raise ValueError("GroqClient.chat: user prompt is empty.")

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            # Important: raise RuntimeError so API layer maps to 503
            raise RuntimeError(f"Groq request failed: {str(e)}") from e

        choices = getattr(resp, "choices", None)
        if not choices:
            raise RuntimeError("Groq returned no choices in the response.")

        message = getattr(choices[0], "message", None)
        content = (getattr(message, "content", None) or "").strip()

        if not content:
            raise RuntimeError("Groq returned empty content.")

        return content
