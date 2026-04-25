from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import asyncio

from app.db.database import get_db
from app.db.models import TradeLog, AppConfig
from app.services.strategy_engine import strategy_engine
from app.services.market_feed import feed_service
from app.services.dhan_manager import dhan_manager

api_router = APIRouter()

@api_router.get("/status")
async def get_bot_status(db: AsyncSession = Depends(get_db)):
    return {
        "bot_active": strategy_engine.is_active,
        "dhan_connected": dhan_manager.connected,
        "live_price": feed_service.latest_ltp,
        "trades_today": strategy_engine.trades_today,
        "max_trades": 3
    }

@api_router.post("/toggle_bot")
async def toggle_bot():
    if not strategy_engine.is_active:
        strategy_engine.is_active = True
        if not feed_service.running:
            await feed_service.start_feed()
            feed_service.subscribe(strategy_engine.ingest_tick)
    else:
        strategy_engine.is_active = False
        feed_service.running = False
        # Stop feed client gracefully in real scenario
        
    return {"status": "success", "bot_active": strategy_engine.is_active}

@api_router.get("/trades")
async def get_trades(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TradeLog).order_by(TradeLog.timestamp.desc()))
    trades = result.scalars().all()
    return trades

@api_router.get("/positions")
async def get_positions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TradeLog).where(TradeLog.status == "OPEN"))
    positions = result.scalars().all()
    
    # Calculate unrealized PNL
    res = []
    for pos in positions:
        # Mock calculation. In reality we get LTP for the specific Option from another feed
        pnl = (feed_service.latest_ltp - pos.entry_price) * pos.quantity if pos.entry_price > 0 else 0
        res.append({
            "id": pos.id,
            "symbol": pos.symbol,
            "strike": pos.strike_price,
            "type": pos.option_type,
            "quantity": pos.quantity,
            "entry_price": pos.entry_price,
            "unrealized_pnl": pnl
        })
    return res

@api_router.post("/config/keys")
async def update_keys(client_id: str, access_token: str, db: AsyncSession = Depends(get_db)):
    from app.config import settings
    # For demo we update runtime settings. In production, securely encrypt in DB.
    settings.DHAN_CLIENT_ID = client_id
    settings.DHAN_ACCESS_TOKEN = access_token
    # Try reconnecting Dhan manager
    dhan_manager.get_client()
    return {"status": "success", "connected": dhan_manager.connected}
