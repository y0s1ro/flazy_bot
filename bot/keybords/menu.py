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

async def get_topup_buttons(is_from_product=False, amount=None, callback_back=None):
    topup_menu = InlineKeyboardBuilder()
    
    if not is_from_product:
        topup_menu.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile"))
    else:
        topup_menu.add(InlineKeyboardButton(text=f"{amount}₽", callback_data=f"topup_{amount}"))
        topup_menu.add(InlineKeyboardButton(text="В каталог", callback_data=callback_back))
    
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

async def get_orders_history_buttons(orders):
    orders_menu = InlineKeyboardBuilder()
    
    for order in orders:
        orders_menu.add(InlineKeyboardButton(
            text=f"№{order.order_number}",
            callback_data=f"view_order_{order.order_number}"
        ))
    orders_menu.adjust(4)
    orders_menu.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_profile"
        )
    )
    return orders_menu.as_markup()

async def get_topup_history_buttons(topup_history):
    topup_menu = InlineKeyboardBuilder()
    
    for topup in topup_history:
        topup_menu.add(InlineKeyboardButton(
            text=f"{topup.id}",
            callback_data=f"view_topup_{topup.order_number}"
        ))

    topup_menu.adjust(4)
    topup_menu.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_profile"
        )
    )
    return topup_menu.as_markup()

async def get_review_channel(button_text:str,url:str):
    review_channel = InlineKeyboardBuilder()
    
    review_channel.add(InlineKeyboardButton(
        text=button_text,
        url = url
    ))
    return review_channel.as_markup()