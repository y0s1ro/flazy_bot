from aiogram import Router, F
from aiogram.filters import Command
from bot.config import START_MESSAGE, BUTTONS_DATA, CATEGORIES_DATA, TOKENS_DATA
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import BaseMiddleware
from bot.keybords import get_admin_menu, get_manage_order_menu, get_change_order_status, get_back_button, get_manage_finance_menu, get_users_menu, build_review_keyboard, get_notifications_menu, get_custom_keyboard
from bot.database import get_orders_by_status, get_session, get_user, get_order, update_balance, get_topups, get_users, ban_user
from bot.payments import crystalpay, acquiring
# from bot.handlers.common import referal_bonus
from datetime import datetime
from bot.fsm import AdminStates

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
        reply_markup=await get_users_menu()
    )

@router.callback_query(F.data == "manage_finances")
async def manage_finances(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять финансами. Используйте соответствующие команды.",
        reply_markup=await get_manage_finance_menu()
    )

@router.callback_query(F.data == "manage_settings")
async def manage_settings(callback: CallbackQuery):
    total_users = 0
    text = f"""🎉 Обновление ассортимента наборов Fortnite! 🎉
Мы добавили наборы, доступные к покупке прямо сейчас! 👇

🆕 Новые наборы:

🇺🇸 Дух независимости — 1190₽
🔥 Лавовый чемпион — 710₽
🌈 Мир грёз — 140₽
🌌 Прикосновение пустоты — 290₽
🌠 Вечное странствие — 1220₽
💀 Кости и черепа — 1220₽
👑 Огненные владыки — 1100₽
🌋 Лавовые легенды — 1080₽
☀️ Летние легенды — 1130₽
🛡 Стражи Галактики — 1620₽
❄️ Ледяные легенды — 1330₽

🆕 Новинка!

🗝 Подписка ExitLag на 1 месяц в виде ключа — 150₽

💬 Вы можете быстро оформить покупку, нажав на кнопку ниже.
⚡️ Успей первым забрать топовые сеты!"""
    async with get_session() as session:
        users = await get_users(session)
        for user in users:
            try:
                await callback.message.bot.send_message(
                    chat_id=user.tg_id,
                    text=text,
                    reply_markup = await get_custom_keyboard(callbacks=["c_2_4_1_fn", "c_2_15_1_fn"],
                                                             texts=["🦸‍♂️ Наборы", "🔑 Ключ"])
                )
                total_users += 1
            except Exception as e:
                print(f"Failed to send notification to {user.tg_id}: {e}")

@router.callback_query(F.data == "manage_notifications")
async def manage_notifications(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Здесь вы можете управлять уведомлениями. Используйте соответствующие команды.",
        reply_markup=await get_notifications_menu()
    )

@router.callback_query(F.data == "send_notifications")
async def send_notifications(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите текст уведомления для отправки всем пользователям:",
        reply_markup=await get_back_button("back_to_admin_menu")
    )
    await callback.answer()
    await state.set_state(AdminStates.send_notification_state)

@router.message(AdminStates.send_notification_state, F.text)
async def handle_send_notification(message: Message, state: FSMContext):
    notification_text = message.text.strip()
    await state.update_data(notification_text=notification_text)
    
    await message.answer(
        text="Вы можете отправить уведомление с изображением или без. Если хотите отправить с изображением, загрузите его сейчас, если без напишите no_image.",
        reply_markup=await get_back_button("back_to_admin_menu")
    )
    await state.set_state(AdminStates.waiting_for_image)

@router.message(AdminStates.waiting_for_image, F.photo | F.document | F.text == "no_image") 
async def handle_notification_image(message: Message, state: FSMContext):
    data = await state.get_data()
    notification_text = data.get("notification_text", "")
    
    total_users = 0
    async with get_session() as session:
        users = await get_users(session)
        
        for user in users:
            try:
                if message.photo:
                    await message.bot.send_photo(
                        chat_id=user.tg_id,
                        photo=message.photo[-1].file_id,
                        caption=notification_text
                    )
                elif message.document:
                    await message.bot.send_document(
                        chat_id=user.tg_id,
                        document=message.document.file_id,
                        caption=notification_text
                    )
                else:
                    await message.bot.send_message(
                        chat_id=user.tg_id,
                        text=notification_text
                    )
                total_users += 1
            except Exception as e:
                print(f"Failed to send notification to {user.tg_id}: {e}")
    
    await message.answer(
        text=f"Уведомление успешно отправлено {total_users} пользователям.",
        reply_markup=await get_back_button("back_to_admin_menu")
    )
    
    await state.clear()

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
            messages = []
            for order in pending_orders:
                user = await get_user(session, order.tg_id)
                line = ""
                line += f"Заказ №{order.order_number} от {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                line += f"Пользователь: {order.tg_id}, {user.username}\n"
                line += f"Товар: {order.product_name}\n"
                line += f"Сумма: {order.price}₽\n\n"
                if len(text) + len(line)> 4000:
                    messages.append(text)
                    text = ""
                text += line
            if text:
                messages.append(text)
            for msg in messages:
                await callback.message.answer(msg)
            await callback.message.answer(
            text="Конец списка.",
            reply_markup=await get_back_button("back_to_admin_menu")
            )
            await callback.message.delete()
        else:
            await callback.message.edit_text(
                text=text,
                reply_markup=await get_back_button("back_to_admin_menu")
            )

@router.callback_query(F.data == "cancelled_orders")
async def show_cancelled_orders(callback: CallbackQuery):
    async with get_session() as session:
        pending_orders = await get_orders_by_status(session, "canselled")
        if pending_orders:
            text = "Выполненые заказы:\n\n"
            messages = []
            for order in pending_orders:
                user = await get_user(session, order.tg_id)
                line = ""
                line += f"Заказ №{order.order_number} от {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                line += f"Пользователь: {order.tg_id}, {user.username}\n"
                line += f"Товар: {order.product_name}\n"
                line += f"Сумма: {order.price}₽\n\n"
                if len(text) + len(line)> 4000:
                    messages.append(text)
                    text = ""
                text += line
            if text:
                messages.append(text)
            for msg in messages:
                await callback.message.answer(msg)
            await callback.message.answer(
            text="Конец списка.",
            reply_markup=await get_back_button("back_to_admin_menu")
            )
            await callback.message.delete()
        else:
            await callback.message.edit_text(
                text=text,
                reply_markup=await get_back_button("back_to_admin_menu")
            )
            await callback.answer()

@router.callback_query(F.data.startswith("ap_"))
async def approve_order(callback: CallbackQuery, state: FSMContext):
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
                text=f"Ваш заказ №{order.order_number} на товар '{order.product_name}' был успешно выполнен.",
                reply_markup=await build_review_keyboard(order.order_number)
            )
            from bot.handlers.common import referal_bonus
            await referal_bonus(callback.message, order.tg_id, order.price)
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

@router.callback_query(F.data == "view_users")
async def view_users(callback: CallbackQuery):
    async with get_session() as session:
        users = await get_users(session)
        
        if users:
            text = "Список пользователей:\n\n"
            messages = []
            for user in users:
                line = f"ID: {user.tg_id}, Username: {user.username}\n"
                if len(text) + len(line) > 4000:
                    messages.append(text)
                    text = ""
                text += line
            if text:
                messages.append(text)
            for msg in messages:
                await callback.message.answer(msg)
            await callback.message.answer(
            text="Всего пользователей: " + str(len(users)),
            reply_markup=await get_back_button("back_to_admin_menu")
            )
            await callback.message.delete()
        else:
            await callback.message.edit_text(
            text="Нет зарегистрированных пользователей.",
            reply_markup=await get_back_button("back_to_admin_menu")
            )

@router.callback_query(F.data == "search_user")
async def search_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите ID пользователя для поиска:",
        reply_markup=await get_back_button("back_to_admin_menu")
    )
    await callback.answer()
    await state.set_state(AdminStates.search_user_state)

@router.message(AdminStates.search_user_state, F.text)
async def search_user_by_id(message: Message, state: FSMContext):
    user_id = message.text.strip()
    
    async with get_session() as session:
        user = await get_user(session, int(user_id))
        
        if user:
            text = (
                f"Пользователь найден:\n"
                f"ID: {user.tg_id}\n"
                f"Username: {user.username}\n"
                f"Баланс: {user.balance}₽\n"
                f"Статус: {'Забанен' if user.is_banned else 'Активен'}\n"
            )
            if getattr(user, "refer_id", None):
                text += f"ID реферала: {user.refer_id}\n"
            if getattr(user, "refer_link", None):
                text += f"Ревфральная ссылка: {user.refer_link}\n"
            # Получаем сумму заказов пользователя
            orders = await get_orders_by_status(session, "completed")
            user_orders = [o for o in orders if o.tg_id == user.tg_id]
            total_amount = sum(o.price for o in user_orders)
            text += f"Сумма заказов: {total_amount}₽"
        else:
            text = "Пользователь не найден."
        
        await message.answer(text=text, reply_markup=await get_back_button("back_to_admin_menu"))
    
    await state.clear()

@router.callback_query(F.data == "ban_user")
async def handle_ban_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите ID пользователя для бана:",
        reply_markup=await get_back_button("back_to_admin_menu")
    )
    await callback.answer()
    await state.set_state(AdminStates.ban_user_state)

@router.message(AdminStates.ban_user_state, F.text)
async def ban_user_by_id(message: Message, state: FSMContext):
    user_id = message.text.strip()
    
    async with get_session() as session:
        user = await get_user(session, int(user_id))
        
        if user:
            await ban_user(session, user.tg_id)
            text = f"Пользователь {user.username} (ID: {user.tg_id}) был забанен."
            await send_to_admins(message, text)
        else:
            text = "Пользователь не найден."
        
        await message.answer(text=text, reply_markup=await get_back_button("back_to_admin_menu"))
    
    await state.clear()

@router.callback_query(F.data == "unbun_user")
async def handle_unban_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите ID пользователя для разбана:",
        reply_markup=await get_back_button("back_to_admin_menu")
    )
    await callback.answer()
    await state.set_state(AdminStates.unban_user_state)

@router.message(AdminStates.unban_user_state, F.text)
async def unban_user_by_id(message: Message, state: FSMContext):
    user_id = message.text.strip()
    
    async with get_session() as session:
        user = await get_user(session, int(user_id))
        
        if user:
            user.is_banned = 0
            await session.commit()
            text = f"Пользователь {user.username} (ID: {user.tg_id}) был разбанен."
            await send_to_admins(message, text)
        else:
            text = "Пользователь не найден."
        
        await message.answer(text=text, reply_markup=await get_back_button("back_to_admin_menu"))
    
    await state.clear()

@router.callback_query(F.data == "invite_stat")
async def invite_stat(callback: CallbackQuery):
    async with get_session() as session:
        users = await get_users(session)
        invite_stats = {}
        
        for user in users:
            if user.ref_link:
                if user.ref_link not in invite_stats:
                    invite_stats[user.ref_link] = 0
                invite_stats[user.ref_link] += 1
        
        if invite_stats:
            text = "Статистика приглашений:\n\n"
            for ref_link, count in invite_stats.items():
                text += f"Ссылка: {ref_link}, Зарегестрировано пользователей: {count}\n"
        else:
            text = "Нет статистики приглашений."
        
        await callback.message.edit_text(
            text=text,
            reply_markup=await get_back_button("back_to_admin_menu")
        )

@router.callback_query(F.data == "change_balance")
async def change_balance(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите ID пользователя и новую сумму баланса в формате 'ID сумма':",
        reply_markup=await get_back_button("back_to_admin_menu")
    )
    await callback.answer()
    await state.set_state(AdminStates.change_balance_state)

@router.message(AdminStates.change_balance_state, F.text)
async def change_user_balance(message: Message, state: FSMContext):
    try:
        user_id, amount = map(str.strip, message.text.split())
        user_id = int(user_id)
        amount = float(amount)
        
        async with get_session() as session:
            user = await get_user(session, user_id)
            
            if user:
                await update_balance(session, user.tg_id, amount)
                text = f"Баланс пользователя {user.username} (ID: {user.tg_id}) успешно изменен на {amount}₽."
                await send_to_admins(message, text)
            else:
                text = "Пользователь не найден."
        
        await message.answer(text=text, reply_markup=await get_back_button("back_to_admin_menu"))
    except ValueError:
        await message.answer("Неверный формат ввода. Используйте 'ID сумма'.")
    
    await state.clear()
