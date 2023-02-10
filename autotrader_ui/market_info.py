#import pandas_market_calendars as mcal
import datetime as dt
import pytz

MARKET_OPEN_HOURS = {
    "NYSE": {
        0: {"start": (14, 30), "end": (21, 0)},  # Monday
        1: {"start": (14, 30), "end": (21, 0)},
        2: {"start": (14, 30), "end": (21, 0)},
        3: {"start": (14, 30), "end": (21, 0)},
        4: {"start": (14, 30), "end": (21, 0)},
        5: {"start": (0, 0), "end": (0, 0)},
        6: {"start": (0, 0), "end": (0, 0)}
    },
    "NASDAQ": {
        0: {"start": (14, 30), "end": (21, 0)},  # Monday
        1: {"start": (14, 30), "end": (21, 0)},
        2: {"start": (14, 30), "end": (21, 0)},
        3: {"start": (14, 30), "end": (21, 0)},
        4: {"start": (14, 30), "end": (21, 0)},
        5: {"start": (0, 0), "end": (0, 0)},
        6: {"start": (0, 0), "end": (0, 0)}
    }
}

INSTRUMENT_MARKETS_DICT = {
    'AUD_CAD': 'NYSE',
    'XAU_USD': 'NYSE',
    'XAU_AUD': 'NYSE',
    'XAU_CAD': 'NYSE',
    'XAU_CHF': 'NYSE',
    'XAU_EUR': 'NYSE',
    'XAU_GBP': 'NYSE',
    'XAU_HKD': 'NYSE',
    'XAU_JPY': 'NYSE',
    'XAU_NZD': 'NYSE',
    'XAU_SGD': 'NYSE',
    'XAU_XAG': 'NYSE',
    'XAG_USD': 'NYSE',
    'XAG_AUD': 'NYSE',
    'XAG_CAD': 'NYSE',
    'XAG_CHF': 'NYSE',
    'XAG_EUR': 'NYSE',
    'XAG_GBP': 'NYSE',
    'XAG_HKD': 'NYSE',
    'XAG_JPY': 'NYSE',
    'XAG_NZD': 'NYSE',
    'XAG_SGD': 'NYSE',
    'USB10Y_USD': 'NYSE',
    'USB02Y_USD': 'NYSE',
    'USB05Y_USD': 'NYSE',
    'NAS100_USD': 'NYSE',
    'US2000_USD': 'NYSE',
    'SPX500_USD': 'NYSE',
    'USB30Y_USD': 'NYSE',
    'US30_USD': 'NYSE',
    'USD_CAD': 'NYSE',
    'USD_CHF': 'NYSE',
    'USD_CNH': 'NYSE',
    'USD_CZK': 'NYSE',
    'USD_DKK': 'NYSE',
    'USD_HKD': 'NYSE',
    'USD_HUF': 'NYSE',
    'USD_JPY': 'NYSE',
    'USD_MXN': 'NYSE',
    'USD_NOK': 'NYSE',
    'USD_PLN': 'NYSE',
    'USD_SEK': 'NYSE',
    'USD_SGD': 'NYSE',
    'USD_THB': 'NYSE',
    'USD_TRY': 'NYSE',
    'USD_ZAR': 'NYSE'
}

"""
def get_time_to_market_close(now: dt.datetime, instrument: str):

    now = pytz.utc.localize(now)

    if instrument in INSTRUMENT_MARKETS_DICT.keys():
        market = INSTRUMENT_MARKETS_DICT[instrument]
    else:
        raise ValueError("This market open and close isn't available yet")

    market_obj = mcal.get_calendar(market)
    schedule = market_obj.schedule(start_date=now, end_date=now)

    if schedule.empty:
        return 0
    else:
        market_open = schedule['market_open'].iloc[0]
        market_close = schedule['market_close'].iloc[0]

        if now <= market_open.to_pydatetime():
            return 0
        else:
            #diff_open = now - market_open.to_pydatetime()
            diff_close = market_close.to_pydatetime() - now
            minutes_close = diff_close.seconds / 60

            return minutes_close

def get_time_since_market_opening(now: dt.datetime, instrument: str):

    now = pytz.utc.localize(now)

    if instrument in INSTRUMENT_MARKETS_DICT.keys():
        market = INSTRUMENT_MARKETS_DICT[instrument]
    else:
        raise ValueError("This market open and close isn't available yet")

    market_obj = mcal.get_calendar(market)
    schedule = market_obj.schedule(start_date=now, end_date=now)

    if schedule.empty:
        return 0
    else:
        market_open = schedule['market_open'].iloc[0]
        market_close = schedule['market_close'].iloc[0]

        if now <= market_open.to_pydatetime():
            return 0
        else:
            diff_open = now - market_open.to_pydatetime()
            minutes_open = diff_open.seconds / 60

            return minutes_open
"""

if __name__ == '__main__':
    now = dt.datetime.utcnow()
    time_to_close = get_time_to_market_close(now, "AUD_CAD")
    time_since_open = get_time_since_market_opening(now, "AUD_CAD")
    print(f"Time to close: {time_to_close}")
    print(f"Time since open: {time_since_open}")
