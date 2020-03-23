import altair as alt
import pandas as pd
import streamlit as st

from gettext import NullTranslations

from utils import (
    dataframe_translator,
    get_features,
    formatter,
    calculate_growth_factor,
    regional_growth_factor,
    generate_global_chart,
    generate_regional_chart,
)


def line_plots(data: pd.DataFrame, lang: NullTranslations) -> None:
    """Renders line plots, both general and regional, of data argument. Usually it is the resulting DataFrame from the website of the Protezione civile."""
    _ = lang.gettext
    data.loc[:, :] = dataframe_translator(data, lang)

    st.title(_("COVID-19 in Italy"))

    st.markdown(_("What indicator would you like to visualise?"))
    features = get_features(data)
    feature = st.selectbox(
        label=_("Choose..."), options=features, format_func=formatter, index=8
    )

    # Group data by date
    gf_prefix = _("growth_factor")
    growth_scale = alt.Scale(type="linear")
    general = data.groupby("data", as_index=False).sum()
    general = calculate_growth_factor(general, features, prefix=gf_prefix)

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label=_("Scale"), options=[_("linear"), _("logarithmic")])
    if general_choice == _("logarithmic"):
        general = general[general[feature] > 0]
        general_scale = alt.Scale(type="log")
    else:
        general_scale = alt.Scale(type="linear")

    st.markdown(("## " + _("General data")))
    general_chart = generate_global_chart(
        general, feature, general_scale, _("Month and day")
    )
    st.altair_chart(general_chart)

    st.markdown(("### " + _("Growth factor")))
    st.markdown(
        _(
            """
        The growth factor is the multiplier of the exponential growth curve, calculated as:
        $$
        \\frac{cases_{n+1}}{cases_{n}}
        $$
        where $cases_n$ stands for the number of cases registered on day $n$. For example, if 300 cases were registered
        yesterday and 400 today, the growth factor would be 1.33, as $\\frac{400}{300} = 1.33$.
        """
        )
    )

    growth_chart = generate_global_chart(
        general, f"{gf_prefix}_{feature}", growth_scale, _("Month and day")
    )
    st.altair_chart(growth_chart)

    st.markdown(("## " + _("Situation in different regions")))

    # Get list of regions and select the ones of interest
    region_options = data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label=_("Regions"),
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna"],
    )

    # Group data by date and region, sum up every feature, filter ones in regions selection
    total_regions = data.groupby(
        ["data", "denominazione_regione"], as_index=False
    ).sum()
    selected_regions = total_regions[
        total_regions["denominazione_regione"].isin(regions)
    ]

    if selected_regions.empty:
        st.warning(_("No region selected!"))
    else:
        selected_regions = regional_growth_factor(selected_regions, features, gf_prefix)
        regional_choice = st.radio(
            label=_("Regional Scale"), options=[_("linear"), _("logarithmic")]
        )
        if regional_choice == _("logarithmic"):
            selected_regions = selected_regions[selected_regions[feature] > 0]
            regional_scale = alt.Scale(type="log")
        else:
            regional_scale = alt.Scale(type="linear")

        st.markdown(("### " + _("General data")))
        regional_chart = generate_regional_chart(
            selected_regions,
            feature,
            regional_scale,
            x_title=_("Month and day"),
            color_title=_("Region"),
        )
        st.altair_chart(regional_chart)

        st.markdown(("### " + _("Growth factor")))
        regional_growth_chart = generate_regional_chart(
            selected_regions,
            f"{gf_prefix}_{feature}",
            growth_scale,
            x_title=_("Month and day"),
            color_title=_("Region"),
            legend_position="bottom-left",
        )
        st.altair_chart(regional_growth_chart)
