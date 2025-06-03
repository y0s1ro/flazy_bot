from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

async def get_users_menu():
    users_menu = InlineKeyboardBuilder()
    
    users_menu.add(InlineKeyboardButton(text="👤 Список пользователей", callback_data="view_users"))
    users_menu.add(InlineKeyboardButton(text="🔍 Поиск по ID", callback_data="search_user"))
    users_menu.add(InlineKeyboardButton(text="🚫 Забанить пользователя", callback_data="ban_user"))
    users_menu.add(InlineKeyboardButton(text="✅ Разбанить пользователя", callback_data="unbun_user"))
    users_menu.add(InlineKeyboardButton(text="📊 Статистика приглашенний", callback_data="invite_stat"))
    users_menu.add(InlineKeyboardButton(text="🔙 На главную", callback_data="back_to_admin_menu"))
    
    return users_menu.adjust(2).as_markup()

async def get_notifications_menu():
    notifications_menu = InlineKeyboardBuilder()
    
    notifications_menu.add(InlineKeyboardButton(text="📤 Рассылка по пользователям", callback_data="send_notifications"))
    notifications_menu.add(InlineKeyboardButton(text="🔙 На главную", callback_data="back_to_admin_menu"))
    
    return notifications_menu.adjust(1).as_markup()