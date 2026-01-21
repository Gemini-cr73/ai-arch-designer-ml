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

- **ML Preview Engine**
  - Predicts an architecture pattern (monolith, microservices, data platform, ML system)
  - Estimates complexity / risk with confidence metrics
  - Recommends core components (DB, queue, auth, observability)

- **LLM Architecture Planner**
  - Produces a **schema-validated** architecture plan (Pydantic)
  - Converts user intent into deterministic structured JSON

- **Diagram Generator (Mermaid)**
  - Produces flow/component diagrams
  - Rendered directly in the UI

- **Repository Scaffold Generator**
  - Generates a starter folder tree + boilerplate templates
  - Optional Docker + GitHub Actions
  - Downloads a ZIP scaffold

- **Cloud Deployment Templates**
  - Azure App Service deployment layout + guidance

- **Feedback Loop (ML)**
  - Captures user feedback for future retraining/evaluation

## 🧠 Machine Learning Components

| Model | Goal | Metrics |
|------|------|---------|
| Architecture Pattern Classifier | Predict overall system type | Accuracy, F1 |
| Component Recommendation Model | Suggest infra/services | Precision@K |
| Risk & Complexity Regressor | Estimate deployment difficulty | RMSE, R² |
| Feedback Learning Loop | Improve future predictions | Lift vs baseline |

**Feature sources**
- Text embeddings from project descriptions  
- Graph-derived architecture features  
- Encoded cloud + infra attributes  

## 🏗️ System Architecture

### Production Architecture

Mermaid source lives here (version-controlled):

- `docs/diagrams/architecture-prod.mmd`

Rendered image used by GitHub README:

- `docs/screenshots/architecture-prod.png`

![Production Architecture](docs/screenshots/architecture-prod.png)

### High-Level Flow

1. User enters a project idea in Streamlit UI
2. ML preview generates pattern + confidence metrics
3. LLM planner produces schema-valid architecture JSON
4. Services generate Mermaid diagram + scaffold tree + ZIP
5. Outputs are shown in the UI and downloadable

## 🖼️ App Preview

### Streamlit UI
![UI Dashboard](docs/screenshots/ui-dashboard.png)

### API Documentation (Swagger)
![API Docs](docs/screenshots/api-docs.png)

### Demo Walkthrough
![Demo](docs/screenshots/demo.gif)

## 🚀 Local Development (Docker)

### ✅ Local URLs

- **UI:** http://localhost:8501  
- **API:** http://localhost:8000  
- **Docs:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  

### 1) Start services

```powershell
docker compose -f docker/docker-compose.yml up --build


