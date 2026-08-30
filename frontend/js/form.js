// =============================================
// NEPHROSENSE — Form Step Logic
// =============================================

let currentStep = 1;
const totalSteps = 3;

const stepLabels = {
    1: "Step 1 of 3 — Lab Results",
    2: "Step 2 of 3 — Lifestyle",
    3: "Step 3 of 3 — Diet & Habits"
};

// On page load
document.addEventListener("DOMContentLoaded", () => {
    updateUI();

    // Form submit
    document.getElementById("prediction-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        await submitPrediction();
    });
});

// =============================================
// STEP NAVIGATION
// =============================================
function nextStep() {
    if (!validateStep(currentStep)) return;

    if (currentStep < totalSteps) {
        // Mark current as done
        document.getElementById(`ind-${currentStep}`).classList.remove("active");
        document.getElementById(`ind-${currentStep}`).classList.add("done");

        currentStep++;
        updateUI();
    }
}

function prevStep() {
    if (currentStep > 1) {
        document.getElementById(`ind-${currentStep}`).classList.remove("active");
        currentStep--;
        document.getElementById(`ind-${currentStep}`).classList.remove("done");
        document.getElementById(`ind-${currentStep}`).classList.add("active");
        updateUI();
    }
}

// =============================================
// UPDATE UI
// =============================================
function updateUI() {
    // Show correct step
    document.querySelectorAll(".form-step").forEach(s => s.classList.remove("active"));
    document.getElementById(`step-${currentStep}`).classList.add("active");

    // Update indicator
    document.getElementById(`ind-${currentStep}`).classList.add("active");

    // Update progress bar
    const progress = (currentStep / totalSteps) * 100;
    document.getElementById("progress-fill").style.width = `${progress}%`;

    // Update step label
    document.getElementById("step-label").textContent = stepLabels[currentStep];

    // Show/hide buttons
    document.getElementById("btn-back").style.display = currentStep > 1 ? "block" : "none";
    document.getElementById("btn-next").style.display = currentStep < totalSteps ? "block" : "none";
    document.getElementById("btn-predict").style.display = currentStep === totalSteps ? "block" : "none";
}

// =============================================
// VALIDATION
// =============================================
function validateStep(step) {
    const stepEl = document.getElementById(`step-${step}`);
    const inputs = stepEl.querySelectorAll("input[required], select[required]");
    let valid = true;

    inputs.forEach(input => {
        input.style.borderColor = "";
        if (!input.value.trim()) {
            input.style.borderColor = "rgba(252, 129, 129, 0.6)";
            valid = false;
        }
    });

    // Radio validation for step 3
    if (step === 3) {
        ["diet", "alcohol", "weight_changes"].forEach(name => {
            const checked = stepEl.querySelector(`input[name="${name}"]:checked`);
            if (!checked) {
                const radios = stepEl.querySelectorAll(`input[name="${name}"]`);
                radios.forEach(r => {
                    r.closest(".radio-option").querySelector(".radio-box").style.borderColor = "rgba(252, 129, 129, 0.4)";
                });
                valid = false;
            }
        });
    }

    if (!valid) {
        shakeForm();
    }

    return valid;
}

function shakeForm() {
    const panel = document.querySelector(".right-panel");
    panel.style.animation = "none";
    setTimeout(() => {
        panel.style.animation = "shake 0.3s ease";
    }, 10);
}

// =============================================
// SUBMIT
// =============================================
async function submitPrediction() {
    if (!validateStep(3)) return;

    const btnText = document.getElementById("btn-text");
    const btnLoader = document.getElementById("btn-loader");
    const btnPredict = document.getElementById("btn-predict");

    // Loading state
    btnText.style.display = "none";
    btnLoader.style.display = "inline";
    btnPredict.disabled = true;

    try {
        const formData = collectFormData();
        const result = await callPredictAPI(formData);

        // Save result and redirect
        sessionStorage.setItem("predictionResult", JSON.stringify(result));
        window.location.href = "result.html";

    } catch (error) {
        btnText.style.display = "inline";
        btnLoader.style.display = "none";
        btnPredict.disabled = false;
        alert("Error: " + error.message);
    }
}

// =============================================
// COLLECT FORM DATA
// =============================================
function collectFormData() {
    const form = document.getElementById("prediction-form");
    const data = {};

    // Numerical fields
    const numericalFields = [
        "gfr", "serum_creatinine", "bun", "serum_calcium",
        "blood_pressure", "urine_ph", "c3_c4", "oxalate_levels",
        "water_intake"
    ];

    numericalFields.forEach(field => {
        data[field] = parseFloat(form[field].value);
    });

    // Integer fields
    data["months"] = parseInt(form["months"].value);

    // String fields
    const stringFields = [
        "ana", "hematuria", "physical_activity",
        "smoking", "painkiller_usage", "family_history",
        "stress_level", "diet", "alcohol", "weight_changes"
    ];

    stringFields.forEach(field => {
        const el = form[field];
        if (el.type === "radio" || el instanceof RadioNodeList) {
            const checked = form.querySelector(`input[name="${field}"]:checked`);
            data[field] = checked ? checked.value : "";
        } else {
            data[field] = el.value;
        }
    });

    return data;
}

// CSS for shake animation
const style = document.createElement("style");
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-6px); }
        75% { transform: translateX(6px); }
    }
`;
document.head.appendChild(style);