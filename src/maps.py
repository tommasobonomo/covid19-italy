import pandas as pd
import streamlit as st
import datetime

from gettext import NullTranslations

from utils import (
    get_features,
    formatter,
    generate_regions_choropleth,
    regional_growth_factor,
    provincial_growth_factor,
    get_province_data,
)


def choropleth_maps(data: pd.DataFrame, lang: NullTranslations) -> None:
    """Render choropleth maps of Italy, selecting feature and day"""
    _ = lang.gettext

    st.title(_("COVID-19 in Italy - Geographical distribution"))

    map_scale = st.radio(
        label=_("What resolution would you like to visualise?"),
        options=[_("Province"), _("Region")],
    )
    is_region = map_scale == _("Region")

    if is_region:
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
    else:
        data = get_province_data()
        data.columns = [
            _("totale_casi") if feature == "totale_casi" else feature
            for feature in data.columns
        ]
        feature = _("totale_casi")

        st.markdown(
            _(
                "Only total cases and their growth factor are available at the province resolution."
            )
        )
        feature_str = st.selectbox(
            label=_("What feature would you like to visualise?"),
            options=[_("Total cases"), _("Growth factor of total cases")],
        )
        if feature_str == _("Growth factor of total cases"):
            gf_prefix = _("GF")
            data = provincial_growth_factor(data, [_("totale_casi")], gf_prefix)
            feature = f"{gf_prefix}_{feature}"
            min_day = 1
            log_scale = True
        else:
            # feature_str == _("Total cases")
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
            day_data, feature, _("Region"), log_scale=log_scale, is_region=is_region
        )
        st.altair_chart(choropleth)
