import asyncio
import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class TaskHandler(Protocol):
    """Протокол обработчика задач"""
    async def handle(self, task: dict) -> None:
        """Асинхронно обрабатывает задачу"""
        ...


class EmailTaskHandler:
    """Обработчик для отправки email"""
    async def handle(self, task: dict) -> None:
        logger.info(f"Отправляю email: {task['payload']['to']}")
        await asyncio.sleep(1)
        logger.info(f"Email отправлен на {task['payload']['to']}")


class NotificationHandler:
    """Обработчик для уведомлений"""
    async def handle(self, task: dict) -> None:
        logger.info(f"Отправляю уведомление пользователю: {task['payload']['user_id']}")
        await asyncio.sleep(0.5)
        logger.info(f"Уведомление отправлено пользователю {task['payload']['user_id']}")


class PkgTaskHandler:
    """Обработчик для сборки пакетов"""
    async def handle(self, task: dict) -> None:
        logger.info(f"Начинаю сборку пакета: {task['payload']['package_name']}")
        await asyncio.sleep(2)
        logger.info(f"Пакет {task['payload']['package_name']} собран")