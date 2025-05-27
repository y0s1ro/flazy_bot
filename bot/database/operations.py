import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Order, TopUp

async def get_user(session: AsyncSession, tg_id: int) -> User:
    """Get user by telegram ID"""
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, tg_id: int, username: str = None, ref_link: str = None) -> User:
    """Create new user"""
    user = User(tg_id=tg_id, username=username, ref_link=ref_link, balance=0.0)
    session.add(user)
    await session.commit()
    return user

async def get_or_create_user(session: AsyncSession, tg_id: int, username: str = None) -> User:
    """Get existing user or create new one"""
    user = await get_user(session, tg_id)
    if not user:
        user = await create_user(session, tg_id, username)
    return user

async def update_balance(session: AsyncSession, tg_id: int, amount: float) -> User:
    """Update user balance"""
    user = await get_user(session, tg_id)
    if user:
        user.balance += amount
        await session.commit()
    return user

async def create_order(session: AsyncSession, tg_id: int, category: str, product_name: str, price: float) -> Order:
    """Create a new order for a user"""
    order = Order(
        tg_id=tg_id,
        category=category,
        product_name=product_name,
        price=price,
        created_at=datetime.utcnow()
    )
    session.add(order)
    await session.commit()
    return order

async def get_user_orders(session: AsyncSession, tg_id: int) -> list[Order]:
    """Get all orders for a user"""
    result = await session.execute(
        select(Order)
        .where(Order.tg_id == tg_id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

async def create_topup(session: AsyncSession, tg_id: int, amount: float, payment_type: str, order_number:str) -> TopUp:
    """Create a new top-up for a user"""
    topup = TopUp(
        tg_id=tg_id,
        amount=amount,
        payment_type=payment_type,
        order_number=order_number,
        created_at=datetime.utcnow()
    )
    session.add(topup)
    await session.commit()
    return topup

async def get_user_topups(session: AsyncSession, tg_id: int) -> list[TopUp]:
    """Get all top-ups for a user"""
    result = await session.execute(
        select(TopUp)
        .where(TopUp.tg_id == tg_id)
        .order_by(TopUp.created_at.desc())
    )
    return result.scalars().all()