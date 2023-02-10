import streamlit as st
import datetime as dt
import plotly.graph_objects as go
import plotly.express as px
import traceback

from autotrader_ui.data_utils import get_oanda_data
from autotrader_ui.tpqoa import tpqoa

from autotrader_ui.market_info import (
    INSTRUMENT_MARKETS_DICT
)

@st.cache(hash_funcs={dict: lambda _: None})
def plot_instrument_data(instrument, start_str, end_str, chart_type):
    df = get_oanda_data(instrument=instrument,
                        start=start_str,
                        end=end_str,
                        granularity='M1')

    if chart_type == "Candlestick":
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                             open=df['o'],
                                             high=df['h'],
                                             low=df['l'],
                                             close=df['c'])],
                        layout=go.Layout(
            title=go.layout.Title(text=instrument)
        ))
    elif chart_type == 'Time series':
        fig = px.line(df, x=df.index, y='h', title=instrument)
        fig.update_xaxes(rangeslider_visible=True)

    elif chart_type == 'OHLC':
        fig = go.Figure(data=[go.Ohlc(x=df.index,
                                      open=df['o'],
                                      high=df['h'],
                                      low=df['l'],
                                      close=df['c'])],
                        layout=go.Layout(
                            title=go.layout.Title(text=instrument)))

    return fig


st.header("📈 Trends")

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

# SELECTION MENU
# Instrument and Chart Type
_, col01, _, col02, col03, _ = st.columns((1, 6, 1, 4, 4, 1))

instrument_idx = 0
if "instrument" in st.session_state.keys():
    for idx in range(len(indices_list)):
        if clean_indices_list[idx][1] == st.session_state["instrument"]:
            instrument_idx = idx
            break

st.session_state["instrument"] = col01.selectbox(
    "Instrument", clean_indices_list, instrument_idx)[1]

chart_types = ["Candlestick", "Time series", "OHLC"]
chart_type = col01.selectbox("Chart type", chart_types)

# Start date and end date

def_end_date = dt.datetime.utcnow().date()
def_start_date = def_end_date - dt.timedelta(days=2)
start_date = col02.date_input("Start date", def_start_date)
end_date = col03.date_input("End date", def_end_date)

end = dt.datetime.combine(end_date, dt.time(23, 59))  # End until end of day
# If today, don't exceed present
end = min(dt.datetime.utcnow(), end)


# DATA RETRIEVAL
try:

    with st.spinner("Retrieving ..."):

        DT_STR_FORMAT = "%Y-%m-%d %H:%M"
        DICT_DT_STR_FORMAT = "%Y-%m-%d %H:%M:%S"

        start_str = start_date.strftime(DT_STR_FORMAT)
        end_str = end.strftime(DT_STR_FORMAT)

        instrument = st.session_state["instrument"]
        fig = plot_instrument_data(instrument, start_str, end_str, chart_type)

    st.plotly_chart(fig)

except:
    st.error("Impossible to retrieve the data.")
    st.error(traceback.format_exc())
