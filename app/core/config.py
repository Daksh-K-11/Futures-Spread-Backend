from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    KITE_API_KEY: str
    KITE_API_SECRET: str
    # KITE_ACCESS_TOKEN: str
    
    ZERODHA_USER_ID: str
    ZERODHA_PASSWORD: str
    ZERODHA_TOTP_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()