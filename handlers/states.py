from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import State, StatesGroup

class StaffManagement(StatesGroup):
    """FSM for adding new Drivers or Dispatchers."""
    waiting_for_id = State()
    waiting_for_name = State()

class LoadCreation(StatesGroup):
    """FSM for the PDF upload and assignment workflow."""
    waiting_for_pdf = State()
class StaffManagement(StatesGroup):
    # For Adding
    waiting_for_id = State()
    waiting_for_name = State()
    
    # For Deleting (if choosing by ID input)
    waiting_for_delete_id = State()

class LoadContext(StatesGroup):
    waiting_for_driver_selection = State()