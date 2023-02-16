import datetime as dt
import pandas as pd
import streamlit as st
import traceback
from autotrader_ui.db_utils import (
    connect_to_firebase_db_and_authenticate,
    create_backtest,
    get_all_backtests
)
from autotrader_ui.market_info import (
    MARKET_OPEN_HOURS,
    INSTRUMENT_MARKETS_DICT
)

from autotrader_ui.tpqoa import tpqoa

def get_def_config_values(dict_name, key, value):
    if dict_name in st.session_state.keys() and key in st.session_state[dict_name]:
        def_value = st.session_state[dict_name][key]
    else:
        def_value = value
    return def_value

st.title("🕟 Backtesting")
db = connect_to_firebase_db_and_authenticate(project_name="autotrader")
oanda = tpqoa('oanda.cfg')
indices_list = oanda.get_instruments()
clean_indices_list = [i for i in indices_list if i[1] in INSTRUMENT_MARKETS_DICT.keys()]

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
    

st.header("New Experiment")
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

            macd_condition = st.checkbox("MacD Condition", True)
            rsi50_condition = st.checkbox("RSI50 Condition", True)

        with col02:
            loss_price_perc = st.number_input(
                "Loss price (%)", 0., 100., value=0.01, step=0.001, format="%.3f")
            gain_price_perc = st.number_input(
                "Gain price (%)", 0., 100., value=0.03, step=0.001, format="%.3f")
            ema_condition = st.checkbox("EMA Condition", True)

        agent_config = {
            "rsi_threshold": rsi_threshold,
            "stoch_threshold": stoch_threshold,
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
        
        sim_len_days = col11.number_input(
            "Duration (days)", 1, 7, 3)
        sim_spread = col11.checkbox("Simulate spread", True)
        initial_stocks = col12.number_input(
            "Initial stocks", 0, 10000, step=1, value=0)
        initial_capital = col12.number_input(
            "Initial capital", 1000, 10000, step=1000, value=10000)

        execution_config = {
            "instrument": st.session_state["instrument"],
            "sim_len_days": sim_len_days,
            "initial_capital": initial_capital,
            "initial_stocks": initial_stocks,
            "spread_simulation": sim_spread
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

        st.subheader("🧪 Experiment")
        _, col31, _, col32, _ = st.columns((1, 5, 2, 5, 1))
        exp_name = col31.text_input("Experiment name")
        submitted = col31.form_submit_button("Create New Experiment")

#_, col41, col42, _ = st.columns((1, 5, 5, 3))

if exp_name == "" and submitted:
    st.error("Error - Please use an experiment name.")
    st.stop()

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

            create_backtest(db, backtest_name=exp_name, data=data_dict)
            st.success("Experiment successfuly submitted !")

        except:
            st.error("Error in experiment submission !")
            st.error(traceback.format_exc())

st.header("Pending Backtests")

with st.spinner("Loading ..."):
    all_backtests = get_all_backtests(db)
    backtest_name = list(all_backtests.keys())
    backtest_statuses = [v["status"] for v in all_backtests.values()]
    backtest_times = [v["created_at"] for v in all_backtests.values()]
    df = pd.DataFrame({
        "Experiment Name": backtest_name,
        "Current Status": backtest_statuses,
        "Created At (UTC)": backtest_times
    })

    if len(df) == 0:
        st.write("There are currently no pending backtests.")
    else:
        st.write("There are currently ", len(df), " pending backtest(s).")
    st.dataframe(df, use_container_width=True)

    if st.button("Refresh Table"):
        st.experimental_rerun()
