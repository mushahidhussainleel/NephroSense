// =============================================
// NEPHROSENSE — Result Page Logic
// =============================================

const STAGE_COLORS = {
    0: "#68d391", 1: "#68d391", 2: "#f6e05e",
    3: "#f6ad55", 4: "#fc8181", 5: "#e53e3e"
};

document.addEventListener("DOMContentLoaded", () => {
    const raw = sessionStorage.getItem("predictionResult");

    if (!raw) {
        window.location.href = "index.html";
        return;
    }

    const result = JSON.parse(raw);
    renderResult(result);
});

// =============================================
// RENDER RESULT
// =============================================
function renderResult(result) {
    const stage = result.predicted_stage;
    const confidence = result.confidence;
    const color = STAGE_COLORS[stage];

    // Stage card
    document.getElementById("stage-badge").textContent = `CKD ${stage === 0 ? "Not Detected" : "Detected"}`;
    document.getElementById("stage-number").textContent = stage;
    document.getElementById("stage-label").textContent = result.stage_label;
    document.getElementById("confidence-val").textContent = `${(confidence * 100).toFixed(1)}%`;
    document.getElementById("model-val").textContent = result.model_version.toUpperCase();

    // Stage card color
    document.getElementById("stage-number").style.background = `linear-gradient(135deg, ${color}, ${color}aa)`;
    document.getElementById("stage-number").style.webkitBackgroundClip = "text";
    document.getElementById("stage-number").style.backgroundClip = "text";
    document.getElementById("stage-number").style.color = "transparent";

    // Confidence bar
    setTimeout(() => {
        document.getElementById("conf-bar").style.width = `${confidence * 100}%`;
        document.getElementById("conf-pct").textContent = `${(confidence * 100).toFixed(1)}%`;
    }, 200);

    // Stage scale
    for (let i = 0; i <= 5; i++) {
        const el = document.getElementById(`scale-${i}`);
        el.classList.add(`stage-${i}`);
        if (i === stage) el.classList.add("active");
    }

    // LLM Explanation
    renderLLMExplanation(result.llm_explanation, result.llm_source);
    document.getElementById("disclaimer-text").textContent = result.disclaimer;

    // Features table
    renderFeaturesTable(result.shap_top_features);

    // Waterfall chart
    renderWaterfall(result.shap_all_features);
}

// =============================================
// LLM EXPLANATION
// =============================================
function renderLLMExplanation(text, source) {
    const badge = document.getElementById("llm-badge");
    const label = document.getElementById("llm-source-label");
    const textEl = document.getElementById("llm-text");

    const isGemini = source === "gemini-2.5-flash";
    badge.className = `llm-badge ${isGemini ? "source-gemini" : "source-fallback"}`;
    label.textContent = isGemini ? "Gemini 2.5 Flash" : "Predefined Response";

    textEl.innerHTML = formatLLMText(text);
}

function formatLLMText(text) {
    if (!text) return "No explanation available.";
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>");
}

// =============================================
// FEATURES TABLE
// =============================================
function renderFeaturesTable(features) {
    const tbody = document.getElementById("features-tbody");
    tbody.innerHTML = "";

    features.forEach((f, idx) => {
        const isPositive = f.shap_value > 0;
        const direction = isPositive ? "↑ Increases risk" : "↓ Decreases risk";
        const shapClass = isPositive ? "shap-positive" : "shap-negative";
        const dirClass = isPositive ? "direction-up" : "direction-down";

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>
                <span style="color: var(--text-muted); font-size: 11px; margin-right: 8px">${idx + 1}</span>
                ${formatFeatureName(f.feature)}
            </td>
            <td style="font-family: var(--font-mono); color: var(--accent-blue)">${f.value.toFixed(3)}</td>
            <td class="${shapClass}">${f.shap_value > 0 ? "+" : ""}${f.shap_value.toFixed(4)}</td>
            <td class="${dirClass}" style="font-size: 12px">${direction}</td>
        `;
        tbody.appendChild(row);
    });
}

// =============================================
// WATERFALL CHART
// =============================================
function renderWaterfall(features) {
    const container = document.getElementById("waterfall-chart");
    container.innerHTML = "";

    if (!features || features.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align:center">No SHAP data available</p>';
        return;
    }

    // Sort by absolute SHAP value
    const sorted = [...features].sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value));
    const maxVal = Math.max(...sorted.map(f => Math.abs(f.shap_value)));

    sorted.forEach(f => {
        const pct = (Math.abs(f.shap_value) / maxVal) * 45;
        const isPositive = f.shap_value > 0;
        const color = isPositive ? "positive" : "negative";
        const valColor = isPositive ? "var(--accent-red)" : "var(--accent-green)";

        const row = document.createElement("div");
        row.className = "wf-row";
        row.innerHTML = `
            <div class="wf-label">${formatFeatureName(f.feature)}</div>
            <div class="wf-bar-container">
                <div class="wf-zero-line"></div>
                <div class="wf-bar ${color}" style="width: 0%" data-width="${pct}%"></div>
            </div>
            <div class="wf-value" style="color: ${valColor}">
                ${f.shap_value > 0 ? "+" : ""}${f.shap_value.toFixed(3)}
            </div>
        `;
        container.appendChild(row);
    });

    // Animate bars
    setTimeout(() => {
        document.querySelectorAll(".wf-bar").forEach(bar => {
            bar.style.width = bar.dataset.width;
        });
    }, 300);
}

// =============================================
// HELPERS
// =============================================
function formatFeatureName(name) {
    return name
        .replace(/_/g, " ")
        .replace(/\b\w/g, c => c.toUpperCase());
}