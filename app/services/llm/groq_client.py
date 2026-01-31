from __future__ import annotations

from groq import Groq


class GroqClient:
    """
    Minimal Groq client wrapper that matches the interface used by PlannerAgent:

      chat(system: str, user: str, timeout: int = 60) -> str

    Notes:
    - The Groq SDK does not expose a requests-style timeout parameter the same way.
      We keep `timeout` only for compatibility with the rest of the codebase.
    """

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant") -> None:
        api_key = (api_key or "").strip()
        if not api_key:
            raise ValueError("GroqClient: api_key is missing or empty.")

        self.client = Groq(api_key=api_key)
        self.model = (model or "llama-3.1-8b-instant").strip()

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
            # Re-raise as RuntimeError so the API layer can map it to 503 cleanly.
            raise RuntimeError(f"Groq request failed: {e}") from e

        # Defensive parsing
        choices = getattr(resp, "choices", None)
        if not choices:
            raise RuntimeError("Groq returned no choices in the response.")

        message = getattr(choices[0], "message", None)
        content = (getattr(message, "content", None) or "").strip()

        if not content:
            raise RuntimeError("Groq returned empty content.")

        return content
