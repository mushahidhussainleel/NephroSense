from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv, find_dotenv
from app.model_loader import get_active_version, set_active_version

router = APIRouter()


# ADMIN ACCESS PROTECTION

load_dotenv(find_dotenv())
API_KEY = os.getenv("NEPHROSENSE_ADMIN_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_admin(key: str = Depends(api_key_header)):
    if key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Admin access only!"
        )


# ROLLBACK ORDER

ROLLBACK_ORDER = ["v2", "v3"]  

# REQUEST METRICS TRACKER

request_log = {
    "v2": {"total": 0},
    "v3": {"total": 0}
}

# USER ROUTE — View metrics

@router.get("/metrics")
async def get_metrics():
    try:
        active = get_active_version()
        log = request_log[active]
        return {
            "active_version": active,
            "total_requests": log["total"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ADMIN ROUTES — Protected

@router.post("/admin/rollback")
async def manual_rollback(_: str = Depends(verify_admin)):
    try:
        current = get_active_version()
        current_idx = ROLLBACK_ORDER.index(current)

        if current_idx + 1 >= len(ROLLBACK_ORDER):
            raise HTTPException(
                status_code=400,
                detail="No more versions to rollback to"
            )

        next_version = ROLLBACK_ORDER[current_idx + 1]
        set_active_version(next_version)

        return {
            "message": "Rollback successful",
            "previous_version": current,
            "new_version": next_version
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))