from dhanhq import marketfeed
from app.config import settings
import asyncio
import logging
import threading

logger = logging.getLogger(__name__)

class MarketFeedService:
    def __init__(self):
        self.feed_client = None
        self.running = False
        self.latest_ltp = 0.0
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def _on_connect(self, instance):
        logger.info("Market feed connected!")
        
    def _on_message(self, instance, message):
        # Extract LTP using dhanhq marketfeed structure
        try:
            if isinstance(message, dict) and "LTP" in message:
                ltp = float(message["LTP"])
                self.latest_ltp = ltp
                
                # Notify subscribers asynchronously safely
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    for cb in self.subscribers:
                        asyncio.run_coroutine_threadsafe(cb(ltp), loop)
        except Exception as e:
            logger.error(f"Error in on_message: {e}")
                
    def _on_error(self, instance, exception):
        logger.error(f"Market feed error: {exception}")

    def _on_close(self, instance):
        logger.info("Market feed closed")
        self.running = False

    def start_feed(self):
        if not settings.DHAN_CLIENT_ID or not settings.DHAN_ACCESS_TOKEN:
            logger.error("Missing Dhan configuration for Market feed")
            return
            
        # Connect to requested instrument
        ex_seg = marketfeed.MCX if settings.EXCHANGE_SEGMENT == "MCX" else marketfeed.IDX
        instruments = [(ex_seg, settings.UNDERLYING_SECURITY_ID, marketfeed.Quote)]
        
        self.feed_client = marketfeed.DhanFeed(
            client_id=settings.DHAN_CLIENT_ID,
            access_token=settings.DHAN_ACCESS_TOKEN,
            instruments=instruments,
            version="v2",
            on_connect=self._on_connect,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self.running = True
        
        # DhanFeed connect is usually blocking/sync or requires a background thread
        # We run it in a daemon thread so it runs in background
        def run_feed():
            try:
                self.feed_client.connect()
            except Exception as e:
                logger.error(f"Error starting feed: {e}")
                self.running = False

        t = threading.Thread(target=run_feed, daemon=True)
        t.start()

feed_service = MarketFeedService()
