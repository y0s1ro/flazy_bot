from aiogram import Router, F
from aiogram.filters import Command
from bot.config import START_MESSAGE, BUTTONS_DATA, CATEGORIES_DATA, TOKENS_DATA
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.keybords import get_admin_menu, get_manage_order_menu, get_change_order_status, get_back_button, get_manage_finance_menu
from bot.database import get_orders_by_status, get_session, get_user, get_order, update_balance, get_topups
from bot.payments import crystalpay, acquiring
from datetime import datetime

router = Router()

async def send_to_admins(message: Message, text: str):
    for admin_id in TOKENS_DATA["admin_chat_id"]:
        await message.bot.send_message(chat_id=admin_id, text=text)

@router.callback_query(F.data == "back_to_admin_menu")
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if isinstance(message, CallbackQuery):
        await message.message.answer(
            text="Вы вернулись в главное меню администратора.",
            reply_markup=await get_admin_menu()
        )
        await message.message.delete()
        return
    if str(message.from_user.id) in TOKENS_DATA["admin_chat_id"]:
        await message.answer(
            text="Вы администратор. Используйте команды для управления ботом.",
            reply_markup=await get_admin_menu()
        )
    else:
        await message.answer("У вас нет прав администратора.")

@router.callback_query(F.data == "manage_products")
async def manage_products(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять товарами. Используйте соответствующие команды.",
        reply_markup=await get_admin_menu()
    )

@router.callback_query(F.data == "manage_orders")
async def manage_orders(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять заказами. Используйте соответствующие команды.",
        reply_markup=await get_manage_order_menu()
    )

@router.callback_query(F.data == "manage_users")
async def manage_users(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять пользователями. Используйте соответствующие команды.",
        reply_markup=await get_admin_menu()
    )

@router.callback_query(F.data == "manage_finances")
async def manage_finances(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять финансами. Используйте соответствующие команды.",
        reply_markup=await get_manage_finance_menu()
    )

@router.callback_query(F.data == "manage_settings")
async def manage_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять настройками бота. Используйте соответствующие команды.",
        reply_markup=await get_admin_menu()
    )

@router.callback_query(F.data == "manage_notifications")
async def manage_notifications(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять уведомлениями. Используйте соответствующие команды.",
        reply_markup=await get_admin_menu()
    )

@router.callback_query(F.data == "pending_orders")
async def show_pending_orders(callback: CallbackQuery):
    async with get_session() as session:
        pending_orders = await get_orders_by_status(session, "pending")
        
        if pending_orders:
            await callback.message.delete()
            
            for order in pending_orders:
                text = ""
                user = await get_user(session, order.tg_id)
                text += f"Заказ №{order.order_number} от {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                text += f"Пользователь: {order.tg_id} {user.username}\n"
                text += f"Товар: {order.product_name}\n"
                text += f"Сумма: {order.price}₽\n"
                await callback.message.answer(
                    text=text,
                    reply_markup=await get_change_order_status(order.order_number)
                )
        else:
            text = "Нет ожидающих заказов."
            await callback.message.edit_text(text=text, reply_markup=await get_back_button("back_to_admin_menu"))
        

@router.callback_query(F.data == "completed_orders")
async def show_pending_orders(callback: CallbackQuery):
    async with get_session() as session:
        pending_orders = await get_orders_by_status(session, "completed")
        if pending_orders:
            text = "Выполненые заказы:\n\n"
            for order in pending_orders:
                user = await get_user(session, order.tg_id)
                text += f"Заказ №{order.order_number} от {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                text += f"Пользователь: {order.tg_id}, {user.username}\n"
                text += f"Товар: {order.product_name}\n"
                text += f"Сумма: {order.price}₽\n"
        else:
            text = "Нет Выполненых заказов."
        await callback.message.edit_text(
            text=text,
            reply_markup=await get_back_button("back_to_admin_menu")
        )

@router.callback_query(F.data == "cancelled_orders")
async def show_cancelled_orders(callback: CallbackQuery):
    async with get_session() as session:
        cancelled_orders = await get_orders_by_status(session, "cancelled")
        if cancelled_orders:
            text = "Отмененные заказы:\n\n"
            for order in cancelled_orders:
                user = await get_user(session, order.tg_id)
                text += f"Заказ №{order.order_number} от {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                text += f"Пользователь: {order.tg_id} {user.username}\n"
                text += f"Товар: {order.product_name}\n"
                text += f"Сумма: {order.price}₽\n"
        else:
            text = "Нет Отмененых заказов."
        await callback.message.edit_text(
            text=text,
            reply_markup=await get_back_button("back_to_admin_menu")
        )
    await callback.answer()

@router.callback_query(F.data.startswith("ap_"))
async def approve_order(callback: CallbackQuery):
    order_number = callback.data.split("_")[1]
    async with get_session() as session:
        order = await get_order(session, int(order_number))
        if order:
            order.status = "completed"
            await session.commit()
            await callback.message.edit_text(
                text=f"Заказ №{order.order_number} успешно выполнен."
            )
            await callback.bot.send_message(
                chat_id=order.tg_id,
                text=f"Ваш заказ №{order.order_number} на товар '{order.product_name}' был успешно выполнен."
            )
        else:
            await callback.message.edit_text(
                text="Заказ не найден.",
                reply_markup=await get_manage_order_menu()
            )

@router.callback_query(F.data.startswith("re_"))
async def reject_order(callback: CallbackQuery):
    order_number = callback.data.split("_")[1]
    async with get_session() as session:
        order = await get_order(session, int(order_number))
        if order and order.status == "pending":
            order.status = "cancelled"
            await session.commit()
            await callback.message.edit_text(
                text=f"Заказ №{order.order_number} успешно отменен."
            )
            await callback.bot.send_message(
                chat_id=order.tg_id,
                text=f"Ваш заказ №{order.order_number} на товар '{order.product_name}' был отменен. Деньги будут возвращены на ваш баланс."
            )
            user = await get_user(session, order.tg_id)
            await update_balance(session, user.tg_id, order.price)
        else:
            await callback.message.edit_text(
                text="Заказ не найден.",
                reply_markup=await get_manage_order_menu()
            )

@router.callback_query(F.data == "check_balance")
async def check_balance(callback: CallbackQuery):
    data = await crystalpay.get_balance()
    if data:
        text = f"Ваш текущий баланс CrystalPay:\n"
        for item in data:
            text += data[item]["currency"] + ": " + str(data[item]["amount"]) + "\n"
    else:
        text = "Не удалось получить баланс."
    data = await acquiring.get_balance()
    text += f"\nВаш текущий баланс Digital:\n"
    text += f"RUB: {data['rub_balance']}\n"
    text += f"USD: {data['usd_balance']}\n"
    text += f"USDT: {data['usdt_balance']}\n"
    await callback.message.edit_text(
        text=text,
        reply_markup=await get_back_button("back_to_admin_menu")
    )

@router.callback_query(F.data == "sales_stat")
async def sales_stat(callback: CallbackQuery):
    async with get_session() as session:
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        orders = await get_orders_by_status(session, "completed")
        month_orders = [o for o in orders if o.created_at >= month_start]
        total_sales = sum(o.price for o in month_orders)
        order_count = len(month_orders)
        avg_check = total_sales / order_count if order_count else 0

        text = (
            f"Статистика продаж за {now.strftime('%B %Y')}:\n"
            f"Общий объем продаж: {total_sales}₽\n"
            f"Количество заказов: {order_count}\n"
            f"Средний чек: {avg_check:.2f}₽"
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=await get_back_button("back_to_admin_menu")
        )

@router.callback_query(F.data == "payment_history")
async def payment_history(callback: CallbackQuery):
    async with get_session() as session:
        topups = await get_topups(session)
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_topups = [t for t in topups if t.created_at >= month_start]
        if month_topups:
            text = f"Пополнения за {now.strftime('%B %Y')}:\n\n"
            for t in month_topups:
                text += (
                    f"Тип оплаты: {t.payment_type}\n"
                    f"Номер заказа: {t.order_number}\n"
                    f"Пользователь: {t.tg_id}\n"
                    f"Сумма: {t.amount}₽\n"
                    f"Дата: {t.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
        else:
            text = "Нет пополнений за текущий месяц."
        await callback.message.edit_text(
            text=text,
            reply_markup=await get_back_button("back_to_admin_menu")
        )