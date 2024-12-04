# bots/bot_whatsapp/db/models.py
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    JSON, 
    BigInteger,
    Text,
    DateTime
)
import json
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from settings.logger import setup_logger


Base = declarative_base()

logger = setup_logger(__name__)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, doc="Имя клиента")
    phone_number = Column(String(22), nullable=False, unique=True, doc="Номер телефона клиента")
    language = Column(String(50), nullable=True, doc="Предпочитаемый язык клиента")
    city = Column(String(100), nullable=True, doc="Город клиента")
    blocked_for_ai = Column(Boolean, nullable=False, default=False, doc="Флаг блокировки для AI")
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ConversationContext(Base):
    __tablename__ = 'conversation_contexts'
    
    phone_number = Column(String(22), primary_key=True, nullable=False)
    context = Column(JSONB, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    async def get_or_create(cls, session, phone_number: str):
        """Получает или создает контекст для указанного номера телефона"""
        try:
            from sqlalchemy.future import select
            stmt = select(cls).where(cls.phone_number == phone_number)
            result = await session.execute(stmt)
            context = result.scalar_one_or_none()
            
            if not context:
                context = cls(phone_number=phone_number, context={})  # Чистый Python-словарь
                session.add(context)
                await session.commit()
            
            return context
        except Exception as e:
            logger.error(f"Ошибка при получении/создании контекста: {str(e)}")
            raise

    async def save_context(self, session, conversation_history: list):
        """Сохраняет историю разговора в базу данных с корректной сериализацией"""
        try:
            # Используем словарь напрямую, без доп. сериализации
            self.context = {
                "history": conversation_history
            }
            self.updated_at = datetime.now()
            await session.commit()
        except Exception as e:
            logger.error(f"Ошибка при сохранении контекста: {str(e)}")
            raise

    @property
    def conversation_history(self) -> list:
        """Возвращает историю разговора в человеко-читаемом виде"""
        if not self.context:
            return []
        try:
            # Напрямую возвращаем список истории
            return self.context.get("history", [])
        except Exception as e:
            logger.error(f"Ошибка при обработке истории: {str(e)}")
            return []


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, nullable=False, doc="ID квитанции")
    type_webhook = Column(String(50), nullable=False, doc="Тип вебхука")
    instance_id = Column(BigInteger, nullable=False, doc="ID инстанции")
    wid = Column(String(100), nullable=False, doc="ID WhatsApp")
    type_instance = Column(String(50), nullable=False, doc="Тип инстанции")
    timestamp = Column(BigInteger, nullable=False, doc="Метка времени")
    message_id = Column(String(100), nullable=False, doc="ID сообщения")
    chat_id = Column(String(100), nullable=False, doc="ID чата")
    chat_name = Column(String(255), doc="Имя чата")
    sender = Column(String(100), nullable=False, doc="ID отправителя")
    sender_name = Column(String(255), doc="Имя отправителя")
    sender_contact_name = Column(String(255), doc="Имя контакта отправителя")
    message_type = Column(String(50), nullable=False, doc="Тип сообщения")
    message_text = Column(Text, doc="Текст сообщения")
    description = Column(Text, doc="Описание")
    title = Column(String(255), doc="Заголовок")
    preview_type = Column(String(50), doc="Тип превью")
    jpeg_thumbnail = Column(Text, doc="Миниатюра JPEG (Base64)")
    forwarding_score = Column(Integer, default=0, doc="Счет пересылок")
    is_forwarded = Column(Boolean, default=False, doc="Флаг пересылки")
    raw_data = Column(JSON, doc="Сырые данные уведомления")

    timestamp = Column(DateTime, default=datetime.now)