def normalize_language(language: str) -> str:
    return language.strip().lower()


def sanitize_prompt(text: str, max_len: int = 1500) -> str:
    cleaned = " ".join(text.strip().split())
    return cleaned[:max_len]
