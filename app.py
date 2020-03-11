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
        "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv"
    )
    return data[["data", "denominazione_regione", "totale_casi"]]


filtered = get_data()

st.title("COVID-19 in Italy")
is_log = st.checkbox(label="Logarithmic scale", value=False)
scale = alt.Scale(type="symlog") if is_log else alt.Scale(type="linear")

st.sidebar.markdown("# Possible comparisons")
st.sidebar.markdown(
    "Choose if you want to see the total value corresponding to a specific date or if you would like to see instead the increase/decrease compared to the previous day:"
)
choice = st.sidebar.radio(label="Possible comparisons", options=["total", "day-to-day"])

# %%
# TOTAL NUMBERS
if choice == "total":
    st.markdown("## Total numbers")
    st.markdown("### General trend")

    general = filtered.groupby("data", as_index=False).sum()

    st.altair_chart(
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("monthdate(data)", title="Day and month"),
            y=alt.Y("totale_casi:Q", title="Total number of cases", scale=scale),
            tooltip=[
                alt.Tooltip("totale_casi", title="Total cases"),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )

    # %%
    st.markdown("### Regional trend")
    region_options = filtered["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Selectable regions",
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna", "Trento"],
    )
    # %%
    final_all = filtered.groupby(
        ["data", "denominazione_regione"], as_index=False
    ).sum()
    final = final_all[final_all["denominazione_regione"].isin(regions)]
    # %%

    st.altair_chart(
        alt.Chart(final)
        .mark_line(point=True)
        .encode(
            x=alt.X("monthdate(data)", title="Day and month"),
            y=alt.Y("totale_casi:Q", title="Total number of cases", scale=scale),
            color="denominazione_regione:N",
            tooltip=[
                alt.Tooltip("denominazione_regione", title="Region"),
                alt.Tooltip("totale_casi", title="Total cases"),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )
else:
    st.markdown("## Day-to-day variation")
    st.markdown("### All of Italy")

    general = filtered.groupby("data", as_index=False).sum()
    general["totale_casi"] = general["totale_casi"].diff()
    general = general.dropna()

    st.altair_chart(
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("monthdate(data)", title="Day and month"),
            y=alt.Y("totale_casi:Q", title="Day-to-day change", scale=scale),
            tooltip=[
                alt.Tooltip("totale_casi", title="Day-to-day change"),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )

    # %%
    st.markdown("### Regional trend")
    region_options = filtered["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Selectable regions",
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna", "Trento"],
    )
    # %%
    final_all = filtered.groupby(
        ["data", "denominazione_regione"], as_index=False
    ).sum()
    final_all = final_all[final_all["denominazione_regione"].isin(regions)]
    final = []
    for _, region in final_all.groupby("denominazione_regione"):
        region = region.sort_values("data")
        region["change"] = region["totale_casi"].diff()
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
                alt.Tooltip("totale_casi", title="Total cases"),
                alt.Tooltip("data", title="Date", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )
