import pytest
import asyncio
from bobot.services.quiz import QuizService, QuizQuestion

class DummyLLM:
    async def generate(self, prompt, user_key=None):
        if 'JSON' in prompt:
            return '{"pergunta": "Qual a saída de print(1+1)?", "opcoes": ["1", "2", "3", "4"], "resposta_correta": 1}'
        return 'erro'

@pytest.mark.asyncio
async def test_generate_quiz_fallback():
    class FailingLLM:
        async def generate(self, prompt, user_key=None):
            return 'erro'
    service = QuizService(llm_service=FailingLLM())
    quiz = await service.generate_quiz()
    assert quiz.pergunta == "O que faz o operador '==' em Python?"
    assert quiz.opcoes[0] == "Compara valores"
    assert quiz.resposta_correta == 0

@pytest.mark.asyncio
async def test_get_daily_quiz_return_existing():
    service = QuizService(llm_service=DummyLLM())
    user_id = "userX"
    quiz = QuizQuestion(pergunta="Q?", opcoes=["A", "B", "C", "D"], resposta_correta=2)
    service._user_quiz[user_id] = quiz
    result = await service.get_daily_quiz(user_id)
    assert result == quiz

@pytest.mark.asyncio
async def test_get_score():
    service = QuizService(llm_service=DummyLLM())
    user_id = "userY"
    service._user_scores[user_id] = 7
    assert service.get_score(user_id) == 7
