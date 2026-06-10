from datetime import datetime, timedelta
import pandas as pd

from kiteconnect import KiteConnect

from app.consts import PREVIOUS_DAYS
from app.enums.symbols import TradeToken
from app.services.get_metrices import calculate_pcr, get_option_metrics
from app.services.json_db import get_auth, get_data_by_file_name, save_data_file_name
from app.config import KITE_API_KEY
from app.services.strike_finder import get_atm_itm_otm
from app.services.telegram import send_telegram_message


def get_kite():
    auth = get_auth()

    kite = KiteConnect(api_key=KITE_API_KEY)
    kite.set_access_token(auth["access_token"])

    return kite


def calculate_ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()


def get_min_data(instrument_token, time_frame):
    kite = get_kite()

    to_date = datetime.now()
    from_date = to_date - timedelta(days=PREVIOUS_DAYS)

    data = kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval=time_frame,
    )

    return pd.DataFrame(data)

def save_index_data(
    instrument_token: TradeToken,
    time_frame="5minute"
):
    df = get_min_data(instrument_token.value, time_frame)

    if df.empty:
        print(f"No data found for {instrument_token.name}")
        return []
    
    df["date"] = df["date"].astype(str)

    save_data_file_name(json_data=df.to_dict(orient="records"), file_name=instrument_token.name)

def get_index_data(instrument_token: TradeToken, time_frame):
    # savedData = get_data_by_file_name(file_name=instrument_token.name)

    # if savedData:
    #     return pd.DataFrame(savedData)

    # else:
    return get_min_data(instrument_token=instrument_token.value, time_frame=time_frame)


def get_ema_data(instrument_token: TradeToken, time_frame, req_type = 'cron'):

    df = get_index_data(instrument_token=instrument_token, time_frame=time_frame)

    if df.empty:
        return None

    df["ema_8"] = calculate_ema(df, 8)
    df["ema_13"] = calculate_ema(df, 13)

    if req_type == 'cron':
        return df

    # -----

    kite = get_kite()

    latest = df.iloc[-1]

    strike_data = get_atm_itm_otm(
        index_name=instrument_token.name,
        spot_price=round(float(latest["close"]), 2),
    )
    totalPeOI = 0
    totalCeOI = 0

    for strike_name, strike in strike_data["options"].items():

        strike["metrics"] = get_option_metrics(
            kite=kite,
            ce_symbol=strike["CE"]["symbol"],
            ce_token=strike["CE"]["token"],
            pe_symbol=strike["PE"]["symbol"],
            pe_token=strike["PE"]["token"],
            time_frame=time_frame
        )

        totalPeOI += strike["metrics"]['PE_OI']
        totalCeOI += strike["metrics"]['CE_OI']

        return {
            "datetime": str(latest["date"]),
            "close": round(float(latest["close"]), 2),
            # "strike": strike_data,
            "ema_8": round(float(latest["ema_8"]), 2),
            "ema_13": round(float(latest["ema_13"]), 2),
            "pcr": calculate_pcr(totalCeOI, totalPeOI)
        }

    # ------
