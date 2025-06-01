from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class AdminStates(StatesGroup):
    search_user_state = State()
    ban_user_state = State()
    unban_user_state = State()

class TopUpStates(StatesGroup):
    waiting_for_amount = State()
    invoice_id = State()

class ReviewStates(StatesGroup):
    waiting_for_review_text = State()
    waiting_for_review_rating = State()
    waiting_for_review_confirmation = State()