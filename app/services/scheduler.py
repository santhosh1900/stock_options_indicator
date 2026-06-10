from datetime import datetime, time
from threading import Lock
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from app.enums.symbols import TradeToken
from app.enums.timeFrame import TimeFrames
from app.services.instrument_loader import download_instruments
from app.services.market import get_ema_data
from app.services.signal import get_signal
from app.services.telegram import send_telegram_message

# -----------------------
# Globals
# -----------------------

scheduler = BackgroundScheduler()

scan_lock = Lock()

IST = ZoneInfo("Asia/Kolkata")

last_processed_candle = {
    TradeToken.NIFTY.name: None,
    TradeToken.SENSEX.name: None,
    TradeToken.NIFTY_4_MIN.name: None,
}

last_signal = {
    TradeToken.NIFTY.name: None,
    TradeToken.SENSEX.name: None,
    TradeToken.NIFTY_4_MIN.name: None,
}


# -----------------------
# Helpers
# -----------------------


def now_ist():
    return datetime.now(IST)


def is_market_open():

    current_time = now_ist().time()

    return time(9, 30) <= current_time <= time(15, 30)


def is_valid_candle(token: TradeToken, candle_time):

    minute = candle_time.minute

    if token == TradeToken.NIFTY:
        return minute % 5 == 0

    if token == TradeToken.SENSEX:
        return minute % 3 == 0

    if token == TradeToken.NIFTY_4_MIN:
        return True

    return False


# -----------------------
# Scanner
# -----------------------


def run_scan(token: TradeToken, time_frame: TimeFrames):

    with scan_lock:

        try:

            if not is_market_open():
                return

            print(
                f"[{now_ist()}] " f"{token.name} - {time_frame.name} function started"
            )

            df = get_ema_data(instrument_token=token, time_frame=time_frame.value)

            if df is None or df.empty:
                return

            latest = df.iloc[-1]

            candle_time = latest["date"]

            if not is_valid_candle(token, candle_time):
                return

            candle_key = str(candle_time)

            if candle_key == last_processed_candle[token.name]:
                return

            last_processed_candle[token.name] = candle_key

            current = df.iloc[-1]
            previous = df.iloc[-2]

            # ----------------------------
            # EMA values
            # ----------------------------

            current_ema8 = current["ema_8"]
            current_ema13 = current["ema_13"]

            previous_ema8 = previous["ema_8"]
            previous_ema13 = previous["ema_13"]

            print(
                f"[{now_ist()}] "
                f"{token.name} - {time_frame.name} current 8 ema = {current_ema8} and current 13 ema {current_ema13}"
            )
            print(
                f"[{now_ist()}] "
                f"{token.name} - {time_frame.name} previous 8 ema = {previous_ema8} and previous 13 ema {previous_ema13}"
            )

            signal = get_signal(df)

            print(f"[{now_ist()}] " f"{token.name} - {time_frame.name} checked")

            if not signal:
                return

            if signal == last_signal[token.name]:
                return

            last_signal[token.name] = signal

            print(f"\n{'=' * 50}")

            print(f"{token.name} " f"SIGNAL : {signal}")

            print(f"PRICE : " f"{latest['close']}")

            print(f"CANDLE : " f"{candle_time}")

            print(f"{'=' * 50}\n")

            telegramMessage = f"""
                {token.name} SIGNAL = {signal}
                Time frame = {time_frame.value}
                Nifty Current Price : " f"{latest['close']}
            """

            send_telegram_message(telegramMessage)

            # TODO:
            # save paper trade
            # save signal to json
            # send telegram alert

        except Exception as e:

            print(f"{token.name} ERROR: {e}")


# -----------------------
# NIFTY
# -----------------------


def run_nifty_scan():

    run_scan(token=TradeToken.NIFTY, time_frame=TimeFrames.MIN_5)


def run_nifty_scan_4_min():

    run_scan(token=TradeToken.NIFTY_4_MIN, time_frame=TimeFrames.MIN_4)


# -----------------------
# SENSEX
# -----------------------


def run_sensex_scan():

    run_scan(token=TradeToken.SENSEX, time_frame=TimeFrames.MIN_3)


# -----------------------
# Scheduler Jobs
# -----------------------

scheduler.add_job(
    run_nifty_scan,
    trigger="cron",
    day_of_week="mon-fri",
    minute="0,5,10,15,20,25,30,35,40,45,50,55",
    second=3,
    id="nifty_scanner_5min",
    replace_existing=True,
)

scheduler.add_job(
    run_nifty_scan_4_min,
    trigger="cron",
    day_of_week="mon-fri",
    minute="3,7,11,15,19,23,27,31,35,39,43,47,51,55,59",
    second=3,
    id="nifty_scanner_4min",
    replace_existing=True,
)

scheduler.add_job(
    run_sensex_scan,
    trigger="cron",
    day_of_week="mon-fri",
    minute="0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57",
    second=3,
    id="sensex_scanner",
    replace_existing=True,
)

scheduler.add_job(
    download_instruments,
    trigger="cron",
    day_of_week="mon-fri",
    hour=9,
    minute=0,
    id="instruments_loader",
    replace_existing=True,
)
