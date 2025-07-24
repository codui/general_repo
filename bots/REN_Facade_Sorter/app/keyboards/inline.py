"""
Inline keyboards for the REN Facade Sorter bot with radio button logic.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional


def selection_menu(
    inspection: Optional[str] = None, 
    block: Optional[str] = None,
    orientation: Optional[str] = None
) -> InlineKeyboardMarkup:
    """
    Dynamic selection menu with radio button logic.
    
    Args:
        inspection: Selected inspection ('BW' or 'SR')
        block: Selected block ('A' or 'B')
        orientation: Selected orientation
    """
    keyboard = InlineKeyboardMarkup()
    
    # Первый ряд - выбор инспекции
    row1 = []
    bw_text = "✅ BW" if inspection == "BW" else "BW"
    sr_text = "✅ SR" if inspection == "SR" else "SR"
    
    row1.append(InlineKeyboardButton(bw_text, callback_data="inspection_BW"))
    row1.append(InlineKeyboardButton(sr_text, callback_data="inspection_SR"))
    keyboard.row(*row1)
    
    # Второй ряд - выбор блока (показывается только если выбрана инспекция)
    if inspection:
        row2 = []
        block_a_text = "✅ Block A" if block == "A" else "Block A"
        block_b_text = "✅ Block B" if block == "B" else "Block B"
        
        row2.append(InlineKeyboardButton(block_a_text, callback_data="block_A"))
        row2.append(InlineKeyboardButton(block_b_text, callback_data="block_B"))
        keyboard.row(*row2)
        
        # Направления (показываются только если выбран блок)
        if block:
            # Основные направления для всех блоков
            row3 = []
            row4 = []
            
            east_text = "✅ East" if orientation == "East" else "🧭 East"
            north_text = "✅ North" if orientation == "North" else "🧭 North"
            south_text = "✅ South" if orientation == "South" else "🧭 South"
            west_text = "✅ West" if orientation == "West" else "🧭 West"
            
            row3.append(InlineKeyboardButton(east_text, callback_data="orient_East"))
            row3.append(InlineKeyboardButton(north_text, callback_data="orient_North"))
            keyboard.row(*row3)
            
            row4.append(InlineKeyboardButton(south_text, callback_data="orient_South"))
            row4.append(InlineKeyboardButton(west_text, callback_data="orient_West"))
            keyboard.row(*row4)
            
            # Courtyard направления только для блока A
            if block == "A":
                row5 = []
                row6 = []
                
                courtyard_east_text = "✅ Courtyard East" if orientation == "Courtyard_East" else "🏛️ Courtyard East"
                courtyard_north_text = "✅ Courtyard North" if orientation == "Courtyard_North" else "🏛️ Courtyard North"
                courtyard_south_text = "✅ Courtyard South" if orientation == "Courtyard_South" else "🏛️ Courtyard South"
                courtyard_west_text = "✅ Courtyard West" if orientation == "Courtyard_West" else "🏛️ Courtyard West"
                
                row5.append(InlineKeyboardButton(courtyard_east_text, callback_data="orient_Courtyard_East"))
                row5.append(InlineKeyboardButton(courtyard_north_text, callback_data="orient_Courtyard_North"))
                keyboard.row(*row5)
                
                row6.append(InlineKeyboardButton(courtyard_south_text, callback_data="orient_Courtyard_South"))
                row6.append(InlineKeyboardButton(courtyard_west_text, callback_data="orient_Courtyard_West"))
                keyboard.row(*row6)
    
    return keyboard


def level_menu(inspection: str, block: str, orientation: str) -> InlineKeyboardMarkup:
    """
    Level selection menu (GF + L1-L11).
    
    Args:
        inspection: Selected inspection
        block: Selected block
        orientation: Selected orientation
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # Добавляем Ground Floor
    keyboard.add(InlineKeyboardButton("🏢 GF", callback_data=f"level_{inspection}_{block}_{orientation}_GF"))
    
    # Добавляем уровни L1-L11
    levels = []
    for i in range(1, 12):
        levels.append(InlineKeyboardButton(f"L{i}", callback_data=f"level_{inspection}_{block}_{orientation}_L{i}"))
    
    # Группируем по 3 кнопки в ряд
    for i in range(0, len(levels), 3):
        keyboard.row(*levels[i:i+3])
    
    # Кнопка возврата к выбору параметров
    keyboard.add(
        InlineKeyboardButton("⬅️ Back to Selection", callback_data="back_to_selection")
    )
    
    return keyboard


def confirm_selection_menu(inspection: str, block: str, orientation: str, level: str) -> InlineKeyboardMarkup:
    """
    Confirmation menu showing selected parameters.
    
    Args:
        inspection: Selected inspection
        block: Selected block
        orientation: Selected orientation  
        level: Selected level
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("✅ Confirm and Upload Photos", 
                           callback_data=f"confirm_{inspection}_{block}_{orientation}_{level}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ Back to Level Selection", 
                           callback_data=f"back_to_level_{inspection}_{block}_{orientation}")
    )
    keyboard.add(
        InlineKeyboardButton("🏠 Start Over", callback_data="start_over")
    )
    
    return keyboard


def upload_complete_menu() -> InlineKeyboardMarkup:
    """
    Menu shown after successful photo upload.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("📸 Upload More Photos", callback_data="start_over"),
        InlineKeyboardButton("✅ Finish", callback_data="finish")
    )
    
    return keyboard 