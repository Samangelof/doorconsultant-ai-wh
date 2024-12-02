# bot_whatsapp/utils/webhook_handler.py
from typing import Dict
import logging
from settings.logger import setup_logger
from settings.config import load_config
from bots.bot_whatsapp.stack.traveler import AITraveler
from bots.bot_whatsapp.utils.extract_message import extract_message_text
from bots.bot_whatsapp.controller.green_api_handler import GreenAPIHandler


logger = setup_logger(__name__)

class WebhookHandler:
    """Класс для обработки вебхуков WhatsApp."""
    def __init__(self):
        self.config = load_config()
        self.ai_travelers = {}
        instance_id = self.config.WHATSAPP_INSTANCE_ID
        api_token = self.config.WHATSAPP_API_TOKEN
            
        self.green_api = GreenAPIHandler(instance_id, api_token)


    async def handle_incoming_message(self, body: Dict):
        """Обрабатывает входящее сообщение."""
        message_data = body.get("messageData", {})
        message_text = extract_message_text(message_data)
        logger.info(f"Входящее сообщение {message_text}")
        # Получаем номер телефона отправителя
        phone_number = body.get("senderData", {}).get("sender", "")
        if not phone_number:
            raise ValueError("Номер телефона отсутствует в данных вебхука.")

        # Инициализируем AITraveler для нового номера телефона
        if phone_number not in self.ai_travelers:
            logger.info(f"Создание нового AITraveler для номера: {phone_number}")
            self.ai_travelers[phone_number] = AITraveler()
            
        # Генерируем ответ с помощью AI
        ai_traveler = self.ai_travelers[phone_number]
        ai_response = await ai_traveler.process_message(message_text)

        # Отправляем ответ через WhatsAppBot
        logger.info(f"Ответ от ИИ {ai_response}")
        await self.green_api.send_message(phone_number, ai_response)
        return ai_response

    async def handle_outgoing_message(self, body: Dict):
        """Обрабатывает исходящее сообщение."""
        # logger.info(f"Обработка исходящего сообщения: {body}")
        logger.info(f"Исходящее сообщения")
        # TODO: Реализовать логику обработки исходящего сообщения
        return "Обработано исходящее сообщение"

    async def handle_outgoing_api_message(self, body: Dict):
        """Обрабатывает исходящее сообщение через API."""
        # logger.info(f"Обработка исходящего API-сообщения: {body}")
        logger.info(f"Исходящее сообщения по API")
        # TODO: Реализовать логику обработки исходящего API-сообщения
        return "Обработано исходящее сообщение через API"

