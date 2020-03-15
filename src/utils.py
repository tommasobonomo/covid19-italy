import pandas as pd
from typing import List


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
    if name == "people_in_ICU":
        return "People in ICU"
    else:
        return " ".join(name.capitalize().split("_"))


def dataframe_translator(data: pd.DataFrame) -> pd.DataFrame:
    """
    Translates Italian columns into English
    """

    feature_mapping = {
        "ricoverati_con_sintomi": "hospitalised_with_symptoms",
        "terapia_intensiva": "people_in_ICU",
        "totale_ospedalizzati": "total_hospitalised",
        "isolamento_domiciliare": "people_in_domestic_isolation",
        "totale_attualmente_positivi": "total_of_current_positives",
        "nuovi_attualmente_positivi": "new_current_positives",
        "dimessi_guariti": "people_discharged_and_recovered",
        "deceduti": "deaths",
        "totale_casi": "total_cases",
        "tamponi": "total_tests",
    }

    data.columns = [
        feature_mapping[feature] if feature in feature_mapping else feature
        for feature in data.columns
    ]

    return data
