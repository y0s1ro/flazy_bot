from bot.database import get_session, get_user
import asyncio

async def main():
    async with get_session() as session:
        user = await get_user(session, tg_id=2061969666)  # Replace with the actual Telegram ID
        if user:
            user.balance = 960  # Set the new balance here
            await session.commit()
            print(f"User balance updated: {user.tg_id}, New Balance: {user.balance}")
        else:
            print("User not found.")

if __name__ == "__main__":
    asyncio.run(main())
