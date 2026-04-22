import json, logging
from src.models.task import Task, TaskSource

logger = logging.getLogger(__name__)


class TaskSourceFile:
    """Источник задач из JSON-файла"""
    def __init__(self, file_name: str):
        """Инициализирует файловый источник"""
        self.file_name = file_name
        logger.info(f"Инициализирован {self.__class__.__name__} с файлом {file_name}")

    def get_tasks(self) -> list[Task]:
        """Читает задачи из JSON-файла. Открывает файл, загружает JSON и преобразует в список задач"""
        try:
            with open(self.file_name, "r") as f:
                data = json.load(f)
                tasks = [Task(id = i["id"], description = "Задача из файла", priority = i["priority"], status = i["status"], payload={"user_id": i["user_id"]}) for i in data]
            return tasks
        except Exception as e:
            logger.error(f"Ошибка при чтении файла: {e}")
            raise