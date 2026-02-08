import pytest

from bobot.adapters.discord_adapter import DiscordAdapter
from bobot.ai.assistant import LocalAssistant
from bobot.commands.handlers import CommandHandlers
from bobot.commands.router import CommandRouter
from bobot.domain.exceptions import (
    BotError,
    ConfigurationError,
    ExternalServiceError,
    PermissionError,
    RateLimitError,
)
from bobot.services.cache import InMemoryCache
from bobot.services.history import ChannelHistory
from bobot.services.permissions import PermissionProfile, PermissionService
from bobot.services.profile import ProfileService, UserProfile
from bobot.services.rate_limit import RateLimit, RateLimiter
from bobot.storage.in_memory import InMemoryProfileStore, ProfileRecord
from bobot.utils.formatting import format_answer
from bobot.utils.text import chunk_text
from bobot.utils.validation import normalize_language, sanitize_prompt


def test_exceptions_hierarchy():
    assert issubclass(ConfigurationError, BotError)
    assert issubclass(PermissionError, BotError)
    assert issubclass(RateLimitError, BotError)
    assert issubclass(ExternalServiceError, BotError)


def test_formatting_and_validation():
    assert format_answer("Titulo", "Corpo") == "**Titulo**\n\nCorpo"
    assert normalize_language("  PYTHON ") == "python"
    assert sanitize_prompt("  ola   mundo ") == "ola mundo"
    assert chunk_text("abc", max_size=2) == ["ab", "c"]
    assert chunk_text("abc", max_size=0) == ["abc"]


def test_cache_set_get_and_expire(monkeypatch):
    cache = InMemoryCache()
    cache.set("key", "value", ttl_seconds=1)
    assert cache.get("key") == "value"

    from datetime import datetime, timedelta

    cache._data["expired"] = cache._data["key"].__class__(
        value="old", expires_at=datetime.utcnow() - timedelta(seconds=1)
    )
    assert cache.get("expired") is None


def test_history_add_list():
    history = ChannelHistory(max_messages=2)
    history.add("1", "user", "msg1")
    history.add("1", "user", "msg2")
    assert len(history.list("1")) == 2


def test_rate_limiter():
    limiter = RateLimiter(RateLimit(max_requests=1, window_seconds=60))
    limiter.check("k")
    with pytest.raises(RateLimitError):
        limiter.check("k")


def test_permission_service():
    service = PermissionService()
    service.ensure_allowed(PermissionProfile(allow_commands=True))
    with pytest.raises(PermissionError):
        service.ensure_allowed(PermissionProfile(allow_commands=False))


def test_profile_service():
    service = ProfileService()
    profile = UserProfile(user_id="1")
    updated = service.set_mode(profile, "rapido")
    assert updated.mode == "rapido"
    with pytest.raises(ValueError):
        service.set_mode(profile, "invalid")


def test_profile_store():
    store = InMemoryProfileStore()
    record = store.get("1")
    assert isinstance(record, ProfileRecord)
    store.set("1", ProfileRecord(mode="rapido"))
    assert store.get("1").mode == "rapido"


def test_router_and_handlers():
    handlers = CommandHandlers(assistant=LocalAssistant())
    router = CommandRouter({"ajuda": handlers.ajuda, "pergunta": handlers.pergunta})
    assert "Ajuda" in router.route("ajuda", "")
    assert "Integração" in router.route("pergunta", "como faço?")
    cached = router.route("pergunta", "como faço?")
    assert cached == router.route("pergunta", "como faço?")
    assert "não reconhecido" in router.route("x", "")


def test_discord_adapter():
    adapter = DiscordAdapter()
    result = adapter.handle("ajuda", "")
    assert "Ajuda" in result
