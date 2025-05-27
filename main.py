import asyncio
import logging
from aiogram import Bot, Dispatcher

from bot.handlers import router
from bot.config import TOKENS_DATA
from bot.database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting bot...")
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    bot = Bot(token=TOKENS_DATA['tg_token'])
    dp = Dispatcher()
    dp.include_router(router)
    
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Closing database connections...")
        await close_db()
        await bot.session.close()
        logger.info("Bot stopped.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Бот выключен')