from app.services.dhan_manager import dhan_manager
from app.config import settings
from datetime import datetime, timedelta
import pydantic
import logging

logger = logging.getLogger(__name__)

class OptionsCalculator:
    def __init__(self):
        self.index_symbol = settings.INSTRUMENT_NAME
        self.strike_gap = settings.STRIKE_GAP
        
    def get_upcoming_thursday_expiry(self):
        """Returns the upcoming Thursday formatted as YYYY-MM-DD"""
        today = datetime.now()
        # weekday(): Monday is 0, Thursday is 3
        days_ahead = 3 - today.weekday()
        if days_ahead < 0:
            # Target is next week's Thursday
            days_ahead += 7
            
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime("%Y-%m-%d")
        
    def calculate_atm_strike(self, spot_price: float):
        # Round to nearest 50 for Nifty
        val = spot_price / self.strike_gap
        val_rounded = round(val)
        return val_rounded * self.strike_gap

    def fetch_options_chain(self):
        client = dhan_manager.get_client()
        if not client:
            return None
            
        expiry_date = self.get_upcoming_thursday_expiry()
        
        try:
            # User constraint for Dhan API
            # For MCX Options: under_exchange_segment is generally MCX
            ex_seg = "MCX" if settings.EXCHANGE_SEGMENT == "MCX" else "IDX_I"
            opt_chain = client.option_chain(
                under_security_id=int(settings.UNDERLYING_SECURITY_ID),                       
                under_exchange_segment=ex_seg,
                expiry=expiry_date
            )
            return opt_chain
        except Exception as e:
            logger.error(f"Error fetching options chain: {e}")
            return None
        
    def find_ditm_security_id(self, spot_price: float, opt_type: str):
        atm = self.calculate_atm_strike(spot_price)
        
        # 3 strikes Deep In The Money
        if opt_type == "CE":
            # For Calls, DITM is strikes BELOW the spot
            target_strike = atm - (3 * self.strike_gap)
        elif opt_type == "PE":
            # For Puts, DITM is strikes ABOVE the spot
            target_strike = atm + (3 * self.strike_gap)
        else:
            return None

        # Fetch chain to map strike to security_id
        chain_response = self.fetch_options_chain()
        if not chain_response or "data" not in chain_response: # Adjust based on actual dhan response structure
            # Fallback mock for testing if api responds empty
            logger.warning(f"Using fallback security ID mapping for {target_strike} {opt_type}")
            return f"MOCK_{self.index_symbol}_{int(target_strike)}_{opt_type}"

        # Assuming chain_response contains a list of options with attributes
        data = chain_response.get("data", [])
        
        for option in data:
            if option.get('strike_price') == target_strike and option.get('option_type') == opt_type:
                return str(option.get('security_id'))
                
        # Fallback if strike not found
        logger.warning(f"Strike {target_strike} {opt_type} not found in chain. Using fallback security ID.")
        return f"{self.index_symbol}_{int(target_strike)}_{opt_type}"

options_calc = OptionsCalculator()
