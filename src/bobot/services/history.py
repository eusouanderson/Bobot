from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, DefaultDict, List


@dataclass
class MessageRecord:
    author: str
    content: str


class ChannelHistory:
    def __init__(self, max_messages: int = 50) -> None:
        self._max_messages = max_messages
        self._messages: DefaultDict[str, Deque[MessageRecord]] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

    def add(self, channel_id: str, author: str, content: str) -> None:
        self._messages[channel_id].append(MessageRecord(author=author, content=content))

    def list(self, channel_id: str) -> List[MessageRecord]:
        return list(self._messages[channel_id])
