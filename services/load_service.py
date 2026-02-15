from sqlalchemy.orm import Session, joinedload
from models import Load, Driver, Dispatcher
from datetime import datetime

class LoadService:
    def __init__(self, db: Session):
        self.db = db

    def create_load(self, external_id: str, pickup_time: datetime) -> Load:
        """
        Unified method to create a load record. 
        Works for both manual PDF parsing and n8n.
        """
        new_load = Load(
            external_load_id=external_id,
            pickup_time=pickup_time,
            status="pending",
            is_verified=False
        )
        self.db.add(new_load)
        self.db.commit()
        self.db.refresh(new_load)
        return new_load

    def assign_driver(self, load_id: int, driver_id: int, dispatcher_tg_id: int):
        """
        Phase A: Links a driver and dispatcher to a load.
        Translates dispatcher_tg_id (BigInt) to dispatcher.id (Integer).
        """
        # 1. Lookup dispatcher by Telegram ID to get their DB Primary Key
        dispatcher = self.db.query(Dispatcher).filter(
            Dispatcher.telegram_id == dispatcher_tg_id
        ).first()

        if not dispatcher:
            return None

        # 2. Lookup the load
        load = self.db.query(Load).filter(Load.id == load_id).first()
        if not load:
            return None
            
        # 3. Update using internal DB IDs
        load.driver_id = driver_id
        load.dispatcher_id = dispatcher.id
        
        self.db.commit()
        self.db.refresh(load)
        return load

    def get_available_drivers(self):
        """Returns list of drivers for selection menus."""
        return self.db.query(Driver).all()
    
    def set_verified(self, load_id: int):
        """Phase C: Marks load as verified/complete."""
        load = self.db.query(Load).filter(Load.id == load_id).first()
        if load:
            load.is_verified = True
            load.status = "verified"
            self.db.commit()
            self.db.refresh(load)
        return load
    
    def get_in_process_loads(self):
        """
        Uses joinedload to prevent DetachedInstanceError.
        """
        return self.db.query(Load).options(
            joinedload(Load.driver) # This fetches driver info immediately
        ).filter(
            Load.driver_id.isnot(None),
            Load.is_verified == False
        ).all()