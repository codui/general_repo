"""
Text messages and constants for the REN Facade Sorter bot.
"""

# Стартовое сообщение для начала работы с ботом
WELCOME_MESSAGE = """**Please provide the details of the apartment for which you would like to upload photos:**"""

# Сообщение помощи
HELP_MESSAGE = """🆘 *REN Facade Sorter Bot Help*

*Available commands:*
• `/start` - start working with the bot
• `/help` - show this help
• `/cancel` - cancel current operation

*Photo upload process:*
1. *Choose inspection* - BW or SR
2. *Select block* - A or B
3. *Specify orientation* - cardinal direction or courtyard
4. *Choose level* - GF or floors from L1 to L11
5. *Upload photos* - send one or multiple photos

*Save structure:*
Photos are saved to the folder:
`structure_inspections/{Inspection}/{Block}/{Level}/{Orientation}/unsorted/`

*Path examples:*
• BW, Block A, East, L5 → `structure_inspections/BW/A/L5/East/unsorted/`
• SR, Block A, Courtyard North, GF → `structure_inspections/SR/A/GF/Courtyard_North/unsorted/`
• SR, Block B, East, GF → `structure_inspections/SR/B/GF/East/unsorted/`

❓ If you encounter problems, use `/cancel` and start over with `/start`"""

# Сообщение отмены операции
CANCEL_MESSAGE = """❌ **Operation cancelled.**

Use /start to begin again."""

# Предупреждение о том, что схема не найдена
SCHEME_NOT_FOUND_WARNING = "\n\n⚠️ *Building scheme image not found*"

# Предупреждение о том, что схема блока не найдена
BLOCK_SCHEME_NOT_FOUND_WARNING = "\n\n⚠️ *Block {} scheme image not found*" 