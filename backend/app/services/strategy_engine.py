import pandas as pd
from datetime import datetime
import asyncio
from app.config import settings
from app.services.options_calculator import options_calc
from app.services.dhan_manager import dhan_manager

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import SessionLocal
from app.db.models import TradeLog
import logging

logger = logging.getLogger(__name__)

class StrategyEngine:
    def __init__(self):
        self.df = pd.DataFrame(columns=['timestamp', 'price'])
        self.trades_today = 0
        self.is_active = False
        self.active_trade = None # Dict storing current trade if any

    def init_order_socket(self):
        dhan_manager.start_order_socket(self._on_order_update)

    def _on_order_update(self, message):
        # Process live order updates from WebSocket Sync
        # e.g., tracking fill price, or manual tracking of hitting 10-12 target profit
        logger.debug(f"Order Update: {message}")
        if not self.active_trade:
             return
             
        # Example logic to match open trade with fill/update and calculate PnL 
        # based on Dhan's Order update message spec.
        pass

    async def ingest_tick(self, ltp: float):
        if not self.is_active:
            return

        # If we have an active trade, track target / stop-loss here as well (if not done via order updates entirely)
        if self.active_trade:
            await self._track_trade_progress(ltp)

        now = datetime.now()
        new_row = pd.DataFrame([{'timestamp': now, 'price': ltp}])
        self.df = pd.concat([self.df, new_row], ignore_index=True)

        # Keep last 100 points
        if len(self.df) > 100:
            self.df = self.df.tail(100)

        # Only check crossover if no active trade
        if not self.active_trade:
             await self._check_crossover(ltp)
             
    async def _track_trade_progress(self, current_spot: float):
        # MOCK Target and Stop-Loss tracking. 
        # In a real scenario, we track the specific Option's LTP via a separate feed subscription, 
        # or we rely on brackets placed directly through DhanAPI.
        # Since the user requested target 10-12 pts per trade and to use Order updates, 
        # we might need to subscribe to the entered option's security_id streaming.
        # For simplicity, we mock logic here pending option delta calculations.
        pass

    async def _check_crossover(self, spot_price: float):
        fast_period = settings.EMA_FAST
        slow_period = settings.EMA_SLOW
        
        if len(self.df) < max(fast_period, slow_period) + 1:
            return # Wait for enough data
            
        # Calculate EMA over the dataframe
        self.df['ema_fast'] = self.df['price'].ewm(span=fast_period, adjust=False).mean()
        self.df['ema_slow'] = self.df['price'].ewm(span=slow_period, adjust=False).mean()

        last_idx = self.df.index[-1]
        prev_idx = self.df.index[-2]
        
        curr_fast = self.df.at[last_idx, 'ema_fast']
        curr_slow = self.df.at[last_idx, 'ema_slow']
        prev_fast = self.df.at[prev_idx, 'ema_fast']
        prev_slow = self.df.at[prev_idx, 'ema_slow']

        # Bullish Crossover: Fast crosses above Slow
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            logger.info("Bullish Crossover detected! Preparing CE trade.")
            await self._execute_trade(spot_price, "CE")
            
        # Bearish Crossover: Fast crosses below Slow
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            logger.info("Bearish Crossover detected! Preparing PE trade.")
            await self._execute_trade(spot_price, "PE")

    async def _execute_trade(self, spot_price: float, opt_type: str):
        if self.trades_today >= settings.MAX_TRADES_PER_DAY:
            logger.info(f"Daily limit of {settings.MAX_TRADES_PER_DAY} trades reached. Not trading.")
            # Auto-stop bot if limit reached
            self.is_active = False 
            return

        security_id = options_calc.find_ditm_security_id(spot_price, opt_type)
        if not security_id:
            logger.error("Could not determine Security ID for DITM strike")
            return
            
        logger.info(f"Executing {opt_type} trade for security_id {security_id}")

        # Execute Order via Dhan
        order_res = dhan_manager.place_market_order(
            security_id=security_id,
            transaction_type="BUY",
            quantity=settings.LOT_QTY
        )
        
        # Log to DB
        async with SessionLocal() as db:
            trade = TradeLog(
                symbol=settings.INSTRUMENT_NAME,
                strike_price=options_calc.calculate_atm_strike(spot_price), # ATM as ref
                option_type=opt_type,
                transaction_type="BUY",
                quantity=settings.LOT_QTY,
                entry_price=spot_price, # Using spot as ref, real fill comes from order update
                status="OPEN"
            )
            db.add(trade)
            await db.commit()
            await db.refresh(trade)
            
            self.trades_today += 1
            self.active_trade = trade.id
            logger.info(f"Trade marked active. Trades today: {self.trades_today}/3")
            
strategy_engine = StrategyEngine()
