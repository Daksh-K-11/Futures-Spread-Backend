# token_store.py

import json

TOKEN_FILE = "kite_token.json"

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": token}, f)

def load_token():
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)["access_token"]
    except:
        return None