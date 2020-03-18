# COVID-19 in Italy

Quick streamlit dashboard to visualise the impact of COVID-19 in Italy

## Demos

* Check out this [link](http://covid19italy.herokuapp.com/), it is quite a bit slow as it's hosted on Heroku's free tier.
* This other [link](https://covid19italy.crisidev.org/) is available on a more powerful machine.

## Install and run

- Clone the repository
- `pip install -r requirements.txt`
- `PORT=8501 ./setup.sh`
- `streamlit run src/COVID-19-Italy.py`

## Docker

A docker image for x86 is available [here](https://hub.docker.com/r/crisidev/covid19-italia):

```sh
docker run -p 8501:8501 crisidev/covid19-italia:linux-x86
```

## Translations

Adding/managing languages can be done without recompile the code.
Inside folde *src/translations* there is a file called ***lang_mapping.yml***. It contains on each line a mapping in the form

> `<language_name>: <language_file`

where:

- **language_name** is the one shown in the language radio selection
- **language_file** is the name *without extension* of the file that contains the translation variables


## Attribution

All the data displayed in this dashboard is provided by the Italian Ministry of Health (Ministero della Salute) and elaborated by Dipartimento della Protezione Civile. This work is therefore a derivative of [COVID-19 Italia - Monitoraggio situazione](https://github.com/pcm-dpc/COVID-19) licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
