import random, logging
from src.models.task import Task, TaskSource

logger = logging.getLogger(__name__)


class TaskSourceAPI:
    """Имитация источника задач из внешнего API"""
    def __init__(self):
        """Инициализирует API-источник"""
        logger.info(f"Инициализирован {self.__class__.__name__}")

    def get_tasks(self) -> list[Task]:
        """Получает задачи из имитированного API"""
        return [
            Task(id=10, description="Задача из API", priority=random.randint(1, 10), payload={"user_id": random.randint(100, 1001), "count": random.randint(1000,10001)}),
            Task(id=11, description="Задача из API", priority=random.randint(1, 10), payload={"user_id": random.randint(100, 1001), "count": random.randint(1000,10001)}),
            Task(id=12, description="Задача из API", priority=random.randint(1, 10), payload={"user_id": random.randint(100, 1001), "count": random.randint(1000,10001)}),
            Task(id=13, description="Задача из API", priority=random.randint(1, 10), payload={"user_id": random.randint(100, 1001), "count": random.randint(1000,10001)})
        ]