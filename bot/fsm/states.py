from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    search_user_state = State()
    ban_user_state = State()
    unban_user_state = State()
    send_notification_state = State()
    waiting_for_image = State()

class TopUpStates(StatesGroup):
    waiting_for_amount = State()
    invoice_id = State()

class ReviewStates(StatesGroup):
    waiting_for_review_text = State()
    waiting_for_review_rating = State()
    waiting_for_review_confirmation = State()