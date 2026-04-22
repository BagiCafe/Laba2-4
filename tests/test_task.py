import pytest
from datetime import datetime
from src.models.task import Task, TaskSource
from src.exceptions import TaskStateError, TaskValidationError


class TestTask:

    def test_task_creation_old(self):
        task = Task(id=67, description="Задача", payload={"user_id": 121})
        assert task.id == 67
        assert task.payload == {"user_id": 121}

    def test_task_creation_new(self):
        task = Task(id=1, description="Тестовая задача", priority=5, status="created", payload={"user_id": 123, "data": "test"})
        assert task.id == 1
        assert task.description == "Тестовая задача"
        assert task.priority == 5
        assert task.status == "created"
        assert task.payload == {"user_id": 123, "data": "test"}
        assert isinstance(task.created_at, datetime)

    def test_task_different_payloads(self):
        task1 = Task(id=6, description="Задача", payload={"user_id": 123})
        task2 = Task(id=7, description="Задача", payload={"user_id": 456, "count": 10})
        assert task1.id != task2.id
        assert task1.payload != task2.payload

    def test_task_creation_valid(self):
        task = Task(id=1, description="Задача", payload={"user_id": 123, "data": "test"})
        assert task.id == 1
        assert task.description == "Задача"
        assert task.payload == {"user_id": 123, "data": "test"}
        assert isinstance(task.id, int)
        assert isinstance(task.description, str)
        assert isinstance(task.payload, dict)

    def test_task_creation_minimal(self):
        task = Task(id=42, description="Минимальная задача")
        assert task.id == 42
        assert task.description == "Минимальная задача"
        assert task.priority == 1
        assert task.status == "created"
        assert task.payload == {}

    def test_task_creation_different_types(self):
        task1 = Task(id=1, description="Задача", payload={"x": 1})
        task2 = Task(id=999, description="Задача", payload={"y": 2})
        task3 = Task(id=7, description="Задача", payload={"z": 3})

        assert task1.id == 1
        assert task2.id == 999
        assert task3.id == 7

    def test_task_equality(self):
        task1 = Task(id=1, description="Задача", payload={"x": 1})
        task2 = Task(id=1, description="Задача", payload={"x": 1})
        task3 = Task(id=2, description="Другая задача", payload={"x": 1})

        assert task1.id == task2.id
        assert task1.description == task2.description
        assert task1.priority == task2.priority
        assert task1.status == task2.status
        assert task1.payload == task2.payload
        assert task1.id != task3.id
        assert task1.description != task3.description

    def test_task_string_representation(self):
        task = Task(id=123, description="Тест", priority=3, payload={"name": "test"})
        repr_str = repr(task)
        assert "Task" in repr_str
        assert "id=123" in repr_str
        assert "payload={'name': 'test'}" in repr_str or "payload={'name': 'test'}" in repr_str
        assert "priority=3" in repr_str


class TestTaskProperties:

    def test_is_ready_property(self):
        task = Task(id=1, description="Готовая задача")
        assert task.is_ready is True
        task.status = "in_progress"
        assert task.is_ready is False
        task2 = Task(id=2, description="Другая задача")
        assert task2.is_ready is True

    def test_is_active_property(self):
        task = Task(id=1, description="Задача")
        assert task.is_active is False
        task.status = "in_progress"
        assert task.is_active is True
        task.status = "completed"
        assert task.is_active is False

    def test_is_completed_property(self):
        task = Task(id=1, description="Задача")
        assert task.is_completed is False
        task.status = "completed"
        assert task.is_completed is True

    def test_is_failed_property(self):
        task = Task(id=1, description="Задача")
        assert task.is_failed is False
        task.status = "failed"
        assert task.is_failed is True


class TestTaskMethods:

    def test_start_method(self):
        task = Task(id=1, description="Задача")
        assert task.status == "created"
        task.start()
        assert task.status == "in_progress"

    def test_start_method_with_invalid_status(self):
        task = Task(id=1, description="Задача")
        task.start()
        with pytest.raises(TaskStateError) as excinfo:
            task.start()
        assert "Нельзя начать" in str(excinfo.value)

    def test_complete_method(self):
        task = Task(id=1, description="Задача")
        task.start()
        task.complete()
        assert task.status == "completed"

    def test_complete_method_without_start(self):
        task = Task(id=1, description="Задача")
        with pytest.raises(TaskStateError) as excinfo:
            task.complete()
        assert "Нельзя завершить" in str(excinfo.value)

    def test_complete_cancelled_task(self):
        task = Task(id=1, description="Задача")
        task.cancel()
        with pytest.raises(TaskStateError):
            task.complete()

    def test_cancel_method(self):
        task = Task(id=1, description="Задача")
        task.cancel()
        assert task.status == "failed"

    def test_cancel_completed_task(self):
        task = Task(id=1, description="Задача")
        task.start()
        task.complete()
        with pytest.raises(TaskStateError) as excinfo:
            task.cancel()
        assert "Нельзя отменить" in str(excinfo.value)

    def test_cancel_in_progress_task(self):
        task = Task(id=1, description="Задача")
        task.start()
        task.cancel()
        assert task.status == "failed"


class TestTaskValidation:

    def test_invalid_id_negative(self):
        with pytest.raises(TaskValidationError):
            Task(id=-5, description="Задача")

    def test_invalid_id_zero(self):
        with pytest.raises(TaskValidationError):
            Task(id=0, description="Задача")

    def test_invalid_id_type(self):
        with pytest.raises(TaskValidationError):
            Task(id="1", description="Задача")

    def test_invalid_priority_low(self):
        with pytest.raises(TaskValidationError):
            Task(id=1, description="Задача", priority=0)

    def test_invalid_priority_high(self):
        with pytest.raises(TaskValidationError):
            Task(id=1, description="Задача", priority=11)

    def test_invalid_priority_type(self):
        with pytest.raises(TaskValidationError):
            Task(id=1, description="Задача", priority="высокий")

    def test_invalid_status(self):
        with pytest.raises(TaskValidationError):
            Task(id=1, description="Задача", status="unknown")


class TestTaskSourceProtocol:

    def test_protocol_with_valid_class(self):

        class ValidSource:
            def get_tasks(self) -> list[Task]:
                return [Task(1, description="Тест")]

        assert isinstance(ValidSource(), TaskSource)

    def test_protocol_with_invalid_class(self):

        class InvalidSource:
            def wrong_method(self) -> list[Task]:
                return []

        assert not isinstance(InvalidSource(), TaskSource)

    def test_protocol_with_wrong_return_type(self):

        class WrongReturnSource:
            def get_tasks(self) -> str:  # Должен быть list[Task]
                return "not a list"

        assert isinstance(WrongReturnSource(), TaskSource)
