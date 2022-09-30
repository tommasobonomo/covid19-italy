FROM python:3.10-slim-buster

RUN mkdir /app && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install -U pip && pip install -r /tmp/requirements.txt

COPY . /app/
WORKDIR /app
EXPOSE 8501

CMD ["streamlit", "run", "--server.port", "8501", "src/COVID-19-Italy.py"]
