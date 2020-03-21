import pandas as pd
import altair as alt
from typing import List

from gettext import NullTranslations


def get_data() -> pd.DataFrame:
    """
    Gets data from the GitHub repository of the Protezione Civile
    """
    data = pd.read_csv(
        "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    )
    # Remove the time and just focus on the date
    data["data"] = pd.to_datetime(data["data"]).apply(lambda x: x.date())
    return data


def get_features(data: pd.DataFrame) -> List[str]:
    """
    Gets features from data, i.e. all columns except data, stato, codice_regione, denominazione_regione, lat, long
    """
    feature_data = data.drop(
        columns=[
            "data",
            "stato",
            "codice_regione",
            "denominazione_regione",
            "lat",
            "long",
        ]
    )
    return feature_data.columns.tolist()


def formatter(name: str) -> str:
    if name == "hospitalised_in_ICU":
        return "Hospitalised in ICU"
    else:
        return " ".join(name.capitalize().split("_"))


def dataframe_translator(data: pd.DataFrame, lang: NullTranslations) -> pd.DataFrame:
    """
    Translates original column features into language defined
    """
    _ = lang.gettext

    feature_mapping = {
        "ricoverati_con_sintomi": _("ricoverati_con_sintomi"),
        "terapia_intensiva": _("terapia_intensiva"),
        "totale_ospedalizzati": _("totale_ospedalizzati"),
        "isolamento_domiciliare": _("isolamento_domiciliare"),
        "totale_attualmente_positivi": _("totale_attualmente_positivi"),
        "nuovi_attualmente_positivi": _("nuovi_attualmente_positivi"),
        "dimessi_guariti": _("dimessi_guariti"),
        "deceduti": _("deceduti"),
        "totale_casi": _("totale_casi"),
        "tamponi": _("tamponi"),
    }

    data.columns = [
        feature_mapping[feature] if feature in feature_mapping else feature
        for feature in data.columns
    ]

    return data


def calculate_growth_factor(
    data: pd.DataFrame, features: List[str], prefix: str = "growth_factor"
):
    for feature in features:
        data[f"{feature}_yesterday"] = data[feature].shift()
        data[f"{prefix}_{feature}"] = data[feature] / data[f"{feature}_yesterday"]
    return data


def generate_global_chart(
    data: pd.DataFrame,
    feature: str,
    scale: alt.Scale,
    x_title: str,
    padding: int = 5,
    width: int = 700,
    height: int = 500,
):
    return (
        alt.Chart(data)
        .mark_line(point={"size": 70})
        .encode(
            x=alt.X("data:T", title=x_title),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=scale),
            tooltip=[
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title=x_title, type="temporal"),
            ],
        )
        .configure_scale(continuousPadding=padding)
        .properties(width=width, height=height)
        .interactive()
    )


def generate_regional_chart(
    data: pd.DataFrame,
    feature: str,
    scale: alt.Scale,
    x_title: str,
    color_title: str,
    padding: int = 5,
    width: int = 700,
    height: int = 500,
    legend_position: str = "top-left",
):
    return (
        alt.Chart(data)
        .mark_line(point={"size": 70})
        .encode(
            x=alt.X("data:T", title=x_title),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=scale),
            color=alt.Color("denominazione_regione:N", title=color_title),
            tooltip=[
                alt.Tooltip("denominazione_regione", title=color_title),
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title=x_title, type="temporal"),
            ],
        )
        .configure_legend(
            fillColor="white",
            strokeWidth=3,
            strokeColor="#f63366",
            cornerRadius=5,
            padding=10,
            orient=legend_position,
        )
        .configure_scale(continuousPadding=padding)
        .properties(width=width, height=height)
        .interactive()
    )


def generate_regions_choropleth(
    data: pd.DataFrame, feature: str, title: str, width: int = 700, height: int = 1000,
) -> alt.Chart:
    regions_shape = alt.topo_feature(
        "https://raw.githubusercontent.com/openpolis/geojson-italy/master/topojson/limits_IT_regions.topo.json",
        "regions",
    )
    data.loc[:, "data"] = data["data"].apply(lambda x: x.isoformat())
    data = data[data[feature] > 0]

    base_chart = (
        alt.Chart(regions_shape)
        .mark_geoshape(stroke="black", strokeWidth=0.5, color="white")
        .encode(tooltip=[alt.Tooltip("properties.reg_name:N", title=title)])
    )

    color_chart = (
        alt.Chart(regions_shape)
        .mark_geoshape(stroke="black", strokeWidth=0.5)
        .encode(
            color=alt.Color(
                f"{feature}:Q",
                title=formatter(feature),
                scale=alt.Scale(type="log", scheme="teals"),
            ),
            tooltip=[
                alt.Tooltip("properties.reg_name:N", title=title),
                alt.Tooltip(f"{feature}:Q", title=formatter(feature)),
            ],
        )
        .transform_lookup(
            "properties.reg_istat_code_num",
            from_=alt.LookupData(data=data, key="codice_regione", fields=[feature],),
        )
    )

    final_chart = (
        (base_chart + color_chart)
        .configure_view(strokeWidth=0)
        .properties(width=width, height=height)
    )

    return final_chart
