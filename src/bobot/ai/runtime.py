from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from bobot.ai.base import BaseLLM
from bobot.domain.exceptions import ExternalServiceError
from bobot.services.cache import InMemoryCache
from bobot.services.rate_limit import RateLimiter
from bobot.services.queue import AsyncTaskQueue
from bobot.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LLMService:
    providers: List[BaseLLM]
    cache: InMemoryCache
    rate_limiter: RateLimiter
    queue: AsyncTaskQueue
    cache_ttl: int = 300

    async def generate(self, prompt: str, user_key: str) -> str:
        self.rate_limiter.check(user_key)
        cached = self.cache.get(prompt)
        if cached:
            return cached

        if not self.providers:
            raise ExternalServiceError("Nenhum provider LLM configurado.")

        last_error: Exception | None = None
        for provider in self.providers:
            try:
                result = await self.queue.submit(lambda: provider.generate(prompt))
                self.cache.set(prompt, result, ttl_seconds=self.cache_ttl)
                return result
            except Exception as exc:
                logger.warning("Provider %s falhou: %s", provider.name, exc)
                last_error = exc

        raise ExternalServiceError("Todos os providers falharam.") from last_error

    async def health(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for provider in self.providers:
            try:
                await provider.health()
                results[provider.name] = True
            except Exception as exc:
                logger.warning("Health falhou para %s: %s", provider.name, exc)
                results[provider.name] = False
        return results


def provider_names(providers: Iterable[BaseLLM]) -> list[str]:
    return [provider.name for provider in providers]
