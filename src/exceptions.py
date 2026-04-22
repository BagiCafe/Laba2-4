class TaskError(Exception):
    """Базовое исключение для всех ошибок, связанных с задачами"""
    pass

class TaskStateError(TaskError):
   """Исключение при нарушении состояния задачи"""
   def __init__(self, message: str):
        self.message = message
        super().__init__(f"Ошибка состояния задачи: {message}")

class TaskValidationError(TaskError):
    """Ошибка валидации атрибута задачи"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Ошибка валидации: {message}")
