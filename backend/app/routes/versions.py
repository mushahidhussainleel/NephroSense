from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv, find_dotenv
from app.schemas import (
    VersionInfo, 
    ActiveVersionResponse,      
    AdminVersionsResponse,      
    SwitchVersionRequest
)
from app.model_loader import get_active_version, set_active_version

router = APIRouter()

load_dotenv(find_dotenv())
API_KEY = os.getenv("NEPHROSENSE_ADMIN_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

# ADMIN ACCESS PROTECTION

async def verify_admin(key: str = Depends(api_key_header)):
    if key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Admin access only!"
        )


# MODEL VERSION METADATA

VERSION_METADATA = {
    "v1": VersionInfo(
        version_name="V1_RandomForest",
        model_type="Random Forest Classifier",
        accuracy=0.9812,
        f1_weighted=0.9788,
        status="baseline"
    ),
    "v2": VersionInfo(
        version_name="V2_XGBoost",
        model_type="XGBoost Classifier",
        accuracy=0.9862,
        f1_weighted=0.9861,
        status="production"
    ),
    "v3": VersionInfo(
        version_name="V3_XGBoost_Tuned",
        model_type="XGBoost Classifier (Tuned)",
        accuracy=0.9850,
        f1_weighted=0.9849,
        status="challenger"
    )
}

# USER ROUTE — Show active version

@router.get("/version", response_model=ActiveVersionResponse)
async def get_active_version_info():
    try:
        active = get_active_version()
        info = VERSION_METADATA[active]
        return ActiveVersionResponse(
            active_version=active,
            model_type=info.model_type,
            status=info.status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ADMIN ROUTES — Protected

@router.get("/admin/versions", response_model=AdminVersionsResponse)
async def get_all_versions(_: str = Depends(verify_admin)):
    try:
        return AdminVersionsResponse(
            active_version=get_active_version(),
            versions=list(VERSION_METADATA.values())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/switch-version")
async def switch_version(
    request: SwitchVersionRequest,
    _: str = Depends(verify_admin)
):
    try:
        previous = get_active_version()
        set_active_version(request.version)
        return {
            "message": f"Switched from {previous} to {request.version}",
            "previous_version": previous,
            "new_version": request.version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))