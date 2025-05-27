from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from bot.config import BUTTONS_DATA

async def get_menu():
    
    menu = ReplyKeyboardBuilder()
    
    for row in BUTTONS_DATA:
        menu.add(KeyboardButton(text=row))
    
    return menu.adjust(3).as_markup(resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

async def get_profile_buttons():
    profile_menu = InlineKeyboardBuilder()
    
    profile_menu.add(InlineKeyboardButton(text="История заказов", callback_data="orders_history"))
    profile_menu.add(InlineKeyboardButton(text="История пополнений", callback_data="topup_history"))
    profile_menu.add(InlineKeyboardButton(text="Пополнить баланс", callback_data="topup_balance"))
    
    return profile_menu.adjust(2).as_markup()

async def get_topup_buttons(is_from_product=False, product_id = None,  amount=None):
    topup_menu = InlineKeyboardBuilder()
    
    if not is_from_product:
        topup_menu.add(InlineKeyboardButton(text="Назад", callback_data="back_to_profile"))
    else:
        topup_menu.add(InlineKeyboardButton(text=f"{amount}₽"))
        topup_menu.add(InlineKeyboardButton(text="Назад", callback_data=product_id))
    
    return topup_menu.adjust(2).as_markup()

async def get_back_button(callback_data: str):
    back_menu = InlineKeyboardBuilder()
    
    back_menu.add(InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data))
    
    return back_menu.as_markup()

async def get_payments_button(acquiring_link: str, crystal_link: str):
    payments_menu = InlineKeyboardBuilder()
    
    payments_menu.add(InlineKeyboardButton(text="СПБ", url=acquiring_link))
    payments_menu.add(InlineKeyboardButton(text="Lolz/Crypto", url=crystal_link))
    payments_menu.add(InlineKeyboardButton(text="Проверить оплату", callback_data="check_payment_status"))
    
    return payments_menu.adjust(1).as_markup()

