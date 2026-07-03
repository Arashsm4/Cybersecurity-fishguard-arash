const emailText = document.getElementById("emailText");
const analyzeBtn = document.getElementById("analyzeBtn");
const samplePhishingBtn = document.getElementById("samplePhishingBtn");
const sampleLegitBtn = document.getElementById("sampleLegitBtn");
const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");
const refreshReportBtn = document.getElementById("refreshReportBtn");
const resultBox = document.getElementById("resultBox");
const historyBox = document.getElementById("historyBox");
const reportBox = document.getElementById("reportBox");

const phishingSample = `URGENT SECURITY ALERT

Your online banking account has been suspended because of suspicious login activity.
Confirm your username, password, and card number immediately at:
http://bank-update.example.com

If you do not verify your account now, your access will be permanently blocked.`;

const legitimateSample = `Hello team,

Please find attached the meeting notes from today's project discussion.
The next meeting will be on Friday at 10:00.

Kind regards,
Project Coordinator`;

function percent(value) {
    return `${(value * 100).toFixed(2)}%`;
}

function clearElement(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

function makeLine(label, value) {
    const p = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    p.appendChild(strong);
    p.appendChild(document.createTextNode(value));
    return p;
}

function showResult(result) {
    clearElement(resultBox);
    resultBox.className = `result ${result.prediction}`;

    const badge = document.createElement("span");
    badge.className = `badge ${result.prediction}`;
    badge.textContent = result.prediction.toUpperCase();
    resultBox.appendChild(badge);

    resultBox.appendChild(makeLine("Confidence", percent(result.confidence)));
    resultBox.appendChild(makeLine("Database ID", String(result.id)));
    resultBox.appendChild(
        makeLine(
            "Suspicious keywords",
            result.suspicious_keywords.length ? result.suspicious_keywords.join(", ") : "None"
        )
    );

    const featureTitle = document.createElement("h3");
    featureTitle.textContent = "Security indicators";
    resultBox.appendChild(featureTitle);

    const list = document.createElement("ul");
    for (const [key, value] of Object.entries(result.features)) {
        const item = document.createElement("li");
        item.textContent = `${key}: ${value}`;
        list.appendChild(item);
    }
    resultBox.appendChild(list);

    resultBox.classList.remove("hidden");
}

async function analyzeEmail() {
    const text = emailText.value.trim();

    if (!text) {
        alert("Please paste an email first.");
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email_text: text})
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis failed.");
        }

        showResult(data);
        await loadHistory();
        await loadReport();
    } catch (error) {
        alert(error.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze";
    }
}

async function loadHistory() {
    const response = await fetch("/api/history?limit=8");
    const rows = await response.json();

    clearElement(historyBox);

    if (!rows.length) {
        historyBox.textContent = "No history yet.";
        return;
    }

    for (const row of rows) {
        const item = document.createElement("div");
        item.className = "history-item";

        const title = document.createElement("strong");
        title.textContent = `${row.prediction.toUpperCase()} - ${percent(row.confidence)}`;

        const meta = document.createElement("div");
        meta.className = "history-meta";
        meta.textContent = row.created_at;

        const text = document.createElement("div");
        text.className = "history-text";
        text.textContent = row.email_text.length > 120
            ? `${row.email_text.slice(0, 120)}...`
            : row.email_text;

        item.appendChild(title);
        item.appendChild(meta);
        item.appendChild(text);
        historyBox.appendChild(item);
    }
}

async function loadReport() {
    const response = await fetch("/api/report");
    const data = await response.json();
    const stats = data.statistics;

    reportBox.textContent =
`Database summary
Total scanned: ${stats.total_scanned}
Phishing predictions: ${stats.phishing_detected}
Legitimate predictions: ${stats.legitimate_detected}
Average confidence: ${percent(stats.average_confidence)}

Model evaluation
${data.evaluation_report || "No evaluation report found."}`;
}

analyzeBtn.addEventListener("click", analyzeEmail);

samplePhishingBtn.addEventListener("click", () => {
    emailText.value = phishingSample;
});

sampleLegitBtn.addEventListener("click", () => {
    emailText.value = legitimateSample;
});

refreshHistoryBtn.addEventListener("click", loadHistory);
refreshReportBtn.addEventListener("click", loadReport);

loadHistory();
loadReport();
