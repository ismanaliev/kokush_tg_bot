import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler 

from config import API_TOKEN, GROUP_CHAT_ID
from database import Base, engine
from handlers.common import common_router
from handlers.admin import admin_router
from handlers.pdf_handler import pdf_router
from handlers.dispatcher import dispatch_router
from services.notify_service import NotifyService

# Logging setup
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
dp.include_router(admin_router)
dp.include_router(common_router)
dp.include_router(dispatch_router)
dp.include_router(pdf_router)

async def main():
    # 1. Initialize the Notification Service
    notifier = NotifyService(bot)

    # 2. Setup and Start the Scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        notifier.run_check_cycle, 
        "interval", 
        minutes=1, 
        args=[GROUP_CHAT_ID]
    )
    scheduler.start()
    logger.info("Scheduler started: checking for alerts every 1 minute")

    logger.info("Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)