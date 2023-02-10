#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Data Utility Functions.

Todo:
    * ...
"""

# Built-in modules
import datetime as dt

# Third-party modules
from autotrader_ui.tpqoa import tpqoa
import yfinance as yf

# Local modules

def get_historical_data(source: str = 'oanda', data_kwargs: dict = {}):

    # Define API based on selected source
    if source.lower() == 'oanda':
        data = get_oanda_data(**data_kwargs)

    elif source.lower() == 'yahoo':
        data = get_yahoo_data(**data_kwargs)

    return data

def get_oanda_instruments(config: str = "oanda.cfg"):
    api = tpqoa(config)
    instruments = api.get_instruments()
    return instruments

def get_spread(instrument: str, config: str = "oanda.cfg"):
    api = tpqoa(config)
    bid, ask = api.get_bid_ask(instrument)
    if ask <= bid:
        err = f"Warning, weird values for bid and ask. bid: {bid}, ask: {ask}"
        raise RuntimeError(err)
    return ask - bid

def get_positions(config: str = "oanda.cfg"):
    api = tpqoa(config)
    positions = api.get_positions()
    return positions

def get_oanda_data(instrument: str = 'SPX500_USD',
                   start: str = "2022-05-01 10:00:00",
                   end: str = "2021-08-23 11:00:00",
                   granularity: str = "M1",
                   price: str = "M",
                   config: str = "oanda.cfg"):
    """Gets data using the OANDA API.

    Args:
        instrument (str, optional): Quantity of interest to retrieve. Defaults to "EUR_USD".
        start (str, optional): Start date. Defaults to "2020-08-10".
        end (str, optional): End date. Defaults to "2020-08-12".
        granularity (str, optional): Time series granularity. Defaults to "M1".
        price (str, optional): Price. Defaults to "M".

    Returns:
        _type_: _description_
    """

    api = tpqoa(config)
    data = api.get_history(instrument, start, end, granularity, price)
    return data

def get_yahoo_data(instrument: str = 'AAPL',
                   start: str = (dt.datetime.utcnow() -
                                 dt.timedelta(days=2)).strftime("%Y-%m-%d"),
                   end: str = dt.datetime.utcnow().strftime("%Y-%m-%d"),
                   granularity: str = "M1"):
    """Gets data using the Yahoo Finance API.

    Args:
        instrument (str, optional): Quantity of interest to retrieve. Defaults to "EUR_USD".
        start (str, optional): Start date. Defaults to "2020-08-10".
        end (str, optional): End date. Defaults to "2020-08-12".
        granularity (str, optional): Time series granularity. Defaults to "M1".

    Returns:
        _type_: _description_
    """

    interval_dict = {
        "M1": "1m",
        "M2": "2m",
        "M5": "5m",
        "M15": "15m"
    }

    obj = yf.Ticker(instrument)
    data = obj.history(interval=interval_dict[granularity],
                       start=start,
                       end=end
                       )

    data = data.rename(columns={"Open": "o", "High": "h", "Low": "l",
                                "Close": "c", "Volume": "volume"})

    return data
