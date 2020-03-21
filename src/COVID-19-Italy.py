import gettext
import streamlit as st
import pandas as pd
from babel import Locale
from typing import Dict, Callable

from italian import italian_line_plots, italian_map
from english import english_line_plots, english_map
from utils import get_data

data = get_data()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=["English", "Italiano"])

if language == "Italiano":
    locale = Locale("it", "IT")
    it = gettext.translation("messages", localedir="locale", languages=["it_IT"])
    it.install()
    _ = it.gettext
else:
    # language == "English" is the default
    locale = Locale("en", "GB")
    en = gettext.translation("messages", localedir="locale", languages=["en_GB"])
    en.install()
    _ = en.gettext

# Page choice
st.sidebar.title(_("Page"))
page = st.sidebar.selectbox(
    label=_("Page"), options=[_("Temporal trend"), _("Geographical distribution")]
)
page_function_mapping: Dict[str, Callable[[pd.DataFrame], None]] = {
    _("Temporal trend"): english_line_plots,
    _("Geographical distribution"): english_map,
}

page_function_mapping[page](data)

st.sidebar.markdown(
    _("Source code can be found at ")
    + "[GitHub](https://github.com/tommasobonomo/covid19-italy)."
)
