# 🏗️ AI Architecture Designer

ML + LLM system that converts a project idea into a full software architecture — including  
structured plans, diagrams, repository scaffolds, and cloud deployment templates.

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/ML-Scikit--Learn-00427E?style=for-the-badge&logo=scikitlearn" />
  <img src="https://img.shields.io/badge/LLM-Ollama_Local-000000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Cloud-Azure_App_Service-0078D4?style=for-the-badge&logo=microsoftazure" />
</p>

---

## 🎯 Purpose of the Project

This project demonstrates how **machine learning models and agentic LLM systems can work together**
to design production-ready software architectures automatically.

It is built as both:

- ✅ an **Applied Machine Learning project** (explicit trained models + metrics)
- ✅ a **cloud-ready AI engineering system** (APIs, diagrams, repo generation, deployment templates)

This is not prompt-only automation — it is a **hybrid ML + LLM decision system**.

---

## ✅ What It Does

### 🧠 ML Preview Engine
- Predicts architecture pattern (monolith, microservices, data platform, ML system)
- Estimates system complexity and deployment risk
- Recommends infrastructure components

### 🤖 LLM Architecture Planner
- Converts project intent into structured JSON architecture plans
- Validated using strict Pydantic schemas
- Designed for deterministic downstream automation

### 📐 Diagram Generator
- Creates Mermaid flow and component diagrams
- Rendered directly in the UI

### 🧱 Repository Scaffold Generator
- Produces folder trees and boilerplate templates
- Optional Docker + GitHub Actions
- Downloadable ZIP project starter

### ☁️ Cloud Deployment Templates
- Azure App Service guidance
- Docker-based deployment layouts

### 🔁 Feedback Loop (ML)
- Captures user ratings
- Supports future retraining and evaluation

---

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
- Encoded cloud + infra attributes

---

## 🏗️ System Architecture

### Production Architecture

> Same production model as AI Market Coach — UI and API deployed as separate containers on Azure App Service behind Cloudflare.

![Production Architecture](docs/screenshots/architecture-prod.png)

### High-Level Flow

1. User submits project idea via Streamlit UI
2. ML models generate preview + confidence metrics
3. LLM planner produces structured architecture JSON
4. Services generate diagrams, scaffolds, and deployment templates
5. ZIP starter project is downloadable

---

## 🖼️ App Preview

### Streamlit UI
![UI Dashboard](docs/screenshots/ui-dashboard.png)

### API Documentation (Swagger)
![API Docs](docs/screenshots/api-docs.png)

### Demo Walkthrough
![Demo](docs/screenshots/demo.gif)

---

## 🚀 Local Development

### 1. Start Docker Services

```powershell
docker compose -f docker/docker-compose.yml up --build
