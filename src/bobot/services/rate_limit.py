from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import DefaultDict

from bobot.domain.exceptions import RateLimitError


@dataclass
class RateLimit:
    max_requests: int
    window_seconds: int


class RateLimiter:
    def __init__(self, limit: RateLimit) -> None:
        self._limit = limit
        self._requests: DefaultDict[str, list[datetime]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self._limit.window_seconds)
        window = [ts for ts in self._requests[key] if ts >= window_start]
        window.append(now)
        self._requests[key] = window

        if len(window) > self._limit.max_requests:
            raise RateLimitError("Limite de requisições excedido.")
