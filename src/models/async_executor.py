import asyncio
import logging
from typing import Dict
from src.models.async_task_queue import AsyncTaskQueue
from src.models.task_handlers import TaskHandler

logger = logging.getLogger(__name__)


class AsyncTaskExecutor:
    """Асинхронный исполнитель задач"""
    def __init__(self, queue: 'AsyncTaskQueue', max_workers: int = 3):
        self.queue = queue
        self.max_workers = max_workers
        self.handlers: Dict[str, TaskHandler] = {}
        self._running = False
        self._workers = []
        logger.info(f"Создан AsyncTaskExecutor (max_workers={max_workers})")

    def register_handler(self, task_type: str, handler: TaskHandler) -> None:
        """Регистрирует обработчик для определённого типа задач"""
        if not isinstance(handler, TaskHandler):
            raise TypeError("Обработчик должен реализовывать TaskHandler")
        self.handlers[task_type] = handler
        logger.info(f"Зарегистрирован обработчик для типа '{task_type}'")

    async def _worker(self, worker_id: int) -> None:
        """Берёт задачи и обрабатывает их"""
        logger.info(f"Worker #{worker_id} запущен")

        while self._running:
            try:
                task = await self.queue.get()
                logger.info(f"Worker #{worker_id} получил задачу: {task['id']}")
                task_type = task.get('type', 'default')
                handler = self.handlers.get(task_type)

                if not handler:
                    logger.info(f"Worker #{worker_id}: нет обработчика для типа '{task_type}', задача {task['id']} пропущена")
                    continue

                await handler.handle(task)
                logger.info(f"Worker #{worker_id}: задача {task['id']} успешно обработана")

            except asyncio.CancelledError:
                logger.info(f"Worker #{worker_id} отменён")
                break
            except Exception as e:
                logger.error(f"Worker #{worker_id}: ошибка: {e}")

        logger.info(f"Worker #{worker_id} остановлен")

    async def run(self) -> None:
        """Запускает исполнителя"""
        if self._running:
            logger.info("Исполнитель уже запущен")
            return

        self._running = True
        logger.info(f"Запуск исполнителя с {self.max_workers} workers")

        self._workers = [asyncio.create_task(self._worker(i)) for i in range(self.max_workers)]

    async def stop(self) -> None:
        """Останавливает исполнителя"""
        if not self._running:
            return

        logger.info("Остановка исполнителя...")
        self._running = False

        for worker in self._workers:
            if not worker.done():
                worker.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Исполнитель остановлен")

    async def __aenter__(self):
        """Вход в контекстный менеджер"""
        await self.run()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        await self.stop()