FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/ /requirements/
COPY services/decision_engine/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/decision_engine/src/ ./src/

WORKDIR /app/src

EXPOSE 8000

CMD ["python", "main.py"]