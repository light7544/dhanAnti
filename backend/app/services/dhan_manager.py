from dhanhq import dhanhq, orderupdate
from app.config import settings
import threading
import logging

logger = logging.getLogger(__name__)

class DhanManager:
    def __init__(self):
        self.dhan = None
        self.order_client = None
        self.connected = False
        self.order_callbacks = []

    def get_client(self):
        if not self.dhan and settings.DHAN_CLIENT_ID and settings.DHAN_ACCESS_TOKEN:
            self.dhan = dhanhq(
                settings.DHAN_CLIENT_ID,
                settings.DHAN_ACCESS_TOKEN
            )
            self.connected = True
        return self.dhan

    def place_market_order(self, security_id: str,
                           transaction_type: str,
                           quantity: int): # Default handled by strategy engine now
        client = self.get_client()
        if not client:
            return {"status": "failed", "remarks": "Dhan Client not initialized"}
        
        try:
            logger.info(f"Placing {transaction_type} order for security_id {security_id}")
            res = client.place_order(
                security_id=str(security_id),
                exchange_segment=client.MCX if settings.EXCHANGE_SEGMENT == "MCX" else client.NSE_FNO,
                transaction_type=client.BUY if transaction_type == "BUY" else client.SELL,
                quantity=quantity,
                order_type=client.MARKET,
                product_type=client.INTRA,
                price=0
            )
            return res
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"status": "error", "error": str(e)}

    def start_order_socket(self, on_message_callback=None):
        if not settings.DHAN_CLIENT_ID or not settings.DHAN_ACCESS_TOKEN:
            return
            
        if on_message_callback:
            self.order_callbacks.append(on_message_callback)

        def _on_message(ws, message):
            for cb in self.order_callbacks:
                cb(message)

        # Assuming OrderSocket takes an on_message callback, if not, we try passing it or wrapping it.
        # User snippet: order_client = orderupdate.OrderSocket(client_id, access_token)
        # order_client.connect_to_dhan_websocket_sync()
        self.order_client = orderupdate.OrderSocket(
            settings.DHAN_CLIENT_ID, 
            settings.DHAN_ACCESS_TOKEN
        )
        
        # We might need to monkey-patch or attach to OrderSocket based on dhanhq implementation,
        # but typical implementation allows passing callbacks or overriding.
        if hasattr(self.order_client, 'on_message'):
             self.order_client.on_message = _on_message
             
        # Run sync connect in a background thread to avoid blocking FastAPI
        def run_sync_socket():
            logger.info("Connecting to Dhan Order WebSocket...")
            try:
                self.order_client.connect_to_dhan_websocket_sync()
            except Exception as e:
                logger.error(f"Order Socket Error: {e}")

        t = threading.Thread(target=run_sync_socket, daemon=True)
        t.start()
        
dhan_manager = DhanManager()
