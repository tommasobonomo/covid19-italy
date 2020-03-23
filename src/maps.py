import pandas as pd
import streamlit as st
import datetime

from gettext import NullTranslations

from utils import (
    dataframe_translator,
    get_features,
    formatter,
    generate_regions_choropleth,
    regional_growth_factor,
)


def choropleth_maps(data: pd.DataFrame, lang: NullTranslations) -> None:
    """Render choropleth maps of Italy, selecting feature and day"""
    _ = lang.gettext
    data.loc[:, :] = dataframe_translator(data, lang)

    st.title(_("COVID-19 in Italy"))

    st.markdown(_("What indicator would you like to visualise?"))
    features = get_features(data)
    feature = st.selectbox(
        label=_("Choose..."), options=features, format_func=formatter, index=8
    )

    is_growth_factor = st.checkbox(label=_("Growth factor of feature"))
    if is_growth_factor:
        gf_prefix = _("GF")
        data = regional_growth_factor(data, [feature], gf_prefix)
        feature = f"{gf_prefix}_{feature}"
        min_day = 1
        log_scale = False
    else:
        min_day = 0
        log_scale = True

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
    chosen_n_days = st.slider(
        _("Days:"), min_value=min_day, max_value=n_days, value=n_days,
    )
    st.markdown(
        (
            _("Chosen date: ")
            + f"{datetime.date(2020, 2, 24) + datetime.timedelta(days=chosen_n_days)}"
        )
    )
    day_data = data[data["days_passed"] == chosen_n_days]

    if day_data.empty:
        st.warning(_("No information is available for the selected date"))
    else:
        choropleth = generate_regions_choropleth(
            day_data, feature, _("Region"), log_scale=log_scale
        )
        st.altair_chart(choropleth)
