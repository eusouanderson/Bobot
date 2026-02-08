import os

def _load_dotenv() -> bool:
    try:
        from dotenv import load_dotenv

        load_dotenv()
        return True
    except Exception:
        return False


_DOTENV_LOADED = _load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Variável de ambiente ausente: {name}. "
            "Crie um arquivo .env ou exporte a variável antes de iniciar o bot."
        )
    return value


BOT_TOKEN = _require_env("BOT_TOKEN")
ID_CANAL = _require_env("ID_CANAL")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-coder:6.7b")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

LLM_OLLAMA_URL = os.getenv("LLM_OLLAMA_URL", "http://localhost:11434")
LLM_LMSTUDIO_URL = os.getenv("LLM_LMSTUDIO_URL", "http://localhost:1234")
LLM_GPT4ALL_URL = os.getenv("LLM_GPT4ALL_URL", "http://localhost:4891")

LLM_FALLBACKS = [
    item.strip()
    for item in os.getenv("LLM_FALLBACKS", "").split(",")
    if item.strip()
]

LLM_MAX_CONCURRENCY = int(os.getenv("LLM_MAX_CONCURRENCY", "2"))
LLM_CACHE_TTL = int(os.getenv("LLM_CACHE_TTL", "300"))
LLM_RATE_LIMIT_MAX = int(os.getenv("LLM_RATE_LIMIT_MAX", "5"))
LLM_RATE_LIMIT_WINDOW = int(os.getenv("LLM_RATE_LIMIT_WINDOW", "60"))
