import pytest
import asyncio
from src.models.async_task_queue import AsyncTaskQueue
from src.models.task_handlers import EmailTaskHandler, NotificationHandler, PkgTaskHandler
from src.models.async_executor import AsyncTaskExecutor


@pytest.mark.asyncio
class TestAsyncTaskQueue:
    """Тесты асинхронной очереди"""
    async def test_put_and_get(self):
        queue = AsyncTaskQueue()
        task = {"id": 1, "type": "test", "payload": {}}

        await queue.put(task)
        result = await queue.get()

        assert result["id"] == 1

    async def test_qsize(self):
        queue = AsyncTaskQueue()
        assert queue.qsize() == 0

        await queue.put({"id": 1, "type": "test"})
        assert queue.qsize() == 1

        await queue.get()
        assert queue.qsize() == 0

    async def test_empty(self):
        queue = AsyncTaskQueue()
        assert queue.empty() is True

        await queue.put({"id": 1, "type": "test"})
        assert queue.empty() is False

    async def test_clear(self):
        queue = AsyncTaskQueue()
        await queue.put({"id": 1, "type": "test"})
        await queue.put({"id": 2, "type": "test"})

        assert queue.qsize() == 2
        await queue.clear()
        assert queue.qsize() == 0


@pytest.mark.asyncio
class TestAsyncTaskExecutor:
    """Тесты асинхронного исполнителя"""
    async def test_register_handler(self):
        queue = AsyncTaskQueue()
        executor = AsyncTaskExecutor(queue, max_workers=1)
        handler = EmailTaskHandler()

        executor.register_handler("email", handler)

        assert "email" in executor.handlers
        assert executor.handlers["email"] == handler

    async def test_register_invalid_handler(self):
        queue = AsyncTaskQueue()
        executor = AsyncTaskExecutor(queue, max_workers=1)

        class InvalidHandler:
            pass

        with pytest.raises(TypeError):
            executor.register_handler("test", InvalidHandler())

    async def test_run_and_stop(self):
        queue = AsyncTaskQueue()
        executor = AsyncTaskExecutor(queue, max_workers=2)

        await executor.run()
        assert executor._running is True
        assert len(executor._workers) == 2

        await executor.stop()
        assert executor._running is False
        assert len(executor._workers) == 0

    async def test_context_manager(self):
        queue = AsyncTaskQueue()
        executor = AsyncTaskExecutor(queue, max_workers=1)

        async with executor:
            assert executor._running is True
            assert len(executor._workers) == 1

        assert executor._running is False
        assert len(executor._workers) == 0

    async def test_process_task_with_handler(self):
        queue = AsyncTaskQueue()
        executor = AsyncTaskExecutor(queue, max_workers=1)
        executor.register_handler("email", EmailTaskHandler())
        handler = executor.handlers.get("email")
        assert handler is not None

    async def test_process_task_without_handler(self):
        queue = AsyncTaskQueue()
        executor = AsyncTaskExecutor(queue, max_workers=1)
        handler = executor.handlers.get("unknown")
        assert handler is None


@pytest.mark.asyncio
class TestTaskHandlers:
    """Тесты для обработчиков задач"""
    async def test_email_handler(self):
        handler = EmailTaskHandler()
        task = {"id": 1, "type": "email", "payload": {"to": "test@example.com"}}

        result = await handler.handle(task)
        assert result is None

    async def test_notification_handler(self):
        handler = NotificationHandler()
        task = {"id": 2, "type": "notification", "payload": {"user_id": 123}}

        result = await handler.handle(task)
        assert result is None

    async def test_pkg_handler(self):
        handler = PkgTaskHandler()
        task = {"id": 3, "type": "pkg", "payload": {"package_name": "test.tar.gz"}}

        result = await handler.handle(task)
        assert result is None