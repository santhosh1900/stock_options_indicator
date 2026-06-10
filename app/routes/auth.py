from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.services.zerodha import (
    get_login_url,
    generate_session
)
from app.services.json_db import (
    save_auth,
    get_auth
)
from app.config import KITE_API_SECRET

router = APIRouter()


@router.get("/login")
def login():
    return RedirectResponse(url= get_login_url())


@router.get("/login/callback")
def callback(request_token: str):

    session = generate_session(
        request_token,
        KITE_API_SECRET
    )

    save_auth(session)

    return {
        "message": "Login successful",
        "user_id": session["user_id"],
        "user_name": session["user_name"]
    }


@router.get("/token")
def token():
    return get_auth()