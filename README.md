# 🏗️ AI Architecture Designer (ML-First Decision Support)

**An Applied Machine Learning System for Empirical Software Architecture Decision Support**

AI Architecture Designer investigates whether **supervised machine learning models** trained on **real labeled engineering datasets** can provide **empirically evaluable decision support** for early-stage software architecture design. Natural-language project descriptions are accepted as inputs, but the **core contribution is ML training + evaluation**, not an LLM agent.

> ⚠️ This project is **ML-first**.  
> The UI and LLM components exist **only to present ML results**, not to replace them.

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/ML-Scikit--Learn-00427E?style=for-the-badge&logo=scikitlearn" />
  <img src="https://img.shields.io/badge/LLM-Groq_API_(Optional_Post--ML)-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Cloud-Azure_App_Service-0078D4?style=for-the-badge&logo=microsoftazure" />
</p>

## 🌐 Live App URLs

- **UI (Streamlit):** https://arch.ai-coach-lab.com  
- **API (FastAPI):** https://arch-api.ai-coach-lab.com  
- **API Docs (Swagger):** https://arch-api.ai-coach-lab.com/docs  
- **Health:** https://arch-api.ai-coach-lab.com/health  

> These interfaces are provided for **demonstration and reproducibility**.  
> The primary contribution of this project is the **machine learning models and their evaluation**, not the UI.

## 📌 Project Motivation

Early software architecture decisions are **high-impact and difficult to reverse**, yet they are often made using informal heuristics or prior experience.

Modern systems introduce additional complexity through:
- cloud platforms
- data pipelines
- machine learning components

This project explores whether **supervised machine learning** can provide **consistent, measurable, and reproducible decision support** for these early design choices.

## 📂 Datasets (Professor Requirement: Used Independently)

This project uses **real labeled datasets** so that models can be **trained and evaluated empirically** (train/validation/test splits).  
**Important:** Per professor requirement, these datasets are **NOT merged** and are **not assumed to share identical features or targets**.  
Each dataset defines its **own supervised task**, and algorithms are compared **within-dataset only**. Cross-dataset analysis is treated as a **robustness/generalization study**.

- **NASA PROMISE Software Defect Dataset (MW1)**  
  Software module metrics (e.g., McCabe/Halstead-style metrics) with **defect labels** used for supervised learning evaluation.  
  Source: https://openscience.us/repo/defect/mccabehalsted/mw1.html

- **Google Cluster Workload Traces (Google Cluster Data)**  
  Large-scale workload traces (resource usage / scheduling behavior) used to derive **system behavior and complexity signals** for a dataset-specific supervised task.  
  Source: https://github.com/google/cluster-data

- **NASA Benchmark Defect Dataset Collection (Mendeley)**  
  Multi-dataset benchmark collection used for **robustness testing and cross-dataset evaluation** (without merging).  
  Source: https://data.mendeley.com/datasets/923xvkk5mm/1

> Dataset usage is documented under `data/` (raw/processed) and experiment scripts produce reproducible artifacts.

## 🎯 Research Questions

This project addresses the following applied ML questions:

- Can supervised ML models learn architecture decision signals using labeled engineering datasets?
- How do non-linear models compare to interpretable baselines within each dataset?
- How robust are model behaviors under cross-dataset evaluation (generalization study)?
- How do learned ML models compare against explicit **baseline methods**?

The emphasis is on **evaluation, comparison, and interpretability**, consistent with graduate-level applied ML expectations.

## 🧠 Machine Learning Contributions (Core)

### Algorithms Evaluated (Within Each Dataset)

| Algorithm | Purpose |
|---------|--------|
| Logistic Regression | Interpretable baseline |
| Random Forest | Non-linear ensemble |
| Support Vector Machine (SVM) | High-dimensional feature modeling |

Multiple algorithms are used to:
- establish baselines
- justify performance claims
- meet empirical ML standards

## 📊 Learning Tasks & Metrics

The project supports dataset-specific supervised tasks. Current emphasis is on **classification evaluation**; additional tasks may be added as extensions.

| Task | Model Type | Metrics |
|----|----------|--------|
| Defect / Label Prediction (per dataset) | Classification | Accuracy, Precision, Recall, F1, ROC-AUC |
| Baseline Comparison | Control Models | Relative performance |

All models use **train / validation / test splits** and consistent evaluation protocols.

## 🧩 Feature Engineering

Features are derived from:
- encoded system attributes (scale, data intensity, cloud usage)
- structured metadata indicators
- dataset-driven engineering metrics (software metrics and workload signals)
- vectorized text fields (where applicable)

Baseline feature pipelines are implemented for comparison.

## 📈 Experimental Evaluation

Evaluation artifacts include:
- confusion matrices
- ROC curves
- baseline vs ML model comparisons
- summary tables of metrics across algorithms

All experiments are **reproducible** using scripts in this repository.

## 🧠 Role of the LLM (Clarification)

A hosted LLM via the **Groq API** is used **only after ML inference**.

### The LLM is NOT used for:
- learning
- prediction
- model training
- evaluation
- optimization

### The LLM is used only for:
- formatting ML outputs into structured architecture plans
- enforcing schema validity
- improving human readability

The LLM can be removed without affecting ML results.

## 🏗️ System Architecture

### High-Level ML-First Flow

1. User submits a project description  
2. Feature extraction pipeline processes input  
3. ML models generate predictions and confidence scores  
4. Optional planner formats results (LLM post-processing only)  
5. Outputs are displayed via API and UI  

## 📐 Production Architecture Diagram

![Production Architecture](docs/screenshots/architecture-prod.png)

> Mermaid source: `docs/diagrams/architecture-prod.mmd`

## 🖼️ Application Screenshots

### Streamlit UI — Architecture Recommendations

![Streamlit UI](docs/screenshots/ui-dashboard.png)

### Streamlit UI — Continued View

![Streamlit UI Continued](docs/screenshots/ui-dashboard-continues.png)

### FastAPI — Swagger Documentation

![API Docs](docs/screenshots/api-docs.png)

## 🗂️ Repository Structure (Course-Relevant)

```text
data/           # Datasets and documentation (raw/processed)
artifacts/      # Models, preprocessors, metrics/results.json
app/            # FastAPI backend + ML pipeline + schemas
ui/             # Streamlit UI (demonstration only)
docs/           # Diagrams and screenshots
docker/         # Reproducible environment
scripts/        # Training/evaluation utilities
tests/          # (optional) tests for core logic
