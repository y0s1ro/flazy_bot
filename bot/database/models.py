from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    referrer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('users.tg_id'), nullable=True)
    ref_link: Mapped[str | None] = mapped_column(String(100), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationship with orders
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    # Relationship with top-ups
    topups: Mapped[list["TopUp"]] = relationship("TopUp", back_populates="user")
    
    def __repr__(self):
        return f"<User(tg_id={self.tg_id}, username={self.username})>"

class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    region: Mapped[str | None] = mapped_column(String(50), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    order_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False,)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user: Mapped["User"] = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(tg_id={self.tg_id}, product_name={self.product_name}, price={self.price})>"
    
class TopUp(Base):
    __tablename__ = 'topups'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    order_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user: Mapped["User"] = relationship("User", back_populates="topups")
    
    def __repr__(self):
        return f"<TopUp(tg_id={self.tg_id}, amount={self.amount})>"
