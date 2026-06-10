from kiteconnect import KiteConnect

from datetime import datetime, timedelta

from app.consts import PREVIOUS_DAYS

def get_avg_volume(kite: KiteConnect, instrument_token, time_frame):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=PREVIOUS_DAYS)

    candles = kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval=time_frame,
        oi=True,
    )

    candles = candles[-20:]

    avg_volume = sum(c["volume"] for c in candles) / len(candles)

    return round(avg_volume, 2)


def get_quote_data(kite: KiteConnect, symbol: str):
    pre = 'NFO'
    if 'SENSEX' in symbol:
        pre = 'BFO'

    quote = kite.quote([f"{pre}:{symbol}"])

    return quote[f"{pre}:{symbol}"]


def calculate_pcr(ce_oi, pe_oi):
    if ce_oi == 0:
        return None

    return round(pe_oi / ce_oi, 2)


def get_option_metrics(kite: KiteConnect, ce_symbol, ce_token, pe_symbol, pe_token, time_frame):
    ce_quote = get_quote_data(kite, ce_symbol)

    pe_quote = get_quote_data(kite, pe_symbol)

    ce_avg_volume = get_avg_volume(kite, ce_token, time_frame)

    pe_avg_volume = get_avg_volume(kite, pe_token, time_frame)

    ce_oi = ce_quote["oi"]
    pe_oi = pe_quote["oi"]

    return {
        "CE": {
            "symbol": ce_symbol,
            "oi": ce_oi,
            "volume": ce_quote["volume"],
            "avg_20_volume": ce_avg_volume,
        },
        "PE": {
            "symbol": pe_symbol,
            "oi": pe_oi,
            "volume": pe_quote["volume"],
            "avg_20_volume": pe_avg_volume,
        },
        "PE_OI": ce_oi,
        "CE_OI": pe_oi
    }
