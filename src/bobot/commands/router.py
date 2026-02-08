from dataclasses import dataclass
from typing import Callable, Dict


CommandHandler = Callable[[str], str]


@dataclass
class CommandRouter:
    handlers: Dict[str, CommandHandler]

    def route(self, command: str, payload: str) -> str:
        handler = self.handlers.get(command)
        if not handler:
            return "Comando não reconhecido. Use /ajuda."
        return handler(payload)
