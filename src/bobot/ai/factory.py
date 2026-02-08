from __future__ import annotations

from dataclasses import dataclass
from typing import List

from bobot.ai.gpt4all_client import GPT4AllClient
from bobot.ai.lmstudio_client import LMStudioClient
from bobot.ai.ollama_client import OllamaClient
from bobot.ai.runtime import LLMService
from bobot.config import (
    LLM_CACHE_TTL,
    LLM_FALLBACKS,
    LLM_GPT4ALL_URL,
    LLM_LMSTUDIO_URL,
    LLM_MAX_CONCURRENCY,
    LLM_MODEL,
    LLM_OLLAMA_URL,
    LLM_PROVIDER,
    LLM_RATE_LIMIT_MAX,
    LLM_RATE_LIMIT_WINDOW,
    LLM_TIMEOUT,
)
from bobot.services.cache import InMemoryCache
from bobot.services.rate_limit import RateLimit, RateLimiter
from bobot.services.queue import AsyncTaskQueue


@dataclass
class LLMSettings:
    provider: str
    model: str
    timeout: int
    fallbacks: List[str]
    ollama_url: str
    lmstudio_url: str
    gpt4all_url: str


def build_settings() -> LLMSettings:
    return LLMSettings(
        provider=LLM_PROVIDER,
        model=LLM_MODEL,
        timeout=LLM_TIMEOUT,
        fallbacks=LLM_FALLBACKS,
        ollama_url=LLM_OLLAMA_URL,
        lmstudio_url=LLM_LMSTUDIO_URL,
        gpt4all_url=LLM_GPT4ALL_URL,
    )


def build_providers(settings: LLMSettings):
    providers = {
        "ollama": OllamaClient(settings.ollama_url, settings.model, settings.timeout),
        "lmstudio": LMStudioClient(settings.lmstudio_url, settings.model, settings.timeout),
        "gpt4all": GPT4AllClient(settings.gpt4all_url, settings.model, settings.timeout),
    }
    ordered = [settings.provider, *settings.fallbacks]
    return [providers[name] for name in ordered if name in providers]


def create_llm_service() -> LLMService:
    settings = build_settings()
    providers = build_providers(settings)
    cache = InMemoryCache()
    limiter = RateLimiter(RateLimit(LLM_RATE_LIMIT_MAX, LLM_RATE_LIMIT_WINDOW))
    queue = AsyncTaskQueue(concurrency=LLM_MAX_CONCURRENCY)
    return LLMService(
        providers=providers,
        cache=cache,
        rate_limiter=limiter,
        queue=queue,
        cache_ttl=LLM_CACHE_TTL,
    )
