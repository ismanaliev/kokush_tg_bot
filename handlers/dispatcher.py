from datetime import datetime, timedelta
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
from aiogram import Router, F, types
from database import SessionLocal
from services.load_service import LoadService
from database import SessionLocal
from models import Load, Driver
from handlers.states import LoadCreation
from keyboards import get_driver_selection_keyboard, get_dispatcher_main_board
from services.load_service import LoadService

dispatch_router = Router()

# --- Navigation ---
@dispatch_router.callback_query(F.data.startswith("confirm_"))
async def handle_confirm_pickup(callback: types.CallbackQuery):
    load_id = int(callback.data.split("_")[1])
    
    db = SessionLocal()
    load_service = LoadService(db)
    
    try:
        load = load_service.set_verified(load_id)
        if load:
            await callback.message.edit_text(
                f"✅ <b>Load {load.external_load_id} Verified</b>\n"
                f"Status updated in database."
            )
            await callback.answer("Success")
        else:
            await callback.answer("Load not found", show_alert=True)
    finally:
        db.close()

@dispatch_router.message(F.text == "➕ Add New Load (PDF)")
async def start_add_load(message: types.Message, state: FSMContext):
    """Triggers the FSM state to wait for a PDF file."""
    await state.set_state(LoadCreation.waiting_for_pdf)
    await message.answer(
        "📎 Please upload the <b>Load PDF</b> now.",
        parse_mode="HTML"
    )

@dispatch_router.message(F.text == "📦 Active Loads")
async def show_active_loads(message: types.Message):
    db = SessionLocal()
    load_service = LoadService(db)
    
    try:
        active_loads = load_service.get_in_process_loads()

        if not active_loads:
            await message.answer("⏸️ No loads currently in process.")
            return

        text = "<b>Current Loads In Process:</b>\n\n"
        for load in active_loads:
            # Now load.driver is already loaded in memory
            driver_name = load.driver.name if load.driver else "Unknown"
            text += (
                f"🆔 <code>{load.external_load_id}</code>\n"
                f"👤 <b>Driver:</b> {driver_name}\n"
                f"🕒 <b>Pickup:</b> {load.pickup_time.strftime('%H:%M')} UTC\n"
                f"📍 <b>Status:</b> {load.status}\n"
                f"--------------------------\n"
            )

        await message.answer(text, parse_mode="HTML")
    
    except Exception as e:
        await message.answer(f"❌ Error displaying loads: {str(e)}")
    finally:
        db.close() # Always close in 'finally' after all logic is done
        
@dispatch_router.message(LoadCreation.waiting_for_pdf, F.document.mime_type == "application/pdf")
async def handle_manual_pdf(message: types.Message, state: FSMContext):
    db = SessionLocal()
    test_load_id = f"REF-{message.document.file_unique_id[:6].upper()}"
    test_pickup = datetime.utcnow() + timedelta(hours=2, minutes=5)

    try:
        new_load = Load(
            external_load_id=test_load_id,
            pickup_time=test_pickup,
            status="pending",
            is_verified=False
        )
        db.add(new_load)
        db.commit()
        db.refresh(new_load)
        
        drivers = db.query(Driver).all()
        await state.clear()

        if not drivers:
            await message.reply(f"✅ Load {test_load_id} created, but no drivers in DB.")
            return

        await cmd_show_driver_selection(message, new_load.id, drivers, test_load_id, test_pickup)

    except Exception as e:
        db.rollback()
        await message.reply(f"❌ Failed to create load: {str(e)}")
    finally:
        db.close()

async def cmd_show_driver_selection(message: types.Message, load_id: int, drivers: list, ext_id: str, pickup: datetime):
    """Helper to display the driver list for a specific load."""
    await message.reply(
        f"✅ <b>PDF Parsed:</b> <code>{ext_id}</code>\n"
        f"<b>Pickup:</b> {pickup.strftime('%H:%M')} UTC\n\n"
        "Select a driver to assign to this load:",
        parse_mode="HTML",
        reply_markup=get_driver_selection_keyboard(drivers, load_id)
    )

# --- Callbacks (Phases A & C) ---

@dispatch_router.callback_query(F.data.startswith("assign_"))
async def handle_driver_assignment(callback: types.CallbackQuery):
    # Data format: assign_{load_id}_{driver_id}
    parts = callback.data.split("_")
    load_id, driver_id = int(parts[1]), int(parts[2])
    
    db = SessionLocal()
    load_service = LoadService(db)
    
    try:
        # Pass the Telegram ID here; the service will handle the translation
        load = load_service.assign_driver(
            load_id=load_id, 
            driver_id=driver_id, 
            dispatcher_tg_id=callback.from_user.id
        )
        
        await callback.message.edit_text(
            f"✅ Load <b>{load.external_load_id}</b> assigned successfully.",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"❌ Assignment failed: {str(e)}", show_alert=True)
    finally:
        db.close()
    await callback.answer()

@dispatch_router.callback_query(F.data.startswith("confirm_"))
async def handle_verification(callback: types.CallbackQuery):
    _, load_id = callback.data.split("_")
    db = SessionLocal()
    load_service = LoadService(db)
    
    load_service.set_verified(int(load_id))
    
    await callback.message.edit_text(
        f"🏁 Load {load_id} verified. Workflow complete."
    )
    db.close()
    await callback.answer("Verification Successful")