# settings/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()

@dataclass
class Config:
    WHATSAPP_INSTANCE_ID: str
    WHATSAPP_API_TOKEN: str
    OPENAI_API_KEY: str
    MODEL_GPT: str
    TELEGRAM_BOT_TOKEN: str
    ENABLE_WHATSAPP: bool
    ENABLE_TELEGRAM: bool
    ENABLE_INSTAGRAM: bool
    


def load_config() -> Config:
    """Загружает конфигурацию из переменных окружения"""
    return Config(
        WHATSAPP_INSTANCE_ID=os.getenv("WHATSAPP_INSTANCE_ID", ""),
        WHATSAPP_API_TOKEN=os.getenv("WHATSAPP_API_TOKEN", ""),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        MODEL_GPT=os.getenv("MODEL_GPT", ""),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        ENABLE_WHATSAPP=os.getenv("ENABLE_WHATSAPP", "false").lower() == "true",
        ENABLE_TELEGRAM=os.getenv("ENABLE_TELEGRAM", "false").lower() == "true",
        ENABLE_INSTAGRAM=os.getenv("ENABLE_INSTAGRAM", "false").lower() == "true",
    )