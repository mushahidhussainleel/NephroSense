from fastapi import APIRouter, HTTPException
from app.schemas import PatientInput, STAGE_LABELS
from app.model_loader import models, preprocess_input
import numpy as np

router = APIRouter()

# AB TEST LOG
ab_test_log = {
    "total_tests": 0,
    "v2_wins": 0,
    "v3_wins": 0,
    "ties": 0,
    "agreements": 0,
    "disagreements": 0,
    "v2_total_confidence": 0.0,
    "v3_total_confidence": 0.0
}

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

        # Agreement check
        agreement = (
            results["v2"]["predicted_stage"] ==
            results["v3"]["predicted_stage"]
        )

        # Winner check
        v2_conf = results["v2"]["confidence"]
        v3_conf = results["v3"]["confidence"]

        if v2_conf > v3_conf:
            winner = "v2"
        elif v3_conf > v2_conf:
            winner = "v3"
        else:
            winner = "tie"

        # LOG UPDATE
        ab_test_log["total_tests"] += 1

        if agreement:
            ab_test_log["agreements"] += 1
        else:
            ab_test_log["disagreements"] += 1

        if winner == "v2":
            ab_test_log["v2_wins"] += 1
        elif winner == "v3":
            ab_test_log["v3_wins"] += 1
        else:
            ab_test_log["ties"] += 1

        ab_test_log["v2_total_confidence"] += v2_conf
        ab_test_log["v3_total_confidence"] += v3_conf

        return {
            "v2_result": results["v2"],
            "v3_result": results["v3"],
            "models_agree": agreement,
            "winner": winner
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AB TEST STATS
@router.get("/ab-test/stats")
async def get_ab_stats():
    total = ab_test_log["total_tests"]
    return {
        "total_tests": total,
        "v2_wins": ab_test_log["v2_wins"],
        "v3_wins": ab_test_log["v3_wins"],
        "ties": ab_test_log["ties"],
        "agreements": ab_test_log["agreements"],
        "disagreements": ab_test_log["disagreements"],
        "v2_avg_confidence": round(
            ab_test_log["v2_total_confidence"] / total, 4
        ) if total > 0 else None,
        "v3_avg_confidence": round(
            ab_test_log["v3_total_confidence"] / total, 4
        ) if total > 0 else None
    }