from __future__ import annotations

from typing import List


def chunk_text(text: str, max_size: int = 1900) -> List[str]:
    if max_size <= 0:
        return [text]
    return [text[i : i + max_size] for i in range(0, len(text), max_size)]
