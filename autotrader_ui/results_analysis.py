import streamlit as st
import datetime as dt
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from autotrader.data_utils import get_oanda_data

# Load experiments dictionary

# TODO: Add market comparison analysis

def gain_analysis(exp_dict: dict) -> dict:

    exp_name = list(exp_dict.keys())[0]
    exp_values = exp_dict[exp_name]

    start = exp_values['start']
    end = exp_values['end']
    instrument = exp_values["execution"]["instrument"]
    final_capital = exp_values["execution"]["final_capital"]
    initial_capital = exp_values["execution"]["initial_capital"]
    gain = final_capital - initial_capital
    gain_perc = (gain / initial_capital) * 100

    analysis = {
        "start": start,
        "end": end,
        "instrument": instrument,
        "initial_capital": initial_capital,
        "final_capital": final_capital,
        "gain": gain,
        "gain_%": gain_perc
    }

    return analysis

def convert_raw_transactions_to_trades(exp_dict: dict) -> dict:

    DICT_DT_STR_FORMAT = "%Y-%m-%d %H:%M:%S"

    exp_name = list(exp_dict.keys())[0]
    exp_values = exp_dict[exp_name]

    buy_dict, sell_dict = {}, {}

    for transaction_time_str, transaction_dict in exp_values["transactions"].items():
        t = dt.datetime.strptime(transaction_time_str, DICT_DT_STR_FORMAT)
        price = transaction_dict["price"]
        volume = transaction_dict["volume"]
        reason = transaction_dict["reasons"]
        if transaction_dict["action"] == "buy":
            buy_dict[t] = (price, volume, reason)
        else:
            sell_dict[t] = (price, volume, reason)

    buy_times = list(buy_dict.keys())
    sell_times = list(sell_dict.keys())

    trades = []
    for i in range(len(buy_times)):

        buy_t = buy_times[i]
        sell_t = sell_times[i]
        delta_t = (sell_t - buy_t).total_seconds() / 60

        buy_price = buy_dict[buy_t][0]
        buy_volume = buy_dict[buy_t][1]

        sell_price = sell_dict[sell_t][0]
        sell_volume = sell_dict[sell_t][1]
        sell_reason = sell_dict[sell_t][2]

        gain = sell_price * sell_volume - buy_price * buy_volume
        gain_perc = exp_values['execution']['initial_capital']

        assert buy_volume == abs(sell_volume)

        trade_dict = {
            "start": buy_t,
            "end": sell_t,
            "open_len": delta_t,
            "volume": sell_volume,
            "gain": gain,
            "gain_%": gain_perc,
            "sell_reason": sell_reason
        }
        trades.append(trade_dict)

    return trades
