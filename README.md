# NephroSense — CKD Stage Prediction System

> AI-powered Chronic Kidney Disease stage prediction with SHAP explainability, Model Governance, A/B Testing, and a full-stack deployed web application.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://nephro-sense-nine.vercel.app)
[![Backend API](https://img.shields.io/badge/Backend%20API-Railway-purple?style=for-the-badge&logo=railway)](https://nephrosense-production.up.railway.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green?style=for-the-badge&logo=swagger)](https://nephrosense-production.up.railway.app/docs)
[![GitHub](https://img.shields.io/badge/GitHub-mushahidhussainleel-black?style=for-the-badge&logo=github)](https://github.com/mushahidhussainleel/NephroSense)

---

## What is NephroSense?

NephroSense is a production-level AI system designed to assist nephrologists and healthcare professionals in early detection and staging of **Chronic Kidney Disease (CKD)**. It accepts 26 clinical features from a patient and predicts the CKD stage (0–5), along with SHAP-based explainability showing which features contributed most to the prediction.

---

## Live Links

| Service | URL |
|---------|-----|
| Frontend App | https://nephro-sense-nine.vercel.app |
| Backend API | https://nephrosense-production.up.railway.app |
| API Documentation | https://nephrosense-production.up.railway.app/docs |
| GitHub Repository | https://github.com/mushahidhussainleel/NephroSense |

---

## Key Features

- **CKD Stage Prediction** — Predicts Stage 0 to Stage 5 from 26 patient features
- **SHAP Explainability** — Waterfall plots showing which features influenced the prediction
- **Model Governance** — Champion (V2) vs Challenger (V3) framework with MLflow tracking
- **A/B Testing** — Compare V2 XGBoost vs V3 XGBoost Tuned on same patient data
- **Admin Panel** — Switch model versions and manual rollback via protected API
- **Stage Recommendations** — Clinical advice per predicted stage
- **Medical Disclaimer** — Built-in AI disclaimer for responsible use
- **Dockerized** — Docker + Docker Compose ready for deployment

---

## CKD Stages

| Stage | GFR Range | Description |
|-------|-----------|-------------|
| Stage 0 | Normal | Healthy — No CKD detected |
| Stage 1 | >= 90 | Mild — Kidney damage with normal filtering |
| Stage 2 | 60-89 | Mild-Moderate — Slight reduction in function |
| Stage 3 | 30-59 | Moderate — Noticeable reduction |
| Stage 4 | 15-29 | Severe — Significant damage |
| Stage 5 | < 15 | Kidney Failure — Immediate intervention required |

---

## Model Performance

| Version | Model | Accuracy | F1 Weighted | Role |
|---------|-------|----------|-------------|------|
| V1 | Random Forest | 98.12% | 97.88% | Baseline |
| V2 | XGBoost | 98.62% | 98.61% | Champion — Production |
| V3 | XGBoost Tuned | 98.50% | 98.49% | Challenger — Staging |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Models | XGBoost, Scikit-learn, Random Forest |
| Explainability | SHAP (Summary + Waterfall plots) |
| Experiment Tracking | MLflow |
| Backend | FastAPI, Pydantic, Uvicorn |
| Frontend | HTML5, CSS3, JavaScript, Nginx |
| Containerization | Docker, Docker Compose |
| Backend Deploy | Railway |
| Frontend Deploy | Vercel |

---

## Project Structure

```
NephroSense/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── model_loader.py
│   │   ├── templates/
│   │   └── routes/
│   │       ├── predict.py
│   │       ├── versions.py
│   │       ├── monitoring.py
│   │       └── ab_testing.py
│   ├── models/
│   ├── assets/
│   ├── notebooks/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── result.html
│   ├── ab_test.html
│   ├── admin.html
│   ├── css/
│   ├── js/
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml
├── .env
└── README.md
```

---

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| POST | `/predict/explain` | Predict CKD stage + SHAP explanation |
| GET | `/version` | Active model version |
| GET | `/metrics` | Request count metrics |
| POST | `/ab-test` | Compare V2 vs V3 on same data |

### Admin Endpoints (API Key Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/versions` | All model versions detail |
| POST | `/admin/switch-version` | Switch active model |
| POST | `/admin/rollback` | Rollback to previous version |

---

## Quick Start — Local

```bash
# Clone repo
git clone https://github.com/mushahidhussainleel/NephroSense.git
cd NephroSense

# Setup environment
cp .env.example .env
# Add: NEPHROSENSE_ADMIN_KEY=your_secret_key

# Run with Docker
docker-compose up --build

# Access
# Frontend: http://localhost
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Notebooks

| Notebook | Description |
|----------|-------------|
| 01_eda_and_preprocessing.ipynb | Data exploration, cleaning, feature engineering |
| 02_model_training.ipynb | Model training, MLflow tracking, SHAP analysis |

---

## SHAP Analysis

NephroSense uses SHAP (SHapley Additive exPlanations) to explain every prediction:

- **Summary Plot** — Overall feature importance across all patients
- **Waterfall Plot** — Per-patient breakdown of feature contributions

Key finding: **GFR** is the most influential feature in Stage 2 predictions, followed by Serum Creatinine and Serum Calcium.

---

## Disclaimer

> This system is an AI/ML clinical decision support tool. All predictions must be verified by a qualified nephrologist. Not a substitute for professional medical advice.

---

## Future Improvements

- Oracle Cloud deployment with Docker for permanent free hosting
- LLM integration (Gemini/Claude API) for natural language SHAP explanation
- Auto rollback when model accuracy drops below threshold
- Patient history tracking and longitudinal monitoring
- Urdu language support for local healthcare providers
- Mobile-responsive UI improvements
- Authentication system for multi-doctor access

---

## Developer

**Mushahid Hussain**


- GitHub: [mushahidhussainleel](https://github.com/mushahidhussainleel)
- LinkedIn: [mushahid-hussain-dev](https://linkedin.com/in/mushahid-hussain-dev)
- Email: mushahidh442007@gmail.com