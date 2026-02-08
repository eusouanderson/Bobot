from dataclasses import dataclass
from typing import Dict


@dataclass
class ProfileRecord:
    mode: str


class InMemoryProfileStore:
    def __init__(self) -> None:
        self._profiles: Dict[str, ProfileRecord] = {}

    def get(self, user_id: str) -> ProfileRecord:
        return self._profiles.get(user_id, ProfileRecord(mode="estudo"))

    def set(self, user_id: str, record: ProfileRecord) -> None:
        self._profiles[user_id] = record
