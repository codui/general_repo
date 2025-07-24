"""
Photo upload handlers for the REN Facade Sorter bot.
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from app.utils.logger import logger
from app.keyboards.inline import post_upload_menu
from app.states import PhotoUploadStates

# Global dictionary to store media groups
media_groups: Dict[str, List[Message]] = {}
media_group_timers: Dict[str, asyncio.Task] = {}


def register_handlers(bot: AsyncTeleBot):
    """
    Register all photo upload handlers.
    """
    
    @bot.message_handler(content_types=['photo'], state=PhotoUploadStates.waiting_for_photos)
    async def handle_photo_upload(message: Message):
        """
        Handle photo upload during waiting_for_photos state.
        Supports both single photos and media groups.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Проверяем параметры пользователя
        async with bot.retrieve_data(user_id, chat_id) as data:
            inspection = data.get('inspection')
            block = data.get('block')
            orientation = data.get('orientation')
            level = data.get('level')
            
            if not all([inspection, block, orientation, level]):
                await bot.send_message(
                    chat_id,
                    "❌ **Error:** Missing selection parameters. Please start over with /start",
                    parse_mode='Markdown'
                )
                logger.error(f"User {user_id} missing parameters: {data}")
                return
        
        # Проверяем, является ли это частью медиагруппы
        if message.media_group_id:
            await handle_media_group_photo(bot, message)
        else:
            await handle_single_photo(bot, message)

    @bot.message_handler(content_types=['document'], state=PhotoUploadStates.waiting_for_photos)
    async def handle_document_upload(message: Message):
        """
        Handle document upload (images sent as files) during waiting_for_photos state.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Проверяем параметры пользователя
        async with bot.retrieve_data(user_id, chat_id) as data:
            inspection = data.get('inspection')
            block = data.get('block')
            orientation = data.get('orientation')
            level = data.get('level')
            
            if not all([inspection, block, orientation, level]):
                await bot.send_message(
                    chat_id,
                    "❌ **Error:** Missing selection parameters. Please start over with /start",
                    parse_mode='Markdown'
                )
                logger.error(f"User {user_id} missing parameters: {data}")
                return
        
        # Проверяем, что это изображение
        document = message.document
        if not document.mime_type or not document.mime_type.startswith('image/'):
            await bot.send_message(
                chat_id,
                "❌ **Error:** Please send only image files (JPG, PNG, etc.)",
                parse_mode='Markdown'
            )
            return
        
        # Проверяем, является ли это частью медиагруппы
        if message.media_group_id:
            await handle_media_group_document(bot, message)
        else:
            await handle_single_document(bot, message)

    @bot.message_handler(content_types=['text'], state=PhotoUploadStates.waiting_for_photos)
    async def handle_text_during_upload(message: Message):
        """
        Handle text messages during photo upload state.
        """
        if message.text and not message.text.startswith('/'):
            await bot.send_message(
                message.chat.id,
                "📸 **Send photos or use commands:**\n\n"
                "• Send photos to upload them\n"
                "• Send images as files if needed\n"
                "• Use /cancel to cancel operation",
                parse_mode='Markdown'
            )


async def handle_media_group_photo(bot: AsyncTeleBot, message: Message):
    """
    Handle photo that is part of a media group.
    """
    media_group_id = message.media_group_id
    user_id = message.from_user.id
    
    # Создаем уникальный ключ для пользователя и медиагруппы
    group_key = f"{user_id}_{media_group_id}"
    
    # Добавляем фото в медиагруппу
    if group_key not in media_groups:
        media_groups[group_key] = []
    
    media_groups[group_key].append(message)
    
    # Отменяем предыдущий таймер если он есть
    if group_key in media_group_timers:
        media_group_timers[group_key].cancel()
    
    # Запускаем новый таймер (ждем 1 секунду после последнего фото)
    media_group_timers[group_key] = asyncio.create_task(
        process_media_group_delayed(bot, group_key, user_id, message.chat.id)
    )


async def handle_media_group_document(bot: AsyncTeleBot, message: Message):
    """
    Handle document (image file) that is part of a media group.
    """
    media_group_id = message.media_group_id
    user_id = message.from_user.id
    
    # Создаем уникальный ключ для пользователя и медиагруппы
    group_key = f"{user_id}_{media_group_id}"
    
    # Добавляем документ в медиагруппу
    if group_key not in media_groups:
        media_groups[group_key] = []
    
    media_groups[group_key].append(message)
    
    # Отменяем предыдущий таймер если он есть
    if group_key in media_group_timers:
        media_group_timers[group_key].cancel()
    
    # Запускаем новый таймер (ждем 1 секунду после последнего файла)
    media_group_timers[group_key] = asyncio.create_task(
        process_media_group_delayed(bot, group_key, user_id, message.chat.id)
    )


async def process_media_group_delayed(bot: AsyncTeleBot, group_key: str, user_id: int, chat_id: int):
    """
    Process media group after a delay to ensure all photos are received.
    Now saves photos immediately without confirmation.
    """
    try:
        # Ждем 1 секунду чтобы получить все фото из группы
        await asyncio.sleep(1.0)
        
        if group_key not in media_groups:
            return
        
        messages = media_groups[group_key]
        photo_count = len(messages)
        
        # Получаем параметры пользователя
        async with bot.retrieve_data(user_id, chat_id) as data:
            inspection = data.get('inspection')
            block = data.get('block')
            orientation = data.get('orientation')
            level = data.get('level')
        
        # Подготавливаем список фотографий для сохранения
        photos_to_save = []
        for msg in messages:
            if msg.photo:
                # Фотография
                photo = msg.photo[-1]  # Наивысшее качество
                photo_info = {
                    'file_id': photo.file_id,
                    'file_unique_id': photo.file_unique_id,
                    'width': photo.width,
                    'height': photo.height,
                    'file_size': photo.file_size,
                    'timestamp': datetime.now().isoformat(),
                    'caption': msg.caption or "",
                    'type': 'photo'
                }
            elif msg.document:
                # Документ (изображение)
                document = msg.document
                photo_info = {
                    'file_id': document.file_id,
                    'file_unique_id': document.file_unique_id,
                    'width': getattr(document, 'width', 0),
                    'height': getattr(document, 'height', 0),
                    'file_size': document.file_size,
                    'timestamp': datetime.now().isoformat(),
                    'caption': msg.caption or "",
                    'type': 'document',
                    'file_name': document.file_name or 'image'
                }
            
            photos_to_save.append(photo_info)
        
        # Сразу сохраняем фотографии
        await save_photos_immediate(bot, user_id, chat_id, photos_to_save, inspection, block, orientation, level)
        
        logger.info(f"User {user_id} uploaded media group with {photo_count} photos for {inspection}/{block}/{level}/{orientation}")
        
        # Очищаем медиагруппу
        del media_groups[group_key]
        del media_group_timers[group_key]
        
    except asyncio.CancelledError:
        # Таймер был отменен, ничего не делаем
        pass
    except Exception as e:
        logger.error(f"Error processing media group {group_key}: {e}")


async def handle_single_photo(bot: AsyncTeleBot, message: Message):
    """
    Handle single photo upload. Now saves immediately without confirmation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Получаем параметры пользователя
    async with bot.retrieve_data(user_id, chat_id) as data:
        inspection = data.get('inspection')
        block = data.get('block')
        orientation = data.get('orientation')
        level = data.get('level')
    
    # Получаем фото в наивысшем качестве
    photo = message.photo[-1]
    
    # Подготавливаем информацию о фото
    photo_info = {
        'file_id': photo.file_id,
        'file_unique_id': photo.file_unique_id,
        'width': photo.width,
        'height': photo.height,
        'file_size': photo.file_size,
        'timestamp': datetime.now().isoformat(),
        'caption': message.caption or "",
        'type': 'photo'
    }
    
    # Сразу сохраняем фотографию
    await save_photos_immediate(bot, user_id, chat_id, [photo_info], inspection, block, orientation, level)
    
    logger.info(f"User {user_id} uploaded single photo for {inspection}/{block}/{level}/{orientation}")


async def handle_single_document(bot: AsyncTeleBot, message: Message):
    """
    Handle single document (image file) upload. Saves immediately without confirmation.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Получаем параметры пользователя
    async with bot.retrieve_data(user_id, chat_id) as data:
        inspection = data.get('inspection')
        block = data.get('block')
        orientation = data.get('orientation')
        level = data.get('level')
    
    # Получаем документ
    document = message.document
    
    # Подготавливаем информацию о файле
    photo_info = {
        'file_id': document.file_id,
        'file_unique_id': document.file_unique_id,
        'width': getattr(document, 'width', 0),
        'height': getattr(document, 'height', 0),
        'file_size': document.file_size,
        'timestamp': datetime.now().isoformat(),
        'caption': message.caption or "",
        'type': 'document',
        'file_name': document.file_name or 'image'
    }
    
    # Сразу сохраняем файл
    await save_photos_immediate(bot, user_id, chat_id, [photo_info], inspection, block, orientation, level)
    
    logger.info(f"User {user_id} uploaded single document for {inspection}/{block}/{level}/{orientation}")


async def save_photos_immediate(bot: AsyncTeleBot, user_id: int, chat_id: int, photos: List[dict], 
                               inspection: str, block: str, orientation: str, level: str):
    """
    Save uploaded photos immediately to the file system.
    
    Args:
        bot: Telegram bot instance
        user_id: User ID
        chat_id: Chat ID  
        photos: List of photo info dictionaries
        inspection: Inspection type
        block: Building block
        orientation: Orientation
        level: Level/floor
    """
    try:
        # Создаем путь для сохранения
        save_path = os.path.join(
            "structure_inspections",
            inspection,
            block,
            level,
            orientation,
            "unsorted"
        )
        
        # Создаем директорию если она не существует
        os.makedirs(save_path, exist_ok=True)
        
        # Отправляем сообщение о начале сохранения только если больше 1 фото
        progress_msg = None
        if len(photos) > 1:
            progress_msg = await bot.send_message(
                chat_id,
                f"💾 **Saving {len(photos)} files...**\n\n🔄 Processing...",
                parse_mode='Markdown'
            )
        
        saved_count = 0
        failed_count = 0
        saved_files = []
        
        # Сохраняем каждое фото
        for i, photo_info in enumerate(photos, 1):
            try:
                # Получаем файл
                file_path = await bot.get_file(photo_info['file_id'])
                downloaded_file = await bot.download_file(file_path.file_path)
                
                # Генерируем имя файла
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if photo_info['type'] == 'document' and 'file_name' in photo_info:
                    # Для документов сохраняем оригинальное расширение
                    original_name = photo_info['file_name']
                    extension = os.path.splitext(original_name)[1] or '.jpg'
                    filename = f"{timestamp}_{i:03d}_{photo_info['file_unique_id']}{extension}"
                else:
                    # Для фотографий используем .jpg
                    filename = f"{timestamp}_{i:03d}_{photo_info['file_unique_id']}.jpg"
                
                full_path = os.path.join(save_path, filename)
                
                # Сохраняем файл
                with open(full_path, 'wb') as f:
                    f.write(downloaded_file)
                
                saved_files.append(filename)
                saved_count += 1
                
                # Обновляем прогресс каждые 3 фото или на последнем (только если есть progress_msg)
                if progress_msg and (i % 3 == 0 or i == len(photos)):
                    await bot.edit_message_text(
                        f"💾 **Saving {len(photos)} files...**\n\n"
                        f"📊 Progress: {i}/{len(photos)}\n"
                        f"✅ Saved: {saved_count}\n"
                        f"❌ Failed: {failed_count}",
                        chat_id,
                        progress_msg.message_id,
                        parse_mode='Markdown'
                    )
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to save photo {i} for user {user_id}: {e}")
        
        # Создаем отчет
        file_word = "file" if len(photos) == 1 else "files"
        report_text = f"""✅ **Upload Complete!**

**Location:**
• Inspection: **{inspection}**
• Block: **{block}**
• Orientation: **{orientation.replace('_', ' ')}**
• Level: **{level}**

📊 **Results:**
• ✅ Successfully saved: **{saved_count}** {file_word}
• ❌ Failed to save: **{failed_count}** {file_word}

📁 **Save path:**
`{save_path}`

**What's next?**"""

        if failed_count > 0:
            report_text += f"\n\n⚠️ **Warning:** {failed_count} {file_word} failed to save. Check logs for details."
        
        # Удаляем сообщение прогресса если оно было и отправляем финальный отчет
        if progress_msg:
            await bot.delete_message(chat_id, progress_msg.message_id)
        
        # Убеждаемся, что пользователь остается в состоянии ожидания фотографий
        await bot.set_state(user_id, PhotoUploadStates.waiting_for_photos, chat_id)
        
        await bot.send_message(
            chat_id,
            report_text,
            reply_markup=post_upload_menu(inspection, block, orientation, level),
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user_id} saved {saved_count} files to {save_path}, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Error saving photos for user {user_id}: {e}")
        await bot.send_message(
            chat_id,
            f"❌ **Error saving files**\n\n{str(e)}\n\nPlease try again or contact support.",
            parse_mode='Markdown'
        )
        