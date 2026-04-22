import random, logging
from src.models.task import Task, TaskSource

logger = logging.getLogger(__name__)


class TaskSourceGenerator:
    """Генератор случайных задач"""
    def __init__(self):
        """Инициализирует генератор задач"""
        logger.info(f"Инициализирован {self.__class__.__name__}")

    def get_tasks(self) -> list[Task]:
        """Генерирует список случайных задач"""
        return [Task(id = random.randint(1,101), description=f"Сгенерированная задача", priority=random.randint(1, 10), status=random.choice(["created", "in_progress", "completed", "failed"]), payload = {"user_id": random.randint(100,1001), "count": random.randint(1000,10001)}) for i in range(10)]