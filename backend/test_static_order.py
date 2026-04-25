import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.dhan_manager import dhan_manager
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_static_order():
    client = dhan_manager.get_client()
    if not client:
        print("Failed to initialize Dhan client. Check .env variables.")
        return

    print("Attempting to place a static INTRA order for Reliance (Security ID: 2885, NSE_EQ)...")
    
    try:
        res = client.place_order(
            security_id="2885",   # Reliance NSE Equity
            exchange_segment=client.NSE,
            transaction_type=client.BUY,
            quantity=1,
            order_type=client.MARKET,
            product_type=client.CNC, # CNC/Delivery valid for AMO
            price=0,
            after_market_order=True,
            amo_time='OPEN' # Dhan AMO parameter
        )
        print("\n=== Order Response ===")
        pprint(res)
    except Exception as e:
        print(f"\nException during order placement: {e}")

if __name__ == "__main__":
    test_static_order()
