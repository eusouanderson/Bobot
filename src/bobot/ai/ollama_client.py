from __future__ import annotations

from dataclasses import dataclass

from bobot.ai.base import BaseLLM
from bobot.ai.http_client import get_json, post_json
from bobot.domain.exceptions import ExternalServiceError


@dataclass
class OllamaClient(BaseLLM):
    base_url: str
    model: str
    timeout: int
    name: str = "ollama"

    async def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        data = await post_json(
            url=f"{self.base_url}/api/generate",
            payload=payload,
            timeout=self.timeout,
        )
        response = data.get("response")
        if not response:
            raise ExternalServiceError("Resposta inválida do Ollama.")
        return response

    async def health(self) -> bool:
        await get_json(url=f"{self.base_url}/api/tags", timeout=self.timeout)
        return True
