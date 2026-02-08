from dataclasses import dataclass


@dataclass
class UserProfile:
    user_id: str
    mode: str = "estudo"


class ProfileService:
    def set_mode(self, profile: UserProfile, mode: str) -> UserProfile:
        if mode not in {"estudo", "rapido"}:
            raise ValueError("Modo inválido. Use 'estudo' ou 'rapido'.")
        profile.mode = mode
        return profile
