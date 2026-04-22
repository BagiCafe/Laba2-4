import pytest
import json
import os
import tempfile
from src.sources.generator_source import TaskSourceGenerator
from src.sources.api_source import TaskSourceAPI
from src.sources.file_source import TaskSourceFile
from src.models.task import Task, TaskSource


class TestTaskSourceGenerator:

    def setup_method(self):
        self.source = TaskSourceGenerator()

    def test_implements_protocol(self):
        source = TaskSourceGenerator()
        assert isinstance(source, TaskSource)

    def test_get_tasks_returns_list(self):
        source = TaskSourceGenerator()
        tasks = source.get_tasks()
        assert isinstance(tasks, list)

    def test_get_tasks_returns_10_tasks(self):
        source = TaskSourceGenerator()
        tasks = source.get_tasks()
        assert len(tasks) == 10

    def test_all_tasks_are_task_instances(self):
        source = TaskSourceGenerator()
        tasks = source.get_tasks()
        for task in tasks:
            assert isinstance(task, Task)

    def test_tasks_have_required_structure(self):
        source = TaskSourceGenerator()
        tasks = source.get_tasks()
        for task in tasks:
            assert hasattr(task, 'id')
            assert hasattr(task, 'payload')
            assert isinstance(task.id, int)
            assert isinstance(task.payload, dict)
            assert 'user_id' in task.payload
            assert 'count' in task.payload

    def test_tasks_have_required_payload_fields(self):
        tasks = self.source.get_tasks()
        for task in tasks:
            assert 'user_id' in task.payload
            assert 'count' in task.payload
            assert isinstance(task.payload['user_id'], int)
            assert isinstance(task.payload['count'], int)

    def test_payload_values_in_range(self):
        tasks = self.source.get_tasks()
        for task in tasks:
            assert 100 <= task.payload['user_id'] <= 1001
            assert 1000 <= task.payload['count'] <= 10001

class TestTaskSourceAPI:

    def setup_method(self):
        self.source = TaskSourceAPI()

    def test_implements_protocol(self):
        source = TaskSourceAPI()
        assert isinstance(source, TaskSource)

    def test_get_tasks_returns_list(self):
        tasks = self.source.get_tasks()
        assert isinstance(tasks, list)

    def test_get_tasks_returns_4_tasks(self):
        source = TaskSourceAPI()
        tasks = source.get_tasks()
        assert len(tasks) == 4

    def test_tasks_have_fixed_ids(self):
        source = TaskSourceAPI()
        tasks = source.get_tasks()
        expected_ids = {10, 11, 12, 13}
        actual_ids = {task.id for task in tasks}
        assert actual_ids == expected_ids

    def test_tasks_have_correct_structure(self):
        tasks = self.source.get_tasks()
        for task in tasks:
            assert isinstance(task, Task)
            assert isinstance(task.id, int)
            assert isinstance(task.payload, dict)
            assert 'user_id' in task.payload
            assert 'count' in task.payload

    def test_payload_values_in_range(self):
        tasks = self.source.get_tasks()
        for task in tasks:
            assert 100 <= task.payload['user_id'] <= 1001
            assert 1000 <= task.payload['count'] <= 10001

class TestTaskSourceFile:
    @pytest.fixture
    def temp_json_file(self):
        """Создаёт временный JSON-файл с тестовыми данными."""
        data = [
            {"id": 1, "description": "Задача из файла 1", "priority": 5, "status": "created", "user_id": 101},
            {"id": 2, "description": "Задача из файла 2", "priority": 3, "status": "in_progress", "user_id": 102},
            {"id": 3, "description": "Задача из файла 3", "priority": 1, "status": "completed", "user_id": 103}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        # Передаём путь к файлу в тест
        yield temp_path

        # Очистка после теста
        os.unlink(temp_path)

    def test_implements_protocol(self, temp_json_file):
        source = TaskSourceFile(temp_json_file)
        assert isinstance(source, TaskSource)

    def test_read_tasks_from_file(self, temp_json_file):
        source = TaskSourceFile(temp_json_file)
        tasks = source.get_tasks()

        assert len(tasks) == 3
        assert tasks[0].id == 1
        assert tasks[0].payload == {"user_id": 101}
        assert tasks[1].id == 2
        assert tasks[1].payload == {"user_id": 102}

    def test_file_not_found(self):
        source = TaskSourceFile("non_existent_file.json")
        with pytest.raises(FileNotFoundError):
            source.get_tasks()

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_path = f.name

        try:
            source = TaskSourceFile(temp_path)
            tasks = source.get_tasks()
            assert len(tasks) == 0
        finally:
            os.unlink(temp_path)

class TestIntegration:

    def setup_method(self):
        self.temp_files = []

    def teardown_method(self):
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.unlink(file_path)

    def create_temp_json_file(self, data):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        self.temp_files.append(temp_path)
        return temp_path

    def test_all_sources_implement_protocol(self):
        generator = TaskSourceGenerator()
        api = TaskSourceAPI()
        file_source = TaskSourceFile(self.create_temp_json_file([]))

        sources = [generator, api, file_source]
        for source in sources:
            assert isinstance(source, TaskSource), f"{source.__class__.__name__} не реализует протокол"

    def test_unified_processing_function(self):

        def count_tasks(source):
            return len(source.get_tasks())

        generator = TaskSourceGenerator()
        api = TaskSourceAPI()
        file_source = TaskSourceFile(self.create_temp_json_file([
            {"id": 1, "description": "Тест 1", "priority": 3, "status": "created", "user_id": 101},
            {"id": 2, "description": "Тест 2", "priority": 5, "status": "in_progress", "user_id": 102}
        ]))
        assert count_tasks(generator) == 10
        assert count_tasks(api) == 4
        assert count_tasks(file_source) == 2

    def test_runtime_type_check_with_isinstance(self):

        class NotASource:
            def not_get_tasks(self):
                return []

        generator = TaskSourceGenerator()
        api = TaskSourceAPI()
        file_source = TaskSourceFile(self.create_temp_json_file([]))
        invalid = NotASource()

        assert isinstance(generator, TaskSource)
        assert isinstance(api, TaskSource)
        assert isinstance(file_source, TaskSource)
        assert not isinstance(invalid, TaskSource)