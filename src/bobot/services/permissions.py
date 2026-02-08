from dataclasses import dataclass

from bobot.domain.exceptions import PermissionError


@dataclass
class PermissionProfile:
    allow_commands: bool = True


class PermissionService:
    def ensure_allowed(self, profile: PermissionProfile) -> None:
        if not profile.allow_commands:
            raise PermissionError("Você não tem permissão para este comando.")
