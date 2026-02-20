import pytest
import types
import bobot.bot as bot_module

class DummyCtx:
    def __init__(self):
        self.author = types.SimpleNamespace(id="user_test", name="TestUser")
        self.sent = []
        self.channel = types.SimpleNamespace(id=int(bot_module.ID_CANAL))
        self.bot = types.SimpleNamespace()
    async def send(self, content=None, embed=None):
        self.sent.append({"content": content, "embed": embed})

@pytest.mark.asyncio
async def test_quiz_command(monkeypatch):
    ctx = DummyCtx()
    async def fake_get_daily_quiz(user_id):
        return bot_module.QuizQuestion(
            pergunta="Pergunta de teste?",
            opcoes=["A", "B", "C", "D"],
            resposta_correta=1,
        )
    monkeypatch.setattr(bot_module.quiz_service, "get_daily_quiz", fake_get_daily_quiz)
    await bot_module.quiz_command(ctx)
    assert ctx.sent[-1]["embed"] is not None
    assert "Pergunta de teste?" in ctx.sent[-1]["embed"].description

@pytest.mark.asyncio
async def test_quiz_command_already_answered(monkeypatch):
    ctx = DummyCtx()
    async def fake_get_daily_quiz(user_id):
        return None
    monkeypatch.setattr(bot_module.quiz_service, "get_daily_quiz", fake_get_daily_quiz)
    await bot_module.quiz_command(ctx)
    assert "já respondeu" in ctx.sent[-1]["content"]

@pytest.mark.asyncio
async def test_responder_command(monkeypatch):
    ctx = DummyCtx()
    ctx.bot.quiz_question = bot_module.QuizQuestion(
        pergunta="Pergunta de teste?",
        opcoes=["A", "B", "C", "D"],
        resposta_correta=1,
    )
    def fake_submit_answer(user_id, question, answer_idx):
        return answer_idx == 1
    monkeypatch.setattr(bot_module.quiz_service, "submit_answer", fake_submit_answer)
    await bot_module.responder_command(ctx, 2)
    assert "correta" in ctx.sent[-1]["content"]

@pytest.mark.asyncio
async def test_responder_command_incorreta(monkeypatch):
    ctx = DummyCtx()
    ctx.bot.quiz_question = bot_module.QuizQuestion(
        pergunta="Pergunta de teste?",
        opcoes=["A", "B", "C", "D"],
        resposta_correta=1,
    )
    def fake_submit_answer(user_id, question, answer_idx):
        return False
    monkeypatch.setattr(bot_module.quiz_service, "submit_answer", fake_submit_answer)
    await bot_module.responder_command(ctx, 1)
    assert "incorreta" in ctx.sent[-1]["content"]

@pytest.mark.asyncio
async def test_responder_command_no_quiz():
    ctx = DummyCtx()
    await bot_module.responder_command(ctx, 1)
    assert "Nenhum quiz ativo" in ctx.sent[-1]["content"]

@pytest.mark.asyncio
async def test_ranking_command(monkeypatch):
    ctx = DummyCtx()
    def fake_get_ranking():
        return [("user_test", 5), ("user2", 3)]
    monkeypatch.setattr(bot_module.quiz_service, "get_ranking", fake_get_ranking)
    await bot_module.ranking_command(ctx)
    assert ctx.sent[-1]["embed"] is not None
    assert "user_test" in ctx.sent[-1]["embed"].fields[0].value

@pytest.mark.asyncio
async def test_ranking_command_no_participantes(monkeypatch):
    ctx = DummyCtx()
    def fake_get_ranking():
        return []
    monkeypatch.setattr(bot_module.quiz_service, "get_ranking", fake_get_ranking)
    await bot_module.ranking_command(ctx)
    assert "Nenhum participante" in ctx.sent[-1]["content"]
