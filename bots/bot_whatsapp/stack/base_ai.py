# bots/bot_whatsapp/stack/base_ai.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAI(ABC):
    """Абстрактный базовый класс для AI-моделей"""
    
    @abstractmethod
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Генерация ответа на основе входящего сообщения
        
        :param message: Текст входящего сообщения
        :param context: Дополнительный контекст для генерации ответа
        :return: Сгенерированный ответ
        """
        pass

    @abstractmethod
    async def process_conversation(self, messages: list) -> str:
        """
        Обработка цепочки сообщений
        
        :param messages: Список сообщений в контексте беседы
        :return: Сгенерированный ответ
        """
        pass

