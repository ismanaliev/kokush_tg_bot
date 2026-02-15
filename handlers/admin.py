from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import SessionLocal
from models import Driver, Dispatcher
from handlers.states import StaffManagement
from config import ADMIN_CHAT_ID
from datetime import datetime
from models import Load
from keyboards import (
    get_admin_keyboard,
    get_staff_management_board,
    get_delete_staff_keyboard,
    get_loads_management_board,
    get_cancel_keyboard
)

admin_router = Router()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_CHAT_ID

# --- Main Entry ---

@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "👨‍💼 <b>Admin Board</b>\n\nPersistent menu activated.",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )

# --- Reply Keyboard Handlers (Text based) ---
@admin_router.message(F.text == "❌ Cancel")
async def cancel_action(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data.get("role", "drivers")
    await state.clear()

    # 1. Reset the physical keyboard immediately
    # 2. Direct the user to the specific management they were in
    if role == "loads":
        await admin_loads_entry(message) # Reuse your existing logic
    else:
        await message.answer(
            f"🚫 <b>Action Cancelled.</b>",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
        await message.answer(
            f"👥 {role.capitalize()} Management",
            reply_markup=get_staff_management_board(role)
        )

@admin_router.message(F.text == "🚛 Drivers") 
async def manage_drivers_text(message: types.Message):
    await message.answer("👥 Driver Management", reply_markup=get_staff_management_board("drivers"))

@admin_router.message(F.text == "🎧 Dispatchers")
async def manage_disps_text(message: types.Message):
    await message.answer("👥 Dispatcher Management", reply_markup=get_staff_management_board("dispatchers"))

# --- Inline Keyboard Handlers (Callback based) ---
@admin_router.callback_query(F.data.startswith("manage_"))
async def back_to_staff_management(callback: types.CallbackQuery):
    role = callback.data.split("_")[1] # Extracts 'drivers' or 'dispatchers'
    
    await callback.message.edit_text(
        f"👥 <b>{role.capitalize()} Management</b>",
        reply_markup=get_staff_management_board(role),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_router.message(F.text == "📦 Loads")
async def admin_loads_entry(message: types.Message):
    if not is_admin(message.from_user.id): return
    await message.answer(
        "📦 <b>Load Management</b>\nView current active and unverified loads.",
        reply_markup=get_loads_management_board(),
        parse_mode="HTML"
    )

# 2. Logic to display the actual loads
from sqlalchemy.orm import joinedload # Ensure this import is at the top

@admin_router.callback_query(F.data == "list_loads")
async def list_active_loads(callback: types.CallbackQuery):
    db = SessionLocal()
    try:
        # Added joinedload to prevent crashes when accessing driver data
        active_loads = db.query(Load).options(joinedload(Load.driver)).filter(Load.is_verified == False).all()
        
        builder = InlineKeyboardBuilder()
        
        if not active_loads:
            text = "📭 <b>No active loads found.</b>"
        else:
            text = "📋 <b>Active Loads:</b>\n\n"
            for l in active_loads:
                driver_name = l.driver.name if l.driver else "Unassigned"
                # Add summary text for each load
                text += (
                    f"📦 <b>{l.external_load_id}</b>\n"
                    f"👤 Driver: {driver_name}\n"
                    f"⏰ Pickup: {l.pickup_time.strftime('%H:%M')} UTC\n"
                    f"--------------------------\n"
                )
                # Keep individual buttons for detailed info if needed
                builder.button(text=f"Details: {l.external_load_id}", callback_data=f"info_{l.id}")
        
        builder.button(text="⬅️ Back", callback_data="loads_manage")
        builder.adjust(1)
        
        await callback.message.edit_text(
            text, 
            reply_markup=builder.as_markup(), 
            parse_mode="HTML"
        )
    except Exception as e:
        # Log the error so you know WHY it crashed
        print(f"Error in list_active_loads: {e}")
        await callback.answer("❌ Error loading data", show_alert=True)
    finally:
        db.close()
    await callback.answer()
        
# 3. Handler to return to the Loads sub-menu
@admin_router.callback_query(F.data == "loads_manage")
async def back_to_loads_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📦 <b>Load Management</b>", 
        reply_markup=get_loads_management_board(),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("add_"))
async def start_add_staff(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    
    role = callback.data.split("_")[1]
    await state.set_state(StaffManagement.waiting_for_id)
    await state.update_data(role=role)
    
    await callback.message.answer(
        f"➕ Adding {role[:-1]}. Please send the <b>Telegram ID</b>:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard() 
    )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("del_"))
async def show_delete_list(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id): return
    role = callback.data.split("_")[1]
    db = SessionLocal()
    staff = db.query(Driver).all() if role == "drivers" else db.query(Dispatcher).all()
    db.close()
    
    if not staff:
        return await callback.answer("List is empty.", show_alert=True)
        
    await callback.message.edit_text(
        f"🗑 <b>Delete {role[:-1]}</b>\nSelect a name to remove:",
        parse_mode="HTML",
        reply_markup=get_delete_staff_keyboard(staff, role)
    )

@admin_router.callback_query(F.data.startswith("remove_"))
async def perform_deletion(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    parts = callback.data.split("_")
    role, db_id = parts[1], parts[2]
    
    db = SessionLocal()
    model = Driver if role == "drivers" else Dispatcher
    target = db.query(model).filter(model.id == int(db_id)).first()
    
    if target:
        name = target.name
        db.delete(target)
        db.commit()
        await callback.answer(f"Deleted {name}")
    
    db.close()
    # Return to management menu
    await callback.message.edit_text(
        f"👥 <b>{role.capitalize()} Management</b>",
        reply_markup=get_staff_management_board(role)
    )

# --- FSM Message Handlers ---

@admin_router.message(StaffManagement.waiting_for_id)
async def process_staff_id(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    if not message.text.isdigit():
        return await message.answer("❌ ID must be a number. Try again:")
    
    await state.update_data(tg_id=int(message.text))
    await state.set_state(StaffManagement.waiting_for_name)
    await message.answer("Now send the <b>Full Name</b>:", parse_mode="HTML")

@admin_router.message(StaffManagement.waiting_for_name)
async def process_staff_name(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    data = await state.get_data()
    db = SessionLocal()
    
    try:
        model = Driver if data['role'] == "drivers" else Dispatcher
        new_person = model(telegram_id=data['tg_id'], name=message.text)
        db.add(new_person)
        db.commit()
        await message.answer(f"✅ Success! {message.text} added.")
    except Exception:
        db.rollback()
        await message.answer(f"❌ Error: ID likely already exists.")
    finally:
        db.close()
        await state.clear()