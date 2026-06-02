from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.kite import kite
from app.core.config import settings
from app.core.token_manager import save_access_token
from app.core.token_store import save_token

router = APIRouter()

# -----------------------------------
# Login Route
# -----------------------------------

@router.get("/login")
def login():

    login_url = kite.login_url()

    return RedirectResponse(
        url=login_url
    )

# -----------------------------------
# Callback Route
# -----------------------------------

@router.get("/callback")
def callback(request_token: str):

    data = kite.generate_session(
        request_token,
        api_secret=settings.KITE_API_SECRET
    )

    access_token = data["access_token"]

    # Save token permanently
    save_access_token(access_token)

    # Set token in runtime
    save_token(access_token)
    kite.set_access_token(access_token)

    return {
        "success": True,
        "message": "Login successful",
        "access_token": access_token
    }