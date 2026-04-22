from typing import Protocol, runtime_checkable
from datetime import datetime
from src.exceptions import TaskStateError
from src.descriptors import IntegerValidator, StringValidator, StatusValidator


class Task:
    """Модель задачи с валидацией через дескрипторы"""
    id = IntegerValidator("_id", min_value=1)
    priority = IntegerValidator("_priority", min_value=1, max_value=10)
    description = StringValidator("_description")
    status = StatusValidator("_status")

    def __init__(self, id: int, description: str, priority: int = 1, status: str = "created", payload: dict = None):
        self.id = id
        self.description = description
        self.priority = priority
        self.status = status
        self._created_at = datetime.now()
        self.payload = payload or {}

    @property
    def created_at(self) -> datetime:
        """Время создания задачи"""
        return self._created_at

    @property
    def is_ready(self) -> bool:
        """Готовность задачи к выполнению"""
        return self.status == "created" and len(self.description) > 0

    @property
    def is_active(self) -> bool:
        """Проверка выполнения задачи сейчас"""
        return self.status == "in_progress"

    @property
    def is_completed(self) -> bool:
        """Проверка завершения задачи"""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Проверка отмены задачи"""
        return self.status == "failed"

    def start(self) -> None:
        """Начать выполнение задачи"""
        if self.status != "created":
            raise TaskStateError(f"Нельзя начать задачу со статусом '{self.status}'.")
        self.status = "in_progress"

    def cancel(self) -> None:
        """Отменить задачу"""
        if self.status == "completed":
            raise TaskStateError("Нельзя отменить завершённую задачу")
        self.status = "failed"

    def complete(self) -> None:
        """Отметить задачу как выполненную"""
        if self.status != "in_progress":
            raise TaskStateError(f"Нельзя завершить задачу со статусом '{self.status}'.")
        self.status = "completed"

    def __repr__(self) -> str:
        return f"Task(id={self.id}, description='{self.description}, priority={self.priority}, status={self.status}, payload={self.payload})"


@runtime_checkable
class TaskSource(Protocol):
    """Протокол источника задач. Определяет контракт, которому должны соответствовать все источники задач"""
    def get_tasks(self) -> list[Task]:
        """Получаем список задач из источника"""
        pass