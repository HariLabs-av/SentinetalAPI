/**
 * SentinelAPI Terminal Engine & Dashboard Orchestrator
 */
let currentFindings = [];
let currentScanResult = null;

async function triggerAudit() {
  const btn = document.getElementById("btn-scan") || document.getElementById("btn-execute-scan");
  const specUrl = document.getElementById("spec-url") ? document.getElementById("spec-url").value : "";
  const terminal = document.getElementById("terminal-logs");
  const stepText = document.getElementById("terminal-step");

  if (btn) {
    btn.disabled = true;
    btn.classList.add("opacity-50", "cursor-not-allowed");
  }

  if (terminal) {
    terminal.innerHTML = "";
  }

  function log(msg, color = "text-textMuted") {
    if (!terminal) return;
    const timestamp = new Date().toISOString().substring(11, 23);
    const line = document.createElement("p");
    line.className = `${color} leading-relaxed`;
    line.innerHTML = `<span class="text-textMuted/60">[${timestamp}]</span> ${msg}`;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
  }

  // Real-time status output
  log("Ingesting OpenAPI schema from target...", "text-brandAccent");
  if (stepText) stepText.innerText = "PARSING SPEC";
  const config = arguments.length > 0 && arguments[0] ? arguments[0] : window.scanConfig;
  if (!config) throw new Error("Scan configuration is missing. Return to the configuration step.");
  let data;
  try {
    data = await ApiService.runScan(config);
  } catch (error) {
    log(`Scan failed: ${error.message}`, "text-pastelRed font-bold");
    throw error;
  }
  currentScanResult = data;
  log(`OpenAPI discovery complete: ${data.summary.endpoints_tested} endpoints tested.`, "text-textMain");
  log(`Scan completed with ${data.summary.vulnerabilities} finding(s).`, data.summary.vulnerabilities ? "text-pastelAmber" : "text-pastelGreen");
  currentFindings = (data.findings || []).map((finding) => ({
    ...finding,
    id: finding.finding_id,
    vulnerabilityType: finding.type,
    httpMethod: finding.method,
    details: finding.description,
    evidence: JSON.stringify(finding.evidence, null, 2),
    curlPoc: `${finding.method} ${finding.endpoint}`,
    remediationCode: "Use the AI report for root cause, missing controls, implementation options, and validation tests. Exact code is intentionally not generated from HTTP evidence alone."
  }));

  // 3. Update telemetry metrics
  const metricAudited = document.getElementById("metric-audited");
  const metricBola = document.getElementById("metric-bola");
  const metricLeaks = document.getElementById("metric-leaks");
  const metricScore = document.getElementById("metric-score");
  const badge = document.getElementById("metric-verdict-badge");
  const findingsPill = document.getElementById("findings-pill");

  const severityCounts = data.statistics?.severity_counts || {};
  if (metricAudited) metricAudited.innerText = `${data.summary.endpoints_tested} Endpoints`;
  if (metricBola) metricBola.innerText = `${severityCounts.HIGH || 0} High`;
  if (metricLeaks) metricLeaks.innerText = `${data.summary.vulnerabilities} Findings`;
  if (metricScore) metricScore.innerText = `${data.score.value} / 100`;

  if (badge) {
    if (data.summary.vulnerabilities > 0) {
      badge.innerText = "FINDINGS DETECTED";
      badge.className = "px-2.5 py-0.5 rounded text-[11px] bg-red-950/40 text-pastelRed border border-red-800/40 font-bold whitespace-nowrap";
    } else {
      badge.innerText = "CLEAN";
      badge.className = "px-2.5 py-0.5 rounded text-[11px] bg-emerald-950/40 text-pastelGreen border border-emerald-800/40 font-bold whitespace-nowrap";
    }
  }

  if (findingsPill) {
    findingsPill.innerText = `${currentFindings.length} Findings`;
  }

  // 4. Render left route list & select finding 0
  if (typeof FindingsRenderer !== "undefined" && typeof FindingsRenderer.renderEndpointList === "function") {
    FindingsRenderer.renderEndpointList(currentFindings);
    if (currentFindings.length > 0) {
      FindingsRenderer.selectFinding(0);
    }
  }

  if (btn) {
    btn.disabled = false;
    btn.classList.remove("opacity-50", "cursor-not-allowed");
  }

  if (stepText) stepText.innerText = "AUDIT COMPLETE";
  if (window.lucide) lucide.createIcons();
}

async function requestAIReport() {
  if (!currentScanResult?.scan_id) {
    alert("Run a scan before requesting an AI report.");
    return;
  }
  const button = document.getElementById("btn-ai-report");
  if (button) {
    button.disabled = true;
    button.innerText = "Generating report...";
  }
  try {
    const result = await ApiService.aiReport(currentScanResult.scan_id);
    const panel = document.getElementById("ai-report");
    if (panel) {
      const report = result.report || {};
      panel.textContent = typeof report === "string" ? report : JSON.stringify(report, null, 2);
      panel.classList.remove("hidden");
    }
  } catch (error) {
    const panel = document.getElementById("ai-report");
    if (panel) {
      panel.textContent = `AI report unavailable: ${error.message}`;
      panel.classList.remove("hidden");
    }
  } finally {
    if (button) {
      button.disabled = false;
      button.innerText = "Generate AI report";
    }
  }
}