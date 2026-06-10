from kiteconnect import KiteConnect
import requests
import pandas as pd
from pathlib import Path
from io import StringIO

from app.services.market import get_kite

INSTRUMENT_URL = "https://api.kite.trade/instruments"
SAVE_PATH = Path("app/db/instruments.csv")


def get_spot_prices(kite: KiteConnect):
    quotes = kite.quote([
        "NSE:NIFTY 50",
        "BSE:SENSEX"
    ])

    nifty_price = quotes["NSE:NIFTY 50"]["last_price"]
    sensex_price = quotes["BSE:SENSEX"]["last_price"]

    return nifty_price, sensex_price


def get_relevant_expiries(df, index_name):
    expiries = sorted(
        pd.to_datetime(
            df[
                (df["name"] == index_name)
                & (df["expiry"].notna())
            ]["expiry"]
        ).dt.date.unique()
    )

    today = pd.Timestamp.today().date()

    future_expiries = [
        expiry
        for expiry in expiries
        if expiry >= today
    ]

    if not future_expiries:
        raise Exception(
            f"No future expiry found for {index_name}"
        )

    weekly_expiry = future_expiries[0]

    monthly_expiry = weekly_expiry

    for expiry in future_expiries:
        if (
            expiry.month != (expiry + pd.Timedelta(days=7)).month
        ):
            monthly_expiry = expiry
            break

    return weekly_expiry, monthly_expiry


def download_instruments():

    kite = get_kite()

    nifty_price, sensex_price = get_spot_prices(kite)

    response = requests.get(
        INSTRUMENT_URL,
        timeout=60
    )

    response.raise_for_status()

    df = pd.read_csv(
        StringIO(response.text)
    )

    # NIFTY ±1000
    nifty_min = nifty_price - 1000
    nifty_max = nifty_price + 1000

    # SENSEX ±1500
    sensex_min = sensex_price - 1500
    sensex_max = sensex_price + 1500

    nifty_weekly, nifty_monthly = get_relevant_expiries(
        df,
        "NIFTY"
    )

    sensex_weekly, sensex_monthly = get_relevant_expiries(
        df,
        "SENSEX"
    )

    expiry_series = pd.to_datetime(
        df["expiry"]
    ).dt.date

    nifty_df = df[
        (df["name"] == "NIFTY")
        & (df["segment"] == "NFO-OPT")
        & (df["strike"] >= nifty_min)
        & (df["strike"] <= nifty_max)
        & (
            (expiry_series == nifty_weekly)
            | (expiry_series == nifty_monthly)
        )
    ]

    sensex_df = df[
        (df["name"] == "SENSEX")
        & (df["segment"] == "BFO-OPT")
        & (df["strike"] >= sensex_min)
        & (df["strike"] <= sensex_max)
        & (
            (expiry_series == sensex_weekly)
            | (expiry_series == sensex_monthly)
        )
    ]

    filtered_df = pd.concat(
        [nifty_df, sensex_df],
        ignore_index=True
    )

    SAVE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    filtered_df.to_csv(
        SAVE_PATH,
        index=False
    )

    print("=" * 50)
    print(f"NIFTY Spot : {nifty_price}")
    print(f"SENSEX Spot: {sensex_price}")
    print()
    print(f"NIFTY Weekly Expiry : {nifty_weekly}")
    print(f"NIFTY Monthly Expiry: {nifty_monthly}")
    print()
    print(f"SENSEX Weekly Expiry : {sensex_weekly}")
    print(f"SENSEX Monthly Expiry: {sensex_monthly}")
    print()
    print(f"Saved {len(filtered_df)} instruments")
    print(f"File: {SAVE_PATH}")
    print("=" * 50)