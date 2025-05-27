from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Float, DateTime, ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    tg_id = Column(BigInteger, primary_key=True)
    username = Column(String(32), nullable=True)
    ref_link = Column(String(100), nullable=True)
    balance = Column(Float, default=0.0)
    
    # Relationship with orders
    orders = relationship("Order", back_populates="user")
    # Relationship with top-ups
    topups = relationship("TopUp", back_populates="user")
    
    def __repr__(self):
        return f"<User(tg_id={self.tg_id}, username={self.username})>"

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    category = Column(String(100), nullable=False)
    product_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(tg_id={self.tg_id}, product_name={self.product_name}, price={self.price})>"
    
class TopUp(Base):
    __tablename__ = 'topups'
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_type = Column(String(20), nullable=False)
    order_number = Column(String(40), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user = relationship("User", back_populates="topups")
    
    def __repr__(self):
        return f"<TopUp(tg_id={self.tg_id}, amount={self.amount})>"
