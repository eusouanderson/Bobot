from __future__ import annotations

import asyncio
from typing import Any, Dict

import httpx

from bobot.domain.exceptions import ExternalServiceError
from bobot.utils.logging import get_logger

logger = get_logger(__name__)


async def post_json(
    url: str,
    payload: Dict[str, Any],
    timeout: float,
    retries: int = 2,
) -> Dict[str, Any]:
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            last_error = exc
            logger.warning("Falha ao chamar LLM (%s/%s): %s", attempt + 1, retries + 1, exc)
            await asyncio.sleep(0.2 * (attempt + 1))

    raise ExternalServiceError("Falha ao chamar o serviço de LLM.") from last_error


async def get_json(url: str, timeout: float, retries: int = 1) -> Dict[str, Any]:
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            last_error = exc
            logger.warning("Falha ao consultar health (%s/%s): %s", attempt + 1, retries + 1, exc)
            await asyncio.sleep(0.2 * (attempt + 1))

    raise ExternalServiceError("Falha ao consultar health do LLM.") from last_error
