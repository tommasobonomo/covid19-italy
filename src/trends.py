import altair as alt
import pandas as pd
import streamlit as st

from gettext import NullTranslations

from utils import (
    average_over_days,
    get_features,
    formatter,
    generate_global_chart,
    generate_regional_chart,
)


def line_plots(data: pd.DataFrame, lang: NullTranslations) -> None:
    """Renders line plots, both general and regional, of data argument. Usually it is the resulting DataFrame from the website of the Protezione civile."""
    _ = lang.gettext

    st.title(_("COVID-19 in Italy - Temporal trend"))

    st.markdown(_("What indicator would you like to visualise?"))
    features = get_features(data)
    feature = st.selectbox(
        label=_("Choose..."), options=features, format_func=formatter, index=11
    )

    # Group data by date
    general = data.groupby("data", as_index=False).sum()

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label=_("Scale"), options=[_("linear"), _("logarithmic")])
    if general_choice == _("logarithmic"):
        general = general[general[feature] > 0]
        general_scale = alt.Scale(type="log")
    else:
        general_scale = alt.Scale(type="linear")

    st.markdown(("## " + _("General data")))

    is_general_average = st.checkbox(label=_("Average over days"), key="avg1")
    if is_general_average:
        avg_days = st.slider(
            label=_("Days to average over"),
            min_value=2,
            max_value=21,
            value=7,
            key="slider1",
        )
        general_average = average_over_days(
            general[[feature, "data"]], categorical_columns=["data"], avg_days=avg_days
        )
        general_average_chart = generate_global_chart(
            general_average, feature, general_scale, _("Month and day")
        )
        st.altair_chart(general_average_chart)
    else:
        general_chart = generate_global_chart(
            general, feature, general_scale, _("Month and day")
        )
        st.altair_chart(general_chart)

    st.markdown(("## " + _("Situation in different regions")))

    # Get list of regions and select the ones of interest
    region_options = data["denominazione_regione"].sort_values().unique().tolist()
    regions = st.multiselect(
        label=_("Regions"),
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia-Romagna"],
    )
    # Filter regions in selection
    selected_regions = data[data["denominazione_regione"].isin(regions)]

    if selected_regions.empty:
        st.warning(_("No region selected!"))
    else:
        regional_choice = st.radio(
            label=_("Regional Scale"), options=[_("linear"), _("logarithmic")]
        )
        if regional_choice == _("logarithmic"):
            selected_regions = selected_regions[selected_regions[feature] > 0]
            regional_scale = alt.Scale(type="log")
        else:
            regional_scale = alt.Scale(type="linear")

        st.markdown(("### " + _("General data")))

        is_regional_average = st.checkbox(label=_("Average over days"), key="avg2")
        if is_regional_average:
            avg_days = st.slider(
                label=_("Days to average over"),
                min_value=2,
                max_value=21,
                value=7,
                key="slider2",
            )
            regional_average = (
                selected_regions.groupby(["denominazione_regione"], as_index=False)
                .apply(
                    lambda group: average_over_days(
                        group[[feature, "data", _("denominazione_regione")]],
                        ["data", "denominazione_regione"],
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
