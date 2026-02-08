from dataclasses import dataclass
from typing import Protocol


class AssistantProvider(Protocol):
    def answer(self, prompt: str) -> str:  # pragma: no cover - interface
        ...


@dataclass
class LocalAssistant:
    """Placeholder for future AI integration."""

    def answer(self, prompt: str) -> str:
        return (
            "Integração com IA externa não está ativa. "
            "Descreva sua dúvida e eu retorno um passo-a-passo básico."
        )
