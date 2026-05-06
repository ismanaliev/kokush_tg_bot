from pathlib import Path
import sys
import os
import hmac
import hashlib
from urllib.parse import unquote_plus
import json

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Add project root to Python path so backend can import root-level modules
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from database import SessionLocal, engine
from models import Base, Hostel, Bed, User, Transaction, SupportLog
from config import API_TOKEN

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="KG Hostel API", version="2.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all in development
        "http://localhost:3000",
        "http://localhost:8001",
        "https://nonpalliatively-jellylike-delorse.ngrok-free.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-Telegram-Init-Data", "X-Telegram-User-Id"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for API
class HostelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    priority_score: int = 0

class BedCreate(BaseModel):
    available_count: int
    total_count: int
    price_per_night: float
    bed_type: str

class UserCreate(BaseModel):
    telegram_id: int
    name: str
    phone: Optional[str] = None
    role: str = "user"

class TransactionCreate(BaseModel):
    transaction_id: str
    amount: float
    payment_method: str
    screenshot_url: Optional[str] = None

class SupportMessage(BaseModel):
    message: str
    user_id: Optional[int] = None

# Background task scheduler
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Start the scheduler
    scheduler.start()
    # Add the daily ping task
    scheduler.add_job(
        ping_hostels,
        trigger=IntervalTrigger(hours=24),
        id="ping_hostels",
        name="Check hostel updates daily"
    )

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

# Ping logic: Hide hostels not updated in 24 hours
async def ping_hostels():
    db = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        db.query(Hostel).filter(
            Hostel.last_updated < cutoff_time,
            Hostel.is_partner == False
        ).update({"hidden": True})
        db.commit()
    finally:
        db.close()

# API Endpoints

@app.get("/api/hostels", response_model=List[dict])
async def get_hostels(db: Session = Depends(get_db)):
    """Get all visible hostels sorted by priority"""
    hostels = db.query(Hostel).filter(Hostel.hidden == False).order_by(
        Hostel.is_partner.desc(),
        Hostel.priority_score.desc(),
        Hostel.last_updated.desc()
    ).all()

    result = []
    for hostel in hostels:
        beds = db.query(Bed).filter(Bed.hostel_id == hostel.id).all()
        total_beds = sum(bed.total_count for bed in beds)
        available_beds = sum(bed.available_count for bed in beds)

        result.append({
            "id": hostel.id,
            "name": hostel.name,
            "description": hostel.description,
            "address": hostel.address,
            "is_partner": hostel.is_partner,
            "priority_score": hostel.priority_score,
            "is_verified": hostel.is_verified,
            "total_beds": total_beds,
            "available_beds": available_beds,
            "last_updated": hostel.last_updated
        })

    return result

@app.post("/api/hostels")
async def create_hostel(hostel: HostelCreate, db: Session = Depends(get_db)):
    """Create a new hostel"""
    # Set Bulut Hostel as partner
    is_partner = hostel.name.lower() == "bulut hostel"

    db_hostel = Hostel(
        name=hostel.name,
        description=hostel.description,
        address=hostel.address,
        is_partner=is_partner,
        priority_score=hostel.priority_score if is_partner else 0
    )
    db.add(db_hostel)
    db.commit()
    db.refresh(db_hostel)
    return db_hostel

@app.put("/api/hostels/{hostel_id}/beds")
async def update_beds(hostel_id: int, beds_data: List[BedCreate], db: Session = Depends(get_db)):
    """Update beds for a hostel"""
    # Delete existing beds
    db.query(Bed).filter(Bed.hostel_id == hostel_id).delete()

    # Add new beds
    for bed in beds_data:
        db_bed = Bed(
            hostel_id=hostel_id,
            available_count=bed.available_count,
            total_count=bed.total_count,
            price_per_night=bed.price_per_night,
            bed_type=bed.bed_type
        )
        db.add(db_bed)

    # Update last_updated timestamp
    db.query(Hostel).filter(Hostel.id == hostel_id).update({
        "last_updated": datetime.utcnow(),
        "hidden": False
    })

    db.commit()
    return {"message": "Beds updated successfully"}

@app.post("/api/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create or get user"""
    db_user = db.query(User).filter(User.telegram_id == user.telegram_id).first()
    if db_user:
        return db_user

    db_user = User(
        telegram_id=user.telegram_id,
        name=user.name,
        phone=user.phone,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/transactions")
async def create_transaction(transaction: TransactionCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a transaction"""
    db_transaction = Transaction(
        user_id=user_id,
        transaction_id=transaction.transaction_id,
        amount=transaction.amount,
        payment_method=transaction.payment_method,
        screenshot_url=transaction.screenshot_url
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.post("/api/support/chat")
async def chat_support(message: SupportMessage, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """AI Support chat endpoint"""
    # Simple RAG implementation - in production, use LangChain properly
    knowledge_base = load_knowledge_base()

    # Analyze sentiment (simplified)
    sentiment = analyze_sentiment(message.message)

    # Generate response based on knowledge base
    response = generate_response(message.message, knowledge_base)

    # Log the conversation
    support_log = SupportLog(
        user_id=message.user_id,
        message=message.message,
        response=response,
        sentiment=sentiment,
        human_connected=sentiment in ["angry", "help"]
    )
    db.add(support_log)
    db.commit()

    # If angry or help, trigger human connect
    if sentiment in ["angry", "help"]:
        background_tasks.add_task(notify_human_support, message.user_id, message.message)

    return {
        "response": response,
        "sentiment": sentiment,
        "human_connected": sentiment in ["angry", "help"]
    }


# TMA (Telegram Mini App) Routes
def verify_tma_init_data(init_data: str, bot_token: str) -> bool:
    """Verify Telegram Mini App init data signature"""
    try:
        # Parse init data
        data_check_string = "\n".join(
            f"{k}={v}"
            for k, v in sorted(
                {
                    k: v for k, v in [
                        item.split("=") for item in init_data.split("&")
                    ]
                    if k != "hash"
                }.items()
            )
        )
        
        # Get the hash from init data
        init_data_dict = {
            k: v for k, v in [
                item.split("=") for item in init_data.split("&")
            ]
        }
        provided_hash = init_data_dict.get("hash", "")
        
        # Calculate expected hash
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return provided_hash == expected_hash
    except Exception as e:
        print(f"Error verifying TMA data: {e}")
        return False


def parse_tma_user(init_data: str) -> Optional[dict]:
    """Extract user information from TMA init data"""
    try:
        for item in init_data.split("&"):
            if item.startswith("user="):
                user_json = unquote_plus(item.split("=", 1)[1])
                return json.loads(user_json)
        return None
    except Exception as e:
        print(f"Error parsing TMA user: {e}")
        return None


@app.get("/api/tma/user")
async def get_tma_user(
    x_telegram_init_data: Optional[str] = Header(None),
    x_telegram_user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get authenticated user from TMA init data"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram init data")
    
    # Verify the signature
    if not verify_tma_init_data(x_telegram_init_data, API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid Telegram data signature")
    
    # Parse user info
    user_info = parse_tma_user(x_telegram_init_data)
    if not user_info or "id" not in user_info:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    telegram_id = user_info["id"]
    
    # Get or create user in database
    db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not db_user:
        db_user = User(
            telegram_id=telegram_id,
            name=user_info.get("first_name", ""),
            role="user"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "telegram_id": db_user.telegram_id,
        "name": db_user.name,
        "phone": db_user.phone,
        "role": db_user.role
    }


@app.get("/api/hostels/my")
async def get_user_hostels(
    x_telegram_init_data: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get hostels owned by authenticated user"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram init data")
    
    if not verify_tma_init_data(x_telegram_init_data, API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid Telegram data signature")
    
    user_info = parse_tma_user(x_telegram_init_data)
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    telegram_id = user_info["id"]
    
    # Get user
    db_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not db_user:
        return []
    
    # Get user's hostels
    hostels = db.query(Hostel).filter(Hostel.owner_id == db_user.id).all()
    
    result = []
    for hostel in hostels:
        beds = db.query(Bed).filter(Bed.hostel_id == hostel.id).all()
        result.append({
            "id": hostel.id,
            "name": hostel.name,
            "description": hostel.description,
            "address": hostel.address,
            "beds": len(beds),
            "is_verified": hostel.is_verified,
            "is_partner": hostel.is_partner
        })
    
    return result


@app.post("/api/support")
async def send_support_message(
    message: SupportMessage,
    x_telegram_init_data: Optional[str] = Header(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Send support message with TMA authentication"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram init data")
    
    if not verify_tma_init_data(x_telegram_init_data, API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid Telegram data signature")
    
    user_info = parse_tma_user(x_telegram_init_data)
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    # Get or create user
    db_user = db.query(User).filter(User.telegram_id == user_info["id"]).first()
    if not db_user:
        db_user = User(
            telegram_id=user_info["id"],
            name=user_info.get("first_name", ""),
            role="user"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    # Process support message
    sentiment = analyze_sentiment(message.message)
    response = generate_response(message.message, load_knowledge_base())
    
    # Log support message
    support_log = SupportLog(
        user_id=db_user.id,
        message=message.message,
        response=response,
        sentiment=sentiment,
        human_connected=sentiment in ["angry", "help"]
    )
    db.add(support_log)
    db.commit()
    
    return {
        "response": response,
        "sentiment": sentiment,
        "human_connected": sentiment in ["angry", "help"]
    }


@app.get("/api/support/history")
async def get_support_history(
    x_telegram_init_data: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get support message history for authenticated user"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram init data")
    
    if not verify_tma_init_data(x_telegram_init_data, API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid Telegram data signature")
    
    user_info = parse_tma_user(x_telegram_init_data)
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    # Get user
    db_user = db.query(User).filter(User.telegram_id == user_info["id"]).first()
    if not db_user:
        return []
    
    # Get support history
    history = db.query(SupportLog).filter(
        SupportLog.user_id == db_user.id
    ).order_by(SupportLog.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": log.id,
            "message": log.message,
            "response": log.response,
            "sentiment": log.sentiment,
            "created_at": log.created_at
        }
        for log in history
    ]

@app.get("/aa")
async def root():
    return {"status": "online", "message": "KG Hostel API is running"}

# Helper functions
def load_knowledge_base():
    """Load knowledge base from file"""
    kb_path = Path(__file__).resolve().parent / "knowledge_base.txt"
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Knowledge base not found. Please contact support."

def analyze_sentiment(message: str) -> str:
    """Simple sentiment analysis"""
    angry_words = ["плохо", "ужасно", "злой", "разозлился", "проблема", "не работает"]
    help_words = ["помогите", "помощь", "не понимаю", "как", "что делать"]

    message_lower = message.lower()

    if any(word in message_lower for word in angry_words):
        return "angry"
    elif any(word in message_lower for word in help_words):
        return "help"
    else:
        return "neutral"

def generate_response(message: str, knowledge_base: str) -> str:
    """Generate response based on knowledge base"""
    # Simplified response generation - in production use LangChain
    if "bed" in message.lower() or "кровать" in message.lower():
        return "Для обновления количества кроватей используйте кнопки +1 и -1 в панели управления хостела."
    elif "payment" in message.lower() or "оплата" in message.lower():
        return "Оплата производится через MBank или O!Dengi. Загрузите скриншот транзакции для верификации."
    else:
        return "Спасибо за ваш вопрос. Наша команда поддержки поможет вам в ближайшее время."

async def notify_human_support(user_id: int, message: str):
    """Notify human support team"""
    # In production, send Telegram message or email
    print(f"Human support needed for user {user_id}: {message}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)