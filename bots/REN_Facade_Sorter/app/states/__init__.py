"""
FSM States for the REN Facade Sorter bot.
"""

from telebot.asyncio_handler_backends import State, StatesGroup


class PhotoUploadStates(StatesGroup):
    """States for photo upload flow."""
    
    # Step-by-step selection of parameters (inspection, block, orientation)
    selecting_parameters = State()
    
    # Choose level (floor)
    selecting_level = State()
    
    # Confirmation of selection
    confirming_selection = State()
    
    # Waiting for photos
    waiting_for_photos = State()
    
    # Processing uploaded photos
    processing_photos = State() 