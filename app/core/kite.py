from kiteconnect import KiteConnect
from app.core.config import settings
from app.core.token_store import load_token

kite = KiteConnect(
    api_key=settings.KITE_API_KEY
)

token = load_token()
if token:
    kite.set_access_token(token)