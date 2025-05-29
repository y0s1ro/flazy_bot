from aiogram import Router, F
from aiogram.filters import Command
from bot.config import START_MESSAGE, BUTTONS_DATA, CATEGORIES_DATA
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.keybords import build_category_keyboard, build_product_keyboard, get_menu, get_profile_buttons, get_topup_buttons, get_payments_button, get_back_button
from bot.database import get_session, get_or_create_user, get_user_orders, get_user_topups, update_balance, create_topup, create_order
from bot.payments import acquiring, crystalpay
import uuid

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
    num_of_products = None
    if product.get('type') == 'product' and product.get('product_file_list'):
        with open(f"bot//{product.get('product_file_list')}", 'rb') as f:
            products_list = f.readlines()
            num_of_products = len(products_list)
    caption = (
        f"{product_id.split('&', 1)[1] if '&' in product_id else product_id}\n\n"
        f"💵 Цена: {product['amount']}₽\n\n"
        f"📝 Описание:\n{product['description']}"
    )
    if product.get('type') == 'product' and product.get('product_file_list'):
        reply_markup = await build_product_keyboard(category_path_ids, is_auto_product=True, num_of_products=num_of_products)
    else:
        reply_markup = await build_product_keyboard(category_path_ids)
    if product.get('image_folder'):
        await callback.message.answer_photo(
            FSInputFile(path=photo_path),
            caption=caption,
            reply_markup=reply_markup
        )
        await callback.message.delete()
    else:
        await callback.message.answer(
            text=caption,
            reply_markup=reply_markup
        )
        await callback.message.delete()
    try:
        await callback.answer()
    except Exception as e:
        pass

@router.callback_query(F.data.startswith("b_"))
async def handle_product_buy(callback: CallbackQuery, state: FSMContext):
    num_of_products = None
    if callback.data.endswith("a"):
        num_of_products = int(callback.data.split('_')[-1][:-1]) # Extract the number of products from the callback data
    # Extract the category path IDs from the callback data
    parts = callback.data.split('_')[:-1]
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

    async with get_session() as session:
        user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username)
        if user.balance < product['amount'] or (num_of_products and user.balance < product['amount'] * num_of_products):
            
            if num_of_products:
                await callback.message.answer(f"Вам не хватает {product['amount'] * num_of_products - user.balance}₽")
                await handle_topup_balance(callback, state=state, is_from_product=True, product_id=product_id, amount=product['amount']*num_of_products - user.balance, callback_back=f"p_{callback.data[2:]}")
            else:
                await callback.message.answer(f"Вам не хватает {product['amount'] - user.balance}₽")
                await handle_topup_balance(callback, state=state, is_from_product=True, product_id=product_id, amount=product['amount'] - user.balance, callback_back=f"p_{callback.data[2:]}")
        else:
            if product["type"] == "product":
                await update_balance(session, user.tg_id, -product['amount'] * num_of_products)
                order = await create_order(session, user.tg_id, keys[-2].split('&', 1)[1], product_id.split('&', 1)[1] if '&' in product_id else product_id, num_of_products, product['amount'] * num_of_products)
                with open(f"bot//{product.get('product_file_list')}", 'r') as f:
                    # Read all lines from the file
                    lines = f.readlines()
                    # Get the first n lines (where n = num_of_products)
                    selected_lines = lines[:num_of_products]
                    # Write back the remaining lines to the file (truncate the file)
                    with open(f"bot//{product.get('product_file_list')}", 'w') as fw:
                        fw.writelines(lines[num_of_products:])
                await callback.message.answer(
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"🎲Категория: {keys[-2].split('&', 1)[1]}\n"
                    f"🛍Товар: {product_id.split('&', 1)[1]}\n"
                    f"🖇Количество: {num_of_products} шт.\n"
                    f"💰Сумма: {product['amount'] * num_of_products}₽\n"
                    f"🎭Имя: {callback.from_user.full_name} : {user.tg_id}\n"
                    f"💡Заказ: {order.order_number}\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"🛒Ваш товар:\n{''.join([line for line in selected_lines])}\n"
                    f"Спасибо за покупку!"
                )
                await callback.message.delete()
            elif product["type"] == "tiket":
                await update_balance(session, user.tg_id, -product['amount'])
                order = await create_order(session, user.tg_id, keys[-2].split('&', 1)[1], product_id.split('&', 1)[1] if '&' in product_id else product_id, 1, product['amount'])
                await callback.message.answer(
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"🎲Категория: {keys[-2].split('&', 1)[1]}\n"
                    f"🛍Товар: {product_id.split('&', 1)[1]}\n"
                    f"💰Сумма: {product['amount']}₽\n"
                    f"🎭Имя: {callback.from_user.full_name} : {user.tg_id}\n"
                    f"💡Заказ: {order.order_number}\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"Для получения товара обратитесь к  @FlazySupport"
                )
                await callback.message.delete()

        
@router.callback_query(F.data == "back_to_profile")
async def handle_back_to_profile(callback: CallbackQuery):
    async with get_session() as session:
        user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username)
        user_orders = await get_user_orders(session, user.tg_id)
        text = BUTTONS_DATA["🪪 Профиль"]['text'].format(
            username = user.username if user.username else "Нет имени пользователя",
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
async def handle_topup_balance(callback: CallbackQuery, state: FSMContext, is_from_product: bool = False, product_id: str = None, amount: float = None, callback_back: str = None):
    if is_from_product:
        # If the top-up is initiated from a product, set the state accordingly
        await state.set_state(TopUpStates.waiting_for_amount)
        await callback.message.delete()
        await callback.message.answer("Веддите сумму пополнения в рублях:", reply_markup = await get_topup_buttons(is_from_product=True, product_id=product_id, amount=amount, callback_back="c_0"))
        await state.update_data(callback_back=callback_back, user_id = callback.from_user.id)
        await callback.answer()
    else:
        await state.set_state(TopUpStates.waiting_for_amount)

        await callback.message.edit_text("Веддите сумму пополнения в рублях:", reply_markup = await get_topup_buttons())
        await callback.answer()

@router.callback_query(F.data.startswith("topup_"), TopUpStates.waiting_for_amount)
@router.message(TopUpStates.waiting_for_amount)
async def handle_topup_amount(message, state: FSMContext):
    if isinstance(message, Message):
        try:
            #TODO DELETE
            if message.text.startswith("/"):
                async with get_session() as session:
                    user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
                    await update_balance(session, user.tg_id, float(message.text[1:]))
                return
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

    amount = float(message.text) if isinstance(message, Message) else float(message.data.split('_')[1])
    invoice_crystal = await crystalpay.create_invoice(amount=amount)
    invoice_acquiring = await acquiring.create_invoice(amount=amount, description="-")
    message_text = f"💸 К оплате: {amount}₽\n🔗 Ссылка будет активна в течение 30 минут\nПосле оплаты, пожалуйста, нажмите кнопку «Проверить оплату»"
    tg_id = message.from_user.id if isinstance(message, Message) else message.from_user.id
    await state.update_data(invoice_crystal=invoice_crystal, invoice_acquiring=invoice_acquiring, tg_id=tg_id)

    if isinstance(message, Message):
        await message.answer(
            text=message_text,
            reply_markup=await get_payments_button(invoice_acquiring['acquiring_page'], invoice_crystal['url'])
        )
    else:
        await message.message.edit_text(
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
        if data.get("callback_back"):
            fake_callback = CallbackQuery(
                id=str(uuid.uuid4()),
                from_user=callback.from_user,
                chat_instance=callback.chat_instance,
                message=callback.message,
                data=data["callback_back"]
            )
            await handle_product_selection(fake_callback)
        await callback.answer()
        await state.clear()
    elif acquiring_status['status'] == 'Paid':
        await callback.message.edit_text(f"✅Спасибо за оплату, ваш баланс успешно пополнен на {acquiring_status['amount']}₽.")
        async with get_session() as session:
            user = await get_or_create_user(session, data['tg_id'])
            await update_balance(session, user.tg_id, acquiring_status['amount'])
            await create_topup(session, user.tg_id, acquiring_status['amount'], 'Acquiring', acquiring_status['sbp_uuid'])
        if data.get("callback_back"):
            fake_callback = CallbackQuery(
                id=str(uuid.uuid4()),
                from_user=callback.from_user,
                chat_instance=callback.chat_instance,
                message=callback.message,
                data=data["callback_back"]
            )
            await handle_product_selection(fake_callback)
        await callback.answer()
        await state.clear()
    else:
        await callback.answer("Оплата не найдена или не завершена. Пожалуйста, проверьте статус оплаты.")

@router.message(F.text == "🪪 Профиль")
async def handle_profile(message: Message):
    async with get_session() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
        user_orders = await get_user_orders(session, user.tg_id)
        text = BUTTONS_DATA["🪪 Профиль"]['text'].format(
            username = user.username if user.username else "Нет имени пользователя",
            user_id = user.tg_id,
            balance = user.balance,
            orders = len(user_orders),
            refs = user.ref_link if user.ref_link else "Нет реферальной ссылки"
        )
        await message.answer(text=text, reply_markup=await get_profile_buttons())

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
