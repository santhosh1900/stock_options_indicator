from app.consts import EMA_MIN_GAP, EMA_SLOPE_MIN
from app.enums.signals import TradeSignal


def get_signal(df):

    if len(df) < 3:
        return None

    current = df.iloc[-1]
    previous = df.iloc[-2]

    # ----------------------------
    # EMA values
    # ----------------------------

    current_ema8 = current["ema_8"]
    current_ema13 = current["ema_13"]

    previous_ema8 = previous["ema_8"]
    previous_ema13 = previous["ema_13"]

    # ----------------------------
    # EMA Gap
    # ----------------------------

    ema_gap = abs(current_ema8 - current_ema13)

    # ----------------------------
    # EMA Slope
    # ----------------------------

    ema8_slope = current_ema8 - previous_ema8

    # ----------------------------
    # Candle Color
    # ----------------------------

    previous_green = current["open"] > previous["open"]

    previous_red = current["open"] < previous["open"]

    current_green = current["close"] > current["open"]

    current_red = current["close"] < current["open"]

    # ----------------------------
    # Breakout Confirmation
    # ----------------------------

    bullish_breakout = current["high"] > previous["close"]

    bearish_breakdown = current["low"] < previous["close"]

    # ----------------------------
    # Bullish Cross
    # ----------------------------

    bullish_cross = (
        previous_ema8 <= previous_ema13
        and current_ema8 > current_ema13
        # and ema_gap >= EMA_MIN_GAP
        # and ema8_slope >= EMA_SLOPE_MIN
    )

    # ----------------------------
    # Bearish Cross
    # ----------------------------

    bearish_cross = (
        previous_ema8 >= previous_ema13
        and current_ema8 < current_ema13
        # and ema_gap >= EMA_MIN_GAP
        # and ema8_slope <= -EMA_SLOPE_MIN
    )

    # ----------------------------
    # BUY Signal
    # ----------------------------

    if bullish_cross and previous_green and current_green and bullish_breakout:

        return TradeSignal.BUY.value

    # ----------------------------
    # SELL Signal
    # ----------------------------

    if bearish_cross and previous_red and current_red and bearish_breakdown:

        return TradeSignal.SELL.value

    return None
