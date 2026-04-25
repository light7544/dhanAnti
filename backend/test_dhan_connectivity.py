"""
Dhan API Connectivity Test
Tests: Client init, Fund Limits, Order List, Holdings
"""
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

from app.services.dhan_manager import dhan_manager
from app.config import settings
import logging
from pprint import pprint
from datetime import datetime

logging.basicConfig(level=logging.INFO)

PASS = "[PASS]"
FAIL = "[FAIL]"

def main():
    print("=" * 60)
    print("  PROJECT ANTIGRAVITY - Dhan API Connectivity Report")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ---------- 1. Credentials check ----------
    print("\n[1/5] Credentials loaded from .env")
    cid = settings.DHAN_CLIENT_ID
    tok = settings.DHAN_ACCESS_TOKEN
    print(f"  Client ID : {cid[:4]}...{cid[-4:] if len(cid) > 8 else cid}")
    print(f"  Token     : {tok[:20]}...{tok[-10:] if len(tok) > 30 else tok}")
    creds_ok = bool(cid and tok)
    print(f"  Status    : {PASS if creds_ok else FAIL}")
    if not creds_ok:
        print("\n  WARNING: Missing credentials - cannot proceed. Check .env file.")
        return

    # ---------- 2. Client initialization ----------
    print("\n[2/5] Initializing DhanHQ client")
    client = dhan_manager.get_client()
    init_ok = client is not None
    print(f"  Status    : {PASS if init_ok else FAIL}")
    if not init_ok:
        print("  WARNING: Client failed to initialize.")
        return

    # ---------- 3. Fund Limits (lightweight ping) ----------
    print("\n[3/5] Fetching Fund Limits (API ping)")
    try:
        funds = client.get_fund_limits()
        print(f"  Response  :")
        pprint(funds, indent=4, width=80)
        fund_ok = isinstance(funds, dict) and funds.get("status", "").lower() != "failure"
        print(f"  Status    : {PASS if fund_ok else FAIL}")
        if not fund_ok:
            print(f"  Remarks   : {funds.get('remarks', 'N/A')}")
    except Exception as e:
        fund_ok = False
        print(f"  Exception : {e}")
        print(f"  Status    : {FAIL}")

    # ---------- 4. Order list ----------
    print("\n[4/5] Fetching Order List")
    try:
        orders = client.get_order_list()
        print(f"  Response  :")
        pprint(orders, indent=4, width=80)
        order_ok = isinstance(orders, dict)
        print(f"  Status    : {PASS if order_ok else FAIL}")
    except Exception as e:
        order_ok = False
        print(f"  Exception : {e}")
        print(f"  Status    : {FAIL}")

    # ---------- 5. Positions ----------
    print("\n[5/5] Fetching Positions")
    try:
        positions = client.get_positions()
        print(f"  Response  :")
        pprint(positions, indent=4, width=80)
        pos_ok = isinstance(positions, dict)
        print(f"  Status    : {PASS if pos_ok else FAIL}")
    except Exception as e:
        pos_ok = False
        print(f"  Exception : {e}")
        print(f"  Status    : {FAIL}")

    # ---------- Summary ----------
    results = {
        "Credentials": creds_ok,
        "Client Init": init_ok,
        "Fund Limits": fund_ok,
        "Order List": order_ok,
        "Positions": pos_ok,
    }
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for name, ok in results.items():
        print(f"  {name:15s} : {PASS if ok else FAIL}")
    
    all_ok = all(results.values())
    print("\n" + ("  >>> ALL CHECKS PASSED - Algo is connected to Dhan!" if all_ok
                  else "  >>> Some checks failed - review output above."))
    print("=" * 60)

if __name__ == "__main__":
    main()
