FROM python:3.11-slim

# ENVIRONMENT
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# WORKDIR
WORKDIR /app

# INSTALL SYSTEM PACKAGES
RUN apt-get update && apt-get install -y curl gcc default-libmysqlclient-dev pkg-config && rm -rf /var/lib/apt/lists/*

# COPY REQUIREMENTS
COPY requirements/ /requirements/
COPY services/ingestion_service/requirements.txt .

# INSTALL PYTHON DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

# COPY PROJECT
COPY shared/ ./shared/
COPY services/ ./services/
COPY envs/ ./envs/

# EXPOSE PORT
EXPOSE 8000

# START SERVICE
CMD ["uvicorn", "services.ingestion_service.src.main:app", "--host", "0.0.0.0", "--port", "8000"]