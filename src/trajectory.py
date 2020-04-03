import streamlit as st
import pandas as pd

from utils import generate_trajectory_chart, average_over_days

from gettext import NullTranslations


def trajectory_cases(data: pd.DataFrame, lang: NullTranslations) -> None:
    _ = lang.gettext

    st.markdown(_("# COVID-19 in Italy - Trajectory of cases"))
    show_details = st.checkbox(label=_("Show details"))
    if show_details:
        st.markdown(
            _(
                """
        This visualisation is heavily inspired by [this video](https://www.youtube.com/watch?v=54XLXg4fYsc) by MinutePhysics.
        It plots the new positive cases (total cases of today - total cases of yesterday) against the total number of cases.
        When the phenomenon is following an exponential trajectory, this graph will represent it as a diagonal line.
        This way of visualising the trajectory of the spread is useful as it highlights when the trajectory of cases stops being exponential and starts slowing down, resulting in a flat line.
        Eventually, as there are less and less new cases, the trajectory becomes a vertical line.
        The same graph for many countries in the world can be found at [this link](https://aatishb.com/covidtrends/).

        Please watch the video above for more details.
        """
            )
        )

    data = data[
        ["data", _("totale_casi"), _("nuovi_positivi"), _("denominazione_regione")]
    ]
    data["data"] = pd.to_datetime(data["data"])
    data = data.sort_values(by="data", axis=0)

    # We must average the data, otherwise it just becomes untenable
    n_days = data["data"].unique().shape[0]
    avg_days = st.slider(
        label=_("Days to average over"), min_value=1, max_value=n_days // 4, value=5
    )
    st.write(
        _(
            "This slider selects the number of days to average over. This means that it bins the data in intervals of the selected value backwards from today and takes the average. It is necessary to reduce variability of each day, but can be turned off selecting 1."
        )
    )

    national = (
        data.drop(columns="denominazione_regione").groupby("data", as_index=False).sum()
    )
    national = average_over_days(national, "data", avg_days)

    chart = generate_trajectory_chart(national, _("totale_casi"), _("nuovi_positivi"))
    st.altair_chart(chart)

    st.markdown(_("## Regional breakdown"))

    # Get list of regions and select the ones of interest
    region_options = data["denominazione_regione"].sort_values().unique().tolist()
    regions = st.multiselect(
        label=_("Regions"),
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia-Romagna"],
    )
    # Filter regions in selection
    selected_regions = data[data["denominazione_regione"].isin(regions)]

    if selected_regions.empty:
        st.warning(_("No region selected!"))
    else:
        averaged_regions = (
            selected_regions.groupby(["denominazione_regione"], as_index=False)
            .apply(
                lambda group: average_over_days(
                    group, ["data", "denominazione_regione"], avg_days
                )
            )
            .reset_index(level=0, drop=True)
            .reset_index(drop=True)
        )

        final_data = averaged_regions[
            (averaged_regions[_("totale_casi")] > 0)
            & (averaged_regions[_("nuovi_positivi")] > 0)
        ]

        st.altair_chart(
            generate_trajectory_chart(
                final_data,
                _("totale_casi"),
                _("nuovi_positivi"),
                colour_code_column="denominazione_regione",
            )
        )
