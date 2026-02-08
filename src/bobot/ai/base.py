from __future__ import annotations

from typing import Protocol


class BaseLLM(Protocol):
    name: str

    async def generate(self, prompt: str) -> str:
        ...

    async def health(self) -> bool:
        ...
