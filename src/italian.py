import altair as alt
import pandas as pd
import streamlit as st

from utils import calculate_growth_factor, formatter, generate_global_chart, generate_regional_chart, get_features


def italian_line_plots(data: pd.DataFrame, mode: str = "total") -> None:
    """
    Render line plots with all text in Italian. Takes a data argument that usually comes from utils.get_data()
    """
    st.title("COVID-19 in Italia")

    st.markdown("Che dato vorresti visualizzare?")
    features = get_features(data)
    feature = st.selectbox(label="Scegli...", options=features, format_func=formatter, index=8)
    original_feature = feature

    # Group data by date and calculate log of interested feature
    general = data.groupby("data", as_index=False).sum()
    if mode == "day-to-day":
        general[f"differenza_{feature}"] = general[feature].diff()
        general = general.dropna()
        feature = f"differenza_{feature}"
        features.append(feature)
    calculate_growth_factor(general, features)

    # Choose log scale or linear, defines what feature to use
    general_choice = st.radio(label="Scala", options=["lineare", "logaritmica"])
    general_scale = alt.Scale(type="symlog") if general_choice == "logaritmica" else alt.Scale(type="linear")

    st.markdown("## Dati generali")
    general_chart = generate_global_chart(general, feature, general_scale, "Mese e giorno")
    st.altair_chart(general_chart)

    st.markdown("### Fattore crescita")
    st.markdown(
        "Il fattore di crescita e' il moltiplicatore della curva esponenziale di crescita, calcolato come "
        "(casi(n+1)-casi(n))/casi(n). Ad esempio se ieri sono stati registrati 300 casi e oggi 400, il fattore "
        "di crescita sara' 1.33, visto che 400/300=1.33."
    )
    growth_chart = generate_global_chart(general, f"crescita_{feature}", general_scale, "Mese e giorno")
    st.write(growth_chart)

    st.markdown("## Divisione per regione")
    # Get list of regions and select the ones of interest
    region_options = data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Regioni", options=region_options, default=["Lombardia", "Veneto", "Emilia Romagna"],
    )

    # Group data by date and region, sum up every feature, filter ones in regions selection
    total_regions = data.groupby(["data", "denominazione_regione"], as_index=False).sum()
    selected_regions = total_regions[total_regions["denominazione_regione"].isin(regions)]

    if mode == "day-to-day":
        regions_raw = []
        for _, region in selected_regions.groupby("denominazione_regione"):
            region = region.sort_values("data")
            region[f"differenza_{original_feature}"] = region[original_feature].diff()
            regions_raw.append(region.dropna())
        selected_regions = pd.concat(regions_raw).reset_index(drop=True)
        feature = f"differenza_{original_feature}"
        features.append(feature)

    calculate_growth_factor(selected_regions, features)

    st.markdown("### Dati generali")
    regional_chart = generate_regional_chart(selected_regions, feature, general_scale, "Mese e giorno", "Regione")
    if selected_regions.empty:
        st.warning("Nessuna regione selezionata!")
    else:
        st.write(regional_chart)

    st.markdown("### Fattore crescita")
    regional_growth_chart = generate_regional_chart(
        selected_regions, f"crescita_{feature}", general_scale, "Mese e giorno", "Regione"
    )
    if selected_regions.empty:
        st.warning("Nessuna regione selezionata!")
    else:
        st.write(regional_growth_chart)

    st.subheader("Avvisi:")
    st.warning(
        """
        - 10/03/2020: dati Regione Lombardia parziali.
        - 11/03/2020: dati Regione Abruzzo non pervenuti.
        """
    )

    st.markdown(
        "Tutti i dati visualizzati in questa dashboard provengono dal Ministero della Salute e sono forniti dal "
        "Dipartimento della Protezione Civile. Questo progetto è quindi un derivato di [COVID-19 Italia - Monitoraggio "
        "situazione](https://github.com/pcm-dpc/COVID-19) che è liberamente utilizzabile sotto licenza "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    )
