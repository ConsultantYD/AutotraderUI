import streamlit as st
from autotrader_ui.tpqoa import tpqoa

from autotrader_ui.market_info import (
    INSTRUMENT_MARKETS_DICT
)

_, img_col, _ = st.columns((1, 2, 1))
st.header("🏠 Home")

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

st.info("This page is still under development.")

#db = connect_to_firebase_db_and_authenticate()
#st.session_state['db'] = db
