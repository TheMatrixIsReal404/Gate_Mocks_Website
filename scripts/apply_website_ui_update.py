# -*- coding: utf-8 -*-
"""
Script to apply the enhanced Mock Difficulty UI, calibration banner,
ratings badges, and filter bars in app.js and style.css.
"""

new_section_code = '''// ─── MOCK TESTS ──────────────────────────────────────────────────────────────
function toggleCalibrationTable() {
  state.showCalibrationTable = !state.showCalibrationTable;
  const c = document.getElementById('mock-tab-content');
  if (c && state.mockTab === 'full') {
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');
    const filtered = (state.mockLevelFilter === 'all' || !state.mockLevelFilter)
      ? fullMocks
      : fullMocks.filter(m => m.difficulty === state.mockLevelFilter);
    c.innerHTML = `
      ${buildMockCalibrationGuide()}
      ${buildMockLevelFilterBar(fullMocks)}
      ${buildMockGrid(filtered)}
    `;
    renderMath(c);
  }
}

function buildMockCalibrationGuide() {
  const isExpanded = state.showCalibrationTable || false;
  return `
    <div class="calibration-guide-box">
      <div class="calibration-guide-header">
        <div>
          <div style="font-size:16px;font-weight:700;color:var(--text-primary);display:flex;align-items:center;gap:8px">
            <span>🎯</span> 20 Full-Length Mocks: Difficulty Calibration & Rating Guide
          </div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:2px">
            Official IISc/IIT GATE CS syllabus benchmark — Mocks #01–#10 (Medium) vs. Mocks #11–#20 (Hard)
          </div>
        </div>
        <button class="btn btn-secondary btn-sm" onclick="toggleCalibrationTable()" style="display:inline-flex;align-items:center;gap:6px">
          <span>${isExpanded ? '🔼 Hide Rating Table' : '📋 View 20-Mock Rating Matrix'}</span>
        </button>
      </div>

      <!-- Summary Tier Cards -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;margin-bottom:${isExpanded ? '16px' : '4px'}">
        <!-- Medium Tier Card -->
        <div class="calibration-tier-card medium">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span class="q-badge medium" style="font-size:12px;padding:4px 12px">🟡 MEDIUM MOCKS (#01 – #10)</span>
            <span style="font-size:12px;font-weight:700;color:var(--yellow)">Rating: 4.5 – 6.1 / 10</span>
          </div>
          <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.5;margin-bottom:8px">
            <strong>Standard GATE Pattern:</strong> Replicates typical IISc/IIT papers (e.g. GATE 2021, 2023, 2025 Set 1). Features clean arithmetic bounds, classical K-maps, standard planar graphs (\(V \\le 26\)), and 2-level paging EMAT.
          </div>
          <div style="display:flex;gap:14px;font-size:12px;color:var(--text-primary);background:var(--bg-primary);padding:6px 10px;border-radius:6px;border:1px solid var(--border)">
            <span>🎯 <strong>Est. Cutoff:</strong> 28 – 32 Marks</span>
            <span>🏆 <strong>AIR &lt; 100:</strong> 72 – 78+ Marks</span>
          </div>
        </div>

        <!-- Hard Tier Card -->
        <div class="calibration-tier-card hard">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span class="q-badge hard" style="font-size:12px;padding:4px 12px">🔴 HARD MOCKS (#11 – #20)</span>
            <span style="font-size:12px;font-weight:700;color:var(--red)">Rating: 6.8 – 9.2 / 10</span>
          </div>
          <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.5;margin-bottom:8px">
            <strong>Rank Booster Challenges:</strong> High-intensity rank-booster exams. Modulo arithmetic up to \(\\pmod{89}\), 64-state sliding-window DFAs, 141–266 leaf strict \(k\)-ary trees, 31-child fork trees, 8-fragment IPv4, and 144k matrix chains.
          </div>
          <div style="display:flex;gap:14px;font-size:12px;color:var(--text-primary);background:var(--bg-primary);padding:6px 10px;border-radius:6px;border:1px solid var(--border)">
            <span>🎯 <strong>Est. Cutoff:</strong> 20 – 26 Marks</span>
            <span>🏆 <strong>AIR &lt; 100:</strong> 60 – 68 Marks</span>
          </div>
        </div>
      </div>

      <!-- Expandable Table -->
      ${isExpanded ? `
        <div class="calibration-table-wrap">
          <table class="calibration-table">
            <thead>
              <tr>
                <th style="padding:10px 12px;white-space:nowrap">Mock Exam</th>
                <th style="padding:10px 12px;text-align:center">Difficulty Tier</th>
                <th style="padding:10px 12px;text-align:center">Rating</th>
                <th style="padding:10px 12px;text-align:center">Est. Cutoff</th>
                <th style="padding:10px 12px;text-align:center">AIR &lt; 100</th>
                <th style="padding:10px 12px">Key Technical Complexity Profile</th>
                <th style="padding:10px 12px;text-align:center">Action</th>
              </tr>
            </thead>
            <tbody>
              ${Array.from({length: 20}, (_, idx) => {
                const num = idx + 1;
                const id = 'mock-flm-' + String(num).padStart(2, '0');
                const m = MOCK_TESTS.find(t => t.id === id);
                if (!m) return '';
                const isMed = m.difficulty === 'medium';
                const tierBadge = isMed
                  ? '<span class="q-badge medium" style="padding:2px 8px;font-size:11px">🟡 Medium</span>'
                  : '<span class="q-badge hard" style="padding:2px 8px;font-size:11px">🔴 Hard</span>';
                const rowBg = idx % 2 === 0 ? 'var(--bg-card)' : 'rgba(255,255,255,0.02)';
                return `
                  <tr style="background:${rowBg};border-bottom:1px solid var(--border)">
                    <td style="padding:9px 12px;font-weight:700;white-space:nowrap;color:var(--text-primary)">Mock #${String(num).padStart(2, '0')}</td>
                    <td style="padding:9px 12px;text-align:center">${tierBadge}</td>
                    <td style="padding:9px 12px;text-align:center;font-weight:700;color:var(--yellow)">⭐ ${m.rating ? m.rating.toFixed(1) : ''}/10</td>
                    <td style="padding:9px 12px;text-align:center;color:var(--text-secondary)">${m.cutoff || '28-32'} M</td>
                    <td style="padding:9px 12px;text-align:center;color:var(--text-secondary)">${m.air100 || '72-78'} M</td>
                    <td style="padding:9px 12px;color:var(--text-muted);font-size:11.5px;max-width:320px">${m.desc.split(': ').slice(1).join(': ') || m.desc}</td>
                    <td style="padding:9px 12px;text-align:center;white-space:nowrap">
                      <button class="btn btn-secondary btn-sm" onclick="startMockTest('${m.id}')" style="padding:3px 8px;font-size:11px">Start Test</button>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      ` : ''}
    </div>
  `;
}

function buildMockLevelFilterBar(fullMocks) {
  const currentLvl = state.mockLevelFilter || 'all';
  return `
    <div class="filter-bar" style="margin-bottom:16px;flex-wrap:wrap">
      <button class="chip ${currentLvl === 'all' ? 'active' : ''}" onclick="setMockLevelFilter('all')">All Levels (${fullMocks.length})</button>
      <button class="chip ${currentLvl === 'medium' ? 'active' : ''}" onclick="setMockLevelFilter('medium')">🟡 Moderate / Standard (${fullMocks.filter(m => m.difficulty === 'medium').length})</button>
      <button class="chip ${currentLvl === 'hard' ? 'active' : ''}" onclick="setMockLevelFilter('hard')">🔴 Hard / Rank Booster (${fullMocks.filter(m => m.difficulty === 'hard').length})</button>
      <button class="chip ${currentLvl === 'easy' ? 'active' : ''}" onclick="setMockLevelFilter('easy')">🟢 Easy / Foundational (${fullMocks.filter(m => m.difficulty === 'easy').length})</button>
    </div>
  `;
}

function setMockLevelFilter(lvl) {
  state.mockLevelFilter = lvl;
  const c = document.getElementById('mock-tab-content');
  if (c && state.mockTab === 'full') {
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');
    const filtered = lvl === 'all' ? fullMocks : fullMocks.filter(m => m.difficulty === lvl);
    c.innerHTML = `
      ${buildMockCalibrationGuide()}
      ${buildMockLevelFilterBar(fullMocks)}
      ${buildMockGrid(filtered)}
    `;
    renderMath(c);
  }
}

function renderMocks(c, params={}){
  if (state.activeMockPaper) {
    renderMockPaperView(c);
    return;
  }
  const activeTab = params.tab || state.mockTab || 'full';
  state.mockTab = activeTab;

  const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');
  const filteredFullMocks = state.mockLevelFilter === 'all'
    ? fullMocks
    : fullMocks.filter(m => m.difficulty === state.mockLevelFilter);

  c.innerHTML=`
    <div class="tabs" id="mock-tabs">
      <button class="tab-btn ${activeTab==='full'?'active':''}" onclick="switchMockTab('full',this)">🏆 Full Mocks</button>
      <button class="tab-btn ${activeTab==='subwise'?'active':''}" onclick="switchMockTab('subwise',this)">📂 Subject Mocks</button>
      <button class="tab-btn ${activeTab==='papers'?'active':''}" onclick="switchMockTab('papers',this)">📝 Practice Papers</button>
      <button class="tab-btn ${activeTab==='history'?'active':''}" onclick="switchMockTab('history',this)">📊 My History</button>
    </div>
    <div id="mock-tab-content">
      ${activeTab==='full' ? `${buildMockCalibrationGuide()}${buildMockLevelFilterBar(fullMocks)}${buildMockGrid(filteredFullMocks)}` :
        activeTab==='subwise' ? buildMockGrid(MOCK_TESTS.filter(m=>m.type==='subwise')) :
        activeTab==='papers' ? buildPracticePapersGrid() :
        buildTestHistory()}
    </div>`;
  renderMath(c);
}

function switchMockTab(tab, btn){
  state.mockTab = tab;
  document.querySelectorAll('#mock-tabs .tab-btn').forEach(b=>b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const c=document.getElementById('mock-tab-content');
  if (!c) return;
  if (tab==='full') {
    const fullMocks = MOCK_TESTS.filter(m=>m.type==='full');
    const filtered = state.mockLevelFilter === 'all' ? fullMocks : fullMocks.filter(m=>m.difficulty===state.mockLevelFilter);
    c.innerHTML = `${buildMockCalibrationGuide()}${buildMockLevelFilterBar(fullMocks)}${buildMockGrid(filtered)}`;
  }
  if (tab==='subwise') c.innerHTML=buildMockGrid(MOCK_TESTS.filter(m=>m.type==='subwise'));
  if (tab==='papers')  c.innerHTML=buildPracticePapersGrid();
  if (tab==='history') c.innerHTML=buildTestHistory();
  renderMath(c);
}

function buildMockGrid(mocks){
  if (!mocks.length) return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No tests available for selected filter</div></div>';
  return `<div class="mock-grid">${mocks.map(m=>{
    const past=state.testSessions.filter(s=>s.mockId===m.id);
    const best=past.length?Math.max(...past.map(s=>s.percentage)):null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const totalPages = Math.ceil(questionsCount / 20) || 1;
    const diffLabel = m.difficulty ? m.difficulty.toUpperCase() : 'MEDIUM';
    const ratingBadge = m.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${m.rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (m.cutoff && m.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${m.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${m.air100} M</span>
      </div>` : '';
    return `<div class="mock-card">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <div class="mock-type-badge ${m.type}">${m.type==='full'?'🏆 Full Mock':'📂 Subject Mock'}</div>
        <div style="display:flex;align-items:center;gap:6px">
          <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
          ${ratingBadge}
        </div>
      </div>
      <div class="mock-title">${m.name}</div>
      <div class="text-sm text-muted">${m.subject||'All 13 Subjects Covered'}</div>
      ${m.desc ? `<div class="text-sm text-secondary" style="margin:6px 0 8px;line-height:1.4">${m.desc}</div>` : ''}
      ${targetsRow}
      ${best!==null?`<div class="text-sm mt-2" style="color:var(--green)">Best Score: ${best}%</div>`:''}
      <div class="mock-meta">
        <div class="mock-meta-item">📝 ${questionsCount} Qs (${totalPages} page${totalPages>1?'s':''})</div>
        <div class="mock-meta-item">⏱ ${m.duration} min</div>
        <div class="mock-meta-item">🏅 ${m.marks} marks</div>
      </div>
      <div class="mock-card-actions">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" title="Browse questions in sets of 20 per page">📖 Practice Paper (20/page)</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" title="Start timed exam">▶ Timed Exam</button>
      </div>
      ${past.length?`<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length>1?'s':''}</div>`:''}
    </div>`;
  }).join('')}</div>`;
}

function setPaperLevelFilter(filter) {
  state.paperLevelFilter = filter;
  const c = document.getElementById('page-content');
  if (c) renderPracticePapers(c);
}

function buildPracticePapersGrid(papersList = null){
  const papers = papersList || PRACTICE_PAPERS;
  return `<div class="mock-grid">${papers.map(p=>{
    const qs = getMockQuestions(p.id);
    const totalCount = qs.length || p.questions;
    const totalPages = Math.ceil(totalCount / 20) || 1;
    const diffLabel = p.difficulty ? p.difficulty.toUpperCase() : (p.id.includes('cat1') ? 'EASY' : 'MEDIUM');
    const diffClass = p.difficulty || (p.id.includes('cat1') ? 'easy' : 'medium');
    const ratingBadge = p.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${p.rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (p.cutoff && p.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${p.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${p.air100} M</span>
      </div>` : '';
    return `
      <div class="paper-card">
        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <div class="paper-meta-badge">📝 Practice Paper • 20/Page</div>
            <div style="display:flex;align-items:center;gap:6px">
              <span class="q-badge ${diffClass}">${diffLabel}</span>
              ${ratingBadge}
            </div>
          </div>
          <div class="mock-title">${p.name}</div>
          <div class="text-sm text-muted" style="margin-bottom:8px">${p.desc}</div>
          ${targetsRow}
          <div class="mock-meta">
            <div class="mock-meta-item">📚 ${totalCount} Questions</div>
            <div class="mock-meta-item">📄 ${totalPages} Pages (20/page)</div>
            <div class="mock-meta-item">🏅 ${p.marks} marks</div>
          </div>
        </div>
        <div class="mock-card-actions">
          <button class="btn btn-primary btn-sm" onclick="viewMockPaper('${p.id}')">📖 Open Paper (20/page)</button>
          <button class="btn btn-secondary btn-sm" onclick="startPracticePaperDirect('${p.id}')">▶ Practice Mode</button>
        </div>
      </div>
    `;
  }).join('')}</div>`;
}

function renderPracticePapers(c){
  if (state.activeMockPaper) {
    renderMockPaperView(c);
    return;
  }
  const currentFilter = state.paperLevelFilter || 'all';
  const filteredPapers = currentFilter === 'all' ? PRACTICE_PAPERS :
    currentFilter === 'medium' ? PRACTICE_PAPERS.filter(p => p.difficulty === 'medium') :
    currentFilter === 'hard' ? PRACTICE_PAPERS.filter(p => p.difficulty === 'hard') :
    PRACTICE_PAPERS.filter(p => !p.id.startsWith('paper-flm-'));

  c.innerHTML = `
    <div class="section-header">
      <div class="section-title">Practice Papers <span>${PRACTICE_PAPERS.length} curated papers</span></div>
    </div>
    <p class="text-muted text-sm" style="margin-bottom:14px">Browse curated practice papers paginated at 20 questions per page with step-by-step solutions and explanations.</p>
    <div class="filter-bar" style="margin-bottom:16px;flex-wrap:wrap">
      <button class="chip ${currentFilter === 'all' ? 'active' : ''}" onclick="setPaperLevelFilter('all')">All Papers (${PRACTICE_PAPERS.length})</button>
      <button class="chip ${currentFilter === 'medium' ? 'active' : ''}" onclick="setPaperLevelFilter('medium')">🟡 Medium Mocks #01–#10 (${PRACTICE_PAPERS.filter(p=>p.difficulty==='medium').length})</button>
      <button class="chip ${currentFilter === 'hard' ? 'active' : ''}" onclick="setPaperLevelFilter('hard')">🔴 Hard Mocks #11–#20 (${PRACTICE_PAPERS.filter(p=>p.difficulty==='hard').length})</button>
      <button class="chip ${currentFilter === 'other' ? 'active' : ''}" onclick="setPaperLevelFilter('other')">📅 Official GATE PYQs & Subjects (${PRACTICE_PAPERS.filter(p=>!p.id.startsWith('paper-flm-')).length})</button>
    </div>
    ${buildPracticePapersGrid(filteredPapers)}
  `;
}
'''

with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = '// ─── MOCK TESTS ──────────────────────────────────────────────────────────────'
end_marker = 'function viewMockPaper(mockId, page=1){'

pos1 = text.find(start_marker)
pos2 = text.find(end_marker)

assert pos1 != -1 and pos2 != -1, "Markers not found!"

updated_code = text[:pos1] + new_section_code + '\n' + text[pos2:]

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(updated_code)

print("Updated app.js successfully!")

# Update style.css
css_rules = """

/* ───────────────────────────── MOCK CALIBRATION & RATINGS GUIDE ───────────────────────────── */
.calibration-guide-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}
.calibration-guide-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
}
.calibration-tier-card {
  border-radius: 10px;
  padding: 16px;
  transition: var(--transition);
}
.calibration-tier-card.medium {
  background: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.25);
}
.calibration-tier-card.medium:hover {
  border-color: rgba(245, 158, 11, 0.45);
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.1);
}
.calibration-tier-card.hard {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.25);
}
.calibration-tier-card.hard:hover {
  border-color: rgba(239, 68, 68, 0.45);
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.1);
}
.calibration-table-wrap {
  overflow-x: auto;
  margin-top: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
}
.calibration-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.calibration-table th {
  background: #1e3a8a;
  color: #ffffff;
  padding: 10px 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
  white-space: nowrap;
}
.calibration-table td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--border);
}
.calibration-table tr:hover td {
  background: rgba(108, 99, 255, 0.04);
}
.mock-targets-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0 10px;
  font-size: 11.5px;
  color: var(--text-secondary);
  background: var(--bg-primary);
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
}
"""

with open('style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

if '.calibration-guide-box' not in css_content:
    with open('style.css', 'a', encoding='utf-8') as f:
        f.write(css_rules)
    print("Added calibration styles to style.css")
else:
    print("style.css already has calibration styles")
