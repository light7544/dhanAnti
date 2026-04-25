import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.dhan_manager import dhan_manager
from app.services.options_calculator import options_calc
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_order():
    client = dhan_manager.get_client()
    if not client:
        print("Failed to initialize Dhan client. Check .env variables.")
        return

    print("Fetching option chain for Silver...")
    # Mocking spot price as 75000 for Silver for now to find an ATM.
    # We should ideally fetch real LTP but let's see if we can get a security ID first.
    atm_strike = options_calc.calculate_atm_strike(75000)
    print(f"Calculated ATM Strike based on 75000: {atm_strike}")
    
    security_id = options_calc.find_ditm_security_id(75000, "CE")
    print(f"Target Security ID for DITM CE: {security_id}")
    
    # Check if security ID is valid 
    if str(security_id).startswith("MOCK_") or str(security_id).startswith("SILVER_"):
        print("WARNING: Using a mocked security ID. Order placement will likely fail. Is Silver option chain query succeeding?")
    else:
        print(f"Found valid security ID from chain: {security_id}")

    try:
        # Ask user for confirmation or just fire it as it's what they asked for
        print(f"Attempting to place MARKET BUY order for 1 quantity of {security_id}...")
        res = dhan_manager.place_market_order(
            security_id=str(security_id),
            transaction_type="BUY",
            quantity=1
        )
        print("Order Response:")
        pprint(res)
    except Exception as e:
        print(f"Exception during order placement: {e}")

if __name__ == "__main__":
    test_order()
