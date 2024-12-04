# bot_whatsapp/controller/whatsapp_bot.py
import asyncio
from typing import Dict
from datetime import datetime
from settings.logger import setup_logger
from settings.connection_db import async_session
from urllib.error import HTTPError
from bots.bot_whatsapp.controller.green_api_handler import GreenAPIHandler
from bots.bot_whatsapp.db.queries import save_notification_to_db
from bots.bot_whatsapp.utils.extract_message import extract_message_data
from bots.bot_whatsapp.controller.webhook_handler import WebhookHandler
from bots.bot_whatsapp.stack.traveler import AITraveler


logger = setup_logger(__name__)


class WhatsAppBot:
    def __init__(self, instance_id: str, api_token: str):
        self.green_api = GreenAPIHandler(instance_id, api_token)
        self.webhook_handler = WebhookHandler()
        self.ai_traveler = AITraveler()

    async def start(self):
        logger.info("Запуск бота WhatsApp...")
        while True:
            try:
                async with self.green_api as api:
                    # Получаю уведомление от API
                    notification = await api.receive_notification()
                    
                    if notification:
                        await self.message_handler(notification)
                        try:
                            await api.delete_notification(notification.get("receiptId"))
                        except Exception as delete_error:
                            logger.error(f"Ошибка при удалении уведомления: {delete_error}")
                    else:
                        logger.warning("Пустой ответ от API. Пропускаю обработку уведомления.")
            
            except Exception as e:
                if isinstance(e, HTTPError) and e.response.status_code == 500:
                    logger.warning(f"Ошибка 500 от API, продолжаю работу.")
                else:
                    logger.error(f"Ошибка при опросе: {e}")
            
            await asyncio.sleep(1)

    async def send_message(self, phone: str, message: str) -> Dict:
        """Прокси-метод для отправки сообщения"""
        async with self.green_api as api:
            return await api.send_message(phone, message)

    async def message_handler(self, notification: Dict):
        """Основная логика обработки полученных сообщений от WhatsApp"""
        #* Сохраняю все данные сообщения
        logger.info(f"Получено уведомление/сообщение: {notification}")
        
        data_to_save = extract_message_data(notification)
        
        # Проверка и преобразование timestamp(Unix) в datetime
        if isinstance(data_to_save.get('timestamp'), int):
            data_to_save['timestamp'] = datetime.fromtimestamp(data_to_save['timestamp'])
            
        logger.info(f"\n\nДанные для сохранения: {data_to_save}\n\n")
        async with async_session() as session:
            await save_notification_to_db(session, data_to_save)

        # --------------------------------------------------------------------
        #? Делаю проверку на TypeWebhook и произвожу манипуляции
        #? ...
        body = notification.get("body", {})
        webhook_type = body.get("typeWebhook")

        webhook_handlers = {
            "incomingMessageReceived": self.webhook_handler.handle_incoming_message,
            "outgoingMessageReceived": self.webhook_handler.handle_outgoing_message,
            "outgoingAPIMessageReceived": self.webhook_handler.handle_outgoing_api_message,
        }

        handler = webhook_handlers.get(webhook_type)
        handler_name = handler.__name__ if handler else "Неизвестный обработчик"
        logger.info(f"Пришел хук с типом: {webhook_type}, обработчик: {handler_name}")

        if handler:
            try:
                result = await handler(body)
                logger.info(f"Результат обработки: {result}")
            except Exception as e:
                logger.error(f"Ошибка обработки вебхука {webhook_type}: {str(e)}")

