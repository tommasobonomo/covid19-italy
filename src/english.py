import altair as alt
import pandas as pd
import streamlit as st
import datetime

from utils import (
    calculate_growth_factor,
    dataframe_translator,
    formatter,
    generate_global_chart,
    generate_regional_chart,
    generate_regions_choropleth,
    get_features,
)


def english_line_plots(data: pd.DataFrame) -> None:
    """
    Render line plots with all text in English. Takes a data argument that usually comes from utils.get_data()
    """
    english_data = dataframe_translator(data)

    st.title("COVID-19 in Italy")

    st.markdown("What indicator would you like to visualise?")
    features = get_features(english_data)
    feature = st.selectbox(
        label="Choose...", options=features, format_func=formatter, index=8
    )

    # Group data by date and calculate diff if required
    general = english_data.groupby("data", as_index=False).sum()
    general = calculate_growth_factor(general, features)

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label="Scale", options=["linear", "logarithmic"])
    general_scale = (
        alt.Scale(type="symlog")
        if general_choice == "logarithmic"
        else alt.Scale(type="linear")
    )

    st.markdown("## General data")
    general_chart = generate_global_chart(
        general, feature, general_scale, "Month and day"
    )
    st.altair_chart(general_chart)

    st.markdown("### Growth factor")
    st.markdown(
        """
        The growth factor is the multiplier of the exponential growth curve, calculated as:
        $$
        \\frac{cases_{n+1}}{cases_{n}}
        $$
        where $cases_n$ stands for the number of cases registered on day $n$. For example, if 300 cases were registered
        yesterday and 400 today, the growth factor would be 1.33, as $\\frac{400}{300} = 1.33$.
        """
    )
    growth_chart = generate_global_chart(
        general, f"crescita_{feature}", general_scale, "Month and day"
    )
    st.write(growth_chart)

    st.markdown("## Situation in different regions")

    # Get list of regions and select the ones of interest
    region_options = english_data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Regions",
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna"],
    )

    # Group data by date and region, sum up every feature, filter ones in regions selection
    total_regions = english_data.groupby(
        ["data", "denominazione_regione"], as_index=False
    ).sum()
    selected_regions = total_regions[
        total_regions["denominazione_regione"].isin(regions)
    ]

    regions_raw = []
    for _, region in selected_regions.groupby("denominazione_regione"):
        region = region.sort_values("data")
        region = calculate_growth_factor(region, features)
        regions_raw.append(region)
    selected_regions = pd.concat(regions_raw).reset_index(drop=True)

    regional_choice = st.radio(
        label="Regional scale", options=["linear", "logarithmic"]
    )
    regional_scale = (
        alt.Scale(type="symlog")
        if regional_choice == "logarithmic"
        else alt.Scale(type="linear")
    )

    st.markdown("### General data")
    regional_chart = generate_regional_chart(
        selected_regions, feature, regional_scale, "Month and day", "Region"
    )
    if selected_regions.empty:
        st.warning("No region selected!")
    else:
        st.write(regional_chart)

    st.markdown("### Growth factor")
    regional_growth_chart = generate_regional_chart(
        selected_regions,
        f"crescita_{feature}",
        general_scale,
        "Month and day",
        "Region",
        legend_position="bottom-left",
    )
    if selected_regions.empty:
        st.warning("No region selected!")
    else:
        st.write(regional_growth_chart)

    st.subheader("Warnings:")
    st.warning(
        """
        - 07/03/2020: data from Brescia +300 positive results
        - 10/03/2020: data from Lombardia is partial.
        - 11/03/2020: data from Abruzzo did not come through.
        - 16/03/2020: data from P.A. Trento and Puglia did not come through.
        - 17/03/2020: data from the Province of Rimini is not updated.
        - 18/03/2020: data from Campania and Province of Parma did not come through.
        """
    )

    st.markdown(
        "All the data displayed in this dashboard is provided by the Italian Ministry of Health "
        "(Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore "
        "a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed "
        "under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )


def english_map(data: pd.DataFrame) -> None:
    """Render chropleth of Italy with desired feature"""
    english_data = dataframe_translator(data)

    st.title("COVID-19 in Italy")

    st.markdown("What indicator would you like to visualise?")
    features = get_features(english_data)
    feature = st.selectbox(
        label="Choose...", options=features, format_func=formatter, index=8
    )

    # Date selection
    filtered_data = data
    filtered_data["days_passed"] = filtered_data["data"].apply(
        lambda x: (x - datetime.date(2020, 2, 24)).days
    )
    n_days = filtered_data["days_passed"].unique().shape[0] - 1

    st.markdown(
        "Choose what date to visualise as the number of days elapsed since the first data collection, on 24th February:"
    )
    chosen_n_days = st.slider("Days:", min_value=0, max_value=n_days, value=n_days,)
    st.markdown(
        f"Chosen date: {datetime.date(2020, 2, 24) + datetime.timedelta(days=chosen_n_days)}"
    )
    filtered_data = data[data["days_passed"] == chosen_n_days]

    if filtered_data.empty:
        st.warning("No information is available for the selected date")
    else:
        choropleth = generate_regions_choropleth(filtered_data, feature, "Region")
        st.write(choropleth)

    st.markdown(
        "All the data displayed in this dashboard is provided by the Italian Ministry of Health "
        "(Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore "
        "a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed "
        "under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )
