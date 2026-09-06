from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import os, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv
from app.model_loader import get_active_version, set_active_version
from app.routes.versions import verify_admin

router = APIRouter()


# CONFIG

load_dotenv(find_dotenv())
API_KEY = os.getenv("NEPHROSENSE_ADMIN_KEY")
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")


# ROLLBACK ORDER

ROLLBACK_ORDER = ["v2", "v3"]

# Auto rollback threshold
CONFIDENCE_THRESHOLD = 0.80  # Roll back if confidence falls below 80%
MIN_REQUESTS_FOR_CHECK = 5   # Check after at least 5 requests


# METRICS TRACKER

request_log = {
    "v2": {
        "total": 0,
        "confidence_scores": [],
        "avg_confidence": None,
        "low_confidence_count": 0
    },
    "v3": {
        "total": 0,
        "confidence_scores": [],
        "avg_confidence": None,
        "low_confidence_count": 0
    }
}

rollback_history = []


# GMAIL ALERT

def send_alert_email(subject: str, body: str):
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = GMAIL_SENDER
        msg["To"] = ALERT_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, ALERT_EMAIL, msg.as_string())

        print(f"Alert email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")

# AUTO ROLLBACK LOGIC

def check_and_auto_rollback():
    active = get_active_version()
    log = request_log[active]

    # Check minimum number of requests
    if log["total"] < MIN_REQUESTS_FOR_CHECK:
        return None

    # Calculate average confidence
    recent_scores = log["confidence_scores"][-10:]  # Last 10 scores
    if not recent_scores:
        return None

    avg_confidence = sum(recent_scores) / len(recent_scores)
    log["avg_confidence"] = round(avg_confidence, 4)

    # Check the confidence threshold
    if avg_confidence < CONFIDENCE_THRESHOLD:
        current_idx = ROLLBACK_ORDER.index(active)

        if current_idx + 1 >= len(ROLLBACK_ORDER):
            return None

        next_version = ROLLBACK_ORDER[current_idx + 1]
        set_active_version(next_version)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save rollback history
        rollback_event = {
            "timestamp": timestamp,
            "previous_version": active,
            "new_version": next_version,
            "reason": f"Auto rollback — avg confidence {avg_confidence:.2%} below threshold {CONFIDENCE_THRESHOLD:.0%}",
            "avg_confidence": avg_confidence
        }
        rollback_history.append(rollback_event)

        # Send Gmail alert
        send_alert_email(
            subject=f"NephroSense Alert: Auto Rollback Triggered",
            body=f"""
NephroSense Auto Rollback Alert
================================
Time: {timestamp}

Previous Model: {active.upper()}
New Model: {next_version.upper()}

Reason: Average confidence dropped to {avg_confidence:.2%}
Threshold: {CONFIDENCE_THRESHOLD:.0%}

Last 10 confidence scores:
{recent_scores}

Action: System automatically switched to {next_version.upper()}

Please review model performance.

— NephroSense Monitoring System
            """
        )

        return rollback_event

    return None

# PUBLIC ROUTE — Metrics

@router.get("/metrics")

async def get_metrics():
    try:
        active = get_active_version()
        log = request_log[active]
        return {
            "active_version": active,
            "total_requests": log["total"],
            "avg_confidence": log["avg_confidence"],
            "low_confidence_count": log["low_confidence_count"],
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "recent_rollbacks": len(rollback_history)
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

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        event = {
            "timestamp": timestamp,
            "previous_version": current,
            "new_version": next_version,
            "reason": "Manual rollback by admin",
        }
        rollback_history.append(event)

        # Send alert email
        send_alert_email(
            subject="NephroSense: Manual Rollback by Admin",
            body=f"""
Manual Rollback Performed
==========================
Time: {timestamp}
Previous: {current.upper()}
New: {next_version.upper()}
Reason: Admin triggered manual rollback

— NephroSense System
            """
        )

        return {
            "message": "Rollback successful",
            "previous_version": current,
            "new_version": next_version,
            "timestamp": timestamp,
            "reason": "Manual rollback by admin"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/rollback-history")
async def get_rollback_history(_: str = Depends(verify_admin)):
    return {
        "total_rollbacks": len(rollback_history),
        "history": rollback_history
    }