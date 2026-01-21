# 🏗️ AI Architecture Designer (ML + LLM)

ML + LLM system that converts a project idea into a full software architecture — including structured plans, diagrams, repository scaffolds, and cloud deployment templates.

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/ML-Scikit--Learn-00427E?style=for-the-badge&logo=scikitlearn" />
  <img src="https://img.shields.io/badge/LLM-Ollama_Local-000000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Cloud-Azure_App_Service-0078D4?style=for-the-badge&logo=microsoftazure" />
</p>

## 🎯 Purpose of the Project

This project demonstrates how **trained ML models** and an **agentic LLM planner** can work together to generate production-ready software architectures automatically.

It is built as both:

- ✅ an **Applied Machine Learning project** (explicit trained models + metrics)
- ✅ a **cloud-ready AI engineering system** (APIs, diagrams, repo generation, deployment templates)

This is not prompt-only automation — it is a **hybrid ML + LLM decision system**.

## ✅ What It Does

### 🧠 ML Preview Engine
- Predicts an architecture pattern (monolith, microservices, data platform, ML system)
- Estimates complexity and deployment risk with confidence metrics
- Recommends core components (DB, queue, auth, observability)

### 🤖 LLM Architecture Planner
- Produces **schema-validated** architecture plans (Pydantic)
- Converts user intent into deterministic structured JSON

### 📐 Diagram Generator (Mermaid)
- Produces flow and component diagrams
- Rendered directly in the UI

### 🧱 Repository Scaffold Generator
- Generates starter folder trees and boilerplate templates
- Optional Docker and GitHub Actions templates
- Downloadable ZIP project scaffold

### ☁️ Cloud Deployment Templates
- Azure App Service deployment layouts and guidance
- Docker-based production containers

### 🔁 Feedback Loop (ML)
- Captures user feedback
- Enables future retraining and evaluation

## 🧠 Machine Learning Components

| Model | Goal | Metrics |
|--------|------|--------|
| Architecture Pattern Classifier | Predict overall system type | Accuracy, F1 |
| Component Recommendation Model | Suggest infra/services | Precision@K |
| Risk & Complexity Regressor | Estimate deployment difficulty | RMSE, R² |
| Feedback Learning Loop | Improve future predictions | Lift vs baseline |

### Feature Sources
- Text embeddings from project descriptions  
- Graph-derived architecture features  
- Encoded cloud and infrastructure attributes  

## 🏗️ System Architecture

### Production Architecture

Mermaid source (version controlled):

- `docs/diagrams/architecture-prod.mmd`

Rendered image used by GitHub README:

- `docs/screenshots/architecture-prod.png`

![Production Architecture](docs/screenshots/architecture-prod.png)

> Same production model as AI Market Coach:  
> **Streamlit UI and FastAPI API are deployed as separate containers on Azure App Service behind Cloudflare.**

### High-Level Flow

1. User enters a project idea in Streamlit UI
2. ML preview models generate pattern + confidence metrics
3. LLM planner produces schema-valid architecture JSON
4. Services generate Mermaid diagrams, scaffold trees, and ZIP starter
5. Outputs are shown in the UI and downloadable

## 🖼️ App Preview

### Streamlit UI
![UI Dashboard](docs/screenshots/ui-dashboard.png)

### API Documentation (Swagger)
![API Docs](docs/screenshots/api-docs.png)

### Demo Walkthrough
![Demo](docs/screenshots/demo.gif)

## 📁 Project Structure

```text
app/
 ├─ api/                 # FastAPI routes
 ├─ agents/              # LLM planner agents
 ├─ core/schemas/        # Pydantic contracts
 ├─ ml/                  # Models, features, inference
 ├─ services/            # Diagram + scaffold generators
 └─ main.py

ui/
 └─ streamlit_app.py     # Streamlit frontend

docs/
 ├─ diagrams/architecture-prod.mmd
 └─ screenshots/*.png

docker/
 ├─ Dockerfile.api
 ├─ Dockerfile.ui
 └─ docker-compose.yml
