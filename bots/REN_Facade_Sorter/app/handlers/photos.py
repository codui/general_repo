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
from app.keyboards.inline import photo_upload_menu, post_upload_menu
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


async def process_media_group_delayed(bot: AsyncTeleBot, group_key: str, user_id: int, chat_id: int):
    """
    Process media group after a delay to ensure all photos are received.
    """
    try:
        # Ждем 1 секунду чтобы получить все фото из группы
        await asyncio.sleep(1.0)
        
        if group_key not in media_groups:
            return
        
        messages = media_groups[group_key]
        photo_count = len(messages)
        
        # Обрабатываем все фотографии из медиагруппы
        async with bot.retrieve_data(user_id, chat_id) as data:
            if 'photos' not in data:
                data['photos'] = []
            
            # Добавляем все фото из медиагруппы
            for msg in messages:
                photo = msg.photo[-1]  # Наивысшее качество
                photo_info = {
                    'file_id': photo.file_id,
                    'file_unique_id': photo.file_unique_id,
                    'width': photo.width,
                    'height': photo.height,
                    'file_size': photo.file_size,
                    'timestamp': datetime.now().isoformat(),
                    'caption': msg.caption or ""
                }
                data['photos'].append(photo_info)
            
            total_photos = len(data['photos'])
            inspection = data.get('inspection')
            block = data.get('block')
            orientation = data.get('orientation')
            level = data.get('level')
        
        # Отправляем одно уведомление для всей медиагруппы
        notification_text = f"""📸 **Media Group Received** (+{photo_count} photos)

**Current location:**
• Inspection: **{inspection}**
• Block: **{block}**
• Orientation: **{orientation.replace('_', ' ')}**
• Level: **{level}**

📊 **Photos collected:** {total_photos}

Continue sending photos or save the current batch."""

        await bot.send_message(
            chat_id,
            notification_text,
            reply_markup=photo_upload_menu(total_photos),
            parse_mode='Markdown'
        )
        
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
    Handle single photo upload.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Обрабатываем одиночное фото
    async with bot.retrieve_data(user_id, chat_id) as data:
        if 'photos' not in data:
            data['photos'] = []
        
        # Получаем фото в наивысшем качестве
        photo = message.photo[-1]
        
        # Сохраняем информацию о фото
        photo_info = {
            'file_id': photo.file_id,
            'file_unique_id': photo.file_unique_id,
            'width': photo.width,
            'height': photo.height,
            'file_size': photo.file_size,
            'timestamp': datetime.now().isoformat(),
            'caption': message.caption or ""
        }
        
        data['photos'].append(photo_info)
        photo_count = len(data['photos'])
        
        inspection = data.get('inspection')
        block = data.get('block')
        orientation = data.get('orientation')
        level = data.get('level')
    
    # Отправляем уведомление о получении фото
    notification_text = f"""📸 **Photo Received** ({photo_count})

**Current location:**
• Inspection: **{inspection}**
• Block: **{block}**
• Orientation: **{orientation.replace('_', ' ')}**
• Level: **{level}**

📊 **Photos collected:** {photo_count}

Continue sending photos or save the current batch."""

    await bot.send_message(
        chat_id,
        notification_text,
        reply_markup=photo_upload_menu(photo_count),
        parse_mode='Markdown'
    )
    
    logger.info(f"User {user_id} uploaded single photo {photo_count} for {inspection}/{block}/{level}/{orientation}")

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
                "• Use /cancel to cancel operation",
                parse_mode='Markdown'
            )


async def save_photos(bot: AsyncTeleBot, user_id: int, chat_id: int, data: dict):
    """
    Save uploaded photos to the file system.
    
    Args:
        bot: Telegram bot instance
        user_id: User ID
        chat_id: Chat ID  
        data: User data containing photos and location info
    """
    try:
        inspection = data['inspection']
        block = data['block']
        orientation = data['orientation']
        level = data['level']
        photos = data['photos']
        
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
        
        # Отправляем сообщение о начале сохранения
        progress_msg = await bot.send_message(
            chat_id,
            f"💾 **Saving {len(photos)} photos...**\n\n🔄 Processing...",
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
                filename = f"{timestamp}_{i:03d}_{photo_info['file_unique_id']}.jpg"
                full_path = os.path.join(save_path, filename)
                
                # Сохраняем файл
                with open(full_path, 'wb') as f:
                    f.write(downloaded_file)
                
                saved_files.append(filename)
                saved_count += 1
                
                # Обновляем прогресс каждые 3 фото или на последнем
                if i % 3 == 0 or i == len(photos):
                    await bot.edit_message_text(
                        f"💾 **Saving {len(photos)} photos...**\n\n"
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
        
        # Очищаем фотографии из данных пользователя
        data['photos'] = []
        
        # Переходим обратно к состоянию ожидания фотографий для возможности добавить еще
        await bot.set_state(user_id, PhotoUploadStates.waiting_for_photos, chat_id)
        
        # Создаем отчет
        report_text = f"""✅ **Upload Complete!**

**Location:**
• Inspection: **{inspection}**
• Block: **{block}**
• Orientation: **{orientation.replace('_', ' ')}**
• Level: **{level}**

📊 **Results:**
• ✅ Successfully saved: **{saved_count}** photos
• ❌ Failed to save: **{failed_count}** photos

📁 **Save path:**
`{save_path}`

**What's next?**"""

        if failed_count > 0:
            report_text += f"\n\n⚠️ **Warning:** {failed_count} photos failed to save. Check logs for details."
        
        # Удаляем сообщение прогресса и отправляем финальный отчет
        await bot.delete_message(chat_id, progress_msg.message_id)
        
        await bot.send_message(
            chat_id,
            report_text,
            reply_markup=post_upload_menu(inspection, block, orientation, level),
            parse_mode='Markdown'
        )
        
        logger.info(f"User {user_id} saved {saved_count} photos to {save_path}, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Error saving photos for user {user_id}: {e}")
        await bot.send_message(
            chat_id,
            f"❌ **Error saving photos**\n\n{str(e)}\n\nPlease try again or contact support.",
            parse_mode='Markdown'
        ) 