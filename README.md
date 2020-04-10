# COVID-19 in Italy

Quick streamlit dashboard to visualise the impact of COVID-19 in Italy

## Demos

* Deployed on Heroku at this [link](https://covid19italy.herokuapp.com/).
* This other [deployment](https://covid19italy.crisidev.org/) is hosted by @crisidev on a more powerful machine.

## Install and run

- Clone the repository
- `pip install -r requirements.txt`
- `streamlit run src/COVID-19-Italy.py`

## Docker
A docker image for x86 is available [here](https://hub.docker.com/r/crisidev/covid19-italia):

```sh
docker run -p 8501:8501 crisidev/covid19-italia:linux-x86
```

## Attribution

All the data displayed in this dashboard is provided by the Italian Ministry of Health (Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
