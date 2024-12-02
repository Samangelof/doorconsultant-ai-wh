# bot_whatsapp/controller/green_api_heandler.py
import aiohttp
import logging
from typing import Dict, Optional


logger = logging.getLogger(__name__)

class GreenAPIHandler:
    def __init__(self, instance_id: str, api_token: str):
        self.instance_id = instance_id
        self.api_token = api_token
        # Формируем базовый URL для запросов
        self.base_url = f"https://api.green-api.com/waInstance{instance_id}"
        # Сессия HTTP-клиента (инициализируется позже)
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"Инициализация GreenAPIHandler для инстанса {instance_id}")

    async def __aenter__(self):
        """Контекстный менеджер для автоматического открытия HTTP-сессии"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Контекстный менеджер для автоматического закрытия HTTP-сессии"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def send_message(self, phone: str, message: str) -> Dict:
        # Если сессия не инициализирована или закрыта, создаю временную сессию
        if not self.session or self.session.closed:
            async with aiohttp.ClientSession() as session:
                return await self._send_message(session, phone, message)
        return await self._send_message(self.session, phone, message)

    async def receive_notification(self) -> Dict:
        if not self.session or self.session.closed:
            async with aiohttp.ClientSession() as session:
                return await self._receive_notification(session)
        return await self._receive_notification(self.session)

    async def delete_notification(self, receipt_id: str) -> Dict:
        if not self.session or self.session.closed:
            async with aiohttp.ClientSession() as session:
                return await self._delete_notification(session, receipt_id)
        return await self._delete_notification(self.session, receipt_id)

#* Вспомогательные функции
    # Логика отправки сообщений
    async def _send_message(self, session, phone: str, message: str) -> Dict:
        endpoint = f"{self.base_url}/sendMessage/{self.api_token}"
        payload = {
            "chatId": phone,
            "message": message
        }
        async with session.post(endpoint, json=payload) as response:
            result = await response.json()
            logger.info(f"Отправка сообщения на {phone}")
            logger.info(f"Эндпоинт: {endpoint}")
            logger.info(f"Тело запроса: {payload}")
            logger.info(f"Статус ответа: {response.status}")
            logger.info(f"Результат ответа: {result}")
            return result

    # Логика получения уведомлений
    async def _receive_notification(self, session) -> Dict:
        endpoint = f"{self.base_url}/receiveNotification/{self.api_token}"
        async with session.get(endpoint) as response:
            result = await response.json()
            logger.info("Уведомление получено успешно")
            return result

    # Логика удаления уведомлений
    async def _delete_notification(self, session, receipt_id: str) -> Dict:
        endpoint = f"{self.base_url}/deleteNotification/{self.api_token}/{receipt_id}"
        async with session.delete(endpoint) as response:
            result = await response.json()
            logger.info(f"Уведомление с ID {receipt_id} удалено успешно")
            return result

