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
    _("Source code can be found at ")
    + "[GitHub](https://github.com/tommasobonomo/covid19-italy)."
)

st.subheader(_("Warnings:"))
st.warning(
    _(
        """
    - 07/03/2020: data from Brescia +300 positive results
    - 10/03/2020: data from Lombardia is partial.
    - 11/03/2020: data from Abruzzo did not come through.
    - 16/03/2020: data from P.A. Trento and Puglia did not come through.
    - 17/03/2020: data from the Province of Rimini is not updated.
    - 18/03/2020: data from Campania and Province of Parma did not come through.
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
