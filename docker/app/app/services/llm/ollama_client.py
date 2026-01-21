from __future__ import annotations

from typing import Any

import requests


class OllamaClient:
    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3.1"
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, system: str, user: str, timeout: int = 60) -> str:
        """
        Uses Ollama /api/chat and returns the assistant message content as a string.
        """
        url = f"{self.base_url}/api/chat"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }

        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()

        # Ollama returns: {"message": {"role": "...", "content": "..."} , ...}
        msg = data.get("message") or {}
        content: str | None = msg.get("content")
        if not content:
            raise RuntimeError(f"Ollama returned empty content: {data}")
        return content
