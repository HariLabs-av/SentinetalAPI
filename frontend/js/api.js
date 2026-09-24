/**
 * SentinelAPI backend connector.
 * The browser talks to FastAPI; scan credentials are sent only for the scan
 * request and are never stored in local history or rendered in results.
 */
const API_BASE_URL = window.SENTINEL_API_BASE_URL || "http://127.0.0.1:8000";

const ApiService = {
  formatError(body, status) {
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => {
        const location = Array.isArray(item.loc) ? item.loc.join(".") : "request";
        return `${location}: ${item.msg || "invalid value"}`;
      }).join("; ");
    }
    return body.message || `Backend request failed: HTTP ${status}`;
  },

  async request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
    let body = {};
    try {
      body = await response.json();
    } catch (_) {}
    if (!response.ok) {
      throw new Error(this.formatError(body, response.status));
    }
    return body;
  },

  async discover(specUrl) {
    const url = new URL(specUrl);
    return this.request("/api/v1/discover", {
      method: "POST",
      body: JSON.stringify({
        target_url: url.origin,
        openapi_url: specUrl
      })
    });
  },

  async runScan(config) {
    const required = [
      ["session_id", config.sessionId],
      ["identity_a.username", config.usernameA],
      ["identity_a.password", config.passwordA],
      ["identity_b.username", config.usernameB],
      ["identity_b.password", config.passwordB],
    ];
    const missing = required.filter(([, value]) => !String(value || "").trim()).map(([name]) => name);
    if (missing.length) {
      throw new Error(`Missing scan configuration: ${missing.join(", ")}`);
    }
    return this.request("/api/v1/scan", {
      method: "POST",
      body: JSON.stringify({
        session_id: config.sessionId,
        mode: config.mode,
        login_path: config.loginPath || "/auth/login",
        identity_a: { username: config.usernameA, password: config.passwordA },
        identity_b: { username: config.usernameB, password: config.passwordB }
      })
    });
  },

  async aiReport(scanId) {
    return this.request(`/api/v1/scan/${encodeURIComponent(scanId)}/ai-report`, {
      method: "POST"
    });
  }
};
