import asyncio
from dataclasses import dataclass

import pytest

from bobot.ai.factory import build_providers, build_settings
from bobot.ai.gpt4all_client import GPT4AllClient
from bobot.ai.http_client import post_json
from bobot.ai.lmstudio_client import LMStudioClient
from bobot.ai.ollama_client import OllamaClient
from bobot.ai.prompts import (
    build_ask_prompt,
    build_code_prompt,
    build_debug_prompt,
    build_docs_prompt,
)
from bobot.ai.runtime import LLMService, provider_names
from bobot.domain.exceptions import ExternalServiceError, RateLimitError
from bobot.services.cache import InMemoryCache
from bobot.services.queue import AsyncTaskQueue
from bobot.services.rate_limit import RateLimit, RateLimiter


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self._status_code = status_code

    def raise_for_status(self):
        if self._status_code >= 400:
            raise RuntimeError("bad")

    def json(self):
        return self._payload


class DummyClient:
    def __init__(self, payload, status_code=200, fail=False):
        self._payload = payload
        self._status_code = status_code
        self._fail = fail

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *_args, **_kwargs):
        if self._fail:
            raise RuntimeError("boom")
        return DummyResponse(self._payload, self._status_code)


@pytest.mark.asyncio
async def test_post_json_success(monkeypatch):
    monkeypatch.setattr(
        "httpx.AsyncClient", lambda timeout: DummyClient({"ok": True})
    )
    result = await post_json("http://x", {"a": 1}, timeout=1)
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_post_json_failure(monkeypatch):
    monkeypatch.setattr(
        "httpx.AsyncClient", lambda timeout: DummyClient({}, fail=True)
    )
    with pytest.raises(ExternalServiceError):
        await post_json("http://x", {"a": 1}, timeout=1, retries=1)


@pytest.mark.asyncio
async def test_get_json_success(monkeypatch):
    from bobot.ai.http_client import get_json

    class DummyGetClient:
        def __init__(self, payload):
            self._payload = payload

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *_args, **_kwargs):
            return DummyResponse(self._payload)

    monkeypatch.setattr("httpx.AsyncClient", lambda timeout: DummyGetClient({"ok": True}))
    result = await get_json("http://x", timeout=1)
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_get_json_failure(monkeypatch):
    from bobot.ai.http_client import get_json

    class DummyFailClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr("httpx.AsyncClient", lambda timeout: DummyFailClient())
    with pytest.raises(ExternalServiceError):
        await get_json("http://x", timeout=1, retries=1)


@pytest.mark.asyncio
async def test_ollama_client(monkeypatch):
    async def fake_post(url, payload, timeout, retries=2):
        return {"response": "ok"}

    monkeypatch.setattr("bobot.ai.ollama_client.post_json", fake_post)
    client = OllamaClient("http://x", "model", 1)
    assert await client.generate("ping") == "ok"

    async def bad_post(url, payload, timeout, retries=2):
        return {}

    monkeypatch.setattr("bobot.ai.ollama_client.post_json", bad_post)
    with pytest.raises(ExternalServiceError):
        await client.generate("ping")

    async def ok_health(url, timeout, retries=1):
        return {"models": []}

    monkeypatch.setattr("bobot.ai.ollama_client.get_json", ok_health)
    assert await client.health() is True


@pytest.mark.asyncio
async def test_lmstudio_client(monkeypatch):
    async def fake_post(url, payload, timeout, retries=2):
        return {"choices": [{"message": {"content": "hi"}}]}

    monkeypatch.setattr("bobot.ai.lmstudio_client.post_json", fake_post)
    client = LMStudioClient("http://x", "model", 1)
    assert await client.generate("ping") == "hi"

    async def bad_post(url, payload, timeout, retries=2):
        return {}

    monkeypatch.setattr("bobot.ai.lmstudio_client.post_json", bad_post)
    with pytest.raises(ExternalServiceError):
        await client.generate("ping")

    async def ok_health(url, timeout, retries=1):
        return {"data": []}

    monkeypatch.setattr("bobot.ai.lmstudio_client.get_json", ok_health)
    assert await client.health() is True


@pytest.mark.asyncio
async def test_gpt4all_client(monkeypatch):
    async def fake_post(url, payload, timeout, retries=2):
        return {"choices": [{"message": {"content": "hi"}}]}

    monkeypatch.setattr("bobot.ai.gpt4all_client.post_json", fake_post)
    client = GPT4AllClient("http://x", "model", 1)
    assert await client.generate("ping") == "hi"

    async def bad_post(url, payload, timeout, retries=2):
        return {}

    monkeypatch.setattr("bobot.ai.gpt4all_client.post_json", bad_post)
    with pytest.raises(ExternalServiceError):
        await client.generate("ping")

    async def ok_health(url, timeout, retries=1):
        return {"data": []}

    monkeypatch.setattr("bobot.ai.gpt4all_client.get_json", ok_health)
    assert await client.health() is True


def test_prompt_builders():
    assert "Pergunta" in build_ask_prompt("teste")
    assert "Linguagem" in build_code_prompt("python", "api")
    assert "Erro" in build_debug_prompt("Traceback")
    assert "Tecnologia" in build_docs_prompt("fastapi")


def test_factory_builders():
    settings = build_settings()
    providers = build_providers(settings)
    assert providers
    names = provider_names(providers)
    assert settings.provider in names


@pytest.mark.asyncio
async def test_llm_service_flow():
    @dataclass
    class DummyProvider:
        name: str
        value: str
        fail: bool = False

        async def generate(self, prompt: str) -> str:
            if self.fail:
                raise RuntimeError("fail")
            return f"{self.value}:{prompt}"

    cache = InMemoryCache()
    limiter = RateLimiter(RateLimit(10, 60))
    queue = AsyncTaskQueue(concurrency=1)

    service = LLMService(
        providers=[DummyProvider("a", "ok", True), DummyProvider("b", "ok")],
        cache=cache,
        rate_limiter=limiter,
        queue=queue,
        cache_ttl=5,
    )

    result = await service.generate("prompt", user_key="1")
    assert result == "ok:prompt"
    cached = await service.generate("prompt", user_key="1")
    assert cached == "ok:prompt"


@pytest.mark.asyncio
async def test_llm_service_no_providers():
    cache = InMemoryCache()
    limiter = RateLimiter(RateLimit(10, 60))
    queue = AsyncTaskQueue(concurrency=1)

    service = LLMService(
        providers=[],
        cache=cache,
        rate_limiter=limiter,
        queue=queue,
        cache_ttl=5,
    )

    with pytest.raises(ExternalServiceError):
        await service.generate("prompt", user_key="1")


@pytest.mark.asyncio
async def test_llm_service_all_fail():
    @dataclass
    class DummyProvider:
        name: str

        async def generate(self, prompt: str) -> str:
            raise RuntimeError("fail")

    cache = InMemoryCache()
    limiter = RateLimiter(RateLimit(10, 60))
    queue = AsyncTaskQueue(concurrency=1)

    service = LLMService(
        providers=[DummyProvider("a"), DummyProvider("b")],
        cache=cache,
        rate_limiter=limiter,
        queue=queue,
        cache_ttl=5,
    )

    with pytest.raises(ExternalServiceError):
        await service.generate("prompt", user_key="1")


@pytest.mark.asyncio
async def test_llm_service_health():
    @dataclass
    class DummyProvider:
        name: str
        ok: bool

        async def generate(self, prompt: str) -> str:
            return prompt

        async def health(self) -> bool:
            if not self.ok:
                raise RuntimeError("down")
            return True

    cache = InMemoryCache()
    limiter = RateLimiter(RateLimit(10, 60))
    queue = AsyncTaskQueue(concurrency=1)

    service = LLMService(
        providers=[DummyProvider("a", True), DummyProvider("b", False)],
        cache=cache,
        rate_limiter=limiter,
        queue=queue,
        cache_ttl=5,
    )

    result = await service.health()
    assert result == {"a": True, "b": False}


@pytest.mark.asyncio
async def test_llm_service_rate_limit():
    @dataclass
    class DummyProvider:
        name: str = "a"

        async def generate(self, prompt: str) -> str:
            return prompt

    cache = InMemoryCache()
    limiter = RateLimiter(RateLimit(1, 60))
    queue = AsyncTaskQueue(concurrency=1)

    service = LLMService(
        providers=[DummyProvider()],
        cache=cache,
        rate_limiter=limiter,
        queue=queue,
        cache_ttl=5,
    )

    await service.generate("prompt", user_key="1")
    with pytest.raises(RateLimitError):
        await service.generate("prompt2", user_key="1")


@pytest.mark.asyncio
async def test_task_queue():
    queue = AsyncTaskQueue(concurrency=1)

    async def work():
        await asyncio.sleep(0)
        return 42

    result = await queue.submit(work)
    assert result == 42
