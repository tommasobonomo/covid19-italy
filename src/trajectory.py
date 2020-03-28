import altair as alt
import streamlit as st
import pandas as pd

from gettext import NullTranslations


def trajectory_cases(data: pd.DataFrame, lang: NullTranslations) -> None:
    _ = lang.gettext

    data = data.sort_values(by="data", axis=0)

    national = (
        data[["data", _("totale_casi"), _("nuovi_attualmente_positivi")]]
        .groupby("data", as_index=False)
        .sum()
    )

    national["data"] = pd.to_datetime(national["data"])
    national = national.resample("5D", on="data").mean()
    st.write(national)

    chart = (
        alt.Chart(national)
        .mark_line(point=True)
        .encode(x=_("totale_casi"), y=_("nuovi_attualmente_positivi"))
        .interactive()
    )

    st.altair_chart(chart)
