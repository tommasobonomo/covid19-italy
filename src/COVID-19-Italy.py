import streamlit as st

import line_plots
from utils import get_data

data = get_data()

language = st.sidebar.radio(label="", options=["Italiano", "English"])

if language == "English":
    st.sidebar.markdown("# Possible visualisations")
    st.sidebar.markdown(
        "Choose if you prefer to visualise the total of the chosen indicator or the day-to-day increment or decrement:"
    )
    data_rate = st.sidebar.radio(
        label="Possibili visualisations", options=["total", "day-to-day"]
    )
    line_plots.english_line_plots(data, mode=data_rate)

elif language == "Italiano":
    st.sidebar.markdown("# Possibili visualizzazioni")
    st.sidebar.markdown(
        "Scegli se preferisci visualizzare il dato totale o il relativo cambiamento rispetto al giorno precedente:"
    )
    data_rate = st.sidebar.radio(
        label="Possibili visualizzazioni", options=["totale", "giorno per giorno"]
    )
    mode = "total" if data_rate == "totale" else "day-to-day"
    line_plots.italian_line_plots(data, mode=mode)
