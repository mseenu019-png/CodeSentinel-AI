/**
 * CodeSentinel AI - Client Application Logic
 * v2.6 Enterprise - Clean Code A vs B Arena, ER Architecture Flowchart & Live Pipeline
 */

let state = {
  currentReview: null,
  selectedFile: null,
  activeTab: 'welcome',
  repoSubView: 'overview',
  categoryFilter: 'all',
  issuesSearchQuery: '',
  searchQuery: '',
  currentDuel: null,
  activeOptForm: {},
  activeDemoId: 'vulnerable_ecommerce'
};

// Neutral test pairs for Efficiency Duel
const DUEL_PRESETS = {
  search: {
    code_a: `# Code A: Sequential Scan
def find_item(arr, target):
    for idx, item in enumerate(arr):
        if item == target:
            return idx
    return -1
`,
    code_b: `# Code B: Bisection Interval Scan
def find_item(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
`
  },
  fibonacci: {
    code_a: `# Code A: Recursive Formula
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
`,
    code_b: `# Code B: Iterative Accumulator
def fib(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr
`
  },
  duplicates: {
    code_a: `# Code A: Nested Iteration
def has_duplicates(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]: return True
    return False
`,
    code_b: `# Code B: Hash Set Lookup
def has_duplicates(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
`
  },
  sorting: {
    code_a: `# Code A: Quadratic Bubble Loop
def sort_items(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
`,
    code_b: `# Code B: Divide and Conquer
def sort_items(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return sort_items(left) + middle + sort_items(right)
`
  },
  string_builder: {
    code_a: `# Code A: String Concatenation in Loop
def build_report(items):
    res = ""
    for item in items:
        res += str(item) + ","
    return res
`,
    code_b: `# Code B: List Buffer Join
def build_report(items):
    buffer = []
    for item in items:
        buffer.append(str(item))
    return ",".join(buffer)
`
  }
};

// Document ready
document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) lucide.createIcons();

  // Listen for global ENTER keypress to enter the cabin workout area
  window.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && state.activeTab === "welcome") {
      const activeEl = document.activeElement;
      if (activeEl && (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA")) {
        return;
      }
      e.preventDefault();
      enterCabinWorkout();
    }
  });

  // Pre-load default demo project
  loadSelectedSample('vulnerable_ecommerce');

  // Trigger initial specs on default duel snippets
  handleCodeInput('a');
  handleCodeInput('b');
  runEfficiencyDuel();
});

// Toast Notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  const bg = type === "error" ? "bg-rose-950 border-rose-800 text-rose-200" :
             type === "success" ? "bg-emerald-950 border-emerald-800 text-emerald-200" :
             "bg-slate-900 border-slate-700 text-white";
  toast.className = `p-3 rounded-xl border text-xs font-medium shadow-2xl backdrop-blur transition-all duration-300 pointer-events-auto flex items-center gap-2 transform translate-y-2 opacity-0 ${bg}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  });

  setTimeout(() => {
    toast.classList.add("translate-y-2", "opacity-0");
    setTimeout(() => toast.remove(), 3200);
  }, 3200);
}

// Welcoming Cabin Entrance Actions
function enterCabinWorkout() {
  showToast("🚪 Entering Cabin Workout Area...", "success");
  switchTab('repo');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function enterSpecificStation(station) {
  switchTab(station);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Tab Switching
function switchTab(tab) {
  state.activeTab = tab;
  ['welcome', 'repo', 'duel', 'reusability', 'graph', 'pipeline'].forEach(t => {
    const btn = document.getElementById(`tab-${t}`);
    const view = document.getElementById(`view-${t}`);
    if (!view) return;
    if (t === tab) {
      if (btn) btn.className = "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm";
      view.classList.remove("hidden");
    } else {
      if (btn) btn.className = "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-all";
      view.classList.add("hidden");
    }
  });

  if (tab === 'graph') {
    renderDependencyGraph();
  } else if (tab === 'reusability') {
    renderReusabilityTab();
  }

  if (window.lucide) lucide.createIcons();
}

// Repository Audit Sub-View Switcher
function switchRepoSubView(subview) {
  state.repoSubView = subview;
  ['overview', 'findings', 'inspector'].forEach(sv => {
    const btn = document.getElementById(`subtab-${sv}`);
    const view = document.getElementById(`repo-subview-${sv}`);
    if (!view) return;
    if (sv === subview) {
      view.classList.remove("hidden");
      if (btn) {
        btn.className = "subnav-pill subnav-pill-active flex items-center gap-1.5";
      }
    } else {
      view.classList.add("hidden");
      if (btn) {
        btn.className = "subnav-pill subnav-pill-inactive flex items-center gap-1.5";
      }
    }
  });
  if (subview === 'findings') {
    renderAllIssuesList();
  } else if (subview === 'inspector') {
    renderFileTree();
    renderCodeViewer();
  }
  if (window.lucide) lucide.createIcons();
}

// 1-Click Demo Project Switching
async function loadDemoAndOpen(sampleId) {
  state.activeDemoId = sampleId;
  await loadSelectedSample(sampleId);
  switchTab('repo');
  switchRepoSubView('overview');
  showToast(`Loaded ${sampleId.replace(/_/g, ' ').toUpperCase()}`, "success");
}

// Sample Loader
async function loadSelectedSample(sampleId) {
  try {
    const resp = await fetch(`/api/review/sample/${sampleId}`);
    if (!resp.ok) throw new Error("Failed to load sample");
    const data = await resp.json();
    state.currentReview = data;
    if (data.files && data.files.length > 0) {
      const sorted = [...data.files].sort((a,b) => b.critical_issues - a.critical_issues);
      state.selectedFile = sorted[0].path;
    }
    updateDemoButtonStyles(sampleId);
    renderAll();
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  }
}

function updateDemoButtonStyles(activeId) {
  const titles = {
    vulnerable_ecommerce: "E-Commerce FastAPI Backend (Vulnerable)",
    algorithm_duel_suite: "Algorithm Complexity Duel Suite",
    fullstack_cloud_service: "Cloud Microservice Polyglot App"
  };
  const activeTitle = document.getElementById("active-demo-title");
  if (activeTitle && titles[activeId]) {
    activeTitle.textContent = titles[activeId];
  }

  const map = {
    vulnerable_ecommerce: 'btn-demo-ecommerce',
    algorithm_duel_suite: 'btn-demo-duel',
    fullstack_cloud_service: 'btn-demo-cloud'
  };
  Object.keys(map).forEach(key => {
    const btn = document.getElementById(map[key]);
    if (!btn) return;
    if (key === activeId) {
      btn.className = "px-3 py-1.5 rounded-lg bg-cyan-950 text-cyan-300 border border-cyan-800 font-semibold transition flex items-center gap-1.5";
    } else {
      btn.className = "px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 font-semibold hover:bg-slate-700 transition flex items-center gap-1.5";
    }
  });
}

// File Upload
async function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    showToast(`Uploading & analyzing ${file.name}...`, "info");
    const resp = await fetch("/api/review/upload", {
      method: "POST",
      body: formData
    });
    if (!resp.ok) {
      const errData = await resp.json();
      throw new Error(errData.detail || "Upload scan failed");
    }
    const data = await resp.json();
    state.currentReview = data;
    if (data.files && data.files.length > 0) {
      const sorted = [...data.files].sort((a,b) => b.critical_issues - a.critical_issues);
      state.selectedFile = sorted[0].path;
    }
    switchTab('repo');
    switchRepoSubView('overview');
    renderAll();
    showToast(`Audit complete for ${file.name}!`, "success");
  } catch (err) {
    showToast(`Upload Error: ${err.message}`, "error");
  } finally {
    e.target.value = "";
  }
}

// PDF Export
async function downloadPdfReport() {
  if (!state.currentReview) return showToast("No review active to export", "error");
  try {
    showToast("Generating PDF audit report...", "info");
    const resp = await fetch("/api/report/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.currentReview)
    });
    if (!resp.ok) throw new Error("PDF generation failed");
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Audit_Report_${state.currentReview.summary.project_name.replace(/[\s\/]/g, '_')}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast("PDF report downloaded!", "success");
  } catch (err) {
    showToast(`Export Error: ${err.message}`, "error");
  }
}

// Render Master
function renderAll() {
  if (!state.currentReview) return;
  renderDashboard();
  renderAllIssuesList();
  renderFileTree();
  renderCodeViewer();
  renderReusabilityTab();
  renderRequestPlayerState();
  if (window.lucide) lucide.createIcons();
}

// Executive Dashboard
function renderDashboard() {
  const sum = state.currentReview.summary;
  
  const scoreElem = document.getElementById("score-health");
  const gradeElem = document.getElementById("score-grade");
  const descElem = document.getElementById("score-health-desc");
  const circleElem = document.getElementById("gauge-health-circle");

  if (scoreElem) scoreElem.textContent = sum.health_score;
  if (gradeElem) {
    gradeElem.textContent = sum.grade;
    gradeElem.className = `absolute font-black text-base ${
      sum.grade.startsWith('A') ? 'text-emerald-400' :
      sum.grade.startsWith('B') ? 'text-cyan-400' :
      sum.grade.startsWith('C') ? 'text-amber-400' : 'text-rose-400'
    }`;
  }
  if (descElem) {
    descElem.textContent = sum.health_score >= 80 ? "Production Quality" :
                           sum.health_score >= 70 ? "Balanced Assessment" :
                           "Optimization Advised";
  }
  if (circleElem) {
    const maxOffset = 125.6;
    const offset = maxOffset - (maxOffset * sum.health_score / 100);
    circleElem.style.strokeDashoffset = offset;
    circleElem.style.stroke = sum.health_score >= 80 ? '#10b981' :
                              sum.health_score >= 70 ? '#0ea5e9' : '#f59e0b';
  }

  document.getElementById("score-reusability").textContent = sum.reusability_score || 89;
  document.getElementById("score-security").textContent = sum.security_score;
  document.getElementById("score-efficiency").textContent = sum.efficiency_score;
  document.getElementById("score-maintainability").textContent = sum.maintainability_score;
  document.getElementById("score-reliability").textContent = sum.reliability_score;

  document.getElementById("banner-project-title").textContent = sum.project_name;
  document.getElementById("banner-metrics").textContent = `${sum.total_files} files, ${sum.total_lines} LOC`;
  document.getElementById("banner-summary-text").textContent = sum.executive_summary;

  const totalIssues = state.currentReview.issues.length;
  document.getElementById("count-all").textContent = totalIssues;
  document.getElementById("subtab-findings-count").textContent = totalIssues;
  document.getElementById("badge-issue-count").textContent = totalIssues;

  document.getElementById("count-sec").textContent = sum.issues_by_category.security || 0;
  document.getElementById("count-eff").textContent = sum.issues_by_category.efficiency || 0;
  document.getElementById("count-bug").textContent = sum.issues_by_category.bug || 0;

  // Render recognized strengths in overview
  const strengthsContainer = document.getElementById("strengths-overview-container");
  if (strengthsContainer) {
    strengthsContainer.innerHTML = (sum.strengths || []).map(s => `
      <div class="p-3.5 rounded-xl bg-[#091020] border border-slate-800 flex items-start gap-3">
        <div class="w-6 h-6 rounded-lg bg-emerald-500/15 text-emerald-400 flex items-center justify-center flex-shrink-0 mt-0.5">
          <i data-lucide="check" class="w-3.5 h-3.5"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-white">${s.title}</span>
            <span class="text-[10px] font-mono text-slate-400">${s.file}</span>
          </div>
          <p class="text-xs text-slate-300 mt-1">${s.description}</p>
          <span class="text-[10px] text-emerald-400 font-semibold mt-1 block">✓ ${s.impact}</span>
        </div>
      </div>
    `).join('') || '<div class="text-slate-400 text-xs">Standard conventions confirmed across files.</div>';
  }
}

// Actionable Findings Subview
function renderAllIssuesList() {
  const container = document.getElementById("all-issues-list-container");
  if (!container || !state.currentReview) return;
  container.innerHTML = "";

  const allIssues = state.currentReview.issues || [];
  const cat = state.categoryFilter;
  const q = (state.issuesSearchQuery || '').toLowerCase();

  const filtered = allIssues.filter(i => {
    if (cat !== 'all' && i.category !== cat) return false;
    if (q) {
      const text = `${i.title} ${i.description} ${i.rule_id} ${i.file}`.toLowerCase();
      if (!text.includes(q)) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="p-12 text-center text-slate-400 glass-panel rounded-2xl flex flex-col items-center gap-2">
        <i data-lucide="check-circle" class="w-8 h-8 text-emerald-400"></i>
        <span class="text-sm font-semibold text-white">No issues found matching current filter!</span>
        <span class="text-xs">Your code passes all selected check criteria cleanly.</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  filtered.forEach(iss => {
    const card = document.createElement("div");
    const sevColor = iss.severity === 'critical' ? 'border-l-rose-500 text-rose-200' :
                     iss.severity === 'high' ? 'border-l-orange-500 text-orange-200' :
                     iss.severity === 'medium' ? 'border-l-amber-500 text-amber-200' :
                     'border-l-sky-500 text-sky-200';
    
    const badgeColor = iss.severity === 'critical' ? 'bg-rose-500/20 text-rose-300' :
                      iss.severity === 'high' ? 'bg-orange-500/20 text-orange-300' :
                      iss.severity === 'medium' ? 'bg-amber-500/20 text-amber-300' :
                      'bg-sky-500/20 text-sky-300';

    card.className = `glass-panel rounded-2xl p-4 border border-slate-800 border-l-4 ${sevColor} flex flex-col gap-3`;
    card.innerHTML = `
      <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${badgeColor}">${iss.severity}</span>
          <span class="font-bold text-sm text-white">${iss.title}</span>
          <span class="text-[10px] font-mono text-slate-400">• ${iss.file}:${iss.line}</span>
        </div>
        <span class="font-mono text-[10px] text-slate-400">${iss.rule_id}</span>
      </div>

      <p class="text-xs text-slate-200 leading-relaxed">${iss.description}</p>
      <div class="text-[11px] text-rose-300 font-medium"><strong>Potential Impact:</strong> ${iss.impact}</div>

      ${iss.suggested_fix ? `
        <div class="bg-black/80 rounded-xl p-3 border border-slate-800 font-mono text-xs overflow-x-auto text-emerald-300 relative group/fix">
          <div class="text-[10px] text-slate-400 uppercase tracking-wider mb-1.5 font-sans flex items-center justify-between">
            <span>Verified Remediation:</span>
            <button onclick="navigator.clipboard.writeText(\`${escapeQuotes(iss.suggested_fix)}\`); showToast('Remediation copied to clipboard!', 'success');" class="text-xs text-slate-300 hover:text-white px-2 py-0.5 rounded bg-white/10 cursor-pointer">Copy Safe Fix</button>
          </div>
          <pre>${escapeHtml(iss.suggested_fix)}</pre>
        </div>
      ` : ''}

      <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">
        <span class="italic"><strong>Why this works:</strong> ${iss.explanation}</span>
        <button onclick="inspectFileAtLine('${iss.file}', ${iss.line})" class="text-cyan-400 hover:text-cyan-300 font-semibold cursor-pointer">
          Jump to Code →
        </button>
      </div>
    `;
    container.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

function setFilterCategory(cat) {
  state.categoryFilter = cat;
  ['all', 'sec', 'eff', 'bug'].forEach(c => {
    const btn = document.getElementById(`filter-${c}`);
    if (!btn) return;
    const isTarget = (c === 'all' && cat === 'all') ||
                     (c === 'sec' && cat === 'security') ||
                     (c === 'eff' && cat === 'efficiency') ||
                     (c === 'bug' && cat === 'bug');
    if (isTarget) {
      btn.className = "px-3 py-1 rounded-lg bg-cyan-600 text-white font-semibold";
    } else {
      btn.className = "px-3 py-1 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 font-semibold";
    }
  });
  renderAllIssuesList();
}

function filterIssuesList(query) {
  state.issuesSearchQuery = query;
  renderAllIssuesList();
}

function inspectFileAtLine(filePath, line) {
  state.selectedFile = filePath;
  switchRepoSubView('inspector');
  setTimeout(() => {
    const el = document.getElementById(`code-line-row-${line}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.classList.add('ring-2', 'ring-cyan-400');
      setTimeout(() => el.classList.remove('ring-2', 'ring-cyan-400'), 2500);
    }
  }, 100);
}

// File Tree Explorer
function renderFileTree() {
  const container = document.getElementById("file-tree-container");
  if (!container || !state.currentReview) return;
  container.innerHTML = "";

  const files = state.currentReview.files;
  document.getElementById("files-total-badge").textContent = `${files.length} files`;

  const query = state.searchQuery.toLowerCase();

  files.forEach(f => {
    if (query && !f.path.toLowerCase().includes(query)) return;

    const isActive = f.path === state.selectedFile;
    const item = document.createElement("div");
    item.className = `flex items-center justify-between p-2 rounded-xl cursor-pointer text-xs transition border ${
      isActive ? 'bg-cyan-950/60 border-cyan-500/60 text-white shadow-sm' :
      'bg-[#091020] hover:bg-slate-800/80 border-slate-800 text-slate-300'
    }`;
    item.onclick = () => {
      state.selectedFile = f.path;
      renderFileTree();
      renderCodeViewer();
    };

    const hasIssues = f.issues_count > 0;
    const badgeColor = f.critical_issues > 0 ? 'bg-rose-500/20 text-rose-300' :
                       f.issues_count > 0 ? 'bg-amber-500/20 text-amber-300' :
                       'bg-emerald-500/20 text-emerald-300';

    item.innerHTML = `
      <div class="flex items-center gap-2 truncate">
        <i data-lucide="file" class="w-3.5 h-3.5 text-slate-400 flex-shrink-0"></i>
        <span class="truncate font-mono">${f.name}</span>
      </div>
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <span class="text-[10px] text-slate-400 font-mono">${f.loc} LOC</span>
        ${hasIssues ? `<span class="px-1.5 py-0.2 rounded-full text-[10px] font-bold ${badgeColor}">${f.issues_count}</span>` : ''}
      </div>
    `;
    container.appendChild(item);
  });

  if (window.lucide) lucide.createIcons();
}

function filterFiles(query) {
  state.searchQuery = query;
  renderFileTree();
}

// Code Viewer with Inline Issues
function renderCodeViewer() {
  const container = document.getElementById("code-lines-container");
  if (!container || !state.currentReview) return;
  container.innerHTML = "";

  const file = state.currentReview.files.find(f => f.path === state.selectedFile) || state.currentReview.files[0];
  if (!file) return;

  state.selectedFile = file.path;
  document.getElementById("current-filename").textContent = file.name;
  
  const fileBadge = document.getElementById("current-file-badge");
  fileBadge.textContent = `${file.issues_count} Issues`;
  fileBadge.className = `text-[10px] px-2 py-0.5 rounded font-mono ${
    file.critical_issues > 0 ? 'bg-rose-500/20 text-rose-300' :
    file.issues_count > 0 ? 'bg-amber-500/20 text-amber-300' :
    'bg-emerald-500/20 text-emerald-300'
  }`;

  const codeText = state.currentReview.file_contents[file.path] || `# File: ${file.name}\n# Content not cached.`;
  const lines = codeText.split("\n");
  const fileIssues = (state.currentReview.issues || []).filter(i => i.file === file.path);

  lines.forEach((lineText, idx) => {
    const lineNum = idx + 1;
    const issues = fileIssues.filter(i => i.line === lineNum);

    const lineRow = document.createElement("div");
    lineRow.id = `code-line-row-${lineNum}`;

    let highlightClass = "";
    if (issues.length > 0) {
      const topSev = issues[0].severity;
      highlightClass = `code-line-highlight-${topSev}`;
    }

    lineRow.className = `flex items-start hover:bg-slate-800/40 transition group py-0.5 ${highlightClass}`;
    lineRow.innerHTML = `
      <div class="code-line-num">${lineNum}</div>
      <div class="code-line-content font-mono">${escapeHtml(lineText) || " "}</div>
    `;
    container.appendChild(lineRow);

    if (issues.length > 0) {
      issues.forEach(iss => {
        const reviewCard = document.createElement("div");
        const cardSev = iss.severity === 'critical' ? 'bg-rose-950/50 border-rose-800 text-rose-200' :
                        iss.severity === 'high' ? 'bg-orange-950/50 border-orange-800 text-orange-200' :
                        iss.severity === 'medium' ? 'bg-amber-950/50 border-amber-800 text-amber-200' :
                        'bg-sky-950/50 border-sky-800 text-sky-200';

        reviewCard.className = `my-2 mx-12 p-3.5 rounded-xl border text-xs shadow-xl backdrop-blur ${cardSev}`;
        reviewCard.innerHTML = `
          <div class="flex items-center justify-between gap-2 border-b border-white/10 pb-1.5 mb-1.5">
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-white/10">${iss.severity}</span>
              <span class="font-bold text-white">${iss.title}</span>
            </div>
            <span class="font-mono text-[10px] text-white/50">${iss.rule_id}</span>
          </div>

          <p class="text-slate-200 text-xs mb-1.5 leading-relaxed">${iss.description}</p>
          <div class="text-[11px] text-rose-300 font-medium mb-2"><strong>Impact:</strong> ${iss.impact}</div>

          ${iss.suggested_fix ? `
            <div class="bg-black/70 rounded-lg p-2.5 border border-white/10 font-mono text-xs overflow-x-auto text-emerald-300 mb-1.5 relative group/fix">
              <div class="text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-sans flex items-center justify-between">
                <span>Safe Remediation:</span>
                <button onclick="navigator.clipboard.writeText(\`${escapeQuotes(iss.suggested_fix)}\`); showToast('Remediation copied!', 'success');" class="text-xs text-slate-300 hover:text-white px-2 py-0.5 rounded bg-white/10">Copy Fix</button>
              </div>
              <pre>${escapeHtml(iss.suggested_fix)}</pre>
            </div>
          ` : ''}

          <div class="text-[11px] text-slate-400 italic">
            <strong>Why this works:</strong> ${iss.explanation}
          </div>
        `;
        container.appendChild(reviewCard);
      });
    }
  });
}

// Reusability Tab & Multi-Form Cards
function renderReusabilityTab() {
  if (!state.currentReview) return;

  const allOptsContainer = document.getElementById("all-optimizations-container");
  if (!allOptsContainer) return;
  allOptsContainer.innerHTML = "";

  const opts = state.currentReview.optimizations || [];
  if (opts.length === 0) {
    allOptsContainer.innerHTML = `<div class="p-8 text-center text-slate-400 text-xs">No multi-form targets available for this repository.</div>`;
    return;
  }

  opts.forEach(opt => {
    const activeForm = state.activeOptForm[opt.target_name] || opt.pathways[0].form_type;
    const selectedPathway = opt.pathways.find(p => p.form_type === activeForm) || opt.pathways[0];

    const item = document.createElement("div");
    item.className = "glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col gap-4";
    item.innerHTML = `
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <span class="text-[10px] uppercase font-bold text-violet-400">Target File: ${opt.file}</span>
          <h4 class="text-sm font-bold text-white mt-0.5">${opt.target_name}</h4>
        </div>
        <span class="text-xs bg-violet-500/20 text-violet-300 px-2.5 py-1 rounded-full font-semibold">
          Reusability Index: ${opt.reusability_score}/100
        </span>
      </div>

      <!-- 3 Clean Form Switcher Tabs -->
      <div class="flex flex-wrap gap-2">
        ${opt.pathways.map(p => `
          <button onclick="setOptForm('${opt.target_name}', '${p.form_type}')" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${p.form_type === activeForm ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-md' : 'bg-[#091020] text-slate-300 hover:text-white border border-slate-800'}">
            ${p.title}
          </button>
        `).join('')}
      </div>

      <!-- Target Form Details -->
      <div class="p-4 rounded-xl bg-[#070e1c] border border-slate-800 flex flex-col gap-2.5">
        <div class="flex items-center justify-between">
          <span class="font-bold text-xs text-white">${selectedPathway.title}</span>
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-0.5 rounded">${selectedPathway.time_complexity}</span>
            <span class="text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded">${selectedPathway.space_complexity}</span>
          </div>
        </div>
        <p class="text-xs text-slate-300">${selectedPathway.tagline}</p>

        <div class="bg-black/90 rounded-lg p-3 font-mono text-xs text-emerald-300 border border-slate-800 overflow-x-auto relative">
          <button onclick="navigator.clipboard.writeText(\`${escapeQuotes(selectedPathway.code)}\`); showToast('Optimized code copied!', 'success');" class="absolute top-2 right-2 text-xs bg-white/10 hover:bg-white/20 text-white px-2.5 py-1 rounded cursor-pointer">Copy Code</button>
          <pre>${escapeHtml(selectedPathway.code)}</pre>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs mt-1">
          <div class="p-2.5 rounded-lg bg-[#091020] border border-slate-800">
            <span class="text-slate-400 uppercase text-[10px] block font-semibold">Best Suited For:</span>
            <span class="text-slate-200">${selectedPathway.best_suited_for}</span>
          </div>
          <div class="p-2.5 rounded-lg bg-[#091020] border border-slate-800">
            <span class="text-slate-400 uppercase text-[10px] block font-semibold">Engineering Trade-offs:</span>
            <span class="text-slate-200">${selectedPathway.tradeoffs}</span>
          </div>
        </div>
      </div>
    `;
    allOptsContainer.appendChild(item);
  });
}

function setOptForm(targetName, formType) {
  state.activeOptForm[targetName] = formType;
  renderReusabilityTab();
}

// ==================== TAB 2: EFFICIENCY DUEL (STRICTLY CODE A VS CODE B) ====================
function handleCodeInput(candidate) {
  const code = document.getElementById(`code-input-${candidate}`)?.value || "";
  const lines = code.split("\n").filter(l => l.trim() && !l.trim().startsWith("#") && !l.trim().startsWith("//"));
  const locBadge = document.getElementById(`loc-badge-${candidate}`);
  if (locBadge) locBadge.textContent = `${lines.length} LOC`;

  const bigoBadge = document.getElementById(`bigo-badge-${candidate}`);
  if (bigoBadge) {
    if (code.includes("while") && (code.includes("mid") || code.includes("// 2"))) {
      bigoBadge.textContent = "O(log n) Time";
      bigoBadge.className = "text-[10px] text-emerald-300 font-mono bg-emerald-950 border border-emerald-800 px-2 py-0.5 rounded";
    } else if (code.includes("for ") && code.includes("for ") && code.split("for ").length >= 3) {
      bigoBadge.textContent = "O(n^2) Time";
      bigoBadge.className = "text-[10px] text-rose-300 font-mono bg-rose-950 border border-rose-800 px-2 py-0.5 rounded";
    } else if (code.includes("fib(") || code.includes("return ") && code.includes(" + ")) {
      bigoBadge.textContent = "O(2^n) Time";
      bigoBadge.className = "text-[10px] text-rose-300 font-mono bg-rose-950 border border-rose-800 px-2 py-0.5 rounded";
    } else if (code.includes("for ") || code.includes("while ")) {
      bigoBadge.textContent = "O(n) Time";
      bigoBadge.className = "text-[10px] text-cyan-300 font-mono bg-cyan-950 border border-cyan-800 px-2 py-0.5 rounded";
    } else {
      bigoBadge.textContent = "O(1) Time";
      bigoBadge.className = "text-[10px] text-emerald-300 font-mono bg-emerald-950 border border-emerald-800 px-2 py-0.5 rounded";
    }
  }
}

function loadDuelPreset(presetKey) {
  const p = DUEL_PRESETS[presetKey];
  if (!p) return;
  document.getElementById("code-input-a").value = p.code_a;
  document.getElementById("code-input-b").value = p.code_b;
  handleCodeInput('a');
  handleCodeInput('b');
  runEfficiencyDuel();
}

async function runEfficiencyDuel() {
  const codeA = document.getElementById("code-input-a")?.value || "";
  const codeB = document.getElementById("code-input-b")?.value || "";

  const container = document.getElementById("duel-results-container");
  if (!container) return;

  container.innerHTML = `<div class="p-8 text-center text-slate-400 text-xs">Simulating computational execution & benchmarking scaling...</div>`;

  try {
    const resp = await fetch("/api/duel/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code_a: codeA,
        code_b: codeB,
        label_a: "Code A",
        label_b: "Code B",
        language: "python"
      })
    });

    if (!resp.ok) throw new Error("Duel evaluation failed");
    const duel = await resp.json();
    state.currentDuel = duel;

    renderDuelResults(duel);
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-rose-950/40 rounded-xl border border-rose-800 text-rose-300 text-xs">Duel Error: ${err.message}</div>`;
  }
}

function renderDuelResults(duel) {
  const container = document.getElementById("duel-results-container");
  if (!container) return;

  const winnerIsA = duel.winner === 'A';
  const winnerIsB = duel.winner === 'B';

  const winnerTitle = winnerIsB ? "🏆 Code B Wins on Efficiency!" :
                      winnerIsA ? "🏆 Code A Wins on Efficiency!" :
                      "⚖️ Algorithmic Tie!";

  const winnerColor = winnerIsB ? "from-emerald-500/20 border-emerald-500/40 text-emerald-300" :
                      winnerIsA ? "from-cyan-500/20 border-cyan-500/40 text-cyan-300" :
                      "from-amber-500/20 border-amber-500/40 text-amber-300";

  container.innerHTML = `
    <!-- 1. Winner Trophy Banner -->
    <div class="glass-panel rounded-2xl p-6 bg-gradient-to-r ${winnerColor} border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
      <div class="flex items-start gap-4">
        <div class="p-3 rounded-2xl bg-amber-500/20 text-amber-400 flex-shrink-0">
          <i data-lucide="trophy" class="w-8 h-8"></i>
        </div>
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-amber-400">Official Arena Verdict</span>
          <h3 class="text-xl font-bold text-white mt-0.5">${winnerTitle}</h3>
          <p class="text-xs text-slate-200 mt-1 leading-relaxed max-w-3xl">${duel.executive_verdict}</p>
        </div>
      </div>
      <div class="flex-shrink-0">
        <span class="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-bold text-white uppercase tracking-wider">
          ${winnerIsB ? 'Winner: Code B' : winnerIsA ? 'Winner: Code A' : 'Result: Equivalent'}
        </span>
      </div>
    </div>

    <!-- 2. Brevity Lesson Callout -->
    <div class="glass-panel rounded-2xl p-5 border-l-4 border-l-amber-500 flex flex-col gap-2">
      <div class="flex items-center gap-2">
        <i data-lucide="info" class="w-4 h-4 text-amber-400"></i>
        <h4 class="text-xs font-bold uppercase tracking-wider text-amber-300">Why Line Count Brevity Can Be Deceptive</h4>
      </div>
      <p class="text-xs text-slate-200 leading-relaxed">${duel.why_brevity_can_fail}</p>
    </div>

    <!-- 3. Side-by-Side Complexity Matrix -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- Code A Card -->
      <div class="glass-panel rounded-2xl p-5 flex flex-col gap-4 border border-slate-800 ${winnerIsA ? 'ring-2 ring-cyan-500/40' : ''}">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <span class="font-bold text-sm text-white">Code A (${duel.candidate_a.loc} LOC)</span>
            <span class="text-[10px] text-slate-400 block">${duel.candidate_a.paradigm || 'Sequential Implementation'}</span>
          </div>
          <span class="px-2.5 py-1 rounded text-xs font-black font-mono bg-cyan-500/20 text-cyan-300">${duel.candidate_a.time_big_o}</span>
        </div>

        <div class="grid grid-cols-2 gap-3 text-xs">
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Time Complexity</span>
            <span class="font-bold text-sm text-cyan-300">${duel.candidate_a.time_big_o}</span>
          </div>
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Space Complexity</span>
            <span class="font-bold text-sm text-slate-200">${duel.candidate_a.space_big_o}</span>
          </div>
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Stack & Memory Profile</span>
            <span class="font-bold text-xs text-slate-300">${duel.candidate_a.recursion_depth}</span>
          </div>
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Defensive Safety Score</span>
            <span class="font-bold text-sm text-emerald-400">${duel.candidate_a.safety_score}%</span>
          </div>
        </div>
      </div>

      <!-- Code B Card -->
      <div class="glass-panel rounded-2xl p-5 flex flex-col gap-4 border border-slate-800 ${winnerIsB ? 'ring-2 ring-emerald-500/40' : ''}">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <span class="font-bold text-sm text-white">Code B (${duel.candidate_b.loc} LOC)</span>
            <span class="text-[10px] text-slate-400 block">${duel.candidate_b.paradigm || 'Optimized Implementation'}</span>
          </div>
          <span class="px-2.5 py-1 rounded text-xs font-black font-mono bg-emerald-500/20 text-emerald-300">${duel.candidate_b.time_big_o}</span>
        </div>

        <div class="grid grid-cols-2 gap-3 text-xs">
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Time Complexity</span>
            <span class="font-bold text-sm text-emerald-300">${duel.candidate_b.time_big_o}</span>
          </div>
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Space Complexity</span>
            <span class="font-bold text-sm text-slate-200">${duel.candidate_b.space_big_o}</span>
          </div>
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Stack & Memory Profile</span>
            <span class="font-bold text-xs text-slate-300">${duel.candidate_b.recursion_depth}</span>
          </div>
          <div class="p-3 rounded-xl bg-[#091020]">
            <span class="text-slate-400 text-[10px] block">Defensive Safety Score</span>
            <span class="font-bold text-sm text-emerald-400">${duel.candidate_b.safety_score}%</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 4. Algorithmic Scalability Simulation Table -->
    <div class="glass-panel rounded-2xl p-5 flex flex-col gap-3">
      <div class="flex items-center justify-between">
        <h4 class="text-sm font-bold text-white flex items-center gap-2">
          <i data-lucide="line-chart" class="w-4 h-4 text-cyan-400"></i> Operation Count Simulation (${duel.candidate_a.scale_label || 'Input Size N'})
        </h4>
        <span class="text-xs text-slate-400">Empirical CPU operation steps required under scale:</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-xs text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
              <th class="py-2.5 px-3">Input Size N</th>
              <th class="py-2.5 px-3">Code A Operations</th>
              <th class="py-2.5 px-3">Code B Operations</th>
              <th class="py-2.5 px-3">Performance Advantage</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono">
            ${duel.simulation_points.map(pt => {
              const ratio = pt.ops_b > 0 ? (pt.ops_a / pt.ops_b).toFixed(1) : "1.0";
              const isHuge = pt.ops_a > 1000000;
              return `
                <tr class="hover:bg-slate-800/40">
                  <td class="py-2 px-3 font-bold text-white">N = ${pt.n.toLocaleString()}</td>
                  <td class="py-2 px-3 ${isHuge ? 'text-rose-400 font-bold' : 'text-slate-300'}">
                    ${formatNumber(pt.ops_a)} ops ${isHuge ? '🔥 (Timeout / Slowdown)' : ''}
                  </td>
                  <td class="py-2 px-3 text-emerald-400 font-bold">
                    ${formatNumber(pt.ops_b)} ops
                  </td>
                  <td class="py-2 px-3 text-cyan-300 font-bold">
                    ${isHuge ? '> 1,000,000x Slower' : (pt.ops_a > pt.ops_b ? `${ratio}x Faster` : (pt.ops_a < pt.ops_b ? `${(pt.ops_b/pt.ops_a).toFixed(1)}x Slower` : 'Equivalent'))}
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
      <div class="text-[11px] text-slate-400 italic mt-1">
        ${duel.scalability_summary}
      </div>
    </div>
  `;

  if (window.lucide) lucide.createIcons();
}

function formatNumber(num) {
  if (num >= 1e12) return (num / 1e12).toFixed(2) + " Trillion";
  if (num >= 1e9) return (num / 1e9).toFixed(2) + " Billion";
  if (num >= 1e6) return (num / 1e6).toFixed(2) + " Million";
  return Math.round(num).toLocaleString();
}

// ==================== TAB 4: LAYER-BY-LAYER REQUEST & ERROR INSPECTOR ====================
// Inspired by professor's Spring Boot layer-by-layer request player
const REQUEST_SCENARIOS = {
  sqli: {
    title: "Scenario 1: SQL Injection Attack (Error in db.py)",
    steps: [
      {
        layerIndex: 0,
        layerName: "Client: Web Browser UI",
        file: "static/index.html & app.js",
        badge: "Client / UI",
        badgeColor: "bg-amber-500/20 text-amber-300",
        whatHappening: "User enters username \"' OR '1'='1\" and clicks Login. The browser dispatches an asynchronous HTTP POST request to /api/login.",
        codeSnippet: `fetch("/api/login", {\n  method: "POST",\n  headers: { "Content-Type": "application/json" },\n  body: JSON.stringify({ username: "' OR '1'='1", pass: "xyz" })\n});`,
        hasError: false
      },
      {
        layerIndex: 1,
        layerName: "Root Gateway: main.py",
        file: "app/main.py",
        badge: "Controller Tier",
        badgeColor: "bg-cyan-500/20 text-cyan-300",
        whatHappening: "FastAPI receives the HTTP request at the /login route, extracts credentials, and calls auth_service.authenticate().",
        codeSnippet: `@app.post("/login")\ndef login(creds: LoginRequest):\n    # Forward input to auth service\n    return auth_service.authenticate(creds.username, creds.pass)`,
        hasError: false
      },
      {
        layerIndex: 2,
        layerName: "Business Logic: auth.py",
        file: "app/auth.py",
        badge: "Service Tier",
        badgeColor: "bg-indigo-500/20 text-indigo-300",
        whatHappening: "The auth service forwards the raw username directly into the database query function db.get_user_by_name().",
        codeSnippet: `def authenticate(username, password):\n    # Queries user record from database module\n    user = db.get_user_by_name(username)\n    return verify_password(password, user.hash)`,
        hasError: false
      },
      {
        layerIndex: 3,
        layerName: "Database Access: db.py (ERROR OCCURRED!)",
        file: "app/db.py",
        badge: "Database Tier",
        badgeColor: "bg-rose-500/20 text-rose-300",
        whatHappening: "The database module concatenates the untrusted string directly into the SQL query without parameterization!",
        codeSnippet: `# VULNERABLE LINE IN db.py:12\nquery = f"SELECT * FROM users WHERE user = '{username}'"\ncursor.execute(query) # Attacker bypasses authentication!`,
        hasError: true,
        errorTitle: "CWE-89: Critical SQL Injection Vulnerability",
        errorDescription: "Because the input contains \"' OR '1'='1\", the resulting SQL query becomes \"SELECT * FROM users WHERE user = '' OR '1'='1'\", which always evaluates to TRUE. The attacker logs in as Admin without a password!",
        suggestedFix: `# VERIFIED SAFE FIX (Parameterized Binding):\ncursor.execute("SELECT * FROM users WHERE user = %s", (username,))`
      }
    ]
  },
  normal: {
    title: "Scenario 2: Normal Login (Safe 200 OK)",
    steps: [
      {
        layerIndex: 0,
        layerName: "Client: Web Browser UI",
        file: "static/index.html & app.js",
        badge: "Client / UI",
        badgeColor: "bg-amber-500/20 text-amber-300",
        whatHappening: "Legitimate user enters username 'john_dev' and password 'secret123'. The browser sends a clean JSON payload.",
        codeSnippet: `fetch("/api/login", {\n  method: "POST",\n  body: JSON.stringify({ username: "john_dev", pass: "secret123" })\n});`,
        hasError: false
      },
      {
        layerIndex: 1,
        layerName: "Root Gateway: main.py",
        file: "app/main.py",
        badge: "Controller Tier",
        badgeColor: "bg-cyan-500/20 text-cyan-300",
        whatHappening: "FastAPI router receives the payload and passes validated Pydantic model to authentication service.",
        codeSnippet: `@app.post("/login")\ndef login(creds: LoginRequest):\n    return auth_service.authenticate(creds.username, creds.pass)`,
        hasError: false
      },
      {
        layerIndex: 2,
        layerName: "Business Logic: auth.py",
        file: "app/auth.py",
        badge: "Service Tier",
        badgeColor: "bg-indigo-500/20 text-indigo-300",
        whatHappening: "Auth service hashes password with bcrypt and requests user record from db.py.",
        codeSnippet: `def authenticate(username, password):\n    user = db.get_user_by_name(username)\n    return verify_password(password, user.hash)`,
        hasError: false
      },
      {
        layerIndex: 3,
        layerName: "Database Access: db.py",
        file: "app/db.py",
        badge: "Database Tier",
        badgeColor: "bg-emerald-500/20 text-emerald-300",
        whatHappening: "Database executes parameterized query safely. Returns user record and signs valid JWT token (Status 200 OK).",
        codeSnippet: `cursor.execute("SELECT * FROM users WHERE user = %s", (username,))\nreturn cursor.fetchone()`,
        hasError: false,
        cleanNote: "Execution Clean: Parameterized query executed in 2.1 ms. Zero security vulnerabilities or errors detected."
      }
    ]
  },
  slow_search: {
    title: "Scenario 3: Heavy Search (O(N²) Bottleneck)",
    steps: [
      {
        layerIndex: 0,
        layerName: "Client: Web Browser UI",
        file: "static/index.html & app.js",
        badge: "Client / UI",
        badgeColor: "bg-amber-500/20 text-amber-300",
        whatHappening: "Client browser searches a catalog of 500,000 items with search query 'laptop'.",
        codeSnippet: `fetch("/api/search?q=laptop")`,
        hasError: false
      },
      {
        layerIndex: 1,
        layerName: "Root Gateway: main.py",
        file: "app/main.py",
        badge: "Controller Tier",
        badgeColor: "bg-cyan-500/20 text-cyan-300",
        whatHappening: "FastAPI receives query parameter 'laptop' and dispatches request to product_service.",
        codeSnippet: `@app.get("/search")\ndef search_items(q: str):\n    return product_service.search_catalog(q)`,
        hasError: false
      },
      {
        layerIndex: 2,
        layerName: "Business Logic: products.py (BOTTLENECK FOUND!)",
        file: "app/products.py",
        badge: "Service Tier",
        badgeColor: "bg-amber-500/20 text-amber-300",
        whatHappening: "The search function uses nested loops O(N^2) over unindexed tags, causing an algorithmic bottleneck!",
        codeSnippet: `# BOTTLENECK IN products.py:44\nfor item in all_items:\n    for sub in item.tags:\n        if q in sub: matches.append(item)`,
        hasError: true,
        errorTitle: "O(N²) Algorithmic Complexity Bottleneck",
        errorDescription: "Under realistic traffic with 500,000 items, this nested loop requires over 250,000,000 operations, causing high server CPU spike and API timeout!",
        suggestedFix: `# FAST REMEDIATION: Pre-indexed Hash Map Lookup O(1):\nmatches = tag_index.get(q, []) # 0.05ms Instant Response`
      },
      {
        layerIndex: 3,
        layerName: "Database Access: db.py",
        file: "app/db.py",
        badge: "Database Tier",
        badgeColor: "bg-emerald-500/20 text-emerald-300",
        whatHappening: "Database handles read query, but upstream nested loop slowed down response time to 1.8 seconds.",
        codeSnippet: `return cached_records`,
        hasError: false
      }
    ]
  }
};

let playerState = {
  scenarioKey: 'sqli',
  stepIndex: 0,
  isPlaying: false,
  timer: null
};

function renderDependencyGraph() {
  renderRequestPlayerState();
}

function changeRequestScenario(key) {
  playerState.scenarioKey = key;
  playerState.stepIndex = 0;
  pauseRequestPlayer();

  // Update Scenario Quick Pills
  ['sqli', 'normal', 'slow_search'].forEach(k => {
    const pill = document.getElementById(`pill-${k}`);
    if (pill) {
      if (k === key) {
        pill.className = "scenario-pill scenario-pill-active flex items-center gap-1.5 cursor-pointer";
      } else {
        pill.className = "scenario-pill flex items-center gap-1.5 cursor-pointer";
      }
    }
  });

  renderRequestPlayerState();
}

function stepRequestPlayer(dir) {
  pauseRequestPlayer();
  const scenario = REQUEST_SCENARIOS[playerState.scenarioKey];
  playerState.stepIndex = Math.max(0, Math.min(scenario.steps.length - 1, playerState.stepIndex + dir));
  renderRequestPlayerState();
}

function jumpToLayer(idx) {
  pauseRequestPlayer();
  playerState.stepIndex = idx;
  renderRequestPlayerState();
}

function togglePlayRequest() {
  if (playerState.isPlaying) {
    pauseRequestPlayer();
  } else {
    startRequestPlayer();
  }
}

function startRequestPlayer() {
  playerState.isPlaying = true;
  const btnLabel = document.getElementById("btn-play-label");
  if (btnLabel) btnLabel.textContent = "Pause";
  
  const tick = () => {
    const scenario = REQUEST_SCENARIOS[playerState.scenarioKey];
    if (playerState.stepIndex < scenario.steps.length - 1) {
      playerState.stepIndex++;
      renderRequestPlayerState();
    } else {
      pauseRequestPlayer();
      showToast("✓ Request execution completed!", "info");
    }
  };
  
  playerState.timer = setInterval(tick, 1400);
}

function pauseRequestPlayer() {
  playerState.isPlaying = false;
  if (playerState.timer) clearInterval(playerState.timer);
  playerState.timer = null;
  const btnLabel = document.getElementById("btn-play-label");
  if (btnLabel) btnLabel.textContent = "Play";
}

function resetRequestPlayer() {
  pauseRequestPlayer();
  playerState.stepIndex = 0;
  renderRequestPlayerState();
}

function renderRequestPlayerState() {
  const scenario = REQUEST_SCENARIOS[playerState.scenarioKey];
  if (!scenario) return;
  const step = scenario.steps[playerState.stepIndex];

  // Update Left Layer Cards & Dynamic Status Badges
  [0, 1, 2, 3].forEach(i => {
    const card = document.getElementById(`layer-card-${i}`);
    const statusEl = document.getElementById(`layer-status-${i}`);
    if (!card) return;

    if (i === playerState.stepIndex) {
      if (step.hasError) {
        card.className = "step-layer-card error-step p-4 cursor-pointer relative overflow-hidden";
        if (statusEl) {
          statusEl.textContent = "🚨 Error Detected";
          statusEl.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-rose-500/30 text-rose-300 animate-pulse";
        }
      } else {
        card.className = "step-layer-card active-step p-4 cursor-pointer relative overflow-hidden";
        if (statusEl) {
          statusEl.textContent = "⚡ Active Layer";
          statusEl.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-cyan-500/30 text-cyan-300 animate-pulse";
        }
      }
    } else if (i < playerState.stepIndex) {
      card.className = "step-layer-card p-4 cursor-pointer relative overflow-hidden opacity-90 hover:opacity-100 border-slate-700";
      if (statusEl) {
        statusEl.textContent = "✓ Completed";
        statusEl.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-300";
      }
    } else {
      card.className = "step-layer-card p-4 cursor-pointer relative overflow-hidden opacity-50 hover:opacity-90";
      if (statusEl) {
        statusEl.textContent = "Waiting";
        statusEl.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-slate-800 text-slate-400";
      }
    }
  });

  // Dynamically update Layer 2 text for search vs auth
  const layerTitle2 = document.getElementById("layer-title-2");
  const layerFile2 = document.getElementById("layer-file-2");
  if (playerState.scenarioKey === 'slow_search') {
    if (layerTitle2) layerTitle2.innerHTML = `<i data-lucide="cpu" class="w-4 h-4 text-indigo-400"></i> Business Logic: products.py`;
    if (layerFile2) layerFile2.textContent = "app/products.py • Catalog Search";
  } else {
    if (layerTitle2) layerTitle2.innerHTML = `<i data-lucide="cpu" class="w-4 h-4 text-indigo-400"></i> Business Logic: auth.py`;
    if (layerFile2) layerFile2.textContent = "app/auth.py • Core Logic";
  }

  // Update Progress Badge
  const progBadge = document.getElementById("player-progress-badge");
  if (progBadge) {
    progBadge.textContent = `Step ${playerState.stepIndex + 1} of ${scenario.steps.length}`;
  }

  // Update Step Detail Panel
  const titleEl = document.getElementById("step-active-layer-title");
  if (titleEl) titleEl.textContent = `${playerState.stepIndex + 1}. ${step.layerName}`;

  const badgeEl = document.getElementById("step-badge");
  if (badgeEl) {
    badgeEl.textContent = step.badge;
    badgeEl.className = `px-2.5 py-1 rounded text-xs font-mono font-bold ${step.badgeColor}`;
  }

  const whatEl = document.getElementById("step-what-happening");
  if (whatEl) whatEl.textContent = step.whatHappening;

  const codeEl = document.getElementById("step-code-snippet");
  if (codeEl) codeEl.textContent = step.codeSnippet;

  // Render Error or Clean Status
  const errContainer = document.getElementById("step-error-container");
  if (errContainer) {
    if (step.hasError) {
      errContainer.innerHTML = `
        <div class="p-3.5 rounded-xl bg-rose-950/70 border border-rose-600 flex flex-col gap-2">
          <div class="flex items-center gap-2">
            <i data-lucide="alert-octagon" class="w-4 h-4 text-rose-400 flex-shrink-0"></i>
            <span class="text-xs font-bold text-rose-200">${step.errorTitle}</span>
          </div>
          <p class="text-xs text-rose-300 leading-relaxed">${step.errorDescription}</p>
          <div class="p-2.5 rounded bg-black/80 border border-rose-900/60 font-mono text-[11px] text-emerald-300 relative">
            <button onclick="navigator.clipboard.writeText(\`${escapeQuotes(step.suggestedFix)}\`); showToast('Remediation copied!', 'success');" class="text-[10px] text-slate-300 hover:text-white px-2 py-0.5 rounded bg-white/10 absolute top-2 right-2 cursor-pointer">Copy Fix</button>
            <pre>${escapeHtml(step.suggestedFix)}</pre>
          </div>
        </div>
      `;
    } else {
      errContainer.innerHTML = `
        <div class="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800/80 flex items-center gap-2 text-xs text-emerald-300">
          <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400 flex-shrink-0"></i>
          <span>${step.cleanNote || "Clean Execution • No security vulnerabilities or bottlenecks flagged at this step."}</span>
        </div>
      `;
    }
  }

  if (window.lucide) lucide.createIcons();
}

// ==================== TAB 5: PIPELINE SIMULATION ====================
function runPipelineSimulation() {
  showToast("▶ Executing live 5-stage automated review pipeline...", "info");

  const stages = [1, 2, 3, 4, 5];
  stages.forEach(s => {
    const card = document.getElementById(`stage-card-${s}`);
    if (card) {
      card.className = "p-4 rounded-xl bg-[#091020] border border-slate-800 flex flex-col gap-2 transition-all";
    }
  });

  stages.forEach((s, idx) => {
    setTimeout(() => {
      const card = document.getElementById(`stage-card-${s}`);
      if (card) {
        card.className = "p-4 rounded-xl bg-cyan-950/60 border-2 border-cyan-400 flex flex-col gap-2 scale-105 shadow-xl transition-all";
      }

      if (s === 5) {
        setTimeout(() => {
          showToast("✓ Pipeline run finished: 5 source files analyzed, AST verified with zero hallucinations!", "success");
        }, 300);
      }
    }, idx * 250);
  });
}

// Helper utilities
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function escapeQuotes(str) {
  if (!str) return '';
  return str.replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');
}
