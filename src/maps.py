import pandas as pd
import streamlit as st
import datetime

from gettext import NullTranslations

from utils import (
    dataframe_translator,
    get_features,
    formatter,
    generate_regions_choropleth,
)


def choropleth_maps(data: pd.DataFrame, lang: NullTranslations) -> None:
    """Render choropleth maps of Italy, selecting feature and day"""
    _ = lang.gettext
    data = dataframe_translator(data, lang)

    st.title(_("COVID-19 in Italy"))

    st.markdown(_("What indicator would you like to visualise?"))
    features = get_features(data)
    feature = st.selectbox(
        label=_("Choose..."), options=features, format_func=formatter, index=8
    )

    # Date selection
    data["days_passed"] = data["data"].apply(
        lambda x: (x - datetime.date(2020, 2, 24)).days
    )
    n_days = data["days_passed"].unique().shape[0] - 1
    st.markdown(
        _(
            "Choose what date to visualise as the number of days elapsed since the first data collection, on 24th February:"
        )
    )
    chosen_n_days = st.slider(_("Days:"), min_value=0, max_value=n_days, value=n_days,)
    st.markdown(
        f"{_('Chosen date')}: {datetime.date(2020, 2, 24) + datetime.timedelta(days=chosen_n_days)}"
    )
    day_data = data[data["days_passed"] == chosen_n_days]

    if day_data.empty:
        st.warning(_("No information is available for the selected date"))
    else:
        choropleth = generate_regions_choropleth(day_data, feature, _("Region"))
        st.altair_chart(choropleth)
