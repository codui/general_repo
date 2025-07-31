"""
Handlers module for the REN Facade Sorter bot.
"""

from telebot.async_telebot import AsyncTeleBot
from .start import register_handlers as register_start_handlers
from .callbacks import register_handlers as register_callback_handlers
from .photos import register_handlers as register_photo_handlers


def register_handlers(bot: AsyncTeleBot):
    """
    Register all bot handlers.
    
    Args:
        bot: AsyncTeleBot instance
    """
    # Регистрируем хендлеры команд start, help, cancel
    register_start_handlers(bot)
    
    # Регистрируем хендлеры для inline кнопок
    register_callback_handlers(bot)
    
    # Регистрируем хендлеры для обработки фотографий
    register_photo_handlers(bot)
