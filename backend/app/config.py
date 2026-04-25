from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Dhan API
    DHAN_CLIENT_ID: str = ""
    DHAN_ACCESS_TOKEN: str = ""
    
    # DB
    DATABASE_URL: str = "sqlite+aiosqlite:///./antigravity.db"
    
    # Trading logic
    INSTRUMENT_NAME: str = "SILVER"
    UNDERLYING_SECURITY_ID: str = "11915" # Mock/Placeholder for Silver Active Future
    EXCHANGE_SEGMENT: str = "MCX" # MCX for commodity
    STRIKE_GAP: int = 500
    LOT_QTY: int = 1 # 1 lot (Silver Micro=1, Silver Mini=5)
    
    MAX_TRADES_PER_DAY: int = 3
    PROFIT_TARGET_POINTS: float = 12.0
    STOP_LOSS_POINTS: float = 6.0
    EMA_FAST: int = 9
    EMA_SLOW: int = 20
    
    # Frontend config
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
