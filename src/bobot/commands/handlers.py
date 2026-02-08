from bobot.ai.assistant import AssistantProvider, LocalAssistant
from bobot.services.cache import InMemoryCache
from bobot.utils.formatting import format_answer


class CommandHandlers:
    def __init__(self, assistant: AssistantProvider | None = None) -> None:
        self._assistant = assistant or LocalAssistant()
        self._cache = InMemoryCache()

    def ajuda(self, _payload: str) -> str:
        return format_answer(
            "Ajuda",
            "Use /pergunta, /codigo, /debug, /docs, /status, /perfil.",
        )

    def pergunta(self, payload: str) -> str:
        cached = self._cache.get(payload)
        if cached:
            return cached
        answer = self._assistant.answer(payload)
        self._cache.set(payload, answer)
        return answer
