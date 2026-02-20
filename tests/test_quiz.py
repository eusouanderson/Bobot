import pytest
import asyncio
from bobot.services.quiz import QuizService, QuizQuestion

class DummyLLM:
    async def generate(self, prompt, user_key=None):
        return '{"pergunta": "Qual a saída de print(1+1)?", "opcoes": ["1", "2", "3", "4"], "resposta_correta": 1}'

@pytest.mark.asyncio
async def test_generate_quiz_llm():
    service = QuizService(llm_service=DummyLLM())
    quiz = await service.generate_quiz()
    assert isinstance(quiz, QuizQuestion)
    assert quiz.pergunta.startswith("Qual a saída")
    assert quiz.opcoes[1] == "2"
    assert quiz.resposta_correta == 1

@pytest.mark.asyncio
async def test_get_daily_quiz_and_submit():
    service = QuizService(llm_service=DummyLLM())
    user_id = "user1"
    quiz = await service.get_daily_quiz(user_id)
    assert quiz is not None
    # Responder corretamente
    result = service.submit_answer(user_id, quiz, 1)
    assert result is True
    # Não deve permitir novo quiz no mesmo dia
    quiz2 = await service.get_daily_quiz(user_id)
    assert quiz2 is None

@pytest.mark.asyncio
async def test_ranking():
    service = QuizService(llm_service=DummyLLM())
    user_id = "user2"
    quiz = await service.get_daily_quiz(user_id)
    service.submit_answer(user_id, quiz, 1)
    ranking = service.get_ranking()
    assert ranking[0][0] == user_id
    assert ranking[0][1] == 1
