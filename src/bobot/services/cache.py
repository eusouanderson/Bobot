from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional


@dataclass
class CacheEntry:
    value: str
    expires_at: datetime


class InMemoryCache:
    def __init__(self) -> None:
        self._data: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[str]:
        entry = self._data.get(key)
        if not entry:
            return None
        if entry.expires_at < datetime.utcnow():
            self._data.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        self._data[key] = CacheEntry(
            value=value, expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds)
        )
