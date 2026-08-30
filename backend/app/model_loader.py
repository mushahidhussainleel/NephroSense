import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# PATHS
BASE_DIR = Path(__file__).parent.parent  # backend/
MODELS_DIR = BASE_DIR / "models"

# LOAD ALL MODELS

models = {
    "v1": joblib.load(MODELS_DIR / "v1_random_forest.pkl"),
    "v2": joblib.load(MODELS_DIR / "v2_xgboost.pkl"),
    "v3": joblib.load(MODELS_DIR / "v3_xgboost_tuned.pkl")
}

# Load encoders
encoders = {
    "smoking": joblib.load(MODELS_DIR / "encoders" / "smoking_encoder.pkl"),
    "painkiller_usage": joblib.load(MODELS_DIR / "encoders" / "painkiller_usage_encoder.pkl"),
    "family_history": joblib.load(MODELS_DIR / "encoders" / "family_history_encoder.pkl")
}

# Load feature columns
feature_columns = joblib.load(MODELS_DIR / "feature_columns.pkl")

# ACTIVE MODEL TRACKER

active_version = "v2"  # Default production model

def get_active_model():
    return models[active_version]

def get_active_version():
    return active_version

def set_active_version(version: str):
    global active_version
    active_version = version

# PREPROCESSING — Raw input → Model format

def preprocess_input(data) -> pd.DataFrame:
    """
    Convert raw PatientInput to model-ready DataFrame.
    Applies same encoding as training notebook.
    """

    # Step 1 — Binary encoding (LabelEncoder)
    smoking_encoded = encoders["smoking"].transform([data.smoking])[0]
    painkiller_encoded = encoders["painkiller_usage"].transform([data.painkiller_usage])[0]
    family_encoded = encoders["family_history"].transform([data.family_history])[0]

    # Step 2 — Ordered mapping
    physical_activity_map = {"rarely": 0, "weekly": 1, "daily": 2}
    stress_level_map = {"low": 0, "moderate": 1, "high": 2}

    # Step 3 — ANA and Hematuria
    ana_encoded = 1 if data.ana == "positive" else 0
    hematuria_encoded = 1 if data.hematuria == "positive" else 0

    # Step 4 — Build base dict
    input_dict = {
        "serum_creatinine": data.serum_creatinine,
        "gfr": data.gfr,
        "bun": data.bun,
        "serum_calcium": data.serum_calcium,
        "ana": ana_encoded,
        "c3_c4": data.c3_c4,
        "hematuria": hematuria_encoded,
        "oxalate_levels": data.oxalate_levels,
        "urine_ph": data.urine_ph,
        "blood_pressure": data.blood_pressure,
        "physical_activity": physical_activity_map[data.physical_activity],
        "water_intake": data.water_intake,
        "smoking": smoking_encoded,
        "painkiller_usage": painkiller_encoded,
        "family_history": family_encoded,
        "stress_level": stress_level_map[data.stress_level],
        "months": data.months,
        # OHE — diet
        "diet_balanced": 1 if data.diet == "balanced" else 0,
        "diet_high protein": 1 if data.diet == "high protein" else 0,
        "diet_low salt": 1 if data.diet == "low salt" else 0,
        # OHE — alcohol
        "alcohol_daily": 1 if data.alcohol == "daily" else 0,
        "alcohol_never": 1 if data.alcohol == "never" else 0,
        "alcohol_occasionally": 1 if data.alcohol == "occasionally" else 0,
        # OHE — weight_changes
        "weight_changes_gain": 1 if data.weight_changes == "gain" else 0,
        "weight_changes_loss": 1 if data.weight_changes == "loss" else 0,
        "weight_changes_stable": 1 if data.weight_changes == "stable" else 0,
    }

    # Step 5 — Create DataFrame and match the training feature order
    df = pd.DataFrame([input_dict])
    df = df[feature_columns]  # Keep the exact feature order used during training

    return df