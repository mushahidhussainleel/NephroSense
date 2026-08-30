// =============================================
// NEPHROSENSE — API Calls
// =============================================

const API_BASE = "http://127.0.0.1:8000";

async function callPredictAPI(data) {
    const response = await fetch(`${API_BASE}/predict/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Prediction failed");
    }

    return await response.json();
}

async function getActiveVersion() {
    const response = await fetch(`${API_BASE}/version`);
    return await response.json();
}

async function getMetrics() {
    const response = await fetch(`${API_BASE}/metrics`);
    return await response.json();
}

// Admin calls
async function switchVersion(version, apiKey) {
    const response = await fetch(`${API_BASE}/admin/switch-version`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey
        },
        body: JSON.stringify({ version })
    });
    return await response.json();
}

async function rollback(apiKey) {
    const response = await fetch(`${API_BASE}/admin/rollback`, {
        method: "POST",
        headers: { "X-API-Key": apiKey }
    });
    return await response.json();
}

async function getAllVersions(apiKey) {
    const response = await fetch(`${API_BASE}/admin/versions`, {
        headers: { "X-API-Key": apiKey }
    });
    return await response.json();
}