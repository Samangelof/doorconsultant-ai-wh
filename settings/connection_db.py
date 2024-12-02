# settings/connection_db.py
import os
import urllib.parse
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
urllib.parse.quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

try:
    engine = create_async_engine(DATABASE_URL, echo=True)
except SQLAlchemyError as e:
    print(f'Ошибка подключения к базе данных: {e}')
    raise

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

