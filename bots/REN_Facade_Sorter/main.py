"""
Async entry point for the REN Facade Sorter bot with FSM and Redis storage.
"""

import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateRedisStorage
from telebot.asyncio_filters import StateFilter
from app.utils.logger import logger
from config import settings
# from app.handlers import register_handlers

# FSM storage (Redis)
storage = StateRedisStorage(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    prefix='ren_facade_sorter_bot_'
)

# Initialize bot
bot = AsyncTeleBot(settings.TELEGRAM_BOT_TOKEN, state_storage=storage)

bot.add_custom_filter(StateFilter(bot))

async def main():
    logger.info("Starting REN Facade Sorter bot with Redis FSM...")
    # register_handlers(bot)
    try:
        await bot.infinity_polling(timeout=30)
    except Exception as e:
        logger.exception(f"Bot infinity polling stopped: {e}")

if __name__ == "__main__":
    asyncio.run(main())
