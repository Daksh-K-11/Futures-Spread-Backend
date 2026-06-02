from dotenv import set_key
from app.core.token_store import save_token

ENV_FILE = ".env"

def save_access_token(token: str):
    
    save_token(token)

    # set_key(
    #     ENV_FILE,
    #     "KITE_ACCESS_TOKEN",
    #     token
    # )