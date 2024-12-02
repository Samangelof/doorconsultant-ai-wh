# bots/bot_whatsapp/stack/chatgpt_ai.py
import openai
from typing import Dict, Any
from settings.config import load_config
from settings.logger import setup_logger
from .base_ai import BaseAI


logger = setup_logger(__name__)


class ChatGPTAI(BaseAI):
    def __init__(self, model="gpt-4o-mini"):
        self.config = load_config()
        openai.api_key = self.config.OPENAI_API_KEY
        self.model = model

    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Генерация ответа через ChatGPT
        
        :param message: Текст входящего сообщения
        :param context: Дополнительный контекст для генерации ответа
        :return: Сгенерированный ответ
        """
        try:
            messages = [{"role": "user", "content": message}]
            
            if context and "system_prompt" in context:
                messages.insert(0, {"role": "system", "content": context["system_prompt"]})
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            return "Извините, произошла ошибка при генерации ответа."

    async def process_conversation(self, messages: list) -> str:
        """
        Обработка цепочки сообщений с сохранением контекста
        
        :param messages: Список сообщений в контексте беседы
        :return: Сгенерированный ответ
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Ошибка при обработке беседы: {e}")
            return "Извините, произошла ошибка при обработке беседы."

