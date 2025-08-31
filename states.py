from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()

class ViewProduct(StatesGroup):
    viewing = State()

class AdminProductAdd(StatesGroup):
    waiting_for_category = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_photo = State()

class CheckoutState(StatesGroup):
    waiting_for_payment = State()