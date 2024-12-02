# bot_whatsapp/utils/extract_message.py
from typing import Dict, Optional
import logging


logger = logging.getLogger(__name__)


def extract_message_text(message_data: Dict) -> Optional[str]:
    """
    Функция для извлечения текста сообщения в зависимости от его типа.

    :param message_data: Данные о сообщении (dict)
    :return: Текст сообщения или None, если текста нет
    """
    logger.info(f"Исходные данные для извлечения текста: {message_data}")
    message_type = message_data.get("typeMessage", "")
    if message_type == "textMessage":
        return message_data.get("textMessageData", {}).get("textMessage", None)
    elif message_type == "extendedTextMessage":
        return message_data.get("extendedTextMessageData", {}).get("text", None)
    elif message_type == "audioMessage":
        return None
    else:
        return None
    

def extract_message_data(notification: Dict) -> Dict:
    """Извлекает все необходимые данные из уведомления для сохранения в базу данных"""
    body = notification.get("body", {})
    receipt_id = notification.get("receiptId")
    instance_data = body.get("instanceData", {})
    sender_data = body.get("senderData", {})
    message_data = body.get("messageData", {})
    message_text = extract_message_text(message_data)

    return {
        "receipt_id": receipt_id,
        "type_webhook": body.get("typeWebhook"),
        "instance_id": instance_data.get("idInstance"),
        "wid": instance_data.get("wid"),
        "type_instance": instance_data.get("typeInstance"),
        "timestamp": body.get("timestamp"),
        "message_id": body.get("idMessage"),
        "chat_id": sender_data.get("chatId"),
        "chat_name": sender_data.get("chatName"),
        "sender": sender_data.get("sender"),
        "sender_name": sender_data.get("senderName"),
        "sender_contact_name": sender_data.get("senderContactName"),
        "message_type": message_data.get("typeMessage"),
        "message_text": message_text,
    }


