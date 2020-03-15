import altair as alt
import pandas as pd
import streamlit as st


from utils import get_features, formatter


def italian_line_plots(data: pd.DataFrame) -> None:
    """
    Render line plots with all text in Italian. Takes a data argument that usually comes from utils.get_data()
    """
    st.title("COVID-19 in Italia")

    st.markdown("Che dato vorresti visualizzare?")
    features = get_features(data)
    feature = st.selectbox(
        label="Scegli...", options=features, format_func=formatter, index=8
    )

    # Group data by date and calculate log of interested feature
    general = data.groupby("data", as_index=False).sum()

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

    st.markdown(
        "Tutti i dati visualizzati in questa dashboard provengono dal Ministero della Salute e sono forniti dal Dipartimento della Protezione Civile. Questo progetto è quindi un derivato di [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) che è liberamente utilizzabile sotto licenza [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )
