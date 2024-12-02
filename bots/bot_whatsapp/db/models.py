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
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, doc="Имя клиента")
    phone_number = Column(String(15), nullable=False, unique=True, doc="Номер телефона клиента")
    language = Column(String(50), nullable=True, doc="Предпочитаемый язык клиента")
    city = Column(String(100), nullable=True, doc="Город клиента")
    blocked_for_ai = Column(Boolean, nullable=False, default=False, doc="Флаг блокировки для AI")
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ConversationContext(Base):
    __tablename__ = 'conversation_contexts'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    context = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    


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
