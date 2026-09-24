/**
 * SentinelAPI Inspector Workbench (High-Contrast Burp-Style Diff)
 */
const FindingsRenderer = {
  renderEndpointList(findings) {
    const list = document.getElementById("endpoints-list");
    if (!list) return;

    if (!findings || findings.length === 0) {
      list.innerHTML = `
        <div class="p-8 text-center text-psTextMuted border border-dashed border-psBorder rounded-lg font-mono text-xs bg-white">
          No vulnerabilities detected.
        </div>
      `;
      return;
    }

    list.innerHTML = findings.map((f, idx) => `
      <div 
        onclick="FindingsRenderer.selectFinding(${idx})" 
        id="finding-item-${idx}" 
        class="p-3.5 bg-white border border-psBorder hover:border-slate-400 rounded-lg cursor-pointer transition flex flex-col gap-1.5 shadow-sm"
      >
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-bold px-2 py-0.5 rounded border ${
            f.severity === 'CRITICAL' 
              ? 'bg-rose-50 text-psRed border-rose-200' 
              : 'bg-amber-50 text-psAmber border-amber-200'
          }">${f.severity}</span>
          <span class="text-[10px] text-psTextMuted font-mono font-medium">${f.id}</span>
        </div>
        <div class="font-bold text-psNavy text-xs font-mono truncate">${f.endpoint}</div>
        <div class="text-[11px] text-psTextMuted truncate">${f.vulnerabilityType}</div>
      </div>
    `).join("");
  },

  selectFinding(idx) {
    const f = currentFindings[idx];
    if (!f) return;

    // Highlight active card with Orange accent border
    currentFindings.forEach((_, i) => {
      const el = document.getElementById(`finding-item-${i}`);
      if (el) {
        el.classList.remove("border-psOrange", "bg-orange-50/20", "ring-1", "ring-psOrange/30");
      }
    });
    const selectedEl = document.getElementById(`finding-item-${idx}`);
    if (selectedEl) {
      selectedEl.classList.add("border-psOrange", "bg-orange-50/20", "ring-1", "ring-psOrange/30");
    }

    // Render detailed view in inspector pane
    const inspector = document.getElementById("inspector-pane");
    if (!inspector) return;

    inspector.className = "bg-white border border-psBorder rounded-lg p-6 space-y-4 shadow-sm";
    inspector.innerHTML = `
      <!-- Header -->
      <div class="border-b border-psBorder pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-[10px] font-bold px-2.5 py-0.5 rounded border ${
              f.severity === 'CRITICAL' 
                ? 'bg-rose-50 text-psRed border-rose-200' 
                : 'bg-amber-50 text-psAmber border-amber-200'
            }">${f.severity}</span>
            <span class="text-psTextMuted text-xs font-medium">${f.vulnerabilityType}</span>
          </div>
          <h2 class="text-sm font-bold text-psNavy font-mono tracking-tight">${f.endpoint}</h2>
        </div>
        <div class="text-xs bg-slate-50 px-3 py-1.5 rounded-md border border-psBorder text-psTextMuted font-mono">
          Victim: <strong class="text-amber-600">Alice (101)</strong> | Impersonator: <strong class="text-psRed">Bob (102)</strong>
        </div>
      </div>

      <!-- Description Context Box -->
      <p class="text-slate-700 text-xs leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-psBorder font-sans">
        ${f.details}
      </p>

      <!-- Action Tabs Bar -->
      <div class="border border-psBorder rounded-lg bg-white overflow-hidden shadow-sm">
        <div class="flex border-b border-psBorder bg-slate-50 text-xs font-mono">
          <button id="btn-tab-poc" onclick="FindingsRenderer.switchInspectorTab('poc')" class="px-4 py-2.5 text-psOrange border-b-2 border-psOrange font-bold bg-white">
            Burp-Style HTTP Traffic Diff (Exploit)
          </button>
          <button id="btn-tab-patch" onclick="FindingsRenderer.switchInspectorTab('patch')" class="px-4 py-2.5 text-psTextMuted hover:text-psNavy transition font-medium">
            AI Remediation Guidance
          </button>
        </div>

        <!-- Tab 1: High-Contrast Burp-Style Traffic Side-by-Side -->
        <div id="inspector-tab-poc" class="p-4 bg-slate-50/50">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <!-- Left Box: Request (Sharp Rose / Crimson on Deep Slate) -->
            <div class="bg-[#0B1220] p-4 rounded-lg border border-slate-800 shadow-md relative group">
              <div class="flex items-center justify-between text-[11px] font-mono mb-2.5 border-b border-slate-800 pb-2">
                <span class="text-rose-400 font-bold tracking-wider">REQUEST (BOB'S FORGED TOKEN)</span>
                <button onclick="copyToClipboard('code-poc', this)" class="text-slate-400 hover:text-white transition text-[11px] font-semibold">
                  Copy cURL
                </button>
              </div>
              <pre id="code-poc" class="text-rose-200 text-xs font-mono font-medium overflow-x-auto whitespace-pre leading-relaxed selection:bg-rose-500 selection:text-white">${f.curlPoc}</pre>
            </div>

            <!-- Right Box: Leaked Response (Vivid Amber / Gold on Deep Slate) -->
            <div class="bg-[#0B1220] p-4 rounded-lg border border-slate-800 shadow-md">
              <div class="text-[11px] font-mono text-amber-300 font-bold mb-2.5 border-b border-slate-800 pb-2 tracking-wider">
                LEAKED RESPONSE (HTTP 200 OK)
              </div>
              <pre class="text-amber-200 text-xs font-mono font-medium overflow-x-auto whitespace-pre leading-relaxed selection:bg-amber-500 selection:text-black">${f.evidence}</pre>
            </div>

          </div>
        </div>

        <!-- Tab 2: AI remediation guidance -->
        <div id="inspector-tab-patch" class="p-4 hidden bg-slate-50/50">
          <div class="rounded-lg border border-slate-800 bg-[#0B1220] overflow-hidden shadow-md">
            
            <!-- Editor Titlebar -->
            <div class="bg-[#0F172A] px-3.5 py-2 border-b border-slate-800 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-[#EF4444]"></span>
                  <span class="w-2.5 h-2.5 rounded-full bg-[#F59E0B]"></span>
                  <span class="w-2.5 h-2.5 rounded-full bg-[#10B981]"></span>
                </div>
                <div class="ml-3 px-2.5 py-0.5 bg-[#0B1220] text-slate-200 text-xs font-mono rounded-t border-t border-x border-slate-800 flex items-center gap-1.5">
                  <i data-lucide="file-code" class="w-3.5 h-3.5 text-psOrange"></i>
                  <span>Recommended security controls</span>
                </div>
              </div>
              <button onclick="copyToClipboard('code-patch', this)" class="text-slate-300 hover:text-white text-xs font-mono bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded transition">
                Copy Guidance
              </button>
            </div>

            <div class="p-4 text-xs leading-relaxed text-slate-200 overflow-x-auto">
              <pre id="code-patch" class="whitespace-pre-wrap font-sans">${f.remediationCode}</pre>
            </div>

          </div>
        </div>

      </div>
    `;
    if (window.lucide) lucide.createIcons();
  },

  switchInspectorTab(tab) {
    const tabs = ['poc', 'patch'];
    tabs.forEach(t => {
      const btn = document.getElementById(`btn-tab-${t}`);
      const content = document.getElementById(`inspector-tab-${t}`);
      if (!btn || !content) return;

      if (t === tab) {
        btn.className = "px-4 py-2.5 text-psOrange border-b-2 border-psOrange font-bold bg-white";
        content.classList.remove("hidden");
      } else {
        btn.className = "px-4 py-2.5 text-psTextMuted hover:text-psNavy transition font-medium";
        content.classList.add("hidden");
      }
    });
  }
};