from aiogram import Router, F, types
from datetime import datetime, timedelta
from database import SessionLocal
from models import Load, Driver
from keyboards import get_driver_selection_keyboard

pdf_router = Router()

@pdf_router.message(F.document.mime_type == "application/pdf")
async def process_manual_pdf(message: types.Message):
    db = SessionLocal()
    
    # Simulate data extraction
    test_load_id = f"REF-{message.document.file_unique_id[:6].upper()}"
    test_pickup = datetime.utcnow() + timedelta(hours=2, minutes=5)

    try:
        # 1. Create the Load first
        new_load = Load(
            external_load_id=test_load_id,
            pickup_time=test_pickup,
            status="pending",
            is_verified=False
        )
        db.add(new_load)
        db.commit()
        db.refresh(new_load)

        # 2. Fetch all drivers to assign one immediately
        drivers = db.query(Driver).all()
        
        if not drivers:
            await message.reply(f"📦 Load {test_load_id} created, but no drivers found in system. Add drivers first.")
            return

        # 3. Present driver list tied to this specific load ID
        await message.reply(
            f"📥 <b>PDF Registered:</b> <code>{test_load_id}</code>\n"
            f"<b>Pickup:</b> {test_pickup.strftime('%H:%M')} UTC\n\n"
            f"Select a driver to assign to this load:",
            parse_mode="HTML",
            reply_markup=get_driver_selection_keyboard(drivers, new_load.id)
        )

    except Exception as e:
        db.rollback()
        await message.reply(f"❌ Error: {str(e)}")
    finally:
        db.close()
    db = SessionLocal()
    
    # Generate test data (simulating what n8n would extract)
    # We set pickup to 2 hours and 5 minutes from now to test Phase B triggers
    test_load_id = f"REF-{message.document.file_unique_id[:6].upper()}"
    test_pickup = datetime.utcnow() + timedelta(hours=0, minutes=1)

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
        
        await message.reply(
            f"📥 <b>PDF Registered</b>\n\n"
            f"<b>Load ID:</b> <code>{test_load_id}</code>\n"
            f"<b>Pickup (UTC):</b> {test_pickup.strftime('%H:%M')}\n\n"
            f"Go to <b>Assign Driver</b> to link this load to a driver.",
            parse_mode="HTML"
        )
    except Exception as e:
        db.rollback()
        await message.reply(f"❌ Database Error: {str(e)}")
    finally:
        db.close()