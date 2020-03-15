import altair as alt
import pandas as pd
import streamlit as st


from utils import get_features, formatter, dataframe_translator


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

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label="Scale", options=["linear", "logarithmic"])
    general_scale = (
        alt.Scale(type="symlog")
        if general_choice == "logarithmic"
        else alt.Scale(type="linear")
    )

    # Generate chart
    general_chart = (
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Month and Day"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=general_scale),
            tooltip=[
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .configure_scale(continuousPadding=5)
        .properties(width=700, height=500)
        .interactive()
    )
    st.altair_chart(general_chart)

    st.markdown("### Situation in different regions")

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
    if mode == "day-to-day":
        regions_raw = []
        for _, region in selected_regions.groupby("denominazione_regione"):
            region = region.sort_values("data")
            region[f"{original_feature}_delta"] = region[original_feature].diff()
            regions_raw.append(region.dropna())
        selected_regions = pd.concat(regions_raw).reset_index(drop=True)
        feature = f"{original_feature}_delta"

    # Select scale type
    regional_choice = st.radio(
        label="Scale", options=["linear", "logarithmic"], key="regional_choice"
    )
    regional_scale = (
        alt.Scale(type="symlog")
        if regional_choice == "logarithmic"
        else alt.Scale(type="linear")
    )
    # Plot results

    regional_chart = (
        alt.Chart(selected_regions)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Month and Day"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=regional_scale),
            color=alt.Color("denominazione_regione:N", title="Region"),
            tooltip=[
                alt.Tooltip("denominazione_regione", title="Region"),
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .configure_legend(
            fillColor="white",
            strokeWidth=3,
            strokeColor="#f63366",
            cornerRadius=5,
            padding=10,
            orient="top-left",
        )
        .configure_scale(continuousPadding=5)
        .properties(width=700, height=500)
        .interactive()
    )
    if selected_regions.empty:
        st.warning("No region selected!")
    else:
        st.write(regional_chart)

    st.subheader("Warnings:")
    st.warning(
        """
        - 10/03/2020: data from Lombardia are partial.
        - 11/03/2020: data from Abruzzo did not come through.
        """
    )

    st.markdown(
        "All the data displayed in this dashboard is provided by the Italian Ministry of Health (Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )


def italian_line_plots(data: pd.DataFrame, mode: str = "total") -> None:
    """
    Render line plots with all text in Italian. Takes a data argument that usually comes from utils.get_data()
    """
    st.title("COVID-19 in Italia")

    st.markdown("Che dato vorresti visualizzare?")
    features = get_features(data)
    feature = st.selectbox(
        label="Scegli...", options=features, format_func=formatter, index=8
    )
    original_feature = feature

    # Group data by date and calculate log of interested feature
    general = data.groupby("data", as_index=False).sum()
    if mode == "day-to-day":
        general[f"differenza_{feature}"] = general[feature].diff()
        general = general.dropna()
        feature = f"differenza_{feature}"

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label="Scala", options=["lineare", "logaritmica"])
    general_scale = (
        alt.Scale(type="symlog")
        if general_choice == "logaritmica"
        else alt.Scale(type="linear")
    )

    # Generate chart
    general_chart = (
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Mese e giorno"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=general_scale),
            tooltip=[
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .configure_scale(continuousPadding=5)
        .properties(width=700, height=500)
        .interactive()
    )
    st.altair_chart(general_chart)

    st.markdown("### Divisione per regione")

    # Get list of regions and select the ones of interest
    region_options = data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Regioni",
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

    if mode == "day-to-day":
        regions_raw = []
        for _, region in selected_regions.groupby("denominazione_regione"):
            region = region.sort_values("data")
            region[f"differenza_{original_feature}"] = region[original_feature].diff()
            regions_raw.append(region.dropna())
        selected_regions = pd.concat(regions_raw).reset_index(drop=True)
        feature = f"differenza_{original_feature}"

    # Select scale type
    regional_choice = st.radio(
        label="Scala", options=["lineare", "logaritmica"], key="regional_choice"
    )
    regional_scale = (
        alt.Scale(type="symlog")
        if regional_choice == "logaritmica"
        else alt.Scale(type="linear")
    )
    # Plot results

    regional_chart = (
        alt.Chart(selected_regions)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Mese e giorno"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=regional_scale),
            color=alt.Color("denominazione_regione:N", title="Regione"),
            tooltip=[
                alt.Tooltip("denominazione_regione", title="Regione"),
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .configure_legend(
            fillColor="white",
            strokeWidth=3,
            strokeColor="#f63366",
            cornerRadius=5,
            padding=10,
            orient="top-left",
        )
        .configure_scale(continuousPadding=5)
        .properties(width=700, height=500)
        .interactive()
    )
    if selected_regions.empty:
        st.warning("Nessuna regione selezionata!")
    else:
        st.write(regional_chart)

    st.subheader("Avvisi:")
    st.warning(
        """
        - 10/03/2020: dati Regione Lombardia parziali.
        - 11/03/2020: dati Regione Abruzzo non pervenuti.
        """
    )

    st.markdown(
        "Tutti i dati visualizzati in questa dashboard provengono dal Ministero della Salute e sono forniti dal Dipartimento della Protezione Civile. Questo progetto è quindi un derivato di [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) che è liberamente utilizzabile sotto licenza [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )
