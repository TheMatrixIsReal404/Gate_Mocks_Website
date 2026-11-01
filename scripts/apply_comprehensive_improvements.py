# -*- coding: utf-8 -*-
"""
Applies comprehensive platform improvements to app.js and style.css:
1. Syntax-highlighted code blocks with Copy buttons and inline code styling (formatQuestionContent)
2. Live Search & Sub-Series filter pills for Mock Tests (30 Medium, 30 Easy, 20 Compendium, PYQs)
3. Featured Exam Series Hub & Question Bank Distribution on Dashboard
4. KaTeX Math rendering integration in Test Results / Review overlay (renderMath(ov))
5. Full window exports and synchronization
"""

import sys
import os
import shutil
import re

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app_path = 'app.js'
css_path = 'style.css'

shutil.copyfile(app_path, app_path + '.bak_improvements')
shutil.copyfile(css_path, css_path + '.bak_improvements')

# ─────────────────────────────────────────────────────────────
# 1. UPDATE style.css
# ─────────────────────────────────────────────────────────────
with open(css_path, 'r', encoding='utf-8') as f:
    css_text = f.read()

new_css = """

/* ── CODE SNIPPETS & SYNTAX HIGHLIGHTING ── */
.code-block-container {
  background: #11111b;
  border: 1.5px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-sm);
  margin: 12px 0 16px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}
.code-block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.code-block-lang {
  color: var(--accent);
  display: flex;
  align-items: center;
  gap: 6px;
}
.code-copy-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-secondary);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.code-copy-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}
.code-copy-btn.copied {
  color: var(--green);
  border-color: var(--green);
}
.code-block {
  margin: 0;
  padding: 14px 16px;
  font-family: 'Fira Code', 'Cascadia Code', Consolas, Monaco, monospace;
  font-size: 13.5px;
  line-height: 1.6;
  color: #38bdf8;
  overflow-x: auto;
  white-space: pre;
}
.inline-code {
  background: rgba(108, 99, 255, 0.14);
  color: #a5b4fc;
  border: 1px solid rgba(108, 99, 255, 0.25);
  padding: 1px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', Consolas, monospace;
  font-size: 0.9em;
  font-weight: 600;
}
.q-para-spacer {
  height: 10px;
}

/* ── MOCK CONTROLS & SUB-SERIES PILLS ── */
.mock-controls-bar {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.mock-controls-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.mock-search-box {
  position: relative;
  flex: 1;
  min-width: 240px;
}
.mock-search-box input {
  width: 100%;
  padding: 8px 12px 8px 34px;
  font-size: 13px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-primary);
}
.mock-search-box .search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 13px;
}
.mock-subseries-pills {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 10px;
}
.mock-subseries-pill {
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
  background: var(--bg-input);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s;
}
.mock-subseries-pill:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}
.mock-subseries-pill.active {
  background: var(--accent);
  color: #ffffff;
  border-color: var(--accent);
}

/* ── DASHBOARD FEATURED EXAM SERIES HUB ── */
.dashboard-series-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.series-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: var(--transition);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}
.series-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--series-color, var(--accent));
}
.series-card:hover {
  transform: translateY(-3px);
  border-color: var(--series-color, var(--accent));
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}
.series-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 10px;
}
.series-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}
.series-sub {
  font-size: 12.5px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 14px;
  flex: 1;
}
.series-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11.5px;
  color: var(--text-muted);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 10px;
}
.series-footer-action {
  color: var(--accent);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ── QUESTION BANK DISTRIBUTION BOX ── */
.qbank-dist-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 24px;
}
.qbank-dist-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.qbank-dist-bar {
  display: flex;
  height: 12px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--bg-input);
  margin-bottom: 14px;
}
.qbank-dist-segment {
  height: 100%;
  transition: width 0.4s ease;
  cursor: pointer;
}
.qbank-dist-legend {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.qbank-dist-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 3px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}
.qbank-dist-legend-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}
.qbank-dist-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
"""

if '.code-block-container' not in css_text:
    css_text += new_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_text)
    print("✓ Added code block, mock search, and dashboard series styles to style.css")
else:
    print("style.css already contains code styles")


# ─────────────────────────────────────────────────────────────
# 2. UPDATE app.js
# ─────────────────────────────────────────────────────────────
with open(app_path, 'r', encoding='utf-8') as f:
    js_text = f.read()

# A. Add mockSearch and mockSubSeries to state
if 'mockSearch:' not in js_text:
    js_text = js_text.replace(
        "mockSort:         'default',",
        "mockSort:         'default',\n  mockSearch:       '',\n  mockSubSeries:    'all',"
    )
    print("✓ Added mockSearch and mockSubSeries to state")

# B. Insert formatQuestionContent & copyCodeSnippet helper
formatter_func = """
// ── QUESTION CONTENT FORMATTER (Code Fences & Formatting) ──
function formatQuestionContent(text) {
  if (!text) return '';
  // 1. Process fenced code blocks: ```lang ... ```
  let formatted = text.replace(/```([a-zA-Z0-9_-]*)\\n?([\\s\\S]*?)```/g, (match, lang, code) => {
    const language = (lang || 'code').trim();
    const cleanCode = code.replace(/^\\n+|\\n+$/g, '');
    const escaped = escapeHtml(cleanCode);
    const codeId = 'code_' + Math.random().toString(36).substring(2, 9);
    return `<div class="code-block-container">
      <div class="code-block-header">
        <span class="code-block-lang">💻 ${language.toUpperCase()}</span>
        <button class="code-copy-btn" onclick="copyCodeSnippet('${codeId}', this)" type="button">📋 Copy</button>
      </div>
      <pre class="code-block"><code id="${codeId}">${escaped}</code></pre>
    </div>`;
  });

  // 2. Process inline backtick code and clean paragraph breaks outside code blocks
  const parts = formatted.split(/(<div class="code-block-container">[\\s\\S]*?<\\/div>)/g);
  for (let i = 0; i < parts.length; i += 2) {
    // Inline backticks
    parts[i] = parts[i].replace(/`([^`\\n]+)`/g, (m, inline) => {
      return `<code class="inline-code">${escapeHtml(inline)}</code>`;
    });
    // Double newlines into paragraph spacer
    parts[i] = parts[i].replace(/\\n{2,}/g, '<div class="q-para-spacer"></div>');
    // Single newline into <br/>
    parts[i] = parts[i].replace(/\\n/g, '<br/>');
  }
  return parts.join('');
}

window.copyCodeSnippet = function(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = '✓ Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.innerHTML = orig;
      btn.classList.remove('copied');
    }, 2000);
  }).catch(() => {
    showToast('Failed to copy to clipboard', 'error');
  });
};
"""

if 'function formatQuestionContent' not in js_text:
    target_pos = js_text.find('function escapeHtml')
    assert target_pos != -1, "escapeHtml not found"
    js_text = js_text[:target_pos] + formatter_func + "\n" + js_text[target_pos:]
    print("✓ Injected formatQuestionContent and copyCodeSnippet into app.js")

# C. Update renderTestQuestion to use formatQuestionContent
js_text = js_text.replace('<div class="question-text">${q.question}</div>', '<div class="question-text">${formatQuestionContent(q.question)}</div>')

# D. Update buildPracticeQHTML to use formatQuestionContent
js_text = js_text.replace('Question ${state.currentQuestion + 1} of ${total}</div>\n      <div class="question-text">${q.question}</div>', 'Question ${state.currentQuestion + 1} of ${total}</div>\n      <div class="question-text">${formatQuestionContent(q.question)}</div>')

# E. Update renderMockPaperView question text
js_text = js_text.replace('<strong style="color:var(--accent);margin-right:6px">Q${startIndex + idx + 1}.</strong>${q.question}', '<strong style="color:var(--accent);margin-right:6px">Q${startIndex + idx + 1}.</strong>${formatQuestionContent(q.question)}')

# F. Update showTestResult to use formatQuestionContent and call renderMath(ov)
old_result_q = """<div style="font-size:14px;line-height:1.7;margin-bottom:12px;font-weight:500">${q.question}</div>"""
new_result_q = """<div style="font-size:14px;line-height:1.7;margin-bottom:12px;font-weight:500">${formatQuestionContent(q.question)}</div>"""
js_text = js_text.replace(old_result_q, new_result_q)

old_result_exp = """<div class="explanation-box show" style="display:block"><strong>💡 </strong>${q.explanation||'No explanation.'}</div>"""
new_result_exp = """<div class="explanation-box show" style="display:block"><strong>💡 Solution & Derivation:</strong><br/>${formatQuestionContent(q.explanation||'No explanation.')}</div>"""
js_text = js_text.replace(old_result_exp, new_result_exp)

old_result_end = """ov.classList.add('active'); ov.scrollTop=0;
}"""
new_result_end = """ov.classList.add('active'); ov.scrollTop=0;
  renderMath(ov);
}"""
js_text = js_text.replace(old_result_end, new_result_end)

# G. Update getFilteredAndSortedMocks with search and subseries filters
old_filter_sort = """function getFilteredAndSortedMocks(mockList) {
  const currentSort = state.mockSort || 'default';
  let list = (mockList || []).slice();"""

new_filter_sort = """function getFilteredAndSortedMocks(mockList) {
  const currentSort = state.mockSort || 'default';
  const subSeries = state.mockSubSeries || 'all';
  const query = (state.mockSearch || '').trim().toLowerCase();
  let list = (mockList || []).slice();

  // 1. Sub-series filter
  if (subSeries === 'med-30') {
    list = list.filter(m => m.id.startsWith('mock-med-'));
  } else if (subSeries === 'easy-30') {
    list = list.filter(m => m.id.startsWith('mock-easy-'));
  } else if (subSeries === 'flm-20') {
    list = list.filter(m => m.id.startsWith('mock-flm-'));
  } else if (subSeries === 'cat-10') {
    list = list.filter(m => m.id.startsWith('mock-cat'));
  } else if (subSeries === 'practice-sets') {
    list = list.filter(m => m.type === 'practice-set');
  }

  // 2. Search query filter
  if (query) {
    list = list.filter(m =>
      (m.name && m.name.toLowerCase().includes(query)) ||
      (m.desc && m.desc.toLowerCase().includes(query)) ||
      (m.tier && m.tier.toLowerCase().includes(query)) ||
      (m.id && m.id.toLowerCase().includes(query))
    );
  }"""

js_text = js_text.replace(old_filter_sort, new_filter_sort)

# H. Update buildMockSortBar with search input and sub-series pills
old_mock_sort_bar = """function buildMockSortBar(list, sectionName) {
  const currentSort = state.mockSort || 'default';
  return `
    <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
      <div style="font-size:13px;font-weight:700;color:var(--text-secondary)">
        Showing ${list.length} ${sectionName}
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>
        <select class="form-select form-select-sm" style="width:auto;min-width:185px;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setMockSort(this.value)">
          <option value="default" ${currentSort === 'default' ? 'selected' : ''}>Default Order</option>
          <option value="easy-first" ${currentSort === 'easy-first' ? 'selected' : ''}>Difficulty: Easy → Hard</option>
          <option value="hard-first" ${currentSort === 'hard-first' ? 'selected' : ''}>Difficulty: Hard → Easy</option>
          <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>
          <option value="rating-asc" ${currentSort === 'rating-asc' ? 'selected' : ''}>Rating: Low → High</option>
          <option value="name-asc" ${currentSort === 'name-asc' ? 'selected' : ''}>Name: A → Z</option>
        </select>
      </div>
    </div>
  `;
}"""

new_mock_sort_bar = """function buildMockSortBar(list, sectionName) {
  const currentSort = state.mockSort || 'default';
  const subSeries = state.mockSubSeries || 'all';
  const currentTab = state.mockTab || 'all';

  let pillsHtml = '';
  if (currentTab === 'medium') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Medium (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='med-30'?'active':''}" onclick="setMockSubSeries('med-30')">⚡ 30 Medium Series (30)</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 Compendium Mocks (10)</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Core CS (5)</button>
        <button class="mock-subseries-pill ${subSeries==='practice-sets'?'active':''}" onclick="setMockSubSeries('practice-sets')">📝 Practice Sets (2)</button>
      </div>`;
  } else if (currentTab === 'easy') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Easy (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='easy-30'?'active':''}" onclick="setMockSubSeries('easy-30')">🌟 30 Easy Series (30)</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Topic Sets (5)</button>
      </div>`;
  } else if (currentTab === 'all') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='med-30'?'active':''}" onclick="setMockSubSeries('med-30')">⚡ 30 Medium Series</button>
        <button class="mock-subseries-pill ${subSeries==='easy-30'?'active':''}" onclick="setMockSubSeries('easy-30')">🌟 30 Easy Series</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 20 Compendium Mocks</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Mocks</button>
      </div>`;
  }

  return `
    <div class="mock-controls-bar">
      <div class="mock-controls-top">
        <div class="mock-search-box">
          <span class="search-icon">🔍</span>
          <input type="text" class="search-input" placeholder="Search mock tests by name, rating, #..."
            value="${escapeHtml(state.mockSearch || '')}"
            oninput="updateMockSearch(this.value)" />
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>
          <select class="form-select form-select-sm" style="width:auto;min-width:180px;padding:6px 10px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setMockSort(this.value)">
            <option value="default" ${currentSort === 'default' ? 'selected' : ''}>Default Order</option>
            <option value="easy-first" ${currentSort === 'easy-first' ? 'selected' : ''}>Difficulty: Easy → Hard</option>
            <option value="hard-first" ${currentSort === 'hard-first' ? 'selected' : ''}>Difficulty: Hard → Easy</option>
            <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>
            <option value="rating-asc" ${currentSort === 'rating-asc' ? 'selected' : ''}>Rating: Low → High</option>
            <option value="name-asc" ${currentSort === 'name-asc' ? 'selected' : ''}>Name: A → Z</option>
          </select>
        </div>
      </div>
      ${pillsHtml}
    </div>
  `;
}

function updateMockSearch(val) {
  state.mockSearch = val;
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}

function setMockSubSeries(sub) {
  state.mockSubSeries = sub;
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}"""

js_text = js_text.replace(old_mock_sort_bar, new_mock_sort_bar)

# I. Update Dashboard with Featured Exam Series & Question Bank Distribution
old_dashboard = """    <div class="section-header">
      <div class="section-title">Subjects <span>${SUBJECTS.length} available</span></div>
      <button class="btn btn-secondary btn-sm" onclick="navigate('subjects')">View All →</button>
    </div>
    <div class="subjects-grid">${buildSubjectCards()}</div>`;"""

new_dashboard = """    <!-- ── FEATURED EXAM SERIES HUB ── -->
    <div class="section-header" style="margin-top:28px">
      <div class="section-title">Curated GATE Exam Series <span>4 Flagship Compendiums</span></div>
      <button class="btn btn-secondary btn-sm" onclick="navigate('mocks')">View All Mocks →</button>
    </div>
    <div class="dashboard-series-grid">
      <div class="series-card" style="--series-color:#22c55e" onclick="navigate('mocks',{tab:'easy'})">
        <div>
          <div class="series-badge" style="background:rgba(34,197,94,0.15);color:#22c55e">🌟 FOUNDATIONAL EASY</div>
          <div class="series-title">30 Easy Mock Tests</div>
          <div class="series-sub">Direct formulas, canonical definitions, and core scoring fundamentals strictly aligned with the IISc/IIT syllabus.</div>
        </div>
        <div class="series-footer">
          <span>1,950 Qs • 30 Full Tests • 3.5/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#eab308" onclick="navigate('mocks',{tab:'medium'})">
        <div>
          <div class="series-badge" style="background:rgba(234,179,8,0.15);color:#eab308">⚡ STANDARD GATE CS</div>
          <div class="series-title">30 Medium Mock Tests</div>
          <div class="series-sub">Standard GATE difficulty with multi-step NAT numericals, cache/pipeline timing, logic, and comprehensive algorithms.</div>
        </div>
        <div class="series-footer">
          <span>1,950 Qs • 30 Full Tests • 5.0/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#ef4444" onclick="navigate('mocks',{tab:'hard'})">
        <div>
          <div class="series-badge" style="background:rgba(239,68,68,0.15);color:#ef4444">🔥 RANK BOOSTERS</div>
          <div class="series-title">20 Full Mocks Compendium</div>
          <div class="series-sub">Deep conceptual mastery, edge-case analysis, advanced mathematics, and challenging gate-level problem solving.</div>
        </div>
        <div class="series-footer">
          <span>1,300 Qs • 20 Full Tests • 7.0/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#38bdf8" onclick="navigate('pyq-exams')">
        <div>
          <div class="series-badge" style="background:rgba(56,189,248,0.15);color:#38bdf8">🏛️ OFFICIAL PAPERS</div>
          <div class="series-title">21 Full-Length PYQ Exams</div>
          <div class="series-sub">Complete authentic year-wise examination papers from 2007 to 2025 in a realistic 180-minute timed environment.</div>
        </div>
        <div class="series-footer">
          <span>2,224+ PYQs • 2007–2025 • Official</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>
    </div>

    <!-- ── QUESTION BANK DISTRIBUTION ── -->
    <div class="qbank-dist-box">
      <div class="qbank-dist-header">
        <div>
          <div style="font-size:14px;font-weight:700;color:var(--text-primary)">📚 Master Question Bank Telemetry</div>
          <div style="font-size:12px;color:var(--text-muted)">8,168 verified GATE CS questions with detailed mathematical derivations</div>
        </div>
        <button class="btn btn-secondary btn-sm" onclick="navigate('practice')">Browse All 8,168 Questions →</button>
      </div>
      <div class="qbank-dist-bar">
        <div class="qbank-dist-segment" style="width:52%;background:#eab308" title="Medium Difficulty: 4,252 Questions (52%)" onclick="navigate('practice',{difficulty:'medium'})"></div>
        <div class="qbank-dist-segment" style="width:41%;background:#22c55e" title="Easy Difficulty: 3,358 Questions (41%)" onclick="navigate('practice',{difficulty:'easy'})"></div>
        <div class="qbank-dist-segment" style="width:7%;background:#ef4444" title="Hard Difficulty: 558 Questions (7%)" onclick="navigate('practice',{difficulty:'hard'})"></div>
      </div>
      <div class="qbank-dist-legend">
        <div class="qbank-dist-legend-item" onclick="navigate('practice',{difficulty:'medium'})"><span class="qbank-dist-dot" style="background:#eab308"></span> Medium (4,252 Qs • 52%)</div>
        <div class="qbank-dist-legend-item" onclick="navigate('practice',{difficulty:'easy'})"><span class="qbank-dist-dot" style="background:#22c55e"></span> Easy (3,358 Qs • 41%)</div>
        <div class="qbank-dist-legend-item" onclick="navigate('practice',{difficulty:'hard'})"><span class="qbank-dist-dot" style="background:#ef4444"></span> Hard (558 Qs • 7%)</div>
        <div class="qbank-dist-legend-item" onclick="navigate('practice',{type:'nat'})"><span class="qbank-dist-dot" style="background:#06b6d4"></span> 3,726 NATs</div>
        <div class="qbank-dist-legend-item" onclick="navigate('practice',{type:'mcq'})"><span class="qbank-dist-dot" style="background:#8b5cf6"></span> 3,379 MCQs</div>
        <div class="qbank-dist-legend-item" onclick="navigate('practice',{type:'msq'})"><span class="qbank-dist-dot" style="background:#ec4899"></span> 1,063 MSQs</div>
      </div>
    </div>

    <div class="section-header">
      <div class="section-title">Subjects <span>${SUBJECTS.length} available</span></div>
      <button class="btn btn-secondary btn-sm" onclick="navigate('subjects')">View All →</button>
    </div>
    <div class="subjects-grid">${buildSubjectCards()}</div>`;"""

js_text = js_text.replace(old_dashboard, new_dashboard)

# J. Expose new functions in Object.assign(window, { ... })
target_obj_assign = "Object.assign(window, {\n  state,\n  MOCK_TESTS,\n  getMockQuestions,"
new_obj_assign = """Object.assign(window, {
  state,
  MOCK_TESTS,
  getMockQuestions,
  formatQuestionContent,
  copyCodeSnippet,
  updateMockSearch,
  setMockSubSeries,"""
js_text = js_text.replace(target_obj_assign, new_obj_assign)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(js_text)

print("✅ Successfully applied all comprehensive platform improvements!")
