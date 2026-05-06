from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BIGINT
from database import Base
from datetime import datetime

class Hostel(Base):
    __tablename__ = "hostels"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)
    
    is_partner = Column(Boolean, default=False)
    priority_score = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    hidden = Column(Boolean, default=False)

    # Hostel details for display
    photo_url = Column(String(500))
    score = Column(Float, default=4.5)  # Rating out of 5
    city = Column(String(100), default="Bishkek")
    country = Column(String(100), default="Kyrgyzstan")
    
    # Verification images
    toilet_image_url = Column(String(500))
    kitchen_image_url = Column(String(500))
    sleeping_area_image_url = Column(String(500))
    is_verified = Column(Boolean, default=False)

    # Relationships
    beds = relationship("Bed", back_populates="hostel")
    posts = relationship("Post", back_populates="hostel")
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="hostels")

class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    hostel = relationship("Hostel", back_populates="beds")

    available_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    price_per_night = Column(Float, nullable=False)
    bed_type = Column(String(50))  # single, double, etc.
    duration_type = Column(String(20), default="night")  # hour, night, week, month


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    hostel = relationship("Hostel", back_populates="posts")

    available_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    price_per_night = Column(Float, nullable=False)
    bed_type = Column(String(50))  # single, double, etc.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, unique=True, nullable=False)
    name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(20), default="user")  # user, host, admin
    current_mode = Column(String(20), default="user")  # user or owner mode (for hosts)

    # Relationships
    hostels = relationship("Hostel", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="transactions")

    transaction_id = Column(String(100), unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="KGS")
    payment_method = Column(String(50))  # MBank, O!Dengi
    screenshot_url = Column(String(500))
    status = Column(String(20), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)

class SupportLog(Base):
    __tablename__ = "support_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", foreign_keys=[user_id])

    message = Column(Text, nullable=False)
    response = Column(Text)
    sentiment = Column(String(20))  # neutral, angry, help, etc.
    human_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

