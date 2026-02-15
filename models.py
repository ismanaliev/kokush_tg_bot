from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BIGINT
from datetime import datetime
from database import Base

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, unique=True, nullable=False)
    name = Column(String(100))
    phone = Column(String(20))
    
    loads = relationship("Load", back_populates="driver")

class Dispatcher(Base):
    __tablename__ = "dispatchers"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, unique=True, nullable=False)
    name = Column(String(100))
    
    loads = relationship("Load", back_populates="dispatcher")

class Load(Base):
    __tablename__ = "loads"
    
    id = Column(Integer, primary_key=True)
    external_load_id = Column(String(100), unique=True) # ID from PDF
    
    # Relationships
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    dispatcher_id = Column(Integer, ForeignKey("dispatchers.id"))
    
    # Workflow Timestamps
    pickup_time = Column(DateTime, nullable=False)
    alert_sent_at = Column(DateTime) # Phase B trigger time
    
    # Status tracking
    status = Column(String(50), default="pending") # pending, active, verified, escalated
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    alert_sent_at = Column(DateTime, nullable=True) # Tracks Phase B/C timing
    is_verified = Column(Boolean, default=False)   # Prevents Phase D
    driver = relationship("Driver", back_populates="loads")
    dispatcher = relationship("Dispatcher", back_populates="loads")