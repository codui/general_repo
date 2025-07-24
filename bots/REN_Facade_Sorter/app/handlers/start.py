"""
/start command handler for the REN Facade Sorter bot.
"""

import os
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from app.utils.logger import logger
from app.keyboards import selection_menu
from app.states import PhotoUploadStates


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
        
        # Основное сообщение с картинкой схемы и инлайн кнопками
        main_text = """🏢 **REN Facade Sorter Bot**

👋 Welcome! This bot will help you upload and sort facade photos of the building.

📸 **How it works:**
1. Choose inspection type (BW or SR)
2. Select building block (A or B)
3. Specify orientation (cardinal direction or courtyard)
4. Choose level (GF or L1-L11)
5. Upload photos

🔄 The bot will automatically save photos to the correct folder.

**Please provide the details of the apartment for which you would like to upload photos:**"""

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
                    caption=main_text,
                    reply_markup=selection_menu(),
                    parse_mode='Markdown'
                )
        else:
            # Если файл схемы не найден, отправляем только текст с кнопками
            logger.warning(f"Scheme image not found at {scheme_path}")
            await bot.send_message(
                message.chat.id,
                main_text + "\n\n⚠️ *Building scheme image not found*",
                reply_markup=selection_menu(),
                parse_mode='Markdown'
            )
    
    @bot.message_handler(commands=["help"])
    async def handle_help(message: Message):
        """
        Handle the /help command.
        """
        help_text = r"""🆘 **REN Facade Sorter Bot Help**

**Available commands:**
• `/start` - start working with the bot
• `/help` - show this help
• `/cancel` - cancel current operation

**Photo upload process:**
1. **Choose inspection** - BW or SR
2. **Select block** - A or B
3. **Specify orientation** - cardinal direction or courtyard
4. **Choose level** - GF or floors from L1 to L11
5. **Upload photos** - send one or multiple photos

**Save structure:**
Photos are saved to the folder:
`structure_inspections/{Inspection}/{Block}/{Level}/{Orientation}/unsorted/`

**Path examples:**
• BW, Block A, East, L5 → `structure_inspections/BW/A/L5/East/unsorted/`
• SR, Block B, Courtyard North, GF → `structure_inspections/SR/B/GF/Courtyard\_North/unsorted/`

❓ If you encounter problems, use `/cancel` and start over with `/start`"""

        await bot.send_message(
            message.chat.id,
            help_text,
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
            "❌ **Operation cancelled.**\n\nUse /start to begin again.",
            parse_mode='Markdown'
        )
        
        logger.info(f"User {message.from_user.id} cancelled operation") 