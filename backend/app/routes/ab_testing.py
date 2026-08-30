from fastapi import APIRouter, HTTPException
from app.schemas import PatientInput, STAGE_LABELS
from app.model_loader import models, preprocess_input
import numpy as np

router = APIRouter()

@router.post("/ab-test")
async def ab_test(data: PatientInput):
    try:
        df = preprocess_input(data)

        results = {}
        for version in ["v2", "v3"]:
            model = models[version]
            prediction = int(model.predict(df)[0])
            probabilities = model.predict_proba(df)[0]
            confidence = float(np.max(probabilities))
            results[version] = {
                "predicted_stage": prediction,
                "stage_label": STAGE_LABELS[prediction],
                "confidence": round(confidence, 4)
            }

        agreement = (
            results["v2"]["predicted_stage"] ==
            results["v3"]["predicted_stage"]
        )

        return {
            "v2_result": results["v2"],
            "v3_result": results["v3"],
            "models_agree": agreement  # Check if both models predict the same stage
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))