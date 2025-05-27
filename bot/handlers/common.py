from aiogram import Router, F
from aiogram.filters import Command
from bot.config import START_MESSAGE, BUTTONS_DATA, CATEGORIES_DATA
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.keybords import build_category_keyboard, build_product_keyboard, get_menu, get_profile_buttons, get_topup_buttons, get_payments_button, get_back_button
from bot.database import get_session, get_or_create_user, get_user_orders, get_user_topups, update_balance, create_topup
from bot.payments import acquiring, crystalpay

#add different currency
router = Router()


class TopUpStates(StatesGroup):
    waiting_for_amount = State()
    invoice_id = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    async with get_session() as session:
        # Get or create user in the database
        user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
        photo_path = "bot/commands/start/start.jpg"
        # Open the file and send it
        await message.answer_photo(FSInputFile(path=photo_path),
            caption = START_MESSAGE.format(message.from_user.first_name),
            reply_markup=await get_menu()
        )

@router.callback_query(F.data.startswith("c_"))
async def handle_category_selection(callback: CallbackQuery):
    if len(callback.data.split("_")) == 2:
        # If the callback is for the main categories
        keyboard = await build_category_keyboard(CATEGORIES_DATA)
        await callback.message.edit_text(
            text="Выберите категорию:",
            reply_markup=keyboard
        )
        await callback.answer()
        return
    parts = callback.data.split('_')
    level = int(parts[1])
    category_data = CATEGORIES_DATA
    keys = []
    for part in parts[2:]:
        for name in category_data:
            if name.startswith(part):
                keys.append(name)
                category_data = category_data[name]
                break
    if level == 0:
        # Main category selected
        category_data = CATEGORIES_DATA[keys[0]]
    else:
        # Navigate through the nested structure
        category_data = CATEGORIES_DATA
        for key in keys:
            if key in category_data:
                category_data = category_data[key]
            else:
                await callback.answer("Категория не найдена")
                return
    
    if not category_data:
        await callback.answer("Пустая категория")
        return
    keyboard = await build_category_keyboard(category_data, level+1, '_'.join(parts[2:]))
    await callback.message.answer(
        text=f"Выберете из категории: {keys[-1].split('&', 1)[1] if '&' in keys[-1] else ''}",
        reply_markup=keyboard
    )
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data.startswith("p_"))
async def handle_product_selection(callback: CallbackQuery):
    parts = callback.data.split('_')
    category_path_ids = parts[1:]
    category_data = CATEGORIES_DATA
    keys = []
    for category_id in category_path_ids:
        for name in category_data:
            if name.startswith(category_id):
                keys.append(name)
                category_data = category_data[name]
                break

    product_id = keys[-1]
    # Find the product in the nested structure
    product_data = CATEGORIES_DATA
    for key in keys[:-1]:
        if key in product_data:
            product_data = product_data[key]
        else:
            await callback.answer("Продукт не найден")
            return
    
    product = product_data.get(product_id)
    if not product:
        await callback.answer("Продукт не найден")
        return
    # Create a keyboard with "Buy" button
    # Send product photo with caption and inline keyboard
    photo_path = f"bot//{product.get('image_folder')}"
    caption = (
        f"{product_id.split('&', 1)[1] if '&' in product_id else product_id}\n\n"
        f"💵 Цена: {product['amount']}₽\n\n"
        f"📝 Описание:\n{product['description']}"
    )
    if product.get('image_folder'):
        await callback.message.answer_photo(
            FSInputFile(path=photo_path),
            caption=caption,
            reply_markup=await build_product_keyboard(category_path_ids)
        )
        await callback.message.delete()
    else:
        await callback.message.answer(
            text=caption,
            reply_markup=await build_product_keyboard(category_path_ids)
        )
        await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data.startswith("b_"))
async def handle_product_selection(callback: CallbackQuery):
    # Extract the category path IDs from the callback data
    pass

@router.callback_query(F.data == "back_to_profile")
async def handle_back_to_profile(callback: CallbackQuery):
    async with get_session() as session:
        user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username)
        user_orders = await get_user_orders(session, user.tg_id)
        text = BUTTONS_DATA["🪪 Профиль"]['text'].format(
            user_id = user.tg_id,
            balance = user.balance,
            orders = len(user_orders),
            refs = user.ref_link if user.ref_link else "Нет реферальной ссылки"
        )
        await callback.message.edit_text(text=text, reply_markup=await get_profile_buttons())
    await callback.answer()

@router.callback_query(F.data == "orders_history")
async def handle_orders_history(callback: CallbackQuery):
    async with get_session() as session:
        user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username)
        user_orders = await get_user_orders(session, user.tg_id)
        if not user_orders:
            orders_text = "У вас нет истории пополнений."
        else:
            orders_text = "\n".join(
                f"Заказ #{order.id}: {order.product_name} - {order.price}₽"
                for order in user_orders
            )
        await callback.message.edit_text(orders_text, reply_markup=await get_back_button("back_to_profile"))
    await callback.answer()

@router.callback_query(F.data == "topup_history")
async def handle_topup_history(callback: CallbackQuery):
    async with get_session() as session:
        user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username)
        user_topups = await get_user_topups(session, user.tg_id)
        if not user_topups:
            topups_text = "У вас нет истории пополнений."
        else:
            topups_text = "\n".join(
                f"Пополнение #{topup.id}: {topup.amount}₽ ({topup.payment_type})"
                for topup in user_topups
            )
        await callback.message.edit_text(topups_text, reply_markup=await get_back_button("back_to_profile"))
    await callback.answer()

@router.callback_query(F.data == "topup_balance")
async def handle_topup_balance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TopUpStates.waiting_for_amount)

    await callback.message.edit_text("Веддите сумму пополнения в рублях:", reply_markup = await get_topup_buttons())
    await callback.answer()

@router.message(TopUpStates.waiting_for_amount)
async def handle_topup_amount(message: Message, state: FSMContext):
    try:
        if ',' in message.text or '.' in message.text:
            await message.answer("Пожалуйста, введите корректную сумму без копейек.")
            return
        amount = float(message.text)
        if amount <= 0:
            await message.answer("Сумма должна быть больше нуля. Пожалуйста, введите корректную сумму.")
            return
    except ValueError:
        if message.text in BUTTONS_DATA:
            await state.clear()
            await unknown_command(message)
            return
        else:
            await message.answer("Пожалуйста, введите корректную сумму в рублях.")

    invoice_crystal = await crystalpay.create_invoice(amount=amount)
    invoice_acquiring = await acquiring.create_invoice(amount=amount, description="-")
    message_text = f"💸 К оплате: {amount}₽\n🔗 Ссылка будет активна в течение 30 минут\nПосле оплаты, пожалуйста, нажмите кнопку «Проверить оплату»"
    await state.update_data(invoice_crystal=invoice_crystal, invoice_acquiring=invoice_acquiring, tg_id=message.from_user.id)
    await message.answer(
        text=message_text,
        reply_markup=await get_payments_button(invoice_acquiring['acquiring_page'], invoice_crystal['url'])
    )
    await state.set_state(TopUpStates.invoice_id)
    

@router.callback_query(F.data == "check_payment_status", TopUpStates.invoice_id)
async def handle_check_payment_status(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    invoice_crystal = data['invoice_crystal']
    invoice_acquiring = data['invoice_acquiring']
    # Check the status of the CrystalPAY invoice
    crystal_status = await crystalpay.check_invoice_status(invoice_crystal['id'])
    acquiring_status = await acquiring.check_invoice_status(invoice_acquiring['transaction_uuid'])

    if crystal_status['state'] == 'payed':
        await callback.message.edit_text(f"✅Спасибо за оплату, ваш баланс успешно пополнен на {invoice_crystal['amount']}₽.")
        async with get_session() as session:
            user = await get_or_create_user(session, data['tg_id'])
            await update_balance(session, user.tg_id, invoice_crystal['amount'])
            await create_topup(session, user.tg_id, invoice_crystal['amount'], 'CrystalPAY', invoice_crystal['id'])
        await callback.answer()
        await state.clear()
    elif acquiring_status['status'] == 'Paid':
        await callback.message.edit_text(f"✅Спасибо за оплату, ваш баланс успешно пополнен на {acquiring_status['amount']}₽.")
        async with get_session() as session:
            user = await get_or_create_user(session, data['tg_id'])
            await update_balance(session, user.tg_id, acquiring_status['amount'])
            await create_topup(session, user.tg_id, acquiring_status['amount'], 'Acquiring', acquiring_status['sbp_uuid'])
        await state.clear()
    else:
        await callback.answer("Оплата не найдена или не завершена. Пожалуйста, проверьте статус оплаты.")


@router.message()
async def unknown_command(message: Message):
    if message.text in BUTTONS_DATA:
        if BUTTONS_DATA[message.text]['type'] == 'text':
            if message.text == "🪪 Профиль":
                # Show user profile
                async with get_session() as session:
                    user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
                    user_orders = await get_user_orders(session, user.tg_id)
                    text = BUTTONS_DATA[message.text]['text'].format(
                        username = user.username if user.username else "Нет имени пользователя",
                        user_id = user.tg_id,
                        balance = user.balance,
                        orders = len(user_orders),
                        refs = user.ref_link if user.ref_link else "Нет реферальной ссылки"
                    )
                    await message.answer(text=text, reply_markup=await get_profile_buttons())
            else:
                await message.answer(text=BUTTONS_DATA[message.text]['text'])
        elif BUTTONS_DATA[message.text]['type'] == 'func':
            if BUTTONS_DATA[message.text]['func'] == 'buy':
                # Show main categories
                keyboard = await build_category_keyboard(CATEGORIES_DATA)
                await message.answer(
                    text="Выберите категорию:",
                    reply_markup=keyboard
                )
    else:
        await message.answer(text="Неизвестная команда. Пожалуйста, используйте /start для начала.")
