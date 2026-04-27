import logging
import sys
import asyncio
from src.sources.generator_source import TaskSourceGenerator
from src.sources.file_source import TaskSourceFile
from src.sources.api_source import TaskSourceAPI
from src.models.task import TaskSource, Task
from src.models.task_queue import TaskQueue
from src.models.async_task_queue import AsyncTaskQueue
from src.models.task_handlers import EmailTaskHandler, NotificationHandler, PkgTaskHandler
from src.models.async_executor import AsyncTaskExecutor

def setup_logging() -> None:
    """Настройка логирования только в консоль."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout
    )

def process_tasks(source: TaskSource, logger: logging.Logger) -> None:
    """Обработка задач из любого источника, соответствующего протоколу."""
    tasks = source.get_tasks()
    logger.info(f"Получено {len(tasks)} задач из {source.__class__.__name__}")
    for task in tasks:
        logger.info(f"  Задача {task.id}: {task.payload}")
        logger.info(f"      Описание: {task.description}")
        logger.info(f"      Приоритет: {task.priority}")
        logger.info(f"      Статус: {task.status}")
        logger.info(f"      Время создания: {task.created_at}")
        logger.info(f"      Готовность к выполнению: {task.is_ready}")
        logger.info(f"      Выполняется сейчас: {task.is_active}")
        logger.info(f"      Завершена: {task.is_completed}")
        logger.info(f"      Отменена: {task.is_failed}")

def process_queue(queue: TaskQueue, logger: logging.Logger) -> None:
    """Обработка очереди задач"""
    for task in queue:
        logger.info(f"  Задача {task.id}: статус {task.status}, приоритет {task.priority}")

    for task in queue.filter_by_status("created"):
        logger.info(f"  Фильтр - created: Задача {task.id}")

    for task in queue.filter_by_priority(5, 10):
        logger.info(f"  Фильтр - priority 5-10: Задача {task.id}")


async def process_async_executor(queue: AsyncTaskQueue, logger: logging.Logger) -> None:
    """Обработка асинхронной очереди задач"""
    tasks = [
        {"id": 1, "type": "email", "payload": {"to": "user@example.com"}},
        {"id": 2, "type": "notification", "payload": {"user_id": 123}},
        {"id": 3, "type": "pkg", "payload": {"package_name": "my-package.tar.gz"}},
        {"id": 4, "type": "email", "payload": {"to": "admin@example.com"}},
        {"id": 5, "type": "unknown", "payload": {}},
    ]

    for task in tasks:
        await queue.put(task)
        logger.info(f"Добавлена задача {task['id']} (тип: {task['type']})")

    executor = AsyncTaskExecutor(queue, max_workers=3) # Создаём исполнителя

    executor.register_handler("email", EmailTaskHandler())
    executor.register_handler("notification", NotificationHandler())
    executor.register_handler("pkg", PkgTaskHandler())

    async with executor:
        logger.info("Исполнитель запущен, ожидаем обработку...")
        await asyncio.sleep(6)

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Запуск")

    queue = TaskQueue(max_size=10)
    queue.add_task(Task(1, "Задача 1", status="created", priority=5))
    queue.add_task(Task(2, "Задача 2", status="in_progress", priority=3))
    queue.add_task(Task(3, "Задача 3", status="created", priority=8))
    queue.add_task(Task(4, "Задача 4", status="completed", priority=1))
    queue.add_task(Task(5, "Задача 5", status="created", priority=2))

    process_queue(queue, logger)

    generator = TaskSourceGenerator()
    api = TaskSourceAPI()
    file = TaskSourceFile("data/tasks.json")

    sources = [generator, api, file]
    for source in sources:
        if isinstance(source, TaskSource):
            process_tasks(source, logger)
        else:
            logger.error(f"Источник {source.__class__.__name__} не соответствует протоколу")

    async def run():
        async_queue = AsyncTaskQueue(max_size=10)
        await process_async_executor(async_queue, logger)

    asyncio.run(run())

if __name__ == "__main__":
    main()