from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.database import Base

class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, index=True)
    strike_price = Column(Float)
    option_type = Column(String) # CE or PE
    transaction_type = Column(String) # BUY or SELL
    quantity = Column(Integer)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    status = Column(String, default="OPEN") # OPEN, CLOSED, FAILED
    order_id = Column(String, nullable=True)

class AppConfig(Base):
    __tablename__ = "app_config"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(String)
