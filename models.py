from sqlalchemy import Column, Integer, BigInteger, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy import BigInteger;
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, unique=True, nullable=False)
    name = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    emoji = Column(String(10))
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    photo_file_id = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    active = Column(Boolean, default=True)
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(BIGINT, nullable=False)  # Changed to BigInteger
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    prepayment = Column(Float)
    receipt_photo_id = Column(String(500))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_name = Column(String(200))
    quantity = Column(Integer)
    price = Column(Float)
    order = relationship("Order", back_populates="items")