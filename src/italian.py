import altair as alt
import pandas as pd
import streamlit as st
import datetime

from utils import (
    calculate_growth_factor,
    formatter,
    generate_global_chart,
    generate_regional_chart,
    generate_regions_choropleth,
    get_features,
)


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
    general = calculate_growth_factor(general, features)

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label="Scala", options=["lineare", "logaritmica"])
    general_scale = (
        alt.Scale(type="symlog")
        if general_choice == "logaritmica"
        else alt.Scale(type="linear")
    )

    st.markdown("## Dati generali")
    general_chart = generate_global_chart(
        general, feature, general_scale, "Mese e giorno"
    )
    st.altair_chart(general_chart)

    st.markdown("### Fattore crescita")
    st.markdown(
        """
        Il fattore di crescita è il moltiplicatore della curva esponenziale di crescita, calcolato come:
        $$
        \\frac{casi_{n+1}}{casi_{n}}
        $$
        dove $casi_n$ indica il numero di casi per il giorno $n$. Ad esempio, se ieri fossero stati registrati 300 casi
        e oggi 400, il fattore di crescita sarebbe 1.33, dato che $\\frac{400}{300} = 1.33$
        """
    )
    growth_chart = generate_global_chart(
        general, f"crescita_{feature}", general_scale, "Mese e giorno"
    )
    st.write(growth_chart)

    st.markdown("## Divisione per regione")
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

    regions_raw = []
    for _, region in selected_regions.groupby("denominazione_regione"):
        region = region.sort_values("data")
        region = calculate_growth_factor(region, features)
        regions_raw.append(region)
    selected_regions = pd.concat(regions_raw).reset_index(drop=True)

    regional_choice = st.radio(
        label="Scala regionale", options=["lineare", "logaritmica"]
    )
    regional_scale = (
        alt.Scale(type="symlog")
        if regional_choice == "logaritmica"
        else alt.Scale(type="linear")
    )

    st.markdown("### Dati generali")
    regional_chart = generate_regional_chart(
        selected_regions, feature, regional_scale, "Mese e giorno", "Regione"
    )
    if selected_regions.empty:
        st.warning("Nessuna regione selezionata!")
    else:
        st.write(regional_chart)

    st.markdown("### Fattore crescita")
    regional_growth_chart = generate_regional_chart(
        selected_regions,
        f"crescita_{feature}",
        general_scale,
        "Mese e giorno",
        "Regione",
        legend_position="bottom-left",
    )
    if selected_regions.empty:
        st.warning("Nessuna regione selezionata!")
    else:
        st.write(regional_growth_chart)

    st.subheader("Avvisi:")
    st.warning(
        """
        - 07/03/2020: dati Brescia +300 esiti positivi
        - 10/03/2020: dati Regione Lombardia parziali.
        - 11/03/2020: dati Regione Abruzzo non pervenuti.
        - 16/03/2020: dati P.A. Trento e Puglia non pervenuti.
        - 17/03/2020: dati Provincia di Rimini non aggiornati.
        - 18/03/2020: dati Regione Campania e Provincia di Parma non pervenuti.
        """
    )

    st.markdown(
        "Tutti i dati visualizzati in questa dashboard provengono dal Ministero della Salute e sono forniti dal "
        "Dipartimento della Protezione Civile. Questo progetto è quindi un derivato di [COVID-19 Italia - Monitoraggio "
        "situazione](https://github.com/pcm-dpc/COVID-19) che è liberamente utilizzabile sotto licenza "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )


def italian_map(data: pd.DataFrame) -> None:
    """Render chropleth of Italy with desired factor"""

    st.title("COVID-19 in Italia")

    st.markdown("Che dato vorresti visualizzare?")
    features = get_features(data)
    feature = st.selectbox(
        label="Scegli...", options=features, format_func=formatter, index=8
    )

    # Date selection
    filtered_data = data
    filtered_data["days_passed"] = filtered_data["data"].apply(
        lambda x: (x - datetime.date(2020, 2, 24)).days
    )
    n_days = filtered_data["days_passed"].unique().shape[0] - 1

    st.markdown(
        "Scegli che data visualizzare come numero di giorni dalla prima raccolta dati, il 24 febbraio:"
    )
    chosen_n_days = st.slider("Giorni:", min_value=0, max_value=n_days, value=n_days,)
    st.markdown(
        f"Data scelta: {datetime.date(2020, 2, 24) + datetime.timedelta(days=chosen_n_days)}"
    )
    filtered_data = data[data["days_passed"] == chosen_n_days]

    if filtered_data.empty:
        st.warning("Nessuna informazione disponibile per la data selezionata")
    else:
        choropleth = generate_regions_choropleth(filtered_data, feature, "Regione")
        st.write(choropleth)

    st.markdown(
        "Tutti i dati visualizzati in questa dashboard provengono dal Ministero della Salute e sono forniti dal "
        "Dipartimento della Protezione Civile. Questo progetto è quindi un derivato di [COVID-19 Italia - Monitoraggio "
        "situazione](https://github.com/pcm-dpc/COVID-19) che è liberamente utilizzabile sotto licenza "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )
