# 🏗️ AI Architecture Designer (ML-Enhanced)

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

- **ML Preview**
  - Predicts architecture pattern (e.g., monolith, microservices, data pipeline, ML platform)
  - Estimates system complexity and deployment risk
  - Recommends components (databases, queues, APIs, auth, observability)

- **LLM Planner**
  - Produces structured, schema-validated architecture JSON
  - Converts user intent into detailed system designs

- **Diagram Generator**
  - Builds Mermaid flow and component diagrams
  - Exports SVG/PNG for documentation

- **Repository Scaffold Generator**
  - Creates folder trees and boilerplate files
  - Exports ZIP starter projects

- **Cloud Deployment Templates**
  - Azure App Service deployment guidance
  - Docker + CI-friendly layouts

- **Feedback Loop (ML)**
  - Stores user ratings
  - Enables future retraining and evaluation

---

## 🧠 Machine Learning Components

| Model | Goal | Metrics |
|--------|------|--------|
| Architecture Pattern Classifier | Predict overall system type | Accuracy, F1 |
| Component Recommender | Suggest infra + services | Precision@K |
| Risk / Complexity Regressor | Estimate deployment difficulty | RMSE, R² |
| Feedback Loop | Improve future predictions | Lift vs baseline |

Features include:
- Text embeddings
- Graph-derived architecture features
- Encoded infra characteristics

---

## 🏗️ System Architecture

### Production Architecture
![Production Architecture](docs/screenshots/architecture-prod.png)

### High-Level Flow

1. User submits project idea via UI
2. ML models generate architecture preview and confidence
3. LLM planner produces structured architecture JSON
4. Services generate diagrams, scaffolds, and deploy templates
5. Outputs are downloadable and stored for feedback

---

## 🖼️ App Preview

### Streamlit UI
![UI Dashboard](docs/screenshots/ui-dashboard.png)

### API Documentation (Swagger)
![API Docs](docs/screenshots/api-docs.png)

### Demo Walkthrough
![Demo](docs/screenshots/demo.gif)

---

## 📁 Project Structure


