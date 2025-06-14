import json 
from bot.filter_categories import filter

with open('bot/cfg/buttons.json', 'r', encoding='utf-8') as file:
    BUTTONS_DATA = json.load(file)

with open('bot/cfg/filtered_categories.json', 'r', encoding='utf-8') as file:
    filter()  # Ensure categories are filtered before loading
    CATEGORIES_DATA = json.load(file)

with open('bot/cfg/cfg.json', 'r', encoding='utf-8') as file:
    TOKENS_DATA = json.load(file)

with open('bot/commands/start/start_text.txt', 'r', encoding='utf-8') as file:
    START_MESSAGE = file.read()