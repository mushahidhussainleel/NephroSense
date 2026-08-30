from fastapi import APIRouter, HTTPException
from app.schemas import PatientInput, PredictionOutput, STAGE_LABELS , DISCLAIMER, STAGE_RECOMMENDATIONS
from app.model_loader import get_active_model, get_active_version, preprocess_input
from app.routes.monitoring import request_log
import numpy as np
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
router = APIRouter()

# LOAD SHAP EXPLAINERS

EXPLAINERS = {
    "v2": joblib.load(BASE_DIR / "models" / "shap_explainer_v2.pkl"),
    "v3": joblib.load(BASE_DIR / "models" / "shap_explainer_v3.pkl"),
}

# PREDICTION + SHAP EXPLANATION

@router.post("/predict/explain")
async def predict_with_explanation(data: PatientInput):
    try:
        df = preprocess_input(data)
        model = get_active_model()
        active = get_active_version()

        # Make prediction
        prediction = int(model.predict(df)[0])
        probabilities = model.predict_proba(df)[0]
        confidence = float(np.max(probabilities))

        # Calculate SHAP values
        explainer = EXPLAINERS[active]
        shap_values = explainer.shap_values(df)
        shap_vals = shap_values[0, :, prediction]
        feature_names = df.columns.tolist()

        # Prepare all 26 features for the waterfall chart
        all_features = [
            {
                "feature": feature_names[i],
                "value": float(df.iloc[0][feature_names[i]]),
                "shap_value": float(shap_vals[i])
            }
            for i in range(len(feature_names))
        ]

        # Get top 5 features for the doctor summary
        top_indices = np.argsort(
            np.abs([f["shap_value"] for f in all_features])
        )[::-1][:5]
        top_features = [all_features[i] for i in top_indices]

        request_log[active]["total"] += 1

        return {
            "predicted_stage": prediction,
            "stage_label": STAGE_LABELS[prediction],
            "model_version": active,
            "confidence": round(confidence, 4),
            "shap_top_features": top_features,
            "shap_all_features": all_features,
            "recommendation": STAGE_RECOMMENDATIONS[prediction],
            "disclaimer": DISCLAIMER  
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))