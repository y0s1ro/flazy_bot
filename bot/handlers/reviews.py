from PIL import Image, ImageDraw, ImageFont
import textwrap
import re
from aiogram import Router, F
from aiogram.filters import Command
from bot.config import TOKENS_DATA
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import BaseMiddleware
from bot.keybords import build_review_keyboard, build_review_rating_keyboard
from bot.database import get_session, get_order
from bot.fsm import ReviewStates
from aiogram import Bot
import os

router = Router()

async def create_review_image(username: str, review_text: str, rating: int, product: tuple[str, str], max_width=800, max_height=180) -> str:
    # Create blank image (800x600 pixels, white background)
    img = Image.new('RGB', (900, 400), color='black')
    draw = ImageDraw.Draw(img)
    
    # Load fonts (replace with actual font paths)
    try:
        title_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 40)
        text_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 30)
    except OSError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Add title
    draw.text((50, 50), f"Отзыв от {username}", fill="yellow", font=title_font)
    # Paste star image(s) for rating
    try:
        star_img = Image.open("/Users/yuriizaika/Documents/python/Projects/FlazyBot/bot/img/star1.png").convert("RGBA")
        #star_img = Image.open("bot/img/star1.png").convert("RGBA")
        star_size = 40
        star_img = star_img.resize((star_size, star_size))
        for i in range(rating):
            img.paste(star_img, (50 + i * (star_size + 5), 120), star_img)
        for i in range(5 - rating):
            empty_star_img = Image.open("/Users/yuriizaika/Documents/python/Projects/FlazyBot/bot/img/star0.png").convert("RGBA")
            empty_star_img = empty_star_img.resize((star_size, star_size))
            img.paste(empty_star_img, (50 + (rating + i) * (star_size + 5), 120), empty_star_img)
    except Exception as e:
        print(e)  # If star image not found, skip drawing stars
    # Write product name after stars
    print(product)
    product_name = "/".join(product).strip()  # Join product tuple into a single string
    # Remove emoji from product name
    product_name = re.sub(r'[\U00010000-\U0010ffff]', '', product_name).strip()
    product_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 28) if text_font else ImageFont.load_default()
    stars_width = 5 * (star_size + 5)
    draw.text((50 + stars_width + 20, 130), product_name.strip(), fill="white", font=product_font)
    # Wrap and add review text
    initial_font_size = 30
    font_size = initial_font_size
    text_font = None
    
    for _ in range(10):
        try:
            text_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except:
            text_font = ImageFont.load_default()
        
        # Wrap text and calculate dimensions
        wrapped_lines = []
        for line in review_text.split('\n'):
            wrapped_lines.extend(textwrap.wrap(line, width=max_width // (font_size // 2)))
        
        total_height = len(wrapped_lines) * (font_size + 5)
        
        # Check if fits in allocated space
        if total_height <= max_height:
            break
        font_size -= 2  # Reduce font size if too tall
    
    # Draw wrapped text
    y_position = 200
    for line in wrapped_lines:
        draw.text((50, y_position), line, fill="white", font=text_font)
        y_position += font_size + 5
    
    image_path = f"review_{username}.jpg"
    img.save(image_path)
    return image_path

async def ask_for_review(callback: CallbackQuery, product: tuple[str, str], state: FSMContext, tg_id:int = None):
    """
    Function to ask user for a review.
    :param message: User message
    :param product: Product tuple (name, description)
    """
    await callback.bot.send_message(
        chat_id=tg_id or callback.from_user.id,
        text=f"Пожалуйста, оставьте отзыв о продукте {product[0]} ({product[1]}).\nВаш отзыв поможет другим пользователям сделать правильный выбор.",
        reply_markup=await build_review_keyboard()
    )
    await state.update_data(product=product)
    print("ask_for_review",product)
    data = await state.get_data()
    print("ask_for_review data", data)

@router.callback_query(F.data.startswith("review"))
async def handle_review_request(callback: CallbackQuery, state: FSMContext):
    """
    Handle the review request callback.
    :param callback: Callback query from user
    :param state: FSM context to store data
    """
    if callback.data.startswith("reviewo"):
        async with get_session() as session:
            order_number = int(callback.data.split("_")[-1])
            order = await get_order(session, order_number)
            if not order:
                await callback.message.answer("Заказ не найден.")
                return
            product = (order.category, order.product_name)
            await state.update_data(product=product)
    await callback.message.answer(
        "Оцените продукт от 1 до 5 звезд.",
        reply_markup=await build_review_rating_keyboard()
    )
    await callback.message.delete()
    await state.set_state(ReviewStates.waiting_for_review_rating)
    data = await state.get_data()
    print("handle_review_request data", data)

@router.callback_query(F.data.startswith("rev_rating_"), ReviewStates.waiting_for_review_rating)
async def handle_review_rating(callback: CallbackQuery, state: FSMContext):
    """
    Handle the review rating selection.
    :param callback: Callback query from user
    :param state: FSM context to store data
    """
    rating = int(callback.data.split("_")[-1])
    await state.update_data(rating=rating)
    
    # Ask for review text
    await callback.message.answer(
        "Пожалуйста, напишите ваш отзыв. Вы можете использовать до 500 символов."
    )
    await callback.message.delete()
    await state.set_state(ReviewStates.waiting_for_review_text)

@router.message(ReviewStates.waiting_for_review_text, F.text)
async def handle_review_text(message: Message, state: FSMContext):
    """
    Handle the review text input from user.
    :param message: User message with review text
    :param state: FSM context to store data
    """
    data = await state.get_data()
    rating = data.get("rating")
    product = data.get("product")
    
    # Validate review text length
    if len(message.text) > 500:
        await message.answer("Ваш отзыв слишком длинный. Пожалуйста, сократите его до 500 символов.")
        return
    
    # Create review image
    image_path = await create_review_image(
        username=message.from_user.full_name or "Аноним",
        review_text=message.text,
        rating=rating,
        product=product
    )
    
    # Send the review image to user
    await post_to_channel(message.bot, image_path)
    await message.answer_photo(FSInputFile(image_path), caption=f"Ваш отзыв о {product[0]} ({product[1]}) успешно сохранен!")
    try:
        os.remove(image_path)
    except Exception as e:
        print(f"Failed to delete review image: {e}")
    # Clear the state
    await state.clear()

async def post_to_channel(bot: Bot, image_path: str):
    await bot.send_photo(
        chat_id=TOKENS_DATA["review_channel"],
        photo=FSInputFile(image_path)
    )

@router.callback_query(F.data == "no_review")
async def cancel_review(callback: CallbackQuery):
    """
    Handle the cancellation of the review process.
    :param callback: Callback query from user
    :param state: FSM context to clear data
    """
    await callback.message.answer("Вы отменили процесс оставления отзыва.")
    await callback.message.delete()

# Example usage
if __name__ == "__main__":
    username = "example_user"
    review_text = "Это отличный продукт! Я очень доволен качеством и Это отличный продукт! Я очень доволен качеством и обслуживаниемЭто отличный продукт! Я очеЭто отличный продукт! Я очень доволен качеством и Это отличный продукт! Я очень доволен качествомнь доволен качеством и обслуживаниемобслуживанием.Это отличный продукт! Я очень доволен качеством и обслуживаниемЭто отличный продукт! Я очень доволен качеством и обслуживанием."
    rating = 3
    product = ("👹 Diablo IV", 'Diablo® IV - Standard Edition')
    
    image_path = create_review_image(username, review_text, rating, product)
    print(f"Review image created at: {image_path}")