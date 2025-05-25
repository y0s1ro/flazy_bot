from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.config import BUTTONS_DATA

async def get_menu():
    
    menu = ReplyKeyboardBuilder()
    
    for row in BUTTONS_DATA:
        menu.add(KeyboardButton(text=row))
    
    return menu.adjust(3).as_markup(resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')


