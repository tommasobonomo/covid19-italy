FROM python:3.8-slim-buster

MAINTAINER bigo@crisidev.org

RUN apt-get update && \
        apt-get install --no-install-recommends -y ca-certificates curl build-essential zlib1g-dev && \
        mkdir /app && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY . /app/
RUN /app/setup.sh
EXPOSE 8501

CMD ["streamlit", "run", "/app/src/COVID-19-Italy.py"]
