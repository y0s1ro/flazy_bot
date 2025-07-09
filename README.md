# FlazyBot

FlazyBot is a Python-based Telegram shop bot designed for easy administration, extensibility, and robust data management. It allows administrators to manage products, categories, users, and orders, and provides a modular structure for adding new features and payment integrations.

## Features

- **Easy setup and configuration**
- **Modular architecture** for adding new features
- **Logging and error handling**
- **SQLAlchemy** async database with proper connection management
- **Admin panel** for managing users, products, and orders
- **Easy payment connection**
- **Customizable keyboards and menus**
- **Category and product management**
- **User profile and referral system**

---

## Project Structure

```
FlazyBot/
│
├── main.py                  # Entry point for the bot
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
│
├── bot/
│   ├── config.py            # Loads configuration and tokens
│   ├── handlers/            # Telegram command and message handlers
│   ├── keybords/            # Keyboard and menu utilities
│   ├── database/            # Database models, connection, and operations
│   ├── commands/            # Command-specific resources (e.g., /start)
│   ├── cfg/                 # JSON configuration files (categories, buttons, etc.)
│   └── ...                  # Other modules (payments, FSM, etc.)
│
└── ...
```

---


---

## Usage

- **/start** — Users are greeted and can navigate categories and products.
- **Profile** — Users can view their profile, balance, and referral link.
- **Admin panel** — Admins can manage users, products, and orders.

All user interactions are handled via Telegram's inline keyboards and custom reply menus.

---

## Development

### Handlers

- All message and command handlers are in `bot/handlers/`.
- Add new features by creating new handler modules and including them in the router.

### Database

- All database logic is in `bot/database/`.
- Use the `get_session()` async context manager for all DB operations:

```python
from bot.database import get_session

async with get_session() as session:
    # Use session for DB operations
```

### Adding Payments

- Payment integrations can be added in `bot/payments/`.

---

## Environment Variables

- Store sensitive data (tokens, API keys) in `bot/cfg/cfg.json` or use environment variables with `python-dotenv`.

---

## License

This project is licensed under the MIT License.
