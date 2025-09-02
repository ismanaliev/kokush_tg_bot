from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states import Registration
from keyboards import get_categories_keyboard
from models import User
from database import get_db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if user and user.name:
        await message.answer(
            f"Добро пожаловать обратно, {user.name}! 🎉\n\nВыберите категорию:",
            reply_markup=get_categories_keyboard()
        )
        await state.clear()
    else:
        await message.answer(
            "Добро пожаловать в наш магазин! 🛍️\n\nДавайте зарегистрируемся.\n\nВведите ваше имя:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Registration.waiting_for_name)
    db.close()

@router.message(Registration.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Введите ваш номер телефона:")
    await state.set_state(Registration.waiting_for_phone)

@router.message(Registration.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("📍 Введите ваш адрес доставки:")
    await state.set_state(Registration.waiting_for_address)

@router.message(Registration.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not user:
        user = User(telegram_id=message.from_user.id)
        db.add(user)
    
    user.name = data['name']
    user.phone = data['phone']
    user.address = message.text
    user.username = message.from_user.username
    
    db.commit()
    db.close()
    
    await message.answer(
        "✅ Регистрация завершена!\n\nВыберите категорию:",
        reply_markup=get_categories_keyboard()
    )
    await state.clear()

@router.message(F.text == "🔙 Назад к покупкам")
async def back_to_shopping(message: types.Message):
    await message.answer("Выберите категорию:", reply_markup=get_categories_keyboard())