from pydantic import BaseModel, Field
from typing import Literal, List, Dict


# INPUT SCHEMA — Raw user input

class PatientInput(BaseModel):

    # --- Lab Results (Numerical) ---
    serum_creatinine: float = Field(..., gt=0, 
        description="Serum Creatinine level in mg/dL")
    gfr: float = Field(..., gt=0, 
        description="Glomerular Filtration Rate in mL/min/1.73m²")
    bun: float = Field(..., gt=0, 
        description="Blood Urea Nitrogen in mg/dL")
    serum_calcium: float = Field(..., gt=0, 
        description="Serum Calcium level in mg/dL")
    ana: Literal["positive", "negative"] = Field(...,
    description="ANA test result")
    c3_c4: float = Field(..., gt=0, 
        description="Complement C3/C4 levels")
    hematuria: Literal["positive", "negative"] = Field(...,
    description="Blood in urine test result")
    oxalate_levels: float = Field(..., gt=0, 
        description="Urinary Oxalate levels")
    urine_ph: float = Field(..., gt=0, 
        description="Urine pH level")
    blood_pressure: float = Field(..., gt=0, 
        description="Blood Pressure in mmHg")

    # --- Lifestyle (same order as training) ---
    physical_activity: Literal["daily", "weekly", "rarely"] = Field(...,
        description="Physical activity frequency")
    water_intake: float = Field(..., gt=0,
        description="Daily water intake in Liters")
    smoking: Literal["yes", "no"] = Field(...,
        description="Smoking status")
    painkiller_usage: Literal["yes", "no"] = Field(...,
        description="Regular painkiller usage")
    family_history: Literal["yes", "no"] = Field(...,
        description="Family history of kidney disease")
    stress_level: Literal["low", "moderate", "high"] = Field(...,
        description="Daily stress level")
    months: int = Field(..., gt=0,
        description="Duration of symptoms in months")

    # --- Categorical (will be OHE encoded) ---
    diet: Literal["balanced", "high protein", "low salt"] = Field(...,
        description="Dietary pattern")
    alcohol: Literal["daily", "never", "occasionally"] = Field(...,
        description="Alcohol consumption frequency")
    weight_changes: Literal["stable", "loss", "gain"] = Field(...,
        description="Recent weight change pattern")



# OUTPUT SCHEMA — API response to user

class PredictionOutput(BaseModel):
    predicted_stage: int = Field(...,
        description="Predicted CKD Stage (0-5)")
    stage_label: str = Field(...,
        description="Human-readable stage description")
    model_version: str = Field(...,
        description="Model version used for prediction")
    confidence: float = Field(...,
        description="Model prediction confidence (0-1)")
    shap_top_features: List[Dict] = Field(...,
        description="Top 5 features that influenced prediction")
    shap_all_features: List[Dict] = Field(
        ...,
        description="All 26 features for SHAP waterfall chart"
    )
    llm_explanation: str = Field(
        ...,
        description="LLM-generated explanation of prediction"
    )
    llm_source: str = Field(
        ...,
        description="Source: gemini-2.5-flash or predefined_recommendation"
    )
    disclaimer: str = Field(
        ...,
        description="Medical disclaimer"
    )


# STAGE LABELS — Meaningful output

STAGE_LABELS = {
    0: "Stage 0 — Healthy: No Chronic Kidney Disease detected",
    1: "Stage 1 — Mild: Kidney damage with normal filtering (GFR ≥ 90)",
    2: "Stage 2 — Mild-Moderate: Slight reduction in kidney function (GFR 60–89)",
    3: "Stage 3 — Moderate: Noticeable reduction in kidney function (GFR 30–59)",
    4: "Stage 4 — Severe: Significant kidney damage, dialysis preparation may begin (GFR 15–29)",
    5: "Stage 5 — Kidney Failure: End-stage renal disease, immediate medical intervention required (GFR < 15)"
}

STAGE_RECOMMENDATIONS = {
    0: "No CKD detected. Maintain healthy lifestyle and regular checkups.",
    1: "Mild kidney damage detected. Monitor GFR regularly and consult a nephrologist.",
    2: "Slight reduction in kidney function. Reduce salt intake, control blood pressure, and consult a doctor.",
    3: "Moderate kidney damage. Immediate medical consultation recommended. Dietary restrictions may apply.",
    4: "Severe kidney damage. Urgent specialist consultation required. Dialysis preparation may be needed.",
    5: "Kidney failure detected. Immediate medical intervention required. Contact your doctor immediately."
}

STAGE_CONTEXT = {
    0: {
        "summary": "Kidneys are healthy with no signs of CKD.",
        "urgency": "No immediate action needed.",
        "advice": "Maintain a healthy lifestyle and get annual checkups."
    },
    1: {
        "summary": "Mild kidney damage but filtering is still normal.",
        "urgency": "Low urgency — monitor regularly.",
        "advice": "Stay hydrated, reduce salt intake, monitor blood pressure."
    },
    2: {
        "summary": "Slight reduction in kidney function detected.",
        "urgency": "Moderate — consult a doctor soon.",
        "advice": "Reduce protein and sodium intake. Avoid NSAIDs."
    },
    3: {
        "summary": "Noticeable reduction in kidney function (GFR 30–59).",
        "urgency": "Important — schedule nephrologist appointment soon.",
        "advice": "Strict dietary control, blood pressure management, regular labs."
    },
    4: {
        "summary": "Severe kidney damage, dialysis preparation may begin (GFR 15–29).",
        "urgency": "HIGH PRIORITY — see nephrologist urgently within days.",
        "advice": "Dialysis planning, strict fluid and potassium restrictions."
    },
    5: {
        "summary": "End-stage renal disease, kidneys nearly stopped (GFR < 15).",
        "urgency": "CRITICAL EMERGENCY — immediate intervention required.",
        "advice": "Emergency nephrology care. Dialysis or transplant needed now."
    }
}

DISCLAIMER = (
    "This prediction is generated by an AI/ML model and is not a substitute "
    "for professional medical advice. Please consult a qualified doctor or "
    "nephrologist for proper diagnosis and treatment."
)


# VERSION INFO SCHEMA

class ActiveVersionResponse(BaseModel):
    active_version: str
    model_type: str
    status: str

class VersionInfo(BaseModel):
    version_name: str
    model_type: str
    accuracy: float
    f1_weighted: float
    status: str  # "production", "challenger", "baseline"


class AdminVersionsResponse(BaseModel):
    active_version: str
    versions: List[VersionInfo]




# SWITCH VERSION SCHEMA

class SwitchVersionRequest(BaseModel):
    version: Literal["v2", "v3"] = Field(...,
        description="Version to switch to")



# ROLLBACK SCHEMA

class RollbackResponse(BaseModel):
    previous_version: str
    new_version: str
    reason: str
    timestamp: str