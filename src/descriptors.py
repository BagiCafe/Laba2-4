from src.exceptions import TaskValidationError


class IntegerValidator:
    """Data-дескриптор для целочисленных полей с валидацией"""
    def __init__(self, name: str, min_value: int = 1, max_value: int = None):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TaskValidationError(f"{self.name} должен быть целым числом")
        if value < self.min_value:
            raise TaskValidationError(f"Значение не может быть меньше {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise TaskValidationError(f"Значение не может быть больше {self.max_value}")
        instance.__dict__[self.name] = value


class StringValidator:
    """Data-дескриптор для строковых полей с валидацией"""
    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TaskValidationError(f"{self.name} должен быть строкой")
        if not value.strip():
            raise TaskValidationError(f"{self.name} не может быть пустой")
        instance.__dict__[self.name] = value

class StatusValidator:
    """Data-дескриптор для статуса задачи с фиксированным набором значений"""
    STATUSES_VALID = {"created", "in_progress", "completed", "failed"}

    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if value not in self.STATUSES_VALID:
            raise TaskValidationError(f"Статус должен быть одним из: {self.STATUSES_VALID}")
        instance.__dict__[self.name] = value