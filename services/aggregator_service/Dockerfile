FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /requirements/
COPY services/aggregator_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/aggregator_service/src/ ./src/

WORKDIR /app/src

EXPOSE 8000

CMD ["python", "main.py"]