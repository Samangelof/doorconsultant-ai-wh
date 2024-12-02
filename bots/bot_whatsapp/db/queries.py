# bots/bot_whatsapp/db/queries.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from typing import Dict
from settings.logger import setup_logger
from .models import Notification

logger = setup_logger(__name__)



async def create_notification(session: AsyncSession, data: dict) -> Notification:
    """
    Создает новую запись уведомления в базе данных.
    :param session: Асинхронная сессия SQLAlchemy
    :param data: Данные для создания уведомления
    :return: Созданный объект Notification
    """
    notification = Notification(**data)
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


async def get_notification_by_id(session: AsyncSession, notification_id: int) -> Notification:
    """
    Получает уведомление по ID.
    :param session: Асинхронная сессия SQLAlchemy
    :param notification_id: ID уведомления
    :return: Объект Notification
    """
    stmt = select(Notification).where(Notification.id == notification_id)
    result = await session.execute(stmt)
    try:
        return result.scalar_one()
    except NoResultFound:
        return None


async def get_all_notifications(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[Notification]:
    """
    Получает список уведомлений с пагинацией.
    :param session: Асинхронная сессия SQLAlchemy
    :param limit: Лимит записей
    :param offset: Смещение
    :return: Список объектов Notification
    """
    stmt = select(Notification).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_notification(session: AsyncSession, notification_id: int, data: dict) -> Notification:
    """
    Обновляет уведомление по ID.
    :param session: Асинхронная сессия SQLAlchemy
    :param notification_id: ID уведомления
    :param data: Данные для обновления
    :return: Обновленный объект Notification
    """
    stmt = select(Notification).where(Notification.id == notification_id)
    result = await session.execute(stmt)
    notification = result.scalar_one_or_none()
    if notification is None:
        return None
    for key, value in data.items():
        setattr(notification, key, value)
    await session.commit()
    await session.refresh(notification)
    return notification


async def delete_notification(session: AsyncSession, notification_id: int) -> bool:
    """
    Удаляет уведомление по ID.
    :param session: Асинхронная сессия SQLAlchemy
    :param notification_id: ID уведомления
    :return: Успешность операции
    """
    stmt = select(Notification).where(Notification.id == notification_id)
    result = await session.execute(stmt)
    notification = result.scalar_one_or_none()
    if notification is None:
        return False
    await session.delete(notification)
    await session.commit()
    return True


async def save_notification_to_db(session, data_to_save: Dict):
    """Сохраняет данные уведомления в базу данных"""
    try:
        await create_notification(session, data_to_save)
        logger.info("Уведомление сохранено в БД")
        # logger.info(f"Уведомление сохранено в БД: {data_to_save}")
    except Exception as db_error:
        logger.error(f"Ошибка при сохранении уведомления в БД: {db_error}")

