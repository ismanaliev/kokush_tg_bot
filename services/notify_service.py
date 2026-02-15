import logging
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import joinedload

from database import SessionLocal
from models import Load, Driver, Dispatcher

class NotifyService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def run_check_cycle(self, group_id: int):
        """Main engine called by the scheduler every minute."""
        db = SessionLocal()
        try:
            now = datetime.now()
            phase_b_time = now + timedelta(hours=2)
            
            # 1. PHASE B: 2-hour Warning
            loads_to_alert = db.query(Load).options(
                joinedload(Load.driver), 
                joinedload(Load.dispatcher)
            ).filter(
                Load.pickup_time <= phase_b_time,
                Load.alert_sent_at.is_(None),
                Load.is_verified == False
            ).all()

            for load in loads_to_alert:
                if load.driver and load.dispatcher:
                    await self.send_phase_b_alert(load, load.driver, group_id)
                    await self.send_verification_request(load, load.dispatcher.telegram_id)
                    
                    load.alert_sent_at = now
                    db.commit()

            # 2. PHASE D: 15-minute Escalation
            esc_time = now - timedelta(minutes=15)
            loads_to_escalate = db.query(Load).options(joinedload(Load.driver)).filter(
                Load.alert_sent_at <= esc_time,
                Load.is_verified == False,
                Load.status != "escalated"
            ).all()

            if loads_to_escalate:
                all_dispatchers = db.query(Dispatcher).all()
                for load in loads_to_escalate:
                    await self.trigger_phase_d_escalation(load, load.driver, all_dispatchers)
                    load.status = "escalated"
                    db.commit()

        except Exception as e:
            logging.error(f"Error in notify cycle: {e}")
        finally:
            db.close()

    async def send_phase_b_alert(self, load: Load, driver: Driver, group_id: int):
        driver_mention = f"<a href='tg://user?id={driver.telegram_id}'>{driver.name}</a>"
        text = (
            f"🔔 <b>Upcoming Pickup</b>\n"
            f"ID: <code>{load.external_load_id}</code>\n"
            f"Driver: {driver_mention}\n"
            f"Time: {load.pickup_time.strftime('%H:%M')} UTC\n"
        )
        await self._send_msg(group_id, text)

    async def send_verification_request(self, load: Load, dispatcher_id: int):
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Confirm Status", callback_data=f"confirm_{load.id}")
        
        text = (
            f"📋 <b>Verification Required</b>\n"
            f"Load: <code>{load.external_load_id}</code>\n"
            f"Please confirm once the driver is on-site."
        )
        await self._send_msg(dispatcher_id, text, builder.as_markup())

    async def trigger_phase_d_escalation(self, load: Load, driver: Driver, dispatchers: list[Dispatcher]):
        text = (
            f"⚠️ <b>URGENT ESCALATION</b>\n"
            f"Load <code>{load.external_load_id}</code> NOT verified within 15m.\n"
            f"Driver: {driver.name}"
        )
        await self._send_msg(driver.telegram_id, text)
        for disp in dispatchers:
            await self._send_msg(disp.telegram_id, text)

    async def _send_msg(self, chat_id: int, text: str, reply_markup=None):
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=text, 
                parse_mode="HTML", 
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.warning(f"Failed to send msg to {chat_id}: {e}")