// =============================================
// NEPHROSENSE — A/B Testing Logic
// =============================================

const STAGE_LABELS = {
    0: "Healthy — No CKD",
    1: "Mild — GFR ≥ 90",
    2: "Mild-Moderate — GFR 60-89",
    3: "Moderate — GFR 30-59",
    4: "Severe — GFR 15-29",
    5: "Kidney Failure — GFR < 15"
};

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("ab-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        await runABTest();
    });
});

// =============================================
// RUN A/B TEST
// =============================================
async function runABTest() {
    const btnText = document.getElementById("ab-btn-text");
    const btnLoader = document.getElementById("ab-btn-loader");
    const btn = document.getElementById("btn-ab");

    // Loading
    btnText.style.display = "none";
    btnLoader.style.display = "inline";
    btn.disabled = true;

    try {
        const data = collectData();
        const result = await callABTestAPI(data);
        renderResults(result);

    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        btnText.style.display = "inline";
        btnLoader.style.display = "none";
        btn.disabled = false;
    }
}

// =============================================
// RENDER RESULTS
// =============================================
function renderResults(result) {
    const v2 = result.v2_result;
    const v3 = result.v3_result;
    const agree = result.models_agree;

    // Show results section
    const resultsEl = document.getElementById("ab-results");
    resultsEl.style.display = "flex";
    resultsEl.scrollIntoView({ behavior: "smooth" });

    // Agreement banner
    const banner = document.getElementById("agreement-banner");
    const icon = document.getElementById("agreement-icon");
    const text = document.getElementById("agreement-text");

    if (agree) {
        banner.className = "agreement-banner agree";
        icon.textContent = "✓";
        text.textContent = `Both models agree — Stage ${v2.predicted_stage} predicted. High confidence in result.`;
    } else {
        banner.className = "agreement-banner disagree";
        icon.textContent = "⚠";
        text.textContent = `Models disagree! V2 says Stage ${v2.predicted_stage}, V3 says Stage ${v3.predicted_stage}. Manual review recommended.`;
    }

    // V2 Card
    document.getElementById("v2-stage").textContent = v2.predicted_stage;
    document.getElementById("v2-label").textContent = STAGE_LABELS[v2.predicted_stage];
    document.getElementById("v2-confidence").textContent = `${(v2.confidence * 100).toFixed(1)}%`;
    setTimeout(() => {
        document.getElementById("v2-bar").style.width = `${v2.confidence * 100}%`;
    }, 200);

    // V3 Card
    document.getElementById("v3-stage").textContent = v3.predicted_stage;
    document.getElementById("v3-label").textContent = STAGE_LABELS[v3.predicted_stage];
    document.getElementById("v3-confidence").textContent = `${(v3.confidence * 100).toFixed(1)}%`;
    setTimeout(() => {
        document.getElementById("v3-bar").style.width = `${v3.confidence * 100}%`;
    }, 200);

    // Winner
    const v2Conf = v2.confidence;
    const v3Conf = v3.confidence;

    if (v2Conf > v3Conf) {
        document.getElementById("winner-text").textContent = `V2 Champion — ${(v2Conf * 100).toFixed(1)}% confidence`;
        document.getElementById("v2-card").classList.add("winner");
    } else if (v3Conf > v2Conf) {
        document.getElementById("winner-text").textContent = `V3 Challenger — ${(v3Conf * 100).toFixed(1)}% confidence`;
        document.getElementById("v3-card").classList.add("winner");
    } else {
        document.getElementById("winner-text").textContent = "Both models equally confident";
    }
}

// =============================================
// COLLECT DATA
// =============================================
function collectData() {
    const form = document.getElementById("ab-form");

    const numericalFields = [
        "gfr", "serum_creatinine", "bun", "serum_calcium",
        "blood_pressure", "urine_ph", "c3_c4", "oxalate_levels", "water_intake"
    ];

    const data = {};

    numericalFields.forEach(f => {
        data[f] = parseFloat(form[f].value);
    });

    data["months"] = parseInt(form["months"].value);

    const stringFields = [
        "ana", "hematuria", "physical_activity", "smoking",
        "painkiller_usage", "family_history", "stress_level",
        "diet", "alcohol", "weight_changes"
    ];

    stringFields.forEach(f => {
        data[f] = form[f].value;
    });

    return data;
}

// =============================================
// API CALL
// =============================================
async function callABTestAPI(data) {
    const response = await fetch("http://127.0.0.1:8000/ab-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "A/B Test failed");
    }

    return await response.json();
}

// =============================================
// RESET
// =============================================
function resetTest() {
    document.getElementById("ab-results").style.display = "none";
    document.getElementById("ab-form").reset();
    document.getElementById("v2-card").classList.remove("winner");
    document.getElementById("v3-card").classList.remove("winner");
    document.getElementById("v2-bar").style.width = "0%";
    document.getElementById("v3-bar").style.width = "0%";
    window.scrollTo({ top: 0, behavior: "smooth" });
}