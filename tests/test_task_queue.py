import pytest
from src.models.task import Task
from src.models.task_queue import TaskQueue


class TestTaskQueue:

    def test_create_empty_queue(self):
        queue = TaskQueue()
        assert len(queue) == 0

    def test_add_task(self):
        queue = TaskQueue()
        queue.add_task(Task(13, "Задача"))
        assert len(queue) == 1

    def test_add_task_with_max_size(self):
        queue = TaskQueue(max_size=2)
        queue.add_task(Task(42, "Задача 1"))
        queue.add_task(Task(52, "Задача 2"))
        result = queue.add_task(Task(3, "Задача 3"))
        assert result is False
        assert len(queue) == 2

    def test_clear(self):
        queue = TaskQueue()
        queue.add_task(Task(13, "Задача"))
        queue.clear()
        assert len(queue) == 0

    def test_iteration(self):
        queue = TaskQueue()
        queue.add_task(Task(42, "Задача 1"))
        queue.add_task(Task(52, "Задача 2"))
        ids = [task.id for task in queue]
        assert ids == [42, 52]

    def test_multiple_iterations(self):
        """Проверка, что можно обходить очередь несколько раз."""
        queue = TaskQueue()
        queue.add_task(Task(1, "Задача"))

        first = [task.id for task in queue]
        second = [task.id for task in queue]
        assert first == second

    def test_getitem(self):
        queue = TaskQueue()
        task = Task(13, "Задача")
        queue.add_task(task)
        assert queue[0] == task

    def test_filter_by_status(self):
        queue = TaskQueue()
        queue.add_task(Task(42, "Задача 1", status="created"))
        queue.add_task(Task(52, "Задача 2", status="completed"))
        queue.add_task(Task(62, "Задача 3", status="created"))

        result = list(queue.filter_by_status("created"))
        assert len(result) == 2
        assert result[0].id == 42
        assert result[1].id == 62

    def test_filter_by_priority(self):
        queue = TaskQueue()
        queue.add_task(Task(42, "Задача 1", priority=2))
        queue.add_task(Task(52, "Задача 2", priority=5))
        queue.add_task(Task(62, "Задача 3", priority=8))

        result = list(queue.filter_by_priority(4, 9))
        assert len(result) == 2
        assert result[0].id == 52
        assert result[1].id == 62

    def test_repr(self):
        queue = TaskQueue(max_size=10)
        queue.add_task(Task(1, "Задача"))
        assert "TaskQueue" in repr(queue)
        assert "tasks=1" in repr(queue)
        assert "max_size=10" in repr(queue)