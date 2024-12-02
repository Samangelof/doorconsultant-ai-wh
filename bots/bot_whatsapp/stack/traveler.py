# bots/bot_whatsapp/stack/traveler.py
from typing import Dict, Any, Optional
from settings.logger import setup_logger
from .base_ai import BaseAI
from .chatgpt_ai import ChatGPTAI
from .prompts import SYSTEM_PROMPTS


logger = setup_logger(__name__)


class AITraveler:
    def __init__(self, ai_model: Optional[BaseAI] = None):
        """
        Менеджер взаимодействия с AI-моделями
        
        :param ai_model: Экземпляр AI-модели (по умолчанию ChatGPT)
        """
        self.ai_model = ai_model or ChatGPTAI()
        self.conversation_history = []

    async def process_message(self, 
                               message: str, 
                               context_type: str = "default", 
                               max_history: int = 5) -> str:
        """
        Обработка входящего сообщения с учетом контекста
        
        :param message: Текст сообщения
        :param context_type: Тип контекста для системного промпта
        :param max_history: Максимальное количество сообщений в истории
        :return: Сгенерированный ответ
        """
        context = {
            "system_prompt": SYSTEM_PROMPTS.get(context_type, SYSTEM_PROMPTS["default"])
        }

        # Добавляем текущее сообщение в историю
        self.conversation_history.append({"role": "user", "content": message})
        logger.info(f"Сообщение добавлено в историю: {message}")

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

        # Добавляем ответ в историю
        self.conversation_history.append({"role": "assistant", "content": response})
        logger.info(f"Ответ от AI: {response}")

        return response

    def reset_conversation(self):
        """Сброс истории беседы"""
        self.conversation_history = []

