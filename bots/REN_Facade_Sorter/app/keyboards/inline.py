"""
Inline keyboards for the REN Facade Sorter bot with radio button logic.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional


def selection_menu(
    inspection: Optional[str] = None, 
    block: Optional[str] = None,
    orientation: Optional[str] = None,
    level: Optional[str] = None
) -> InlineKeyboardMarkup:
    """
    Dynamic selection menu with radio button logic.
    
    Args:
        inspection: Selected inspection ('BW' or 'SR')
        block: Selected block ('A' or 'B')
        orientation: Selected orientation
        level: Selected level
    """
    keyboard = InlineKeyboardMarkup()
    
    # First row - inspection selection
    row1 = []
    bw_text = "✅ BW" if inspection == "BW" else "BW"
    sr_text = "✅ SR" if inspection == "SR" else "SR"
    
    row1.append(InlineKeyboardButton(bw_text, callback_data="inspection_BW"))
    row1.append(InlineKeyboardButton(sr_text, callback_data="inspection_SR"))
    keyboard.row(*row1)
    
    # Second row - block selection (shown only if inspection is selected)
    if inspection:
        row2 = []
        block_a_text = "✅ Block A" if block == "A" else "Block A"
        block_b_text = "✅ Block B" if block == "B" else "Block B"
        
        row2.append(InlineKeyboardButton(block_a_text, callback_data="block_A"))
        row2.append(InlineKeyboardButton(block_b_text, callback_data="block_B"))
        keyboard.row(*row2)
        
        # Directions (shown only if block is selected)
        if block:
            # Main directions for all blocks
            directions_row = []
            east_text = "✅ East" if orientation == "East" else "🧭 East"
            north_text = "✅ North" if orientation == "North" else "🧭 North"
            south_text = "✅ South" if orientation == "South" else "🧭 South"
            west_text = "✅ West" if orientation == "West" else "🧭 West"
            
            directions_row.append(InlineKeyboardButton(east_text, callback_data="orient_East"))
            directions_row.append(InlineKeyboardButton(north_text, callback_data="orient_North"))
            directions_row.append(InlineKeyboardButton(south_text, callback_data="orient_South"))
            directions_row.append(InlineKeyboardButton(west_text, callback_data="orient_West"))
            keyboard.row(*directions_row)

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
                
            # Level selection (shown only if orientation is selected)
            if orientation:
                # First row - GF to L5 (6 buttons)
                level_row1 = []
                gf_text = "✅ GF" if level == "GF" else "🏢 GF"
                level_row1.append(InlineKeyboardButton(gf_text, callback_data=f"level_{inspection}_{block}_{orientation}_GF"))
                for i in range(1, 6):
                    level_text = f"✅ L{i}" if level == f"L{i}" else f"L{i}"
                    level_row1.append(InlineKeyboardButton(level_text, callback_data=f"level_{inspection}_{block}_{orientation}_L{i}"))
                keyboard.row(*level_row1)
                
                # Second row - L6 to L11 (6 buttons)
                level_row2 = []
                for i in range(6, 12):
                    level_text = f"✅ L{i}" if level == f"L{i}" else f"L{i}"
                    level_row2.append(InlineKeyboardButton(level_text, callback_data=f"level_{inspection}_{block}_{orientation}_L{i}"))
                keyboard.row(*level_row2)
                
                # Show confirm button when all parameters are selected
                if level:
                    keyboard.add(
                        InlineKeyboardButton("📎 Upload Pictures", 
                                           callback_data=f"confirm_{inspection}_{block}_{orientation}_{level}")
                    )
    
    return keyboard


def post_upload_menu(inspection: str, block: str, orientation: str, level: str) -> InlineKeyboardMarkup:
    """
    Menu shown after successful photo upload with options to continue.
    
    Args:
        inspection: Current inspection
        block: Current block
        orientation: Current orientation
        level: Current level
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("🏠 Another Location", callback_data="next_location")
    )
    
    return keyboard