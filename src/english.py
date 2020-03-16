import altair as alt
import pandas as pd
import streamlit as st

from utils import (
    calculate_growth_factor,
    dataframe_translator,
    formatter,
    generate_global_chart,
    generate_regional_chart,
    get_features,
)


def english_line_plots(data: pd.DataFrame, mode: str = "total") -> None:
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
    original_feature = feature

    # Group data by date and calculate diff if required
    general = english_data.groupby("data", as_index=False).sum()
    if mode == "day-to-day":
        general[f"{feature}_delta"] = general[feature].diff()
        general = general.dropna()
        feature = f"{feature}_delta"
        features.append(feature)
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
        if mode == "day-to-day":
            region[f"{original_feature}_delta"] = region[original_feature].diff()
            features.append(f"{original_feature}_delta")
        region = calculate_growth_factor(region, features)
        regions_raw.append(region)
    selected_regions = pd.concat(regions_raw).reset_index(drop=True)

    st.markdown("### General data")
    regional_chart = generate_regional_chart(
        selected_regions, feature, general_scale, "Month and day", "Region"
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
    )
    if selected_regions.empty:
        st.warning("No region selected!")
    else:
        st.write(regional_growth_chart)

    st.subheader("Warnings:")
    st.warning(
        """
        - 10/03/2020: data from Lombardia is partial.
        - 11/03/2020: data from Abruzzo did not come through.
        """
    )

    st.markdown(
        "All the data displayed in this dashboard is provided by the Italian Ministry of Health "
        "(Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore "
        "a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed "
        "under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )
