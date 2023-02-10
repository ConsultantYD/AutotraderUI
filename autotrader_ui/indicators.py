import pandas as pd
import pandas_ta as ta

pandas_ta_col_converter = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "volume": "Volume"
}


def get_rsi(df: pd.DataFrame, length: int = 14, scalar: int = 100,
            drift: int = 1) -> pd.DataFrame:
    """RSI Calculation.

    Args:
        df (pd.DataFrame): Data.
    """
    df = df.copy()
    df = df.rename(pandas_ta_col_converter, axis=1)
    rsi = df.ta.rsi(length=length, scalar=scalar, drift=drift)

    return rsi


def get_macd(df: pd.DataFrame, fast: int = 12,
             slow: int = 26, signal: int = 9) -> tuple:
    """Calculates MACD.

    Args:
        df (pd.DataFrame): Data.
        fast (int, optional): Period of slow ema calculation. Defaults to 12.
        slow (int, optional): Period of fast ema calculation. Defaults to 26.
        signal (int, optional): Period of ema calculation on macd line. Defaults to 9.
    """

    df = df.copy()
    df = df.rename(pandas_ta_col_converter, axis=1)
    macd_df = df.ta.macd(fast=fast, slow=slow, signal=signal)

    macd = macd_df.iloc[:, 0]
    macd_signal = macd_df.iloc[:, 2]

    return macd, macd_signal


def get_stochastic(df: pd.DataFrame, k: int = 14, d: int = 3, smooth_k: int = 3,
                   mamode: str = 'sma', offset: int = 0) -> tuple:
    """Stochastic (STOCH)

    The Stochastic Oscillator (STOCH) was developed by George Lane in the 1950's.
    He believed this indicator was a good way to measure momentum because changes in
    momentum precede changes in price.
    It is a range-bound oscillator with two lines moving between 0 and 100.
    The first line (%K) displays the current close in relation to the period's
    high/low range. The second line (%D) is a Simple Moving Average of the %K line.
    The most common choices are a 14 period %K and a 3 period SMA for %D.
    Sources:
        https://www.tradingview.com/wiki/Stochastic_(STOCH)
        https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=332&Name=KD_-_Slow
    Calculation:
        Default Inputs:
            k=14, d=3, smooth_k=3
        SMA = Simple Moving Average
        LL  = low for last k periods
        HH  = high for last k periods
        STOCH = 100 * (close - LL) / (HH - LL)
        STOCHk = SMA(STOCH, smooth_k)
        STOCHd = SMA(FASTK, d)

    Args:
        df (pd.DataFrame): Data.
        k (int, optional): The Fast %K period. Defaults to 14.
        d (int, optional): The Slow %K period. Defaults to 3.
        smooth_k (int, optional): The Slow %D period. Defaults to 3.
        mamode (str, optional): See ```help(ta.ma)```. Defaults to 'sma'.
        offset (int, optional): How many periods to offset the result. Defaults to 0.
    """

    df = df.copy()
    df = df.rename(pandas_ta_col_converter, axis=1)
    stoch = df.ta.stoch(k=k, d=d, smooth_k=smooth_k,
                        mamode=mamode, offset=offset)

    stoch_k = stoch.iloc[:, 0]
    stoch_d = stoch.iloc[:, 1]

    return stoch_k, stoch_d


def get_ma(df: pd.DataFrame, length: int = 30, offset: int = 0) -> pd.DataFrame:
    """Calculates a MA.

    Args:
        df (pd.DataFrame): Data.
        length (int, optional): Its period. Defaults to 10.
        offset (int, optional): How many periods to offset the results. Defaults to 0.
    """

    df = df.copy()
    df = df.rename(pandas_ta_col_converter, axis=1)
    ma = df.ta.sma(length=length, offset=offset)

    return ma
