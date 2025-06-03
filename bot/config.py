import json 

with open('bot/cfg/buttons.json', 'r', encoding='utf-8') as file:
    BUTTONS_DATA = json.load(file)

with open('bot/cfg/cat.json', 'r', encoding='utf-8') as file:
    CATEGORIES_DATA = json.load(file)
    CATEGORIES_DATA = {k: v for k, v in CATEGORIES_DATA.items() if CATEGORIES_DATA[k]["Status"] == "True"}  # Remove "Status" key

with open('bot/cfg/cfg.json', 'r', encoding='utf-8') as file:
    TOKENS_DATA = json.load(file)

with open('bot/commands/start/start_text.txt', 'r', encoding='utf-8') as file:
    START_MESSAGE = file.read()
