from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Driver, Dispatcher
from config import ADMIN_CHAT_ID
from keyboards import (
    get_admin_keyboard, 
    get_dispatcher_main_board
)

common_router = Router()

@common_router.message(Command("start"))
async def cmd_start(message: types.Message):
    db: Session = SessionLocal()
    user_id = message.from_user.id
    
    try:
        # 1. Check if Admin
        if user_id == ADMIN_CHAT_ID:
            return await message.answer(
                "👨‍💼 <b>Admin Board Active</b>\nWelcome back, Boss.",
                parse_mode="HTML",
                reply_markup=get_admin_keyboard()
            )

        # 2. Check if Dispatcher
        dispatcher = db.query(Dispatcher).filter(Dispatcher.telegram_id == user_id).first()
        if dispatcher:
            return await message.answer(
                f"🎧 <b>Dispatcher Dashboard</b>\nWelcome back, {dispatcher.name}",
                parse_mode="HTML",
                reply_markup=get_dispatcher_main_board()
            )

        # 3. Check if Driver
        driver = db.query(Driver).filter(Driver.telegram_id == user_id).first()
        if driver:
            return await message.answer(
                f"🚛 <b>Driver Portal</b>\nWelcome, {driver.name}.\nYou will receive load alerts here.",
                parse_mode="HTML"
            )

        # 4. Unknown User
        await message.answer(
            f"Your ID: <code>{user_id}</code>\nStatus: <b>Unregistered</b>.",
            parse_mode="HTML"
        )
    finally:
        db.close()

@common_router.message(Command("me"))
async def cmd_me(message: types.Message):
    db: Session = SessionLocal()
    user_id = message.from_user.id
    
    try:
        dispatcher = db.query(Dispatcher).filter(Dispatcher.telegram_id == user_id).first()
        driver = db.query(Driver).filter(Driver.telegram_id == user_id).first()
        
        if dispatcher:
            await message.answer(f"👤 Role: <b>Dispatcher</b>\nName: {dispatcher.name}", parse_mode="HTML")
        elif driver:
            await message.answer(f"👤 Role: <b>Driver</b>\nName: {driver.name}", parse_mode="HTML")
        else:
            await message.answer("Status: <b>Unregistered</b>", parse_mode="HTML")
    finally:
        db.close()

@common_router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📖 <b>Workflow Guide</b>\n\n"
        "1. <b>Phase A:</b> Dispatcher uploads Load PDF.\n"
        "2. <b>Phase B:</b> 2h before pickup, Driver is notified.\n"
        "3. <b>Phase C:</b> Dispatcher confirms status.\n"
        "4. <b>Phase D:</b> 15m silence triggers escalation."
    )
    await message.answer(help_text, parse_mode="HTML")