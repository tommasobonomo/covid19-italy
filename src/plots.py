import altair as alt
import pandas as pd
import streamlit as st
import locale as loc

from translation import Translate
from data import Data


def line_plots(lang: str, mode: str = "total") -> None:
    """
    Render line plots. Takes a data argument that usually comes from utils.get_data()
    """

    data = Data(lang)
    t = Translate(lang)

    st.title(t.title)

    st.markdown(t.md_data_to_visualize)
    features = data.features
    feature = st.selectbox(
        label=t.label_choose, options=features, format_func=data.formatter, index=8
    )
    original_feature = feature

    # Group data by date and calculate log of interested feature
    national = data.aggregated_data

    # Choose log scale or linear, defines what feature to use
    national_choice = st.radio(label=t.label_national_scale, options=[
            t.opt_linear,
            t.opt_logarithmic])
    national_scale = (
        alt.Scale(type="symlog")
        if national_choice == t.opt_logarithmic
        else alt.Scale(type="linear")
    )

    st.markdown(f"## {t.md_national_data}")
    suffix = "" if mode == "total" else "delta"
    national_chart = data.generate_global_chart(
        national,
        feature,
        suffix,
        national_scale,
        t.axis_month_day
    )
    st.altair_chart(national_chart)

    st.markdown(f"### {t.md_growth_factor}")
    st.markdown(t.md_growth_factor_description_1)
    fraction = """
        $$
        \\frac{%s_{n+1}}{%s_{n}}
        $$
        """
    st.markdown(fraction % (t.str_cases, t.str_cases))
    st.markdown(t.md_growth_factor_description_2)

    suffix = "growth"

    national_growth_chart = data.generate_global_chart(
        national,
        feature,
        suffix,
        national_scale,
        t.axis_month_day
    )
    st.write(national_growth_chart)

    st.markdown(f"## {t.md_per_region}")
    # Get list of regions and select the ones of interest
    region_options = data.regions_list
    regions = st.multiselect(
        label=t.label_regions,
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna"],
    )

    # Group data by date and region, sum up every feature, filter ones in regions selection
    selected_regions = data.get_selected_regions_data(regions)

    regional_choice = st.radio(label=t.label_regional_scale, options=[
            t.opt_linear,
            t.opt_logarithmic])
    regional_scale = (
        alt.Scale(type="symlog")
        if regional_choice == t.opt_logarithmic
        else alt.Scale(type="linear")
    )
    suffix = "" if mode == "total" else "delta"

    st.markdown(f"### {t.md_regional_data}")
    regional_chart = data.generate_regional_chart(
        selected_regions,
        feature,
        suffix,
        regional_scale,
        t.axis_month_day,
        t.axis_region
    )
    if selected_regions.empty:
        st.warning(t.warning_no_sel_region)
    else:
        st.write(regional_chart)

    suffix = "growth"

    st.markdown(f"### {t.md_growth_factor}")
    regional_growth_chart = data.generate_regional_chart(
        selected_regions,
        feature,
        suffix,
        regional_scale,
        t.axis_month_day,
        t.axis_region,
        legend_position="bottom-left",
    )
    if selected_regions.empty:
        st.warning(t.warnings_no_sel_region)
    else:
        st.write(regional_growth_chart)
