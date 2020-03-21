import streamlit as st
import pandas as pd
from gettext import translation, NullTranslations
from typing import Dict, Callable

from utils import get_data
from trends import line_plots

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

# Page choice
st.sidebar.title(_("Page"))
page = st.sidebar.selectbox(
    label=_("Page"), options=[_("Temporal trend"), _("Geographical distribution")]
)
page_function_mapping: Dict[str, Callable[[pd.DataFrame, NullTranslations], None]] = {
    _("Temporal trend"): line_plots,
    _("Geographical distribution"): None,
}

page_function_mapping[page](data, lang)

st.sidebar.markdown(
    _("Source code can be found at ")
    + "[GitHub](https://github.com/tommasobonomo/covid19-italy)."
)
