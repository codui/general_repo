"""
Callback handlers for inline buttons in the REN Facade Sorter bot.
"""

import os
from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InputMediaPhoto
from app.utils.logger import logger
from app.keyboards import selection_menu
from app.states import PhotoUploadStates
from app.messages import WELCOME_MESSAGE, SCHEME_NOT_FOUND_WARNING, BLOCK_SCHEME_NOT_FOUND_WARNING


def escape_markdown(text: str) -> str:
    """
    Escape special markdown characters in text.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for markdown
    """
    # Экранируем специальные символы markdown
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def register_handlers(bot: AsyncTeleBot):
    """
    Register all callback handlers for inline buttons.
    """
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("inspection_"))
    async def handle_inspection_selection(call: CallbackQuery):
        """
        Handle inspection type selection (BW/SR).
        """
        inspection = call.data.split("_")[1]  # "inspection_BW" -> "BW"
        
        # Сохраняем выбор в состоянии пользователя
        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            had_block = 'block' in data and data['block'] is not None
            data['inspection'] = inspection
            # Сбрасываем блок, ориентацию и уровень при смене инспекции
            data.pop('block', None)
            data.pop('orientation', None)
            data.pop('level', None)
        
        # Если до этого был выбран блок, меняем картинку на общую схему
        scheme_path = os.path.join("app", "assets", "images", "scheme", "scheme.png")
        if had_block and os.path.exists(scheme_path):
            from telebot.types import InputMediaPhoto
            with open(scheme_path, 'rb') as photo:
                media = InputMediaPhoto(photo, caption=WELCOME_MESSAGE, parse_mode='Markdown')
                await bot.edit_message_media(
                    media,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=selection_menu(inspection=inspection)
                )
        else:
            # Обновляем клавиатуру с выбранной инспекцией
            await bot.edit_message_reply_markup(
                call.message.chat.id,
                call.message.message_id,
                reply_markup=selection_menu(inspection=inspection)
            )
        
        await bot.answer_callback_query(call.id, f"✅ Selected inspection: {inspection}")
        logger.info(f"User {call.from_user.id} selected inspection: {inspection}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("block_"))
    async def handle_block_selection(call: CallbackQuery):
        """
        Handle building block selection (A/B) and update scheme image.
        """
        block = call.data.split("_")[1]  # "block_A" -> "A"
        
        # Получаем текущие данные и обновляем блок
        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            inspection = data.get('inspection')
            if not inspection:
                await bot.answer_callback_query(call.id, "❌ Please select inspection first!")
                return
            
            data['block'] = block
            # Сбрасываем ориентацию и уровень при смене блока
            data.pop('orientation', None)
            data.pop('level', None)
        
        # Путь к схеме конкретного блока
        scheme_path = os.path.join("app", "assets", "images", "scheme", f"scheme_block_{block}.png")
        
        # Обновляем картинку и клавиатуру
        if os.path.exists(scheme_path):
            with open(scheme_path, 'rb') as photo:
                media = InputMediaPhoto(photo, caption=WELCOME_MESSAGE, parse_mode='Markdown')
                await bot.edit_message_media(
                    media,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=selection_menu(inspection=inspection, block=block)
                )
        else:
            # Если файл схемы блока не найден, обновляем только клавиатуру и добавляем предупреждение
            logger.warning(f"Block scheme image not found at {scheme_path}")
            await bot.edit_message_caption(
                call.message.chat.id,
                call.message.message_id,
                caption=WELCOME_MESSAGE + BLOCK_SCHEME_NOT_FOUND_WARNING.format(block),
                reply_markup=selection_menu(inspection=inspection, block=block),
                parse_mode='Markdown'
            )
        
        await bot.answer_callback_query(call.id, f"✅ Selected block: {block}")
        logger.info(f"User {call.from_user.id} selected block: {block}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("orient_"))
    async def handle_orientation_selection(call: CallbackQuery):
        """
        Handle orientation selection (East/North/South/West/Courtyard_*).
        """
        orientation = call.data.replace("orient_", "")  # "orient_East" -> "East"
        
        # Получаем текущие данные
        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            inspection = data.get('inspection')
            block = data.get('block')
            
            if not inspection or not block:
                await bot.answer_callback_query(call.id, "❌ Please select inspection and block first!")
                return
            
            data['orientation'] = orientation
            # Сбрасываем уровень при смене ориентации
            data.pop('level', None)
        
        # Обновляем клавиатуру с выбранными параметрами, включая кнопки уровня
        await bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=selection_menu(inspection=inspection, block=block, orientation=orientation)
        )
        
        await bot.answer_callback_query(call.id, f"✅ Selected orientation: {orientation}")
        logger.info(f"User {call.from_user.id} selected orientation: {orientation}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("level_"))
    async def handle_level_selection(call: CallbackQuery):
        """
        Handle level (floor) selection.
        """
        # Парсим данные: "level_BW_A_East_L5" -> ["level", "BW", "A", "East", "L5"]
        parts = call.data.split("_")
        if len(parts) < 5:
            await bot.answer_callback_query(call.id, "❌ Invalid level data!")
            return
        
        inspection = parts[1]
        block = parts[2]
        orientation = "_".join(parts[3:-1])  # Поддержка "Courtyard_East"
        level = parts[-1]
        
        # Сохраняем данные
        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data.update({
                'inspection': inspection,
                'block': block,
                'orientation': orientation,
                'level': level
            })
        
        # Переходим к состоянию подтверждения
        await bot.set_state(call.from_user.id, PhotoUploadStates.confirming_selection, call.message.chat.id)
        
        # Обновляем клавиатуру с выбранным уровнем и кнопкой подтверждения
        await bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=selection_menu(inspection=inspection, block=block, orientation=orientation, level=level)
        )
        
        await bot.answer_callback_query(call.id, f"✅ Selected level: {level}")
        logger.info(f"User {call.from_user.id} selected level: {level}")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
    async def handle_confirm_selection(call: CallbackQuery):
        """
        Handle selection confirmation - ready for photo upload.
        """
        # Парсим данные из callback: "confirm_BW_A_East_L5"
        parts = call.data.replace("confirm_", "").split("_")
        if len(parts) < 4:
            await bot.answer_callback_query(call.id, "❌ Invalid selection data!")
            return
        
        inspection = parts[0]
        block = parts[1]
        orientation = "_".join(parts[2:-1])  # Поддержка "Courtyard_East"
        level = parts[-1]
        
        # Переходим к состоянию ожидания фотографий
        await bot.set_state(call.from_user.id, PhotoUploadStates.waiting_for_photos, call.message.chat.id)
        
        # Удаляем старое сообщение с фотографией
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Отправляем новое сообщение с информацией о выбранных параметрах
        upload_text = f"""📸 **Now Please Upload Pictures**

**Selected parameters:**
• **Inspection:** {inspection}
• **Block:** {block}
• **Orientation:** {escape_markdown(orientation)}
• **Level:** {level}

**Commands:**
• /cancel - cancel and start over"""

        await bot.send_message(
            call.message.chat.id,
            upload_text,
            parse_mode='Markdown'
        )
        
        await bot.answer_callback_query(call.id, "📸 Ready! Send your photos now.")
        logger.info(f"User {call.from_user.id} confirmed selection: {inspection}/{block}/{orientation}/{level}, waiting for photos")
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_selection")
    async def handle_back_to_selection(call: CallbackQuery):
        """
        Handle back to parameter selection.
        """
        # Получаем сохраненные данные
        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            inspection = data.get('inspection')
            block = data.get('block')
        
        # Возвращаемся к состоянию выбора параметров
        await bot.set_state(call.from_user.id, PhotoUploadStates.selecting_parameters, call.message.chat.id)
        
        # Удаляем текущее сообщение
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Отправляем исходное сообщение с картинкой схемы

        # Путь к общей схеме
        scheme_path = os.path.join("app", "assets", "images", "scheme", "scheme.png")
        
        # Отправляем с общей схемой
        if os.path.exists(scheme_path):
            with open(scheme_path, 'rb') as photo:
                await bot.send_photo(
                    call.message.chat.id,
                    photo,
                    caption=WELCOME_MESSAGE,
                    reply_markup=selection_menu(inspection=inspection, block=block),
                    parse_mode='Markdown'
                )
        else:
            # Если файл схемы не найден, отправляем только текст
            logger.warning(f"General scheme image not found at {scheme_path}")
            await bot.send_message(
                call.message.chat.id,
                WELCOME_MESSAGE + SCHEME_NOT_FOUND_WARNING,
                reply_markup=selection_menu(inspection=inspection, block=block),
                parse_mode='Markdown'
            )
        
        await bot.answer_callback_query(call.id, "⬅️ Back to parameter selection")
        logger.info(f"User {call.from_user.id} went back to parameter selection")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_level_"))
    async def handle_back_to_level(call: CallbackQuery):
        """
        Handle back to level selection.
        """
        # Парсим данные: "back_to_level_BW_A_East"
        parts = call.data.replace("back_to_level_", "").split("_")
        if len(parts) < 3:
            await bot.answer_callback_query(call.id, "❌ Invalid back data!")
            return
            
        inspection = parts[0]
        block = parts[1] 
        orientation = "_".join(parts[2:])  # Поддержка "Courtyard_East"
        
        # Возвращаемся к состоянию выбора уровня
        await bot.set_state(call.from_user.id, PhotoUploadStates.selecting_level, call.message.chat.id)
        
        # Удаляем текущее сообщение
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Подготавливаем текст для выбора уровня
        level_text = f"""📊 **Level Selection**

**Selected parameters:**
• Inspection: **{inspection}**
• Block: **{block}**  
• Orientation: **{escape_markdown(orientation)}**

**Choose level (floor):**"""

        # Путь к схеме конкретного блока
        scheme_path = os.path.join("app", "assets", "images", "scheme", f"scheme_block_{block}.png")
        
        # Отправляем сообщение с картинкой схемы блока
        if os.path.exists(scheme_path):
            with open(scheme_path, 'rb') as photo:
                await bot.send_photo(
                    call.message.chat.id,
                    photo,
                    caption=level_text,
                    reply_markup=selection_menu(inspection, block, orientation),
                    parse_mode='Markdown'
                )
        else:
            # Если файл схемы блока не найден, отправляем только текст
            logger.warning(f"Block scheme image not found at {scheme_path}")
            await bot.send_message(
                call.message.chat.id,
                level_text + BLOCK_SCHEME_NOT_FOUND_WARNING.format(block),
                reply_markup=selection_menu(inspection, block, orientation),
                parse_mode='Markdown'
            )
        
        await bot.answer_callback_query(call.id, "⬅️ Back to level selection")
        logger.info(f"User {call.from_user.id} went back to level selection")
    


    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_more_"))
    async def handle_add_more(call: CallbackQuery):
        """
        Handle add more photos to the same location.
        """
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        
        # Парсим данные: "add_more_BW_A_East_L5"
        parts = call.data.replace("add_more_", "").split("_")
        if len(parts) < 4:
            await bot.answer_callback_query(call.id, "❌ Invalid location data!")
            return
        
        inspection = parts[0]
        block = parts[1]
        orientation = "_".join(parts[2:-1])  # Поддержка "Courtyard_East"
        level = parts[-1]
        
        # Сохраняем данные локации
        async with bot.retrieve_data(user_id, chat_id) as data:
            data.update({
                'inspection': inspection,
                'block': block,
                'orientation': orientation,
                'level': level,
                'photos': []  # Очищаем предыдущие фото
            })
        
        # Переходим к состоянию ожидания фотографий
        await bot.set_state(user_id, PhotoUploadStates.waiting_for_photos, chat_id)
        
        upload_text = f"""📸 **Ready for More Photos**

**Current location:**
• Inspection: **{inspection}**
• Block: **{block}**
• Orientation: **{orientation.replace('_', ' ')}**
• Level: **{level}**

Send your photos to continue uploading to this location.

**Commands:**
• /cancel - cancel and start over"""

        await bot.edit_message_text(
            upload_text,
            chat_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        await bot.answer_callback_query(call.id, "📸 Ready for more photos!")
        logger.info(f"User {user_id} chose to add more photos to {inspection}/{block}/{level}/{orientation}")
    
    @bot.callback_query_handler(func=lambda call: call.data in ["next_location", "start_over"])
    async def handle_start_over(call: CallbackQuery):
        """
        Handle start over/another location - reset all data and return to beginning.
        """
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        
        # Очищаем все данные пользователя
        async with bot.retrieve_data(user_id, chat_id) as data:
            data.clear()
        
        # Возвращаемся к начальному состоянию
        await bot.set_state(user_id, PhotoUploadStates.selecting_parameters, chat_id)
        
        # Удаляем текущее сообщение
        await bot.delete_message(chat_id, call.message.message_id)
        
        # Отправляем начальное меню с картинкой схемы

        # Путь к общей схеме
        scheme_path = os.path.join("app", "assets", "images", "scheme", "scheme.png")
        
        # Отправляем с общей схемой
        if os.path.exists(scheme_path):
            with open(scheme_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id,
                    photo,
                    caption=WELCOME_MESSAGE,
                    reply_markup=selection_menu(),
                    parse_mode='Markdown'
                )
        else:
            # Если файл схемы не найден, отправляем только текст
            logger.warning(f"General scheme image not found at {scheme_path}")
            await bot.send_message(
                chat_id,
                WELCOME_MESSAGE + SCHEME_NOT_FOUND_WARNING,
                reply_markup=selection_menu(),
                parse_mode='Markdown'
            )
        
        # Определяем текст ответа в зависимости от действия
        callback_text = "🏠 Another location selected" if call.data == "next_location" else "🏠 Starting over..."
        await bot.answer_callback_query(call.id, callback_text)
        
        action = "moved to another location" if call.data == "next_location" else "started over"
        logger.info(f"User {user_id} {action}")