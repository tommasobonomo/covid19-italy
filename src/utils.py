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
    filtered_date_column = data["data"][data["data"].str.len() == 19]
    data["data"] = (
        pd.to_datetime(filtered_date_column).apply(lambda x: x.date()).dropna()
    )
    return data


def get_province_data() -> pd.DataFrame:
    """Gets data from the GitHub repository of the Protezione Civile regarding provinces"""
    data = pd.read_csv(
        "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv"
    )
    # Remove the time and just focus on the date
    filtered_date_column = data["data"][data["data"].str.len() == 19]
    data["data"] = (
        pd.to_datetime(filtered_date_column).apply(lambda x: x.date()).dropna()
    )
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
            "note_it",
            "note_en",
        ]
    )
    return feature_data.columns.tolist()


def get_features_provinces(data: pd.DataFrame) -> List[str]:
    """
    Gets features from data, i.e. all columns except data, stato, codice_regione, denominazione_regione, lat, long
    """
    columns = set(data.columns.tolist())
    features = columns.difference(
        [
            "data",
            "stato",
            "codice_regione",
            "denominazione_regione",
            "lat",
            "long",
            "note_it",
            "note_en",
            "sigla_provincia",
            "denominazione_provincia",
            "codice_provincia",
        ]
    )
    return list(features)


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
        "totale_positivi": _("totale_positivi"),
        "variazione_totale_positivi": _("variazione_totale_positivi"),
        "nuovi_positivi": _("nuovi_positivi"),
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
) -> pd.DataFrame:
    for feature in features:
        data[f"{feature}_yesterday"] = data[feature].shift()
        data[f"{prefix}_{feature}"] = data[feature] / data[f"{feature}_yesterday"]
    return data


def regional_growth_factor(
    data: pd.DataFrame, features: List[str], prefix: str = "growth_factor"
) -> pd.DataFrame:
    regions_raw = []
    for region_name, region in data.groupby("denominazione_regione"):
        region = region.sort_values("data")
        region = calculate_growth_factor(region, features, prefix=prefix)
        regions_raw.append(region)
    data = pd.concat(regions_raw).reset_index(drop=True)
    return data


def provincial_growth_factor(
    data: pd.DataFrame, features: List[str], prefix: str = "growth_factor"
) -> pd.DataFrame:
    provinces_raw = []
    for province_name, province in data.groupby("denominazione_provincia"):
        province = province.sort_values("data")
        province = calculate_growth_factor(province, features, prefix=prefix)
        provinces_raw.append(province)
    data = pd.concat(provinces_raw).reset_index(drop=True)
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
    data: pd.DataFrame,
    feature: str,
    title: str,
    width: int = 700,
    height: int = 1000,
    log_scale: bool = True,
    is_region: bool = True,
) -> alt.Chart:
    if is_region:
        shape = alt.topo_feature(
            "https://raw.githubusercontent.com/openpolis/geojson-italy/master/topojson/limits_IT_regions.topo.json",
            "regions",
        )
    else:
        shape = alt.topo_feature(
            "https://raw.githubusercontent.com/openpolis/geojson-italy/master/topojson/limits_IT_provinces.topo.json",
            "provinces",
        )

    area_name = "reg_name" if is_region else "prov_name"
    lookup_in_shape = "reg_istat_code_num" if is_region else "prov_istat_code_num"
    lookup_in_df = "codice_regione" if is_region else "codice_provincia"

    chart_data = data[data[feature] > 0][[feature, lookup_in_df]]

    base_chart = (
        alt.Chart(shape)
        .mark_geoshape(stroke="black", strokeWidth=0.5, color="white")
        .encode(tooltip=[alt.Tooltip(f"properties.{area_name}:N", title=title)])
    )
    scale = (
        alt.Scale(type="log", scheme="teals")
        if log_scale
        else alt.Scale(type="linear", scheme="teals")
    )
    color_chart = (
        alt.Chart(shape)
        .mark_geoshape(stroke="black", strokeWidth=0.5)
        .encode(
            color=alt.Color(
                f"{feature}:Q",
                title=formatter(feature),
                scale=scale,
                legend=alt.Legend(labelLimit=50),
            ),
            tooltip=[
                alt.Tooltip(f"properties.{area_name}:N", title=title),
                alt.Tooltip(f"{feature}:Q", title=formatter(feature), format=".4~f"),
            ],
        )
        .transform_lookup(
            f"properties.{lookup_in_shape}",
            from_=alt.LookupData(data=chart_data, key=lookup_in_df, fields=[feature],),
        )
    )

    final_chart = (
        (base_chart + color_chart)
        .configure_view(strokeWidth=0)
        .properties(width=width, height=height)
    )

    return final_chart


def average_over_days(
    data: pd.DataFrame, categorical_columns: List[str], avg_days: int = 5
) -> pd.DataFrame:
    """Returns an average over the latest avg_days days of all values in data"""
    data = data.sort_values(by="data", ascending=False, axis=0).reset_index(drop=True)
    grouped_categorical = (
        data[categorical_columns].groupby(data.index // avg_days).first()
    )
    grouped_numerical = data.groupby(data.index // avg_days).mean()
    return pd.concat([grouped_categorical, grouped_numerical], axis=1)


def generate_trajectory_chart(
    data: pd.DataFrame,
    feature_x: str,
    feature_y: str,
    colour_code_column: str = None,
    padding: int = 5,
    width: int = 700,
    height: int = 500,
):

    scale = alt.Scale(type="log")
    chart = (
        alt.Chart(data)
        .mark_line(point={"size": 70})
        .encode(
            x=alt.X(f"{feature_x}:Q", title=formatter(feature_x), scale=scale),
            y=alt.Y(f"{feature_y}:Q", title=formatter(feature_y), scale=scale),
            tooltip=[
                alt.Tooltip(f"{feature_x}", title=formatter(feature_x), format=".2~f"),
                alt.Tooltip(f"{feature_y}", title=formatter(feature_y), format=".2~f"),
                alt.Tooltip("data", type="temporal"),
            ],
        )
    )

    if colour_code_column:
        chart = chart.encode(color=colour_code_column)

    return (
        chart.configure_scale(continuousPadding=padding)
        .properties(width=width, height=height)
        .interactive()
    )
