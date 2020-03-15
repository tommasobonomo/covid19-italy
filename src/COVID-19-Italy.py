import streamlit as st

from italian import italian_line_plots
from english import english_line_plots
from utils import get_data

data = get_data()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=["Italiano", "English"])

if language == "English":
    st.sidebar.markdown("# Available visualisations")
    st.sidebar.markdown(
        "Choose if you prefer to visualise the total of the chosen indicator or the day-to-day increment or decrement:"
    )
    data_rate = st.sidebar.radio(
        label="Available visualisations", options=["total", "day-to-day"]
    )
    english_line_plots(data, mode=data_rate)

elif language == "Italiano":
    st.sidebar.markdown("# Possibili visualizzazioni")
    st.sidebar.markdown(
        "Scegli se preferisci visualizzare il dato totale o il relativo cambiamento rispetto al giorno precedente:"
    )
    data_rate = st.sidebar.radio(
        label="Possibili visualizzazioni", options=["totale", "giorno per giorno"]
    )
    mode = "total" if data_rate == "totale" else "day-to-day"
    italian_line_plots(data, mode=mode)

st.sidebar.title(
    "To contribute or view the code, please see [github](https://github.com/tommasobonomo/covid19-italy)"
)
