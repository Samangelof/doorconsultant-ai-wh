# WorkBox/main.py
import asyncio
import signal
from settings.logger import setup_logger
from settings.config import load_config
from bots.bot_whatsapp.controller.whatsapp_bot import WhatsAppBot


logger = setup_logger(__name__)

class BotsRunner:
    def __init__(self):
        self.config = load_config()
        self.bots = {} 
        self.running_tasks = []
        
    async def start_whatsapp_bot(self):
        try:
            instance_id = self.config.WHATSAPP_INSTANCE_ID
            api_token = self.config.WHATSAPP_API_TOKEN
            
            bot = WhatsAppBot(instance_id, api_token)
            # Запуск бота с его собственным обработчиком
            await bot.start()
            
        except Exception as e:
            logger.error(f'Бот WhatsApp перестал работать: {e}', exc_info=True)
            await asyncio.sleep(5)
            await self.start_whatsapp_bot()

    async def start_telegram_bot(self):
        pass

    async def start_instagram_bot(self):
        pass

    def create_tasks(self):
        if self.config.ENABLE_WHATSAPP:
            self.running_tasks.append(self.start_whatsapp_bot())
        
        if self.config.ENABLE_TELEGRAM:
            self.running_tasks.append(self.start_telegram_bot())
            
        if self.config.ENABLE_INSTAGRAM:
            self.running_tasks.append(self.start_instagram_bot())

    async def run(self):
        logger.info('Запуск всех ботов...')
        self.create_tasks()
        
        if not self.running_tasks:
            logger.warning('В конфигурации не включены боты!')
            return
            
        try:
            await asyncio.gather(*self.running_tasks)
        except Exception as e:
            logger.error(f'Ошибка при запуске ботов: {e}', exc_info=True)
        finally:
            logger.info('Завершение работы всех ботов...')

async def shutdown(loop, signal):
    logger.info(f'Получен сигнал завершения работы {signal.name}...')
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    
    for task in tasks:
        task.cancel()
        
    logger.info(f'Отмена {len(tasks)} активных задач')
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def main():
    runner = BotsRunner()
    
    loop = asyncio.get_event_loop()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        try:
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(shutdown(loop, s))
            )
        except NotImplementedError:
            pass

    try:
        loop.run_until_complete(runner.run())
    finally:
        loop.close()

if __name__ == '__main__':
    main()

