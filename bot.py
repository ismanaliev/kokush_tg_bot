import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from database import Base, engine
from handlers import user_router, admin_router, cart_router, payment_router

# Set up more detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Starting bot...")
logger.info(f"Using token: {API_TOKEN[:5]}...{API_TOKEN[-5:]}")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created")

# Include routers
dp.include_router(user_router)
dp.include_router(cart_router)
dp.include_router(payment_router)
dp.include_router(admin_router)
logger.info("Routers included")

async def main():
    logger.info("Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        logger.info("Bot is starting")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)