# %%
import streamlit as st
import pandas as pd
import altair as alt


@st.cache
def get_data() -> pd.DataFrame:
    """
    Gets data from the GitHub repository of the Protezione Civile
    Keeps only date, region and total of cases
    """
    data = pd.read_csv(
        "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    )
    return data


def formatter(name: str) -> str:
    return " ".join(name.capitalize().split("_"))


data = get_data()

st.sidebar.markdown("# Possible comparisons")
st.sidebar.markdown(
    "Choose if you want to see the total value corresponding to a specific date or if you would like to see instead the increase/decrease compared to the previous day:"
)
choice = st.sidebar.radio(label="Possible comparisons", options=["total", "day-to-day"])

st.title("COVID-19 in Italy")
is_log = st.checkbox(label="Logarithmic scale", value=False)
scale = alt.Scale(type="symlog") if is_log else alt.Scale(type="linear")

st.markdown("What feature would you like to explore?")
features = [
    "ricoverati_con_sintomi",
    "terapia_intensiva",
    "totale_ospedalizzati",
    "isolamento_domiciliare",
    "totale_attualmente_positivi",
    "nuovi_attualmente_positivi",
    "dimessi_guariti",
    "deceduti",
    "totale_casi",
    "tamponi",
]
feature = st.selectbox(
    label="Feature...", options=features, format_func=formatter, index=8
)

# %%
# TOTAL NUMBERS
if choice == "total":
    st.markdown("## Total numbers")
    st.markdown("### General trend")

    general = data.groupby("data", as_index=False).sum()

    st.altair_chart(
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("monthdate(data)", title="Day and month"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=scale),
            tooltip=[
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )

    # %%
    st.markdown("### Regional trend")
    region_options = data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Selectable regions",
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna", "Trento"],
    )
    # %%
    final_all = data.groupby(["data", "denominazione_regione"], as_index=False).sum()
    final = final_all[final_all["denominazione_regione"].isin(regions)]
    # %%

    st.altair_chart(
        alt.Chart(final)
        .mark_line(point=True)
        .encode(
            x=alt.X("monthdate(data)", title="Day and month"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=scale),
            color="denominazione_regione:N",
            tooltip=[
                alt.Tooltip("denominazione_regione", title="Region"),
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )
else:
    st.markdown("## Day-to-day variation")
    st.markdown("### All of Italy")

    general = data.groupby("data", as_index=False).sum()
    general[f"{feature}"] = general[f"{feature}"].diff()
    general = general.dropna()

    st.altair_chart(
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("monthdate(data)", title="Day and month"),
            y=alt.Y(f"{feature}:Q", title="Day-to-day change", scale=scale),
            tooltip=[
                alt.Tooltip(f"{feature}", title="Day-to-day change"),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )

    # %%
    st.markdown("### Regional trend")
    region_options = data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Selectable regions",
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna", "Trento"],
    )
    # %%
    final_all = data.groupby(["data", "denominazione_regione"], as_index=False).sum()
    final_all = final_all[final_all["denominazione_regione"].isin(regions)]
    final = []
    for _, region in final_all.groupby("denominazione_regione"):
        region = region.sort_values("data")
        region["change"] = region[f"{feature}"].diff()
        final.append(region.dropna())

    final = pd.concat(final).reset_index(drop=True)
    # %%

    st.altair_chart(
        alt.Chart(final)
        .mark_line(point=True)
        .encode(
            x=alt.X("monthdate(data)", title="Day and month"),
            y=alt.Y("change:Q", title="Day-to-day change", scale=scale),
            color="denominazione_regione:N",
            tooltip=[
                alt.Tooltip("denominazione_regione", title="Region"),
                alt.Tooltip("change", title="Day-to-day change"),
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )
