# bots/bot_whatsapp/stack/traveler.py
import asyncio
from typing import Dict, Any, Optional
from settings.connection_db import async_session
from bots.bot_whatsapp.db.models import ConversationContext
from settings.logger import setup_logger
from .base_ai import BaseAI
from .chatgpt_ai import ChatGPTAI
from .prompts import SYSTEM_PROMPTS


logger = setup_logger(__name__)


class AITraveler:
    def __init__(self, ai_model: Optional[BaseAI] = None, phone_number: str = None):
        """
        Менеджер взаимодействия с AI-моделями
        
        :param ai_model: Экземпляр AI-модели (по умолчанию ChatGPT)
        :param phone_number: Номер телефона для сохранения контекста
        """
        self.ai_model = ai_model or ChatGPTAI()
        self.phone_number = phone_number
        self.conversation_history = []
        
        # Загрузка контекста из базы данных асинхронно
        if phone_number:
            asyncio.create_task(self.load_context_from_db())

    async def load_context_from_db(self):
        try:
            async with async_session() as session:
                context_record = await ConversationContext.get_or_create(session, self.phone_number)
                self.conversation_history = context_record.conversation_history
                logger.info(f"Загружена история разговора для {self.phone_number}: {self.conversation_history}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке контекста для {self.phone_number}: {str(e)}")


    async def save_context_to_db(self):
        """Сохранение контекста в базу данных"""
        if self.phone_number:
            async with async_session() as session:
                context_record = await ConversationContext.get_or_create(session, self.phone_number)
                await context_record.save_context(session, self.conversation_history)
                logger.info(f"Сохранена история разговора для {self.phone_number}")


    async def process_message(self, 
                               message: str, 
                               context_type: str = "default", 
                               max_history: int = 10) -> str:
        """Обработка входящего сообщения с учетом контекста и сохранением в БД"""
        context = {
            "system_prompt": SYSTEM_PROMPTS.get(context_type, SYSTEM_PROMPTS["default"])
        }

        # Добавляю текущее сообщение в историю
        if not self.conversation_history or self.conversation_history[-1] != {"role": "user", "content": message}:
            self.conversation_history.append({"role": "user", "content": message})

        logger.info(f"[{self.phone_number}] Сообщение добавлено в историю: {message}")

        # Усекаем историю до максимального размера
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]
            logger.info(f"История усечена до последних {max_history} сообщений.")

        # Генерируем полный список сообщений с системным промптом
        full_messages = [
            {"role": "system", "content": context["system_prompt"]}
        ] + self.conversation_history
        logger.info(f"Полный список сообщений для модели: {full_messages}")

        response = await self.ai_model.process_conversation(full_messages)
        if response is None:
            logger.error("AI модель вернула None. Используется ответ по умолчанию.")
            response = "Извините, я не смог обработать ваш запрос."

        # Добавляю ответ в историю
        self.conversation_history.append({"role": "assistant", "content": response})
        logger.info(f"Ответ от AI: {response}")

        # Сохраняем контекст в базу данных
        await self.save_context_to_db()

        return response

    async def reset_conversation(self):
        """Сброс истории беседы с удалением из базы данных"""
        self.conversation_history = []
        
        if self.phone_number:
            async with async_session() as session:
                context_record = await ConversationContext.get_or_create(session, self.phone_number)
                context_record.context = {}
                await session.commit()