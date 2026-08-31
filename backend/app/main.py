from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import predict, versions, monitoring, ab_testing

# APP CONFIGURATION

app = FastAPI(
    title="NephroSense API",
    description="""
NephroSense is an AI-powered clinical decision support system designed to assist
nephrologists and healthcare professionals in early detection and staging of
**Chronic Kidney Disease (CKD)**.

---

### What Does NephroSense Do?
- Predicts CKD stage (0-5) from 26 patient features
- Provides **SHAP-based explainability** — why this prediction was made
- Supports **Model Governance** with Champion/Challenger framework
- Enables **A/B Testing** between model versions
- Delivers **stage-specific recommendations** for clinical decision-making

---

### Models Available
| Version | Model | Role |
|---------|-------|------|
| V2 | XGBoost Classifier | Champion — Production |
| V3 | XGBoost Tuned | Challenger — Staging |

---

### CKD Stages Covered
| Stage | GFR Range | Description |
|-------|-----------|-------------|
| Stage 0 | Normal | Healthy — No CKD |
| Stage 1 | >= 90 | Mild — Kidney damage, normal filtering |
| Stage 2 | 60-89 | Mild-Moderate — Slight reduction |
| Stage 3 | 30-59 | Moderate — Noticeable reduction |
| Stage 4 | 15-29 | Severe — Significant damage |
| Stage 5 | < 15 | Kidney Failure — Immediate intervention |

---

### Disclaimer
> This system is an AI/ML decision support tool.
> All predictions must be verified by a qualified nephrologist.
> Not a substitute for professional medical advice.

---

### Developer
**Mushahid Hussain**

- GitHub: [mushahidhussainleel](https://github.com/mushahidhussainleel/NephroSense)
- Email: [mushahidh442007@gmail.com](mailto:mushahidh442007@gmail.com)
    """,
    version="1.0.0",
   
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
     allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HOME PAGE

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("app/templates/home.html", "r", encoding="utf-8") as f:
        return f.read()

# ROUTES

app.include_router(predict.router, tags=["Prediction"])
app.include_router(versions.router, tags=["Model Versions"])
app.include_router(monitoring.router, tags=["Monitoring"])
app.include_router(ab_testing.router, tags=["A/B Testing"])