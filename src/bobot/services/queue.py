from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Generic, TypeVar

T = TypeVar("T")


class AsyncTaskQueue(Generic[T]):
    def __init__(self, concurrency: int = 1) -> None:
        self._queue: asyncio.Queue[tuple[Callable[[], Awaitable[T]], asyncio.Future[T]]] = (
            asyncio.Queue()
        )
        self._started = False
        self._concurrency = max(1, concurrency)

    def _start_workers(self) -> None:
        if self._started:
            return
        self._started = True
        for _ in range(self._concurrency):
            asyncio.create_task(self._worker())

    async def _worker(self) -> None:
        while True:
            func, fut = await self._queue.get()
            try:
                result = await func()
                if not fut.cancelled():
                    fut.set_result(result)
            except Exception as exc:
                if not fut.cancelled():
                    fut.set_exception(exc)
            finally:
                self._queue.task_done()

    async def submit(self, func: Callable[[], Awaitable[T]]) -> T:
        self._start_workers()
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[T] = loop.create_future()
        await self._queue.put((func, fut))
        return await fut
