import types

import pytest

import bobot.bot as bot_module


@pytest.mark.asyncio
async def test_on_ready_and_typing_and_main(caplog, monkeypatch):
    await bot_module.on_ready()
    assert "We have logged in as" in caplog.text

    class DummyTextChannel:
        def __init__(self, channel_id, name):
            self.id = channel_id
            self.name = name

    monkeypatch.setattr(bot_module.discord, "TextChannel", DummyTextChannel)

    channel = DummyTextChannel(channel_id=int(bot_module.ID_CANAL), name="chan")
    user = types.SimpleNamespace(name="user")
    await bot_module.on_typing(channel, user, None)
    assert "is typing" in caplog.text

    ran = {}

    def fake_run(token):
        ran["token"] = token

    monkeypatch.setattr(bot_module.bot, "run", fake_run)
    bot_module.main()
    assert ran["token"] == bot_module.BOT_TOKEN


@pytest.mark.asyncio
async def test_help_ola_pesquisa_youtube(allowed_ctx):
    await bot_module.help_commands(allowed_ctx)
    assert allowed_ctx.sent[-1]["embed"] is not None

    await bot_module.ola(allowed_ctx)
    assert "Olá" in allowed_ctx.sent[-1]["content"]

    await bot_module.pesquisa(allowed_ctx, query="python tutorial")
    assert "google.com" in allowed_ctx.sent[-1]["content"]

    await bot_module.youtube(allowed_ctx, query="funny cats")
    assert "youtube.com" in allowed_ctx.sent[-1]["content"]


@pytest.mark.asyncio
async def test_docs_commands_allowed_and_blocked(allowed_ctx, blocked_ctx, capsys):
    allowed = [
        bot_module.python_docs,
        bot_module.javascript_docs,
        bot_module.html_docs,
        bot_module.css_docs,
        bot_module.mongodb_docs,
        bot_module.csharp,
        bot_module.c_docs,
    ]

    for func in allowed:
        await func(allowed_ctx)
        assert allowed_ctx.sent[-1]["content"]

    for func in allowed:
        await func(blocked_ctx)
        _ = capsys.readouterr()


@pytest.mark.asyncio
async def test_version_command(allowed_ctx, blocked_ctx, capsys):
    await bot_module.version(allowed_ctx)
    assert "Versão" in allowed_ctx.sent[-1]["content"]

    await bot_module.version(blocked_ctx)
    _ = capsys.readouterr()


@pytest.mark.asyncio
async def test_snippet_variants(allowed_ctx, blocked_ctx):
    await bot_module.snippet(allowed_ctx, "python")
    assert "30secondsofcode" in allowed_ctx.sent[-1]["content"]

    await bot_module.snippet(allowed_ctx, "javascript", "array")
    assert "js" in allowed_ctx.sent[-1]["content"]

    await bot_module.snippet(allowed_ctx, "react")
    assert "react" in allowed_ctx.sent[-1]["content"]

    await bot_module.snippet(allowed_ctx, "css")
    assert "/css" in allowed_ctx.sent[-1]["content"]

    await bot_module.snippet(allowed_ctx, "node")
    assert "js/node" in allowed_ctx.sent[-1]["content"]

    await bot_module.snippet(allowed_ctx, "unknown")
    assert "não suportado" in allowed_ctx.sent[-1]["content"]

    await bot_module.snippet(blocked_ctx, "python")
    assert "canal específico" in blocked_ctx.sent[-1]["content"]


@pytest.mark.asyncio
async def test_calc_variants(allowed_ctx, blocked_ctx, capsys):
    await bot_module.calc(allowed_ctx, "soma", 1, 2)
    assert "= 3" in allowed_ctx.sent[-1]["content"]

    await bot_module.calc(allowed_ctx, "sub", 5, 3)
    assert "= 2" in allowed_ctx.sent[-1]["content"]

    await bot_module.calc(allowed_ctx, "mult", 2, 4)
    assert "= 8" in allowed_ctx.sent[-1]["content"]

    await bot_module.calc(allowed_ctx, "div", 8, 2)
    assert "= 4" in allowed_ctx.sent[-1]["content"]

    await bot_module.calc(allowed_ctx, "div", 8, 0)
    assert "Divisão por zero" in allowed_ctx.sent[-1]["content"]

    await bot_module.calc(allowed_ctx, "x", 1, 1)
    assert "Operação inválida" in allowed_ctx.sent[-1]["content"]

    await bot_module.calc(blocked_ctx, "soma", 1, 2)
    _ = capsys.readouterr()


class DummyResponse:
    def __init__(self, status, payload, text="ok"):
        self.status = status
        self._payload = payload
        self._text = text

    async def text(self):
        return self._text

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummySession:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def post(self, *_args, **_kwargs):
        return self._response


@pytest.mark.asyncio
async def test_run_command_paths(allowed_ctx, monkeypatch):
    await bot_module.run(allowed_ctx)
    assert "Uso correto" in allowed_ctx.sent[-1]["content"]

    await bot_module.run(allowed_ctx, "brain", code="x")
    assert "Linguagem não suportada" in allowed_ctx.sent[-1]["content"]

    response = DummyResponse(
        status=200,
        payload={"run": {"output": "hello"}},
        text="ok",
    )
    monkeypatch.setattr(bot_module.aiohttp, "ClientSession", lambda: DummySession(response))
    await bot_module.run(allowed_ctx, "python", code="print('hi')")
    assert "Resultado da execução" in allowed_ctx.sent[-1]["content"]

    response_error = DummyResponse(status=500, payload={}, text="fail")
    monkeypatch.setattr(bot_module.aiohttp, "ClientSession", lambda: DummySession(response_error))
    await bot_module.run(allowed_ctx, "python", code="print('hi')")
    assert "Erro ao executar" in allowed_ctx.sent[-1]["content"]

    def raising_session():
        raise RuntimeError("boom")

    monkeypatch.setattr(bot_module.aiohttp, "ClientSession", raising_session)
    await bot_module.run(allowed_ctx, "python", code="print('hi')")
    assert "Ocorreu um erro" in allowed_ctx.sent[-1]["content"]


@pytest.mark.asyncio
async def test_llm_handlers_success(monkeypatch, allowed_ctx):
    async def fake_generate(prompt: str, user_key: str):
        return f"Resposta para {user_key}: {prompt}"

    monkeypatch.setattr(bot_module.llm_service, "generate", fake_generate)

    await bot_module.ask_command(allowed_ctx, pergunta="o que é python?")
    assert "Pergunta" in allowed_ctx.sent[-1]["content"]

    await bot_module.code_command(allowed_ctx, "python", tema="api")
    assert "Código" in allowed_ctx.sent[-1]["content"]

    await bot_module.debug_command(allowed_ctx, erro="Traceback...")
    assert "Debug" in allowed_ctx.sent[-1]["content"]

    await bot_module.docs_command(allowed_ctx, tecnologia="fastapi")
    assert "Docs" in allowed_ctx.sent[-1]["content"]


@pytest.mark.asyncio
async def test_llm_handlers_errors(monkeypatch, allowed_ctx):
    async def raise_rate(prompt: str, user_key: str):
        raise bot_module.RateLimitError("limite")

    async def raise_external(prompt: str, user_key: str):
        raise bot_module.ExternalServiceError("falha")

    async def raise_unknown(prompt: str, user_key: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(bot_module.llm_service, "generate", raise_rate)
    await bot_module.ask_command(allowed_ctx, pergunta="x")
    assert "Limite excedido" in allowed_ctx.sent[-1]["content"]

    monkeypatch.setattr(bot_module.llm_service, "generate", raise_external)
    await bot_module.ask_command(allowed_ctx, pergunta="x")
    assert "Falha ao consultar" in allowed_ctx.sent[-1]["content"]

    monkeypatch.setattr(bot_module.llm_service, "generate", raise_unknown)
    await bot_module.ask_command(allowed_ctx, pergunta="x")
    assert "Erro inesperado" in allowed_ctx.sent[-1]["content"]


@pytest.mark.asyncio
async def test_status_command(monkeypatch, allowed_ctx):
    async def fake_health():
        return {"ollama": True, "lmstudio": False}

    monkeypatch.setattr(bot_module.llm_service, "health", fake_health)
    await bot_module.status_command(allowed_ctx)
    assert "Status LLM" in allowed_ctx.sent[-1]["content"]


@pytest.mark.asyncio
async def test_status_command_no_providers(monkeypatch, allowed_ctx):
    async def fake_health():
        return {}

    monkeypatch.setattr(bot_module.llm_service, "health", fake_health)
    await bot_module.status_command(allowed_ctx)
    assert "Nenhum provider" in allowed_ctx.sent[-1]["content"]


@pytest.mark.asyncio
async def test_send_paginated_ctx(allowed_ctx):
    await bot_module._send_paginated_ctx(allowed_ctx, "a" * 4000)
    assert len(allowed_ctx.sent) >= 2
    await bot_module._send_paginated_ctx(allowed_ctx, "")
    assert allowed_ctx.sent[-1]["content"] == ""
