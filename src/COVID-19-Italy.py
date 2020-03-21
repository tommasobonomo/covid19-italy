import streamlit as st
import pandas as pd
from typing import Dict, Callable

from italian import italian_line_plots, italian_map
from english import english_line_plots, english_map
from utils import get_data

data = get_data()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=["Italiano", "English"])

if language == "English":
    # Page choice
    st.sidebar.markdown("# Page")
    page = st.sidebar.selectbox(
        label="Page", options=["Temporal trend", "Geographical distribution"]
    )
    page_function_mapping: Dict[str, Callable[[pd.DataFrame], None]] = {
        "Temporal trend": english_line_plots,
        "Geographical distribution": english_map,
    }

    page_function_mapping[page](data)

elif language == "Italiano":
    # Page choice
    st.sidebar.markdown("# Pagina")
    page = st.sidebar.selectbox(
        label="Pagina", options=["Andamento temporale", "Distribuzione geografica"]
    )
    page_function_mapping: Dict[str, Callable[[pd.DataFrame], None]] = {
        "Andamento temporale": italian_line_plots,
        "Distribuzione geografica": italian_map,
    }

    page_function_mapping[page](data)

st.sidebar.title(
    "To contribute or view the code, please see [github](https://github.com/tommasobonomo/covid19-italy)"
)
