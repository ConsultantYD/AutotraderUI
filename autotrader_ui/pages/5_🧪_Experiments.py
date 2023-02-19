import streamlit as st
import datetime as dt
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from autotrader_ui.data_utils import get_oanda_data
from autotrader_ui.tpqoa import tpqoa

from autotrader_ui.market_info import INSTRUMENT_MARKETS_DICT
from autotrader_ui.db_utils import (
    connect_to_firebase_db_and_authenticate,
    get_all_experiments,
    get_all_experiments_name,
    get_specific_experiment,
    delete_experiment
)

@st.cache_resource()
def get_experiment_values(experiment_name):

    db = connect_to_firebase_db_and_authenticate(project_name="autotrader")
    exp_dict = get_specific_experiment(db, experiment_name)
    exp_values = exp_dict[experiment_name]

    return exp_values

@st.cache_data()
def generate_experiment_df(experiment_name: str, experiment_values: dict,
                           start: str, end: str):

    df = get_oanda_data(instrument=instrument,
                        start=start,
                        end=end,
                        granularity='M1')

    df = df[~df.index.duplicated(keep='first')].asfreq(
        "1T").interpolate(limit=5)

    df.index = pd.to_datetime(df.index)

    df['opening'] = np.nan
    df['closing'] = np.nan
    df['transaction_value'] = np.nan
    df['positive_transaction'] = np.nan
    df['negative_transaction'] = np.nan

    transactions = exp_values["transactions"]
    for i in range(len(df)):
        idx = df.index[i]
        idx_str = idx.strftime(DICT_DT_STR_FORMAT)

        if idx_str in transactions.keys():
            transaction = transactions[idx_str]
            if transaction["action"] == "buy":
                df.loc[idx, "opening"] = transaction["volume"]
                open_transaction_cost = transaction["volume"] * \
                    transaction["price"]
            elif transaction["action"] == "sell":
                df.loc[idx, "closing"] = transaction["volume"]
                transaction_cost = transaction["volume"] * transaction["price"]
                transaction_value = -transaction_cost - open_transaction_cost
                df.loc[idx, "transaction_value"] = transaction_value
                df.loc[idx, "transaction_value_%"] = transaction_value / \
                    open_transaction_cost
                if transaction_value <= 0:
                    df.loc[idx, "negative_transaction"] = transaction_value / \
                        open_transaction_cost
                else:
                    df.loc[idx, "positive_transaction"] = transaction_value / \
                        open_transaction_cost

    df["buy_plot"] = (df["opening"] / df["opening"].values) * df["c"].values
    df["sell_plot"] = (df["closing"] / df["closing"].values) * df["c"].values

    return df

@st.cache_data()
def generate_time_series_transaction_plot(df: pd.DataFrame):
    fig1 = px.line(df, x=df.index, y='c')
    fig1.update_xaxes(rangeslider_visible=True)
    fig2 = px.scatter(df, x=df.index, y='buy_plot')
    fig2.update_traces(marker=dict(
        symbol='triangle-up', size=12), marker_color='green')
    fig3 = px.scatter(df, x=df.index, y='sell_plot')
    fig3.update_traces(marker=dict(
        symbol='triangle-down', size=12), marker_color='red')
    fig = go.Figure(data=fig1.data + fig2.data + fig3.data,
                    layout=go.Layout(
                        title=go.layout.Title(
                            text="Position Opening and Closing")
                    ))
    return fig

@st.cache_data()
def generate_transaction_values_plot(df: pd.DataFrame):
    fig1 = px.scatter(df, x=df.index, y='positive_transaction')
    fig1.update_traces(marker_color='green')
    fig2 = px.line(x=df.index, y=np.zeros(len(df.index)))
    fig2.update_traces(line_color='black')
    fig3 = px.scatter(df, x=df.index, y='negative_transaction')
    fig3.update_traces(marker_color='red')
    fig = go.Figure(data=fig1.data + fig2.data + fig3.data,
                    layout=go.Layout(
                        title=go.layout.Title(
                            text="Transaction Resulting Values (%)")
                    ))
    return fig

def generate_transaction_histogram_plot(df: pd.DataFrame):
    fig = px.histogram(df["transaction_value_%"], marginal="rug",
                       title="Transaction Values Distribution")
    return fig


st.header("🧪 Experiments")
DT_STR_FORMAT = "%Y-%m-%d %H:%M"
DICT_DT_STR_FORMAT = "%Y-%m-%d %H:%M:%S"

db = connect_to_firebase_db_and_authenticate(project_name="autotrader")
oanda = tpqoa('oanda.cfg')
indices_list = oanda.get_instruments()
clean_indices_list = [i for i in indices_list if i[1]
                      in INSTRUMENT_MARKETS_DICT.keys()]

with st.sidebar:
    st.title("AutoTrader")
    instrument_idx = 0
    if "instrument" in st.session_state.keys():
        for idx in range(len(indices_list)):
            if clean_indices_list[idx][1] == st.session_state["instrument"]:
                instrument_idx = idx
                break

    st.session_state["instrument"] = st.selectbox(
        "Default instrument", clean_indices_list, index=instrument_idx)[1]

col00, _, _ = st.columns((2, 1, 1))
experiments_list = get_all_experiments_name(db)
experiment_name = col00.selectbox("Select experiment", experiments_list)
if col00.button("Delete Experiment"):
    delete_experiment(db, experiment_name=experiment_name)
    st.experimental_rerun()
exp_values = get_experiment_values(experiment_name=experiment_name)


if exp_values["failure"]["failure_flag"]:
    st.error("Experiment calculation failed.")
    err_msg = exp_values["failure"]["traceback"]
    st.error(err_msg)

else:
    start = exp_values['start']
    end = exp_values['end']
    instrument = exp_values["execution"]["instrument"]
    final_capital = exp_values["execution"]["final_capital"]
    initial_capital = exp_values["execution"]["initial_capital"]
    initial_stocks = exp_values["execution"]["initial_stocks"]
    final_stocks = exp_values["execution"]["final_stocks"]
    final_bid_price = exp_values["execution"]["final_bid_price"]
    gain = final_capital - initial_capital
    first_transaction = list(exp_values["transactions"].values())[0]
    first_transaction_cost = first_transaction["price"] * \
        first_transaction["volume"]
    gain_perc = (gain / first_transaction_cost) * 100

    col_ratios = (1, 5, 1, 5, 5)

    st.subheader("Performance & Execution")
    _, col11, _, col12, col13 = st.columns(col_ratios)

    with col11:
        st.write("**Instrument**: ", instrument)
        st.date_input("Start & End", dt.datetime.strptime(
            start, DICT_DT_STR_FORMAT), disabled=True)
        st.date_input("", dt.datetime.strptime(
            end, DICT_DT_STR_FORMAT), label_visibility="collapsed", disabled=True)

    with col12:
        st.metric("Gain ($)", round(gain, 2),
                  str(round(gain_perc, 3)) + "%")
        st.write("**Initial capital ($)**: ", round(initial_capital, 2))
        st.write("**Final capital ($)**: ", round(final_capital, 2))
    with col13:
        st.metric("Remaining stocks", final_stocks,
                  final_stocks - initial_stocks, "off")
        st.write("**Final bid price ($)**: ", final_bid_price)
        st.write("**Capital equivalent ($)**: ",
                 final_bid_price * final_stocks)

    st.subheader("Agent")
    _, col31, _ = st.columns((1, 10, 5))
    with col31:
        st.write(exp_values["agent"])

    st.subheader("Transactions")

    df = generate_experiment_df(experiment_name=experiment_name,
                                experiment_values=exp_values,
                                start=start, end=end)

    if df["opening"].count() == 0:
        st.warning("No transactions were done during this experiment.")
    else:
        ratio = (df["positive_transaction"].count(
        ) / df["transaction_value_%"].count()) * 100
        st.write("Positive trades ratio: ", round(ratio, 2), "%.")
        st.dataframe(df[["transaction_value_%"]
                        ].describe().transpose(copy=True), use_container_width=True)

        fig0 = generate_time_series_transaction_plot(df)
        st.plotly_chart(fig0)

        fig1 = generate_transaction_values_plot(df)
        st.plotly_chart(fig1)

        fig2 = generate_transaction_histogram_plot(df)
        st.plotly_chart(fig2)
