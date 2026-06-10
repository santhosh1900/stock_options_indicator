from kiteconnect import KiteConnect
from app.config import KITE_API_KEY

kite = KiteConnect(api_key=KITE_API_KEY)

def get_login_url():
    return kite.login_url()

def generate_session(request_token, api_secret):
    return kite.generate_session(
        request_token=request_token,
        api_secret=api_secret
    )