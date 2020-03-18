import pandas as pd
import altair as alt
from typing import List
from translation import Translate
from cachetools import cached, TTLCache
cache = TTLCache(maxsize=10, ttl=60)

@cached(cache)
class Data:
    csv_url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    data = None
    aggregated_data = None
    total_regions_data = None
    regions_data = None
    regions_list = None
    t = None
    features = []
    extended_features = []
    def __init__(self, lang: str = "English"):
        self.data = self.get_data()
        self.features = self.get_features()
        self.t = Translate(lang)

    def get_data(self):
        _data = pd.read_csv(self.csv_url)
        # Remove the time and just focus on the date
        _data["data"] = pd.to_datetime(_data["data"]).apply(lambda x: x.date())
        self.data = _data.rename(columns = {
            "data": "date",
            "stato": "state",
            "codice_regione": "region_code",
            "denominazione_regione": "region_name",
            "ricoverati_con_sintomi": "feature_hospitalized_with_symptoms",
            "terapia_intensiva": "feature_people_in_icu",
            "totale_ospedalizzati": "feature_total_hospitalized",
            "isolamento_domiciliare": "feature_people_in_domestic_isolation",
            "totale_attualmente_positivi": "feature_total_of_current_positives",
            "nuovi_attualmente_positivi": "feature_new_current_positives",
            "dimessi_guariti": "feature_people_discharged_and_recovered",
            "deceduti": "feature_deaths",
            "totale_casi": "feature_total_cases",
            "tamponi": "feature_total_tests"
        })
        self.get_features()
        self.aggregate_data()
        self.get_total_regions_data()
        self.get_regions_data()
        self.get_regions_list()
        return self.data

    def get_features(self) -> List[str]:
        """
        Gets features from data, i.e. all columns except date, state, region_code, region_name, lat, long
        """
        self.features = self.data.drop(
            columns=[
                "date",
                "state",
                "region_code",
                "region_name",
                "lat",
                "long",
            ]
        ).columns.tolist()
        return self.features


    def calculate_delta(self, data, feature: str):
        suffix = "delta"
        data[f"{feature}_{suffix}"] = data[feature].diff()
        self.extended_features.append(f"{feature}_{suffix}")
        return data

    def calculate_growth(self, data, feature: str):
        suffix = "growth"
        yesterday_val = data[feature].shift()
        data[f"{feature}_{suffix}"] = (
                data[feature] / yesterday_val
            )
        self.extended_features.append(f"{feature}_{suffix}")
        return data


    def aggregate_data(self):
        self.extended_features = self.features.copy()
        self.aggregated_data = self.data.groupby("date", as_index=False).sum()
        for feature in self.features:
            self.aggregated_data = self.calculate_delta(self.aggregated_data, feature)
            self.aggregated_data = self.calculate_growth(self.aggregated_data, feature)
        self.aggregated_data = self.aggregated_data.dropna()
        return self.aggregated_data


    def get_total_regions_data(self):
        self.total_regions_data = self.data.groupby(
            ["date", "region_name"], as_index=False
        ).sum()
        return self.total_regions_data


    def get_regions_data(self):
        self.regions_data = self.total_regions_data.groupby("region_name")
        return self.regions_data


    def get_regions_list(self):
        self.regions_list = self.data["region_name"].unique().tolist()
        return self.regions_list


    def get_selected_regions_data(self, regions: List[str]):
        _selected_regions = self.total_regions_data[
            self.total_regions_data["region_name"].isin(regions)
        ]
        regions_array = []
        for _, region in _selected_regions.groupby("region_name"):
            region = region.sort_values("date")
            for feature in self.features:
                region = self.calculate_delta(region, feature)
                region = self.calculate_growth(region, feature)
            regions_array.append(region)
        return pd.concat(regions_array).reset_index(drop=True)


    def formatter(self, name: str, suffix: str = "") -> str:
        if suffix == "":
            return self.t.get(f"{name}")
        return " - ".join([
                self.t.get(f"{name}"),
                self.t.get(f"suffix_{suffix}")
            ])


    def generate_global_chart(self,
        data: pd.DataFrame,
        feature: str,
        suffix: str,
        scale: alt.Scale,
        title: str,
        padding: int = 5,
        width: int = 700,
        height: int = 500,
    ):
        y_axis = feature if suffix == "" else f"{feature}_{suffix}"
        return (
            alt.Chart(data)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title=title),
                y=alt.Y(f"{y_axis}:Q",
                    title=self.formatter(feature, suffix), scale=scale),
                tooltip=[
                    alt.Tooltip(f"{feature}", title=self.formatter(feature)),
                    alt.Tooltip("date", title=self.t.str_date, type="temporal"),
                ],
            )
            .configure_scale(continuousPadding=padding)
            .properties(width=width, height=height)
            .interactive()
        )


    def generate_regional_chart(self,
        data: pd.DataFrame,
        feature: str,
        suffix: str,
        scale: alt.Scale,
        title: str,
        alt_title: str,
        padding: int = 5,
        width: int = 700,
        height: int = 500,
        legend_position: str = "top-left",
    ):
        y_axis = feature if suffix == "" else f"{feature}_{suffix}"
        return (
            alt.Chart(data)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title=title),
                y=alt.Y(f"{y_axis}:Q", title=self.formatter(feature, suffix), scale=scale),
                color=alt.Color("region_name:N", title=alt_title),
                tooltip=[
                    alt.Tooltip("region_name", title=alt_title),
                    alt.Tooltip(f"{feature}", title=self.formatter(feature, suffix)),
                    alt.Tooltip("date", title=self.t.str_date, type="temporal"),
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
