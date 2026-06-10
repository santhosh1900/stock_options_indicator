from fastapi import APIRouter
from app.enums.symbols import TradeToken
from app.enums.timeFrame import TimeFrames
from app.services.market import get_ema_data

router = APIRouter(prefix="/market")


@router.get("/nifty")
def nifty():
    return get_ema_data(TradeToken.NIFTY_4_MIN, TimeFrames.MIN_4.value, 'route')


@router.get("/sensex")
def sensex():
    return get_ema_data(TradeToken.SENSEX, TimeFrames.MIN_3.value, 'route')