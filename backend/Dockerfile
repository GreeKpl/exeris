FROM python:3.9.0-buster

WORKDIR /app/

COPY requirements.txt /app/

RUN apt update \
    && apt install -y libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

CMD ["python", "run.py"]
