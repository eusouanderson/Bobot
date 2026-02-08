from dataclasses import dataclass

from bobot.commands.handlers import CommandHandlers
from bobot.commands.router import CommandRouter


@dataclass
class DiscordAdapter:
    def __post_init__(self) -> None:
        handlers = CommandHandlers()
        self._router = CommandRouter(
            handlers={
                "ajuda": handlers.ajuda,
                "pergunta": handlers.pergunta,
            }
        )

    def handle(self, command: str, payload: str) -> str:
        return self._router.route(command, payload)
