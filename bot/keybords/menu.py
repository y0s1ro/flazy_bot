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

async def get_admin_menu():
    admin_menu = InlineKeyboardBuilder()
    
    admin_menu.add(InlineKeyboardButton(text="📦 Управление товарами", callback_data="manage_products"))
    admin_menu.add(InlineKeyboardButton(text="📊 Заказы", callback_data="manage_orders"))
    admin_menu.add(InlineKeyboardButton(text="👥 Пользователи", callback_data="manage_users"))
    admin_menu.add(InlineKeyboardButton(text="💰 Финансы", callback_data="manage_finances"))
    admin_menu.add(InlineKeyboardButton(text="⚙️ Настройки", callback_data="manage_settings"))
    admin_menu.add(InlineKeyboardButton(text="📣 Уведомления", callback_data="manage_notifications"))
    
    return admin_menu.adjust(2).as_markup()

async def get_manage_order_menu():
    manage_order_menu = InlineKeyboardBuilder()
    
    manage_order_menu.add(InlineKeyboardButton(text="📦 Обработка заказов", callback_data="pending_orders"))
    manage_order_menu.add(InlineKeyboardButton(text="✅ Выполненные заказы", callback_data="completed_orders"))
    manage_order_menu.add(InlineKeyboardButton(text="❌ Отменённые заказы", callback_data="cancelled_orders"))
    manage_order_menu.add(InlineKeyboardButton(text="🔙 На главную", callback_data="back_to_admin_menu"))
    
    return manage_order_menu.adjust(2).as_markup()

async def get_change_order_status(callback_data: str):
    change_order_status = InlineKeyboardBuilder()
    
    change_order_status.add(InlineKeyboardButton(text="✅ Выполнен", callback_data=f"ap_{callback_data}"))
    change_order_status.add(InlineKeyboardButton(text="❌ Отменить", callback_data=f"re_{callback_data}"))
    change_order_status.add(InlineKeyboardButton(text="🔙 На главную", callback_data="back_to_admin_menu"))
    
    return change_order_status.adjust(2).as_markup()

async def get_manage_finance_menu():
    manage_finance_menu = InlineKeyboardBuilder()
    
    manage_finance_menu.add(InlineKeyboardButton(text="💵 Просмотр баланса", callback_data="check_balance"))
    manage_finance_menu.add(InlineKeyboardButton(text="📈 Статистика продаж", callback_data="sales_stat"))
    manage_finance_menu.add(InlineKeyboardButton(text="🧾 История пополнений", callback_data="payment_history"))
    manage_finance_menu.add(InlineKeyboardButton(text="🔙 На главную", callback_data="back_to_admin_menu"))
    
    return manage_finance_menu.adjust(2).as_markup()

