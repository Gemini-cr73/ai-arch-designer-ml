# 🏗️ AI Architecture Designer (ML-First Decision Support)

**An Applied Machine Learning System for Empirical Software Architecture Decision Support**

AI Architecture Designer investigates whether **supervised machine learning models** trained on **real labeled engineering datasets** can provide **empirically evaluable decision support** for early-stage software architecture design.

> ⚠️ This project is **ML-first**.  
> The UI and LLM components exist **only to present ML results**, not to replace them.

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/ML-Scikit--Learn-00427E?style=for-the-badge&logo=scikitlearn" />
  <img src="https://img.shields.io/badge/LLM-Groq_(Optional_Post--ML)-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Cloud-Railway-0B0D0E?style=for-the-badge" />
</p>

## 🌐 Live App URLs

- **UI (Streamlit):** https://ai-architecture-designer.streamlit.app  
- **API (FastAPI):** https://ai-arch-designer-ml-production.up.railway.app  
- **API Docs (Swagger):** https://ai-arch-designer-ml-production.up.railway.app/docs  
- **Health Check:** https://ai-arch-designer-ml-production.up.railway.app/health  

> These interfaces are provided for **demonstration and reproducibility**.  
> The primary contribution of this project is the **machine learning models and their evaluation**, not the UI.

## 📌 Project Motivation

Early software architecture decisions are **high-impact and difficult to reverse**, yet they are often made using informal heuristics or prior experience.

This project explores whether **supervised machine learning** can provide **consistent, measurable, and reproducible decision support**.

## 📂 Datasets (Used Independently — Required)

This project uses **real labeled datasets** for empirical ML evaluation.

- NASA PROMISE (Defect Prediction)
- Google Cluster Data (System Behavior Signals)
- NASA Benchmark Collection (Robustness Study)

> Datasets are **NOT merged**. Each defines its own supervised task.

## 🧠 Machine Learning Contributions

| Algorithm | Purpose |
|----------|--------|
| Logistic Regression | Baseline |
| Random Forest | Primary model |
| SVM | Comparative model |

Evaluation includes:
- Accuracy
- Precision / Recall
- F1 Score
- ROC-AUC

## 📊 Experimental Evaluation

- Confusion matrices
- ROC curves
- Model comparisons
- Dataset-specific experiments

All experiments are **reproducible**.

## 🧠 Role of the LLM (IMPORTANT)

A hosted LLM via **Groq API** is used **only AFTER ML**.

### ❌ NOT used for:
- Training
- Prediction
- Evaluation

### ✅ ONLY used for:
- Formatting outputs
- Generating readable architecture plans

The ML pipeline works **independently of the LLM**.

## 🏗️ System Architecture

### ML-First Pipeline

1. Input → Feature Engineering  
2. ML Models → Predictions  
3. Evaluation → Metrics  
4. (Optional) LLM → Formatting  
5. UI / API → Output  

## 🖼️ Screenshots

![UI Dashboard](docs/screenshots/ui-dashboard-v2.png)  
![API Docs](docs/screenshots/api-docs-v2.png)

## 🗂️ Repository Structure

```text
data/        # datasets
artifacts/   # trained models + outputs
app/         # FastAPI + ML pipeline
ui/          # Streamlit frontend
docker/      # container setup
docs/        # diagrams + screenshots
scripts/     # training scripts
