# NephroSense — CKD Stage Prediction System

AI-powered Chronic Kidney Disease stage prediction with SHAP explainability and model governance.

---

## Tech Stack

**Backend:** FastAPI, XGBoost, SHAP, MLflow, Scikit-learn  
**Frontend:** HTML, CSS, JavaScript, Nginx  
**DevOps:** Docker, Docker Compose

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

## Key Features

- CKD Stage prediction (Stage 0–5) from 26 clinical features
- SHAP-based explainability with waterfall plots
- Champion/Challenger model governance (V2 vs V3)
- A/B Testing between model versions
- Admin panel with switch & rollback
- Dockerized deployment

---

## Quick Start

```bash
# Clone repo
git clone https://github.com/mushahidhussainleel/NephroSense.git
cd NephroSense

# Setup .env
cp .env.example .env
# Add your NEPHROSENSE_ADMIN_KEY

# Run with Docker
docker-compose up --build
```

**Frontend:** http://localhost  
**Backend:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

---

## Model Performance

| Model | Accuracy | F1 Score | Role |
|-------|----------|----------|------|
| V2 XGBoost | 98.62% | 98.61% | Champion |
| V3 XGBoost Tuned | 98.50% | 98.49% | Challenger |

---

## Developer

**Mushahid Hussain**  
GitHub: [mushahidhussainleel](https://github.com/mushahidhussainleel)  
Email: mushahidh442007@gmail.com

> Full documentation will be updated after deployment.