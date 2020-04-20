import streamlit as st
import pandas as pd
from gettext import translation, NullTranslations
from typing import Dict, Callable

from utils import get_data, dataframe_translator
from trends import line_plots
from trajectory import trajectory_cases
from maps import choropleth_maps


data = get_data()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=["English", "Italiano"])

if language == "Italiano":
    lang = translation("messages", localedir="locale", languages=["it_IT"])
    lang.install()
    _ = lang.gettext
else:
    # language == "English" is the default
    lang = translation("messages", localedir="locale", languages=["en_GB"])
    lang.install()
    _ = lang.gettext

# Translate dataframe to given language
# Features are derived directly from dataframe columns, following the tidy format of dataframes
data.loc[:, :] = dataframe_translator(data, lang)

# Page choice
st.sidebar.title(_("Page"))
page = st.sidebar.selectbox(
    label=_("Page"),
    options=[
        _("Temporal trend"),
        _("Trajectory of cases"),
        _("Geographical distribution"),
    ],
)
page_function_mapping: Dict[str, Callable[[pd.DataFrame, NullTranslations], None]] = {
    _("Temporal trend"): line_plots,
    _("Trajectory of cases"): trajectory_cases,
    _("Geographical distribution"): choropleth_maps,
}

page_function_mapping[page](data, lang)

st.sidebar.markdown(
    _(
        """
    **Please note**:

    All line plots are interactive, you can zoom with scrolling and hover on data points for additional information.
    """
    )
)

st.sidebar.markdown(
    _("Source code can be found at ")
    + "[GitHub](https://github.com/tommasobonomo/covid19-italy)."
)

st.subheader(_("Warnings:"))
st.warning(
    _(
        """
    - 15/04/2020: dati Regione Friuli Venezia Giulia ricalcolati (ricalcolo di isolamento domiciliare e dimessi/guariti)
    - 12/04/2020: dati P.A. Bolzano ricalcolati (ricalcolo dati guariti -110 rispetto a ieri).
    - 10/04/2020: dati Regione Molise parziali (dato tamponi non aggiornato).
    - 29/03/2020: dati Regione Emilia-Romagna parziali (dato tampone non aggiornato).
    - 26/03/2020: dati Regione Piemonte parziali (-50 deceduti - comunicazione tardiva).
    - 18/03/2020: dati Regione Campania non pervenuti.
    - 18/03/2020: dati Provincia di Parma non pervenuti.
    - 17/03/2020: dati Provincia di Rimini non aggiornati.
    - 16/03/2020: dati P.A. Trento e Puglia non pervenuti.
    - 11/03/2020: dati Regione Abruzzo non pervenuti.
    - 10/03/2020: dati Regione Lombardia parziali.
    - 07/03/2020: dati Brescia +300 esiti positivi
    """
    )
)

st.markdown(
    _(
        "All the data displayed in this dashboard is provided by the Italian Ministry of Health "
        "(Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore "
        "a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed "
        "under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )
)
