import pandas as pd

INSTRUMENTS_FILE = "app/db/instruments.csv"


def get_atm_itm_otm(index_name: str, spot_price: float):
    """
    Args:
        index_name: NIFTY or SENSEX
        spot_price: Current spot price

    Returns:
        ATM, ITM, OTM CE/PE contracts
    """

    df = pd.read_csv(INSTRUMENTS_FILE)

    df = df[
        (df["name"] == index_name)
        & (df["instrument_type"].isin(["CE", "PE"]))
    ].copy()

    df["expiry"] = pd.to_datetime(df["expiry"])

    nearest_expiry = (
        df["expiry"]
        .sort_values()
        .iloc[0]
    )

    df = df[
        df["expiry"] == nearest_expiry
    ]

    step = 50 if index_name == "NIFTY" else 100

    atm_strike = round(spot_price / step) * step

    strikes = {
        # "ITM_3": atm_strike - (step * 3),
        # "ITM_2": atm_strike - (step * 2),
        "ITM_1": atm_strike - step,
        "ATM": atm_strike,
        "OTM_1": atm_strike + step,
        # "OTM_2": atm_strike + (step * 2),
        # "OTM_3": atm_strike + (step * 2),
    }

    result = {
        "index": index_name,
        "spot_price": spot_price,
        "expiry": nearest_expiry.strftime("%Y-%m-%d"),
        "options": {}
    }

    for strike_type, strike in strikes.items():

        ce = df[
            (df["strike"] == strike)
            & (df["instrument_type"] == "CE")
        ]

        pe = df[
            (df["strike"] == strike)
            & (df["instrument_type"] == "PE")
        ]

        result["options"][strike_type] = {
            "strike": strike,
            "CE": None if ce.empty else {
                "symbol": ce.iloc[0]["tradingsymbol"],
                "token": int(ce.iloc[0]["instrument_token"])
            },
            "PE": None if pe.empty else {
                "symbol": pe.iloc[0]["tradingsymbol"],
                "token": int(pe.iloc[0]["instrument_token"])
            }
        }

    return result