import streamlit as st

from plots import line_plots
from translation import Languages, Translate

langs = Languages()

st.sidebar.title("Language")
language = st.sidebar.radio(label="", options=langs.get_array(), index=1)

t = Translate(language)

st.sidebar.markdown(f"# {t.md_available_visualizations}")
st.sidebar.markdown(t.md_visualizations_description)
data_rate = st.sidebar.radio(label=t.label_visualizations,
                             options=[t.opt_total,
                                      t.opt_day_to_day])
st.sidebar.title(t.sidebar_github)

if data_rate == t.opt_total:
    data_rate = "total"
else:
    if data_rate == t.opt_day_to_day:
        data_rate = "day-to-day"

line_plots(mode=data_rate, lang=language)

st.subheader(t.str_warnings)
st.warning(t.warnings_updates)

st.markdown(t.md_footer)