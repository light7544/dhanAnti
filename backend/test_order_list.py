import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.dhan_manager import dhan_manager
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_orders():
    client = dhan_manager.get_client()
    if not client:
        print("Failed to initialize Dhan client. Check .env variables.")
        return

    print("Fetching today's order list from Dhan API...")
    
    try:
        res = client.get_order_list()
        print("\n=== Order List Response ===")
        pprint(res)
    except Exception as e:
        print(f"\nException during get_order_list: {e}")

if __name__ == "__main__":
    check_orders()
