from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from models import Category, CartItem
from database import get_db

def get_categories_keyboard():
    db = next(get_db())
    categories = db.query(Category).all()
    
    keyboard = [[KeyboardButton(text=f"{cat.emoji} {cat.name}")] for cat in categories]
    keyboard.append([KeyboardButton(text="🛒 Посмотреть корзину")])
    db.close()
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_product_keyboard(product_id: int, telegram_id: int, current_index: int, total_products: int):
    db = next(get_db())
    cart_item = db.query(CartItem).filter(
        CartItem.user_telegram_id == telegram_id,
        CartItem.product_id == product_id
    ).first()
    
    quantity = cart_item.quantity if cart_item else 0
    db.close()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"prev_{current_index}"),
            InlineKeyboardButton(text="➖", callback_data=f"remove_{product_id}"),
            InlineKeyboardButton(text=f"{quantity}", callback_data="quantity"),
            InlineKeyboardButton(text="➕", callback_data=f"add_{product_id}"),
            InlineKeyboardButton(text="➡️", callback_data=f"next_{current_index}")
        ],
        [InlineKeyboardButton(text="🔙 К категориям", callback_data="back_categories")]
    ])
    
    return keyboard

def get_cart_keyboard():
    keyboard = [
        [KeyboardButton(text="✅ Завершить заказ")],
        [KeyboardButton(text="🗑 Очистить корзину")],
        [KeyboardButton(text="🔙 Назад к покупкам")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton(text="📁 Категории"), KeyboardButton(text="📦 Товары")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📋 Заказы")],
        [KeyboardButton(text="🔙 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)