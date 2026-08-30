// =============================================
// NEPHROSENSE — Admin Panel Logic
// =============================================

let adminKey = "";

async function loadAdminData() {
    adminKey = document.getElementById("admin-key").value.trim();
    const status = document.getElementById("key-status");

    if (!adminKey) {
        status.innerHTML = '<span style="color: var(--accent-red)">Please enter API key</span>';
        return;
    }

    try {
        // Load metrics
        const metrics = await getMetrics();
        document.getElementById("active-model").textContent = metrics.active_version.toUpperCase();
        document.getElementById("total-requests").textContent = metrics.total_requests;
        document.getElementById("model-status").textContent = "Running";

        // Load versions
        const versions = await getAllVersions(adminKey);
        renderVersionsTable(versions);

        // Show content
        document.getElementById("admin-content").style.display = "flex";
        document.getElementById("admin-content").style.flexDirection = "column";
        document.getElementById("admin-content").style.gap = "24px";

        status.innerHTML = '<span style="color: var(--accent-green)">✓ Access granted</span>';

    } catch (err) {
        status.innerHTML = '<span style="color: var(--accent-red)">✗ Invalid API key or server error</span>';
        document.getElementById("admin-content").style.display = "none";
    }
}

function renderVersionsTable(data) {
    const tbody = document.getElementById("versions-tbody");
    tbody.innerHTML = "";

    data.versions.forEach(v => {
        const isActive = v.version_name.toLowerCase().includes(data.active_version);
        const statusClass = `status-${v.status}`;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td style="font-family: var(--font-mono); color: var(--accent-blue)">
                ${v.version_name}
                ${isActive ? '<span style="margin-left:8px; font-size:10px; color: var(--accent-green)">● ACTIVE</span>' : ""}
            </td>
            <td>${v.model_type}</td>
            <td style="font-family: var(--font-mono)">${(v.accuracy * 100).toFixed(2)}%</td>
            <td style="font-family: var(--font-mono)">${(v.f1_weighted * 100).toFixed(2)}%</td>
            <td><span class="status-badge ${statusClass}">${v.status}</span></td>
        `;
        tbody.appendChild(row);
    });
}

async function doSwitch() {
    const version = document.getElementById("switch-select").value;
    const resultEl = document.getElementById("switch-result");

    try {
        const res = await switchVersion(version, adminKey);
        resultEl.className = "action-result success";
        resultEl.textContent = `Switched: ${res.previous_version} → ${res.new_version}`;

        // Refresh metrics
        await loadAdminData();

    } catch (err) {
        resultEl.className = "action-result error";
        resultEl.textContent = "Switch failed: " + err.message;
    }
}

async function doRollback() {
    const resultEl = document.getElementById("rollback-result");

    try {
        const res = await rollback(adminKey);
        resultEl.className = "action-result success";
        resultEl.textContent = `Rolled back: ${res.previous_version} → ${res.new_version}`;

        // Refresh metrics
        await loadAdminData();

    } catch (err) {
        resultEl.className = "action-result error";
        resultEl.textContent = "Rollback failed: " + err.message;
    }
}