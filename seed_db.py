"""
Script to seed the database with test data
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from database import SessionLocal, engine
from models import Base, Hostel, Bed, User, Post

from database import SessionLocal, engine
from models import Base, Hostel, Bed, User, Post

from database import SessionLocal, engine
from models import Base, Hostel, Bed, User, Post

# Drop all tables using CASCADE to handle dependencies
with engine.connect() as connection:
    connection.connection.connection.set_isolation_level(0)  # autocommit mode
    try:
        connection.execute("DROP SCHEMA public CASCADE")
        connection.execute("CREATE SCHEMA public")
    except:
        pass
    connection.connection.connection.set_isolation_level(1)

# Recreate all tables with new schema
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Clear existing data
    db.query(Bed).delete()
    db.query(Post).delete()
    db.query(Hostel).delete()
    db.query(User).delete()
    db.commit()
    
    # Create test users
    # Regular user
    user1 = User(
        telegram_id=123456789,
        name="Aidai",
        role="user",
        current_mode="user"
    )
    
    # Host user
    host_user = User(
        telegram_id=987654321,
        name="Tursunov",
        role="host",
        current_mode="user"  # Starts in user mode but can switch
    )
    
    db.add(user1)
    db.add(host_user)
    db.commit()
    db.refresh(host_user)
    
    # Create hostels
    hostels_data = [
        {
            "name": "Cozy Dreams Hostel",
            "description": "Comfortable rooms with great vibes and friendly staff",
            "address": "Kyrgyz Turasy 23, Bishkek",
            "city": "Bishkek",
            "photo_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400",
            "score": 4.8,
            "is_partner": True,
            "priority_score": 100,
            "owner_id": host_user.id,
            "is_verified": True
        },
        {
            "name": "Mountain View Inn",
            "description": "Beautiful mountain views, peaceful environment, great for travelers",
            "address": "Panfilov 56, Bishkek",
            "city": "Bishkek",
            "photo_url": "https://images.unsplash.com/photo-1611632736579-6b16e2b50449?w=400",
            "score": 4.6,
            "is_partner": False,
            "priority_score": 75,
            "owner_id": host_user.id,
            "is_verified": True
        },
        {
            "name": "Downtown Hostel",
            "description": "Central location, close to restaurants and shops",
            "address": "Chuy Avenue 101, Bishkek",
            "city": "Bishkek",
            "photo_url": "https://images.unsplash.com/photo-1570129477492-45a003537e1f?w=400",
            "score": 4.4,
            "is_partner": False,
            "priority_score": 50,
            "owner_id": None,
            "is_verified": False
        },
        {
            "name": "Silk Road Travelers",
            "description": "Historic building, perfect for cultural experience",
            "address": "Lenin Avenue 234, Bishkek",
            "city": "Bishkek",
            "photo_url": "https://images.unsplash.com/photo-1668738362474-d5e68a0e0f7f?w=400",
            "score": 4.7,
            "is_partner": True,
            "priority_score": 90,
            "owner_id": host_user.id,
            "is_verified": True
        },
        {
            "name": "Budget Beds Plus",
            "description": "Affordable prices, clean rooms, basic amenities",
            "address": "Abdrakhmanov 78, Bishkek",
            "city": "Bishkek",
            "photo_url": "https://images.unsplash.com/photo-1639821176505-b6e1b3f8e087?w=400",
            "score": 4.2,
            "is_partner": False,
            "priority_score": 40,
            "owner_id": None,
            "is_verified": False
        }
    ]
    
    for hostel_data in hostels_data:
        hostel = Hostel(**hostel_data)
        db.add(hostel)
    
    db.commit()
    db.refresh(host_user)
    
    # Create beds for each hostel
    hostels = db.query(Hostel).all()
    
    beds_data = [
        # Hostel 1 - Cozy Dreams
        {
            "hostel_id": hostels[0].id,
            "bed_type": "single",
            "price_per_night": 15.0,
            "total_count": 10,
            "available_count": 5,
            "duration_type": "night"
        },
        {
            "hostel_id": hostels[0].id,
            "bed_type": "double",
            "price_per_night": 25.0,
            "total_count": 5,
            "available_count": 2,
            "duration_type": "night"
        },
        {
            "hostel_id": hostels[0].id,
            "bed_type": "single",
            "price_per_night": 8.0,
            "total_count": 20,
            "available_count": 15,
            "duration_type": "hour"
        },
        # Hostel 2 - Mountain View
        {
            "hostel_id": hostels[1].id,
            "bed_type": "single",
            "price_per_night": 12.0,
            "total_count": 8,
            "available_count": 3,
            "duration_type": "night"
        },
        {
            "hostel_id": hostels[1].id,
            "bed_type": "single",
            "price_per_night": 6.0,
            "total_count": 15,
            "available_count": 8,
            "duration_type": "hour"
        },
        {
            "hostel_id": hostels[1].id,
            "bed_type": "double",
            "price_per_night": 100.0,
            "total_count": 2,
            "available_count": 1,
            "duration_type": "week"
        },
        # Hostel 3 - Downtown
        {
            "hostel_id": hostels[2].id,
            "bed_type": "single",
            "price_per_night": 18.0,
            "total_count": 12,
            "available_count": 7,
            "duration_type": "night"
        },
        {
            "hostel_id": hostels[2].id,
            "bed_type": "single",
            "price_per_night": 9.0,
            "total_count": 25,
            "available_count": 12,
            "duration_type": "hour"
        },
        # Hostel 4 - Silk Road
        {
            "hostel_id": hostels[3].id,
            "bed_type": "single",
            "price_per_night": 14.0,
            "total_count": 15,
            "available_count": 6,
            "duration_type": "night"
        },
        {
            "hostel_id": hostels[3].id,
            "bed_type": "double",
            "price_per_night": 250.0,
            "total_count": 3,
            "available_count": 1,
            "duration_type": "week"
        },
        {
            "hostel_id": hostels[3].id,
            "bed_type": "single",
            "price_per_night": 350.0,
            "total_count": 1,
            "available_count": 1,
            "duration_type": "month"
        },
        # Hostel 5 - Budget Beds
        {
            "hostel_id": hostels[4].id,
            "bed_type": "single",
            "price_per_night": 10.0,
            "total_count": 20,
            "available_count": 18,
            "duration_type": "night"
        },
        {
            "hostel_id": hostels[4].id,
            "bed_type": "single",
            "price_per_night": 5.0,
            "total_count": 30,
            "available_count": 28,
            "duration_type": "hour"
        }
    ]
    
    for bed_data in beds_data:
        bed = Bed(**bed_data)
        db.add(bed)
    
    db.commit()
    
    print("✅ Database seeded successfully!")
    print(f"Created {len(hostels_data)} hostels with beds")
    print(f"Created {len(beds_data)} bed entries")
    print(f"Created 2 users (1 regular user, 1 host)")
    
finally:
    db.close()
