# Run from repo root:  .\scripts\new-dockerfiles.ps1
# Creates: Dockerfile.api, Dockerfile.ui, docker-compose.yml

$ErrorActionPreference = "Stop"

# Safety check: must be run at repo root
if (!(Test-Path ".\app")) {
  Write-Host "ERROR: I don't see an .\app folder here. Run this from the repo root." -ForegroundColor Red
  exit 1
}

@'
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .

COPY . .

EXPOSE 8000
CMD ["bash", "-lc", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
'@ | Set-Content -Encoding UTF8 .\Dockerfile.api


@'
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .

COPY . .

EXPOSE 8501
CMD ["bash", "-lc", "streamlit run app/ui/streamlit_app.py --server.address 0.0.0.0 --server.port ${PORT:-8501}"]
'@ | Set-Content -Encoding UTF8 .\Dockerfile.ui


@'
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      - ENVIRONMENT=prod
    ports:
      - "8000:8000"

  ui:
    build:
      context: .
      dockerfile: Dockerfile.ui
    environment:
      - ENVIRONMENT=prod
      - API_BASE_URL=http://api:8000
    depends_on:
      - api
    ports:
      - "8501:8501"
'@ | Set-Content -Encoding UTF8 .\docker-compose.yml

Write-Host "Created Dockerfile.api, Dockerfile.ui, docker-compose.yml" -ForegroundColor Green
