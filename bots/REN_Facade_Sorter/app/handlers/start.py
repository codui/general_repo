"""
/start command handler for the REN Facade Sorter bot.
"""

import os
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from app.utils.logger import logger
from app.keyboards import selection_menu
from app.states import PhotoUploadStates
from app.messages import WELCOME_MESSAGE, HELP_MESSAGE, CANCEL_MESSAGE, SCHEME_NOT_FOUND_WARNING


def register_handlers(bot: AsyncTeleBot):
    """
    Register all handlers for the /start command.
    """
    
    @bot.message_handler(commands=["start"])
    async def handle_start(message: Message):
        """
        Handle the /start command.
        """
        telegram_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        
        # Логируем начало взаимодействия с пользователем
        logger.info(f"User started bot: {telegram_id} (@{username}) - {first_name} {last_name}")

        # Путь к схеме
        scheme_path = os.path.join("app", "assets", "images", "scheme", "scheme.png")
        
        # Устанавливаем состояние выбора параметров
        await bot.set_state(message.from_user.id, PhotoUploadStates.selecting_parameters, message.chat.id)
        
        # Проверяем существование файла схемы
        if os.path.exists(scheme_path):
            # Отправляем сообщение с картинкой схемы и инлайн кнопками
            with open(scheme_path, 'rb') as photo:
                await bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=WELCOME_MESSAGE,
                    reply_markup=selection_menu(),
                    parse_mode='Markdown'
                )
        else:
            # Если файл схемы не найден, отправляем только текст с кнопками
            logger.warning(f"Scheme image not found at {scheme_path}")
            await bot.send_message(
                message.chat.id,
                WELCOME_MESSAGE + SCHEME_NOT_FOUND_WARNING,
                reply_markup=selection_menu(),
                parse_mode='Markdown'
            )
    
    @bot.message_handler(commands=["help"])
    async def handle_help(message: Message):
        """
        Handle the /help command.
        """
        await bot.send_message(
            message.chat.id,
            HELP_MESSAGE,
            parse_mode='Markdown'
        )
    
    @bot.message_handler(commands=["cancel"])
    async def handle_cancel(message: Message):
        """
        Handle the /cancel command - reset user state.
        """
        await bot.delete_state(message.from_user.id, message.chat.id)
        
        await bot.send_message(
            message.chat.id,
            CANCEL_MESSAGE,
            parse_mode='Markdown'
        )
        
        logger.info(f"User {message.from_user.id} cancelled operation") 