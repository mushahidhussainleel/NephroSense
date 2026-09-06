from fastapi import APIRouter, HTTPException
from app.schemas import PatientInput, STAGE_LABELS, DISCLAIMER, STAGE_RECOMMENDATIONS
from app.model_loader import get_active_model, get_active_version, preprocess_input
from app.routes.monitoring import request_log, check_and_auto_rollback
from app.routes.llm_explain import get_llm_explanation
import numpy as np
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
router = APIRouter()

# SHAP explainers
EXPLAINERS = {
    "v2": joblib.load(BASE_DIR / "models" / "shap_explainer_v2.pkl"),
    "v3": joblib.load(BASE_DIR / "models" / "shap_explainer_v3.pkl"),
}

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

        # Get all 26 features for the waterfall chart
        all_features = [
            {
                "feature": feature_names[i],
                "value": float(df.iloc[0][feature_names[i]]),
                "shap_value": float(shap_vals[i])
            }
            for i in range(len(feature_names))
        ]

        # Get top 5 features for the LLM and summary
        top_indices = np.argsort(
            np.abs([f["shap_value"] for f in all_features])
        )[::-1][:5]
        top_features = [all_features[i] for i in top_indices]

        # Log prediction metrics
        request_log[active]["total"] += 1
        request_log[active]["confidence_scores"].append(confidence)

        if confidence < 0.80:
            request_log[active]["low_confidence_count"] += 1

        check_and_auto_rollback()

        # Get explanation from the LLM
        llm_text = await get_llm_explanation(
            predicted_stage=prediction,
            stage_label=STAGE_LABELS[prediction],
            top_features=top_features,
            confidence=confidence
        )

        # Use fallback recommendation if the LLM fails
        if llm_text is None:
            llm_text = STAGE_RECOMMENDATIONS[prediction]
            llm_source = "predefined_recommendation"
        else:
            llm_source = "gemini-2.5-flash"

        return {
            "predicted_stage": prediction,
            "stage_label": STAGE_LABELS[prediction],
            "model_version": active,
            "confidence": round(confidence, 4),
            "shap_top_features": top_features,
            "shap_all_features": all_features,
            "llm_explanation": llm_text,
            "llm_source": llm_source,
            "disclaimer": DISCLAIMER
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))