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
    return " ".join(name.capitalize().split("_"))
