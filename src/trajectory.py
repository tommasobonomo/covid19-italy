import streamlit as st
import pandas as pd

from utils import generate_trajectory_chart

from gettext import NullTranslations


def trajectory_cases(data: pd.DataFrame, lang: NullTranslations) -> None:
    _ = lang.gettext

    data["data"] = pd.to_datetime(data["data"])
    data = data.sort_values(by="data", axis=0)

    # We must average the data, otherwise it just becomes untenable
    n_days = data["data"].unique().shape[0]
    avg_days = st.slider(
        label=_("Days to average over"), min_value=1, max_value=n_days // 4, value=5
    )
    days_to_average = f"{avg_days}D"

    national = (
        data[["data", _("totale_casi"), _("nuovi_attualmente_positivi")]]
        .groupby("data", as_index=False)
        .sum()
    )
    national = national.resample(days_to_average, on="data").mean().reset_index()

    national_choice = st.radio(
        label=_("Scale"), options=[_("linear"), _("logarithmic")], index=1
    )
    is_log_scale = national_choice == _("logarithmic")
    if is_log_scale:
        national = national[
            (national[_("totale_casi")] > 0)
            & (national[_("nuovi_attualmente_positivi")] > 0)
        ]

    chart = generate_trajectory_chart(
        national,
        _("totale_casi"),
        _("nuovi_attualmente_positivi"),
        is_log_scale=is_log_scale,
    )

    st.altair_chart(chart)
