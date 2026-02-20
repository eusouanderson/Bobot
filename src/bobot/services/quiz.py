from dataclasses import dataclass
from typing import List, Optional
import random

@dataclass
class QuizQuestion:
    pergunta: str
    opcoes: List[str]
    resposta_correta: int 
    dificuldade: str = "normal"

import asyncio

class QuizService:
    def __init__(self, llm_service=None):
        self._llm_service = llm_service
        self._user_scores = {}
        self._user_history = {}
        self._user_quiz = {}

    async def generate_quiz(self) -> QuizQuestion:
        prompt = (
            "Crie uma pergunta de programação para um quiz, com 4 opções e indique qual é a correta. "
            "Formato JSON: {\"pergunta\":..., \"opcoes\":[...], \"resposta_correta\":<índice>}. "
            "Pergunta curta, nível fácil ou médio."
        )
        response = await self._llm_service.generate(prompt, user_key="quiz")
        import json
        try:
            data = json.loads(response)
            return QuizQuestion(
                pergunta=data["pergunta"],
                opcoes=data["opcoes"],
                resposta_correta=data["resposta_correta"],
            )
        except Exception:
            # fallback simples
            return QuizQuestion(
                pergunta="O que faz o operador '==' em Python?",
                opcoes=["Compara valores", "Atribui valor", "Incrementa", "Concatena"],
                resposta_correta=0,
            )

    async def get_daily_quiz(self, user_id: str) -> Optional[QuizQuestion]:
        if user_id in self._user_history:
            return None  # Já respondeu hoje
        if user_id in self._user_quiz:
            return self._user_quiz[user_id]
        quiz = await self.generate_quiz()
        self._user_quiz[user_id] = quiz
        return quiz

    def submit_answer(self, user_id: str, question: QuizQuestion, answer_idx: int) -> bool:
        correct = answer_idx == question.resposta_correta
        self._user_history[user_id] = question
        self._user_scores[user_id] = self._user_scores.get(user_id, 0) + (1 if correct else 0)
        if user_id in self._user_quiz:
            del self._user_quiz[user_id]
        return correct

    def get_score(self, user_id: str) -> int:
        return self._user_scores.get(user_id, 0)

    def get_ranking(self) -> List[tuple]:
        return sorted(self._user_scores.items(), key=lambda x: x[1], reverse=True)
