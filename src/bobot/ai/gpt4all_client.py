from __future__ import annotations

from dataclasses import dataclass

from bobot.ai.base import BaseLLM
from bobot.ai.http_client import get_json, post_json
from bobot.domain.exceptions import ExternalServiceError


@dataclass
class GPT4AllClient(BaseLLM):
    base_url: str
    model: str
    timeout: int
    name: str = "gpt4all"

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Você é um assistente técnico de programação."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        data = await post_json(
            url=f"{self.base_url}/v1/chat/completions",
            payload=payload,
            timeout=self.timeout,
        )
        try:
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            raise ExternalServiceError("Resposta inválida do GPT4All.") from exc

    async def health(self) -> bool:
        await get_json(url=f"{self.base_url}/v1/models", timeout=self.timeout)
        return True
