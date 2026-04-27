import asyncio
import logging
from collections import deque
from typing import Deque

logger = logging.getLogger(__name__)


class AsyncTaskQueue:
    """Асинхронная очередь задач"""

    def __init__(self, max_size=None):
        self._queue: Deque[dict] = deque()
        self._max_size = max_size
        self._condition = asyncio.Condition()
        logger.info(f"Создана асинхронная очередь задач с max_size={max_size}")

    async def put(self, task: dict) -> None:
        """Добавляем задачу в очередь. Если очередь ограничена и заполнена, то ждём"""
        async with self._condition:
            while self._max_size is not None and len(self._queue) >= self._max_size:
                logger.info(f"Очередь заполнена, ожидание...")
                await self._condition.wait()
            self._queue.append(task)
            logger.info(f"Задача добавлена в асинхронную очередь (всего: {len(self._queue)})")
            self._condition.notify() # Уведомляем, что появилась новая задача

    async def get(self) -> dict:
        """Получаем задачу из очереди если пусто, то ждем"""
        async with self._condition:
            while not self._queue:
                logger.info(f"Очередь пуста, ожидание задач...")
                await self._condition.wait()
            task = self._queue.popleft()
            logger.info(f"Задача получена из асинхронной очереди (осталось: {len(self._queue)})")
            self._condition.notify()  # Уведомляем, что появилось место
            return task

    def qsize(self) -> int:
        """Возвращаем текущий размер очереди"""
        return len(self._queue)

    def empty(self) -> bool:
        """Проверяем пуста ли очередь"""
        return len(self._queue) == 0

    def full(self) -> bool:
        """Проверяем заполнена ли очередь (если есть ограничение)"""
        if self._max_size is None:
            return False
        return len(self._queue) >= self._max_size

    async def clear(self) -> None:
        """Очищаем очередь"""
        async with self._condition:
            count = len(self._queue)
            self._queue.clear()
            logger.info(f"Асинхронная очередь очищена (было {count} задач)")

    def __repr__(self) -> str:
        return f"AsyncTaskQueue(tasks={len(self._queue)}, max_size={self._max_size})"