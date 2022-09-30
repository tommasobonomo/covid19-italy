# COVID-19 in Italy

Quick Streamlit dashboard to visualise the impact of COVID-19 in Italy

## Demos

Hosted with Streamlit at this [link](https://share.streamlit.io/tommasobonomo/covid19-italy/src/COVID-19-Italy.py).

## Install and run

- Clone the repository
- `pip install -r requirements.txt`
- `streamlit run src/COVID-19-Italy.py`

## Docker
A docker image for x86 is available here: [hub.docker.com/repository/docker/tommasobonomo/covid19-italy](https://hub.docker.com/repository/docker/tommasobonomo/covid19-italy):

```sh
docker run -p 8501:8501 tommasobonomo/covid19-italy
```

## Attribution

All the data displayed in this dashboard is provided by the Italian Ministry of Health (Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
