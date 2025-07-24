"""
FSM States for the REN Facade Sorter bot.
"""

from telebot.asyncio_handler_backends import State, StatesGroup


class PhotoUploadStates(StatesGroup):
    """States for photo upload flow."""
    
    # Поэтапный выбор параметров (инспекция, блок, ориентация)
    selecting_parameters = State()
    
    # Выбор уровня (этажа)
    selecting_level = State()
    
    # Подтверждение выбора
    confirming_selection = State()
    
    # Ожидание загрузки фотографий
    waiting_for_photos = State()
    
    # Обработка загруженных фотографий
    processing_photos = State() 