import os
from dataclasses import dataclass, field
from typing import List, Optional

import pytest

os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ.setdefault("ID_CANAL", "123")


@dataclass
class FakeChannel:
    id: int
    name: str = "test-channel"


@dataclass
class FakeAuthor:
    name: str = "tester"
    id: int = 1


@dataclass
class FakeCtx:
    channel: FakeChannel
    author: FakeAuthor = field(default_factory=FakeAuthor)
    sent: List[dict] = field(default_factory=list)

    async def send(self, content: Optional[str] = None, embed=None):
        self.sent.append({"content": content, "embed": embed})

    class _Typing:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def typing(self):
        return self._Typing()


@pytest.fixture()
def allowed_ctx():
    return FakeCtx(channel=FakeChannel(id=123))


@pytest.fixture()
def blocked_ctx():
    return FakeCtx(channel=FakeChannel(id=999))
