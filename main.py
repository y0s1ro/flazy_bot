import asyncio
import logging
from aiogram import Bot, Dispatcher

from bot.handlers.common import router as common_router
from bot.handlers.admin import router as admin_router
from bot.handlers.reviews import router as reviews_router
from bot.config import TOKENS_DATA
from bot.database import init_db, close_db, get_session, get_user
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]) -> Any:
        # Check if user is banned (replace with your DB check)
        async with get_session() as session:
            user = await get_user(session, event.from_user.id)
            if user and user.is_banned:
                if isinstance(event, Message):
                    await event.answer("Вы забанены и не можете использовать бота.", show_alert=True)
                elif isinstance(event, CallbackQuery):
                    await event.answer("Вы забанены и не можете использовать бота.", show_alert=True)
                return
        return await handler(event, data)  # Continue if not banned


async def main():
    logger.info("Starting bot...")
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    bot = Bot(token=TOKENS_DATA['tg_token'])
    dp = Dispatcher()
    dp.message.middleware(BanMiddleware())
    dp.include_router(admin_router)
    dp.include_router(reviews_router)
    dp.include_router(common_router)
    
    
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