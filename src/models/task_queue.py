import logging
from src.models.task import Task

logger = logging.getLogger(__name__)


class TaskQueueIterator:
    """Итератор для очереди задач с обработкой StopIteration"""
    def __init__(self, tasks):
        """Инициализируем итератор"""
        self._tasks = tasks
        self._index = 0

    def __iter__(self):
        """Возвращаем итератор"""
        return self

    def __next__(self) -> Task:
        """Возвращаем следующую задачу или StopIteration"""
        if self._index >= len(self._tasks):
            raise StopIteration
        next_task = self._tasks[self._index]
        self._index += 1
        return next_task


class TaskQueue:
    """Очередь задач с поддержкой итерации и ленивой фильтрации"""
    def __init__(self, max_size=None):
        """Инициализируем пустую очередь"""
        self._tasks = []
        self._max_size = max_size
        logger.info(f"Создана очередь задач с max_size={max_size}")

    def add_task(self, task) -> bool:
        """Добавляем задачу в очередь"""
        if self._max_size and len(self._tasks) >= self._max_size:
            logger.warning(f"Очередь переполнена, задача {task.id} не добавлена")
            return False
        self._tasks.append(task)
        logger.info(f"Задача {task.id} добавлена в очередь (всего: {len(self._tasks)})")
        return True

    def __len__(self) -> int:
        """Получаем количество задач в очереди"""
        return len(self._tasks)

    def __getitem__(self, index) -> Task:
        """Возвращаем задачу по индексу"""
        return self._tasks[index]

    def __iter__(self) -> TaskQueueIterator:
        """Возвращаем новый итератор для повторного обхода."""
        logger.info(f"Начало итерации по очереди ({len(self._tasks)} задач)")
        return TaskQueueIterator(self._tasks.copy())

    def __repr__(self) -> str:
        return f"TaskQueue(tasks={len(self._tasks)}, max_size={self._max_size})"

    def filter_by_status(self, status):
        """Лениво фильтрует задачи по статусу"""
        logger.info(f"Фильтрация по статусу '{status}'")
        count = 0
        for task in self._tasks:
            if task.status == status:
                count += 1
                yield task
        logger.info(f"Найдено {count} задач со статусом '{status}'")

    def filter_by_priority(self, min_priority: int, max_priority: int):
        """Лениво фильтрует задачи по диапазону приоритета"""
        logger.info(f"Фильтрация по приоритету от {min_priority} до {max_priority}")
        count = 0
        for task in self._tasks:
            if min_priority <= task.priority <= max_priority:
                count += 1
                yield task
        logger.info(f"Найдено {count} задач в диапазоне приоритетов")

    def clear(self) -> None:
        """Очищаем очередь"""
        count = len(self._tasks)
        self._tasks.clear()
        logger.info(f"Очередь очищена (было {count} задач)")