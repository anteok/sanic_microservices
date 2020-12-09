FROM python:3.8-alpine

WORKDIR /app

RUN apk add postgresql-dev \
            musl-dev \
            cmake \
            automake \
            gcc \
            g++ \
            libc-dev \
            build-base

COPY users/requirements.txt /app
RUN pip install -r requirements.txt

COPY offers/backends /app/backends
COPY offers/server.py /app
COPY base/tables.py /app
COPY base/db_connector.py /app

RUN export PYTHONPATH=/app
CMD ["python", "server.py"]
