from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models import Driver 

# --- Admin Keyboards ---

def get_admin_keyboard() -> ReplyKeyboardMarkup: 
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚛 Drivers"), KeyboardButton(text="🎧 Dispatchers")],
            [KeyboardButton(text="📊 Statistics"), KeyboardButton(text="📦 Loads")]
        ],
        resize_keyboard=True
    )

def get_staff_management_board(role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Add", callback_data=f"add_{role}")
    builder.button(text="🗑️ Delete", callback_data=f"del_{role}")
    builder.button(text="📋 List All", callback_data=f"list_{role}")
    builder.button(text="⬅️ Back", callback_data="menu_main")
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def get_delete_staff_keyboard(staff_list: list, role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for person in staff_list:
        builder.button(
            text=f"❌ {person.name}", 
            callback_data=f"remove_{role}_{person.id}"
        )
    builder.button(text="⬅️ Back", callback_data="menu_main")
    builder.adjust(1)
    return builder.as_markup()

# --- Dispatcher Keyboards ---

def get_dispatcher_main_board() -> ReplyKeyboardMarkup: 
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Add New Load (PDF)")],
            [KeyboardButton(text="📦 Active Loads")]
        ],
        resize_keyboard=True
    )

def get_driver_selection_keyboard(drivers: list[Driver], load_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for driver in drivers:
        builder.button(
            text=f"🚛 {driver.name}", 
            callback_data=f"assign_{load_id}_{driver.id}"
        )
    builder.adjust(1)
    return builder.as_markup()

def get_verification_keyboard(load_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Confirm Status", callback_data=f"confirm_{load_id}")
    return builder.as_markup()