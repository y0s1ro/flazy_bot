from aiogram import Router, F
from aiogram.filters import Command
from bot.keybords.menu import get_menu
from bot.config import START_MESSAGE, BUTTONS_DATA, CATEGORIES_DATA
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.keybords.catalog import build_category_keyboard, build_product_keyboard


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    photo_path = "bot/commands/start/start.jpg"
    # Open the file and send it
    await message.answer_photo(FSInputFile(path=photo_path),
        caption = START_MESSAGE.format(message.from_user.first_name),
        reply_markup=await get_menu()
    )

@router.callback_query(F.data.startswith("c_"))
async def handle_category_selection(callback: CallbackQuery):
    if callback.data == "c_0":
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
                await callback.answer("Category not found")
                return
    
    if not category_data:
        await callback.answer("Empty category")
        return
    
    keyboard = await build_category_keyboard(category_data, level+1, '_'.join(parts[2:]))
    await callback.message.edit_text(
        text=f"Select an item:",
        reply_markup=keyboard
    )
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
            await callback.answer("Product not found")
            return
    
    product = product_data.get(product_id)
    if not product:
        await callback.answer("Product not found")
        return
    # Create a keyboard with "Buy" button
    await callback.message.edit_text(
        text=f"{product_id.split('&', 1)[1] if '&' in product_id else product_id}\n\n"
             f"💵 Цена: {product['amount']}₽\n\n"
             f"📝 Описание:\n{product['description']}",
        reply_markup=await build_product_keyboard(category_path_ids)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("b_"))
async def handle_product_selection(callback: CallbackQuery):
    # Extract the category path IDs from the callback data
    pass

@router.message()
async def unknown_command(message: Message):
    if message.text in BUTTONS_DATA:
        if BUTTONS_DATA[message.text]['type'] == 'text':
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
