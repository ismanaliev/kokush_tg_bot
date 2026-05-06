"""
Telegram Mini App (TMA) handlers
Manages TMA launch button and deep linking
"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
import logging

logger = logging.getLogger(__name__)
tma_router = Router()

# Replace with your actual TMA URL - should be HTTPS
TMA_URL = "https://civilization-code-reaching-feeling.trycloudflare.com"  # Update this to your frontend URL


@tma_router.message(Command("start"))
async def cmd_start(message: Message):
    """Start command - shows TMA launch button"""
    web_app = WebAppInfo(url=TMA_URL)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏨 Open KG Hostel App",
                    web_app=web_app
                )
            ]
        ]
    )
    
    await message.answer(
        "Welcome to KG Hostel Bot! 🏨\n\n"
        "Click the button below to open the hostel management app.",
        reply_markup=keyboard
    )
    logger.info(f"User {message.from_user.id} started bot")


@tma_router.message(Command("app"))
async def cmd_app(message: Message):
    """Direct command to open TMA"""
    web_app = WebAppInfo(url=TMA_URL)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Open Mini App",
                    web_app=web_app
                )
            ]
        ]
    )
    
    await message.answer(
        "Tap the button to access the app.",
        reply_markup=keyboard
    )
