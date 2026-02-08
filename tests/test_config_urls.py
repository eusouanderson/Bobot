import importlib
import os
import runpy
import sys
import types

import pytest


def test_require_env_success():
    from bobot import config

    assert config._require_env("BOT_TOKEN") == "test-token"


def test_require_env_missing(monkeypatch):
    from bobot import config

    monkeypatch.delenv("MISSING_ENV", raising=False)
    with pytest.raises(RuntimeError, match="Variável de ambiente ausente"):
        config._require_env("MISSING_ENV")


def test_config_reload(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "reload-token")
    monkeypatch.setenv("ID_CANAL", "456")
    import bobot.config as config

    config = importlib.reload(config)
    assert config.BOT_TOKEN == "reload-token"
    assert config.ID_CANAL == "456"
    assert config.LLM_PROVIDER


def test_load_dotenv_success(monkeypatch):
    called = {"ok": False}

    def fake_load():
        called["ok"] = True

    fake_dotenv = types.SimpleNamespace(load_dotenv=fake_load)
    monkeypatch.setitem(sys.modules, "dotenv", fake_dotenv)

    import bobot.config as config

    assert config._load_dotenv() is True
    assert called["ok"] is True


def test_load_dotenv_failure(monkeypatch):
    def fake_load():
        raise RuntimeError("boom")

    fake_dotenv = types.SimpleNamespace(load_dotenv=fake_load)
    monkeypatch.setitem(sys.modules, "dotenv", fake_dotenv)

    import bobot.config as config

    assert config._load_dotenv() is False


def test_urls_constants():
    from bobot import urls

    assert urls.URL_PYTHON.startswith("https://")
    assert "javascript" in urls.URL_JAVASCRIPT.lower()
    assert "google" in urls.GOOGLE


def test_python_help_url():
    from bobot.helpers import python_help

    assert python_help.URL.startswith("https://")


def test_package_main_invocation(monkeypatch):
    import bobot.bot as bot

    ran = {}

    def fake_run(token):
        ran["token"] = token

    monkeypatch.setattr(bot.bot, "run", fake_run)
    runpy.run_module("bobot.__main__", run_name="__main__")
    assert ran["token"] == bot.BOT_TOKEN
