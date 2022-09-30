import datetime
from gettext import NullTranslations

import altair as alt
import pandas as pd
import streamlit as st

from utils import (
    average_over_days,
    calculate_positive_tests_ratio,
    diff_over_previous_datapoint,
    formatter,
    generate_global_chart,
    generate_regional_chart,
    get_features,
)

ITALIAN_POPULATION = 60450414


def line_plots(data: pd.DataFrame, lang: NullTranslations) -> None:
    """Renders line plots, both general and regional, of data argument. Usually it is the resulting DataFrame from the website of the Protezione civile."""
    _ = lang.gettext

    # Group data by date
    general = calculate_positive_tests_ratio(
        data.groupby("data", as_index=False).sum(), lang
    )
    st.title(_("COVID-19 in Italy - Temporal trend"))

    st.markdown("### " + _("14-day cases per 100.000:"))

    # Get today
    today = general["data"].sort_values(ascending=False).iloc[0]

    # Filter for most recent 14 days and write calculation
    fourteen_day_new_positves = general[
        today - datetime.timedelta(days=14) < general["data"]
    ][_("new_positive")]
    st.write(
        float(f"{fourteen_day_new_positves.sum() * 100000 / ITALIAN_POPULATION:.2f}")
    )

    # Indicator chooser
    st.markdown(_("What indicator would you like to visualise?"))
    features = get_features(general)
    feature = st.selectbox(
        label=_("Choose..."), options=features, format_func=formatter, index=6
    )
    if feature is None:
        st.error(
            "Feature unavailable. There has been some problem with retrieving data."
        )
        return

    # Add checkbox for diff with most recent data for an indicator
    diff = st.checkbox(label=_("Difference with previous datapoint"))
    st.markdown(
        _(
            "By checking the above box, the indicator will be replaced by the difference of its value between two consecutive days. This helps in untangling cumulative data such as deaths and total tests."
        )
    )
    if diff:
        general = diff_over_previous_datapoint(general, "data", feature)

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label=_("Scale"), options=[_("linear"), _("logarithmic")])
    if general_choice == _("logarithmic"):
        general = general[general[feature] > 0]
        general_scale = alt.Scale(type="log")
    else:
        general_scale = alt.Scale(type="linear")

    st.markdown(("## " + _("General data")))

    # Cutoff to latest X days
    total_number_of_days = general["data"].max() - general["data"].min()
    number_cutoff_days = st.slider(
        label=_("Number of past days to consider"),
        key="cutoff",
        value=365,
        min_value=14,
        max_value=total_number_of_days.days,
    )
    cutoff_date = general["data"].max() - datetime.timedelta(days=number_cutoff_days)
    general = general[general["data"] >= cutoff_date]

    # Average calculation if needed
    is_general_average = st.checkbox(
        label=_("Average over days"), key="avg1", value=True
    )
    if is_general_average:
        avg_days = st.slider(
            label=_("Days to average over"),
            min_value=1,
            max_value=21,
            value=7,
            key="slider1",
        )
        general_average = average_over_days(
            general[[feature, "data"]], categorical_columns=["data"], avg_days=avg_days
        )

        general = general_average

    general_chart = generate_global_chart(
        general, feature, general_scale, _("Month and day")
    )
    st.altair_chart(general_chart)

    todays_latest = general[general["data"] == today][feature].iloc[0]

    st.markdown(
        _("Latest data on ")
        + f"**{formatter(feature).lower()}**: "
        + f"{todays_latest:.2f}"
    )

    st.markdown(("## " + _("Situation in different regions")))

    # Get list of regions and select the ones of interest
    region_options = data[_("denominazione_regione")].sort_values().unique().tolist()
    regions = st.multiselect(
        label=_("Regions"),
        options=region_options,
        default=["Lombardia", "Veneto", "Campania", "Lazio"],
    )
    # Filter regions in selection
    selected_regions = data[data[_("denominazione_regione")].isin(regions)]

    if selected_regions.empty:
        st.warning(_("No region selected!"))
    else:

        # Need to handle positive test percentage in if
        if feature == _("positivi_per_tampone_%"):
            selected_regions = (
                selected_regions.groupby([_("denominazione_regione")])
                .apply(lambda group: calculate_positive_tests_ratio(group, lang))
                .sort_values(by="data", ascending=True)
                .reset_index(level=0, drop=True)
                .reset_index(drop=True)
            )

        if diff:
            selected_regions = (
                selected_regions.groupby([_("denominazione_regione")])
                .apply(
                    lambda group: diff_over_previous_datapoint(group, "data", feature)
                )
                .sort_values(by="data", ascending=True)
                .reset_index(level=0, drop=True)
                .reset_index(drop=True)
            )

        regional_choice = st.radio(
            label=_("Regional Scale"), options=[_("linear"), _("logarithmic")]
        )
        if regional_choice == _("logarithmic"):
            selected_regions = selected_regions[selected_regions[feature] > 0]
            regional_scale = alt.Scale(type="log")
        else:
            regional_scale = alt.Scale(type="linear")

        is_regional_average = st.checkbox(
            label=_("Average over days"), key="avg2", value=True
        )
        if is_regional_average:
            avg_days = st.slider(
                label=_("Days to average over"),
                min_value=1,
                max_value=21,
                value=7,
                key="slider2",
            )
            regional_average = (
                selected_regions.groupby([_("denominazione_regione")], as_index=False)
                .apply(
                    lambda group: average_over_days(
                        group[[feature, "data", _("denominazione_regione")]],
                        ["data", _("denominazione_regione")],
                        avg_days,
                    )
                )
                .reset_index(level=0, drop=True)
                .reset_index(drop=True)
            )

            regional_average_chart = generate_regional_chart(
                regional_average,
                feature,
                regional_scale,
                x_title=_("Month and day"),
                color_title=_("Region"),
            )
            st.altair_chart(regional_average_chart)
        else:
            regional_chart = generate_regional_chart(
                selected_regions,
                feature,
                regional_scale,
                x_title=_("Month and day"),
                color_title=_("Region"),
            )
            st.altair_chart(regional_chart)
