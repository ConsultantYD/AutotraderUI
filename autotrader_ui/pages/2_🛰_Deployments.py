import datetime as dt
import pandas as pd
import streamlit as st
import traceback
from autotrader_ui.db_utils import (
    connect_to_firebase_db_and_authenticate,
    create_live
)
from autotrader_ui.market_info import (
    MARKET_OPEN_HOURS,
    INSTRUMENT_MARKETS_DICT
)

from autotrader_ui.tpqoa import tpqoa

st.header("🛰 Deployments")

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

with st.expander("Show/Hide Configuration", True):
    with st.form("test_form"):
        st.subheader("🕵🏼  Agent")

        _, col01, _, col02, _ = st.columns((1, 5, 2, 5, 1))

        with col01:

            trade_quantity = st.number_input(
                "Trade quantity", 0, 1000, value=1)
            activity_limit = st.number_input(
                "Transactions limit", 0, 100000, value=50000)
            rsi_threshold = st.number_input(
                "RSI Threshold", 0, 1000, value=50, step=1)

        with col02:
            loss_price_perc = st.number_input(
                "Loss price (%)", 0., 100., value=0.01, step=0.001, format="%.3f")
            gain_price_perc = st.number_input(
                "Gain price (%)", 0., 100., value=0.03, step=0.001, format="%.3f")

            macd_condition = st.checkbox("MacD Condition", True)
            rsi50_condition = st.checkbox("RSI50 Condition", True)
            ema_condition = st.checkbox("EMA Condition", True)

        agent_config = {
            "rsi_threshold": rsi_threshold,
            "trade_quantity": trade_quantity,
            "loss_price_%": loss_price_perc,
            "gain_price_%": gain_price_perc,
            "activity_limit": activity_limit,
            "condition_macd": macd_condition,
            "condition_rsi_50": rsi50_condition,
            "condition_ema_true": ema_condition
        }

        st.subheader("⚙️  Execution")

        _, col11, _, col12, _ = st.columns((1, 5, 2, 5, 1))

        instrument_idx = 0
        if "instrument" in st.session_state.keys():
            for idx in range(len(indices_list)):
                if clean_indices_list[idx][1] == st.session_state["instrument"]:
                    instrument_idx = idx
                    break

        st.session_state["instrument"] = col11.selectbox(
            "Instrument", clean_indices_list, index=instrument_idx)[1]

        initial_capital = col12.number_input(
            "Initial capital", 1000, 20000, step=1000, value=10000)

        execution_config = {
            "instrument": st.session_state["instrument"]
        }

        st.subheader("⏳ Time")

        market = INSTRUMENT_MARKETS_DICT[st.session_state["instrument"]]
        time_dict = MARKET_OPEN_HOURS[market]
        weekdays = ["Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"]
        _, col21, _, col22, _ = st.columns((1, 5, 2, 5, 1))
        time_config = {}
        for i in range(7):
            weekday = weekdays[i]
            time_args = time_dict[i]
            start_time = col21.time_input(
                weekday + ' start time', dt.time(*time_args["start"]))
            end_time = col22.time_input(
                weekday + ' end time', dt.time(*time_args["end"]))

            time_config[str(i)] = {"start": (int(start_time.hour), int(start_time.minute)),
                                   "end": (int(end_time.hour), int(end_time.minute))}

        st.subheader("🚀 Launch")
        _, col31, _, col32, _ = st.columns((1, 5, 2, 5, 1))
        agent_name = col31.text_input("Agent name")
        submitted = col31.form_submit_button("Deploy Agent !")

#_, col41, col42, _ = st.columns((1, 5, 5, 3))

if submitted:
    with st.spinner("Running ..."):
        try:

            DT_STR_FORMAT = "%Y-%m-%d %H:%M"

            data_dict = {
                "agent_config": agent_config,
                "execution_config": execution_config,
                "time_config": time_config,
                "status": "Ready to start",
                "created_at": dt.datetime.utcnow().strftime(DT_STR_FORMAT)
            }

            create_live(db, agent_name=agent_name, data=data_dict)
            st.success("Deployment successfuly initiated !")

        except:
            st.error("Error in deployment !")
            st.error(traceback.format_exc())
