# scripts/patch_app_improvements.py
import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. NEW FUNCTIONS BLOCK to place before EXPOSE FUNCTIONS TO GLOBAL SCOPE
new_functions = '''
// ─── EXAM COUNTDOWN & DAILY STUDY STREAK ENGINE ─────────────────────────────
function getExamCountdownData() {
  const now = new Date();
  let targetYear = now.getFullYear();
  let targetDate = new Date(targetYear, 1, 6, 9, 0, 0); // First Saturday of February 9:00 AM
  if (now > targetDate) {
    targetYear++;
    targetDate = new Date(targetYear, 1, 6, 9, 0, 0);
  }
  const diffMs = targetDate - now;
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  return { days, targetYear };
}

function initExamCountdownAndStreak() {
  const cdEl = document.getElementById('countdown-text');
  if (cdEl) {
    const cd = getExamCountdownData();
    cdEl.textContent = `GATE ${cd.targetYear}: ${cd.days}d`;
  }

  try {
    const raw = localStorage.getItem('gate_daily_streak_v1');
    state.dailyStreak = raw ? JSON.parse(raw) : { lastDate: '', streak: 0, todayCount: 0, goal: 20 };
  } catch(e) {
    state.dailyStreak = { lastDate: '', streak: 0, todayCount: 0, goal: 20 };
  }

  const todayStr = new Date().toISOString().slice(0, 10);
  if (state.dailyStreak.lastDate !== todayStr) {
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    if (state.dailyStreak.lastDate !== yesterday && state.dailyStreak.lastDate !== '') {
      state.dailyStreak.streak = 0;
    }
    state.dailyStreak.lastDate = todayStr;
    state.dailyStreak.todayCount = 0;
    saveDailyStreak();
  }
  updateStreakUI();
}

function recordDailyAttemptForStreak() {
  if (!state.dailyStreak) initExamCountdownAndStreak();
  state.dailyStreak.todayCount = (state.dailyStreak.todayCount || 0) + 1;
  if (state.dailyStreak.todayCount === state.dailyStreak.goal) {
    state.dailyStreak.streak = (state.dailyStreak.streak || 0) + 1;
    showToast(`🔥 Daily Goal Reached! ${state.dailyStreak.streak}-day streak!`, 'success');
  }
  saveDailyStreak();
  updateStreakUI();
}

function saveDailyStreak() {
  try {
    localStorage.setItem('gate_daily_streak_v1', JSON.stringify(state.dailyStreak));
  } catch(e) {}
}

function updateStreakUI() {
  const stEl = document.getElementById('streak-text');
  if (stEl && state.dailyStreak) {
    const { streak, todayCount, goal } = state.dailyStreak;
    stEl.textContent = `${streak}d (${todayCount}/${goal} Q)`;
  }
}

// ─── UNIVERSAL GLOBAL QUESTION SEARCH (8,168 QUESTIONS) ──────────────────────
function openGlobalSearch() {
  const modal = document.getElementById('global-search-modal');
  const backdrop = document.getElementById('global-search-backdrop');
  const input = document.getElementById('global-search-input');
  if (modal && backdrop) {
    modal.classList.add('active');
    backdrop.classList.add('active');
    if (input) {
      input.value = state.globalSearchQuery || '';
      input.focus();
      input.select();
      if (input.value) handleGlobalSearchInput(input.value);
    }
  }
}

function closeGlobalSearch() {
  const modal = document.getElementById('global-search-modal');
  const backdrop = document.getElementById('global-search-backdrop');
  if (modal && backdrop) {
    modal.classList.remove('active');
    backdrop.classList.remove('active');
  }
}

let globalSearchDebounceTimer = null;
function handleGlobalSearchInput(query) {
  state.globalSearchQuery = query;
  clearTimeout(globalSearchDebounceTimer);
  globalSearchDebounceTimer = setTimeout(() => {
    executeGlobalSearch(query);
  }, 150);
}

function setGlobalSearchFilter(type, btn) {
  state.globalSearchFilter = type;
  document.querySelectorAll('.global-search-filters .chip').forEach(c => c.classList.remove('active'));
  if (btn) btn.classList.add('active');
  executeGlobalSearch(state.globalSearchQuery || '');
}

function executeGlobalSearch(rawQuery) {
  const container = document.getElementById('global-search-results');
  const countEl = document.getElementById('global-search-count');
  if (!container) return;

  const qStr = (rawQuery || '').trim().toLowerCase();
  const filterType = state.globalSearchFilter || 'all';

  if (!qStr) {
    container.innerHTML = `
      <div style="padding:32px 16px;text-align:center;color:var(--text-muted);font-size:13px">
        Search 8,168 questions by theorem, concept, formula, or code snippet (e.g. <em>Dijkstra, LRU, B+ Tree, Pipelining, Master Theorem</em>)
      </div>`;
    if (countEl) countEl.textContent = `${(state.questions || []).length} questions indexed`;
    return;
  }

  const terms = qStr.split(/\\s+/).filter(Boolean);
  let matches = (state.questions || []).filter(q => {
    if (filterType !== 'all' && q.type !== filterType) return false;
    const hay = ((q.question || '') + ' ' + (q.subject || '') + ' ' + (q.topic || '') + ' ' + (q.explanation || '')).toLowerCase();
    return terms.every(t => hay.includes(t));
  });

  if (countEl) {
    countEl.textContent = `${matches.length} matching questions found`;
  }

  if (!matches.length) {
    container.innerHTML = `
      <div style="padding:32px 16px;text-align:center;color:var(--text-muted)">
        <div style="font-size:24px;margin-bottom:8px">🔍</div>
        <div>No questions found matching "<strong>${escapeHtml(rawQuery)}</strong>"</div>
        <div style="font-size:12px;margin-top:4px">Try searching for broader terms like "scheduling", "cache", "sorting", or "grammar".</div>
      </div>`;
    return;
  }

  const displayList = matches.slice(0, 25);
  container.innerHTML = displayList.map((q, idx) => {
    const snippet = (q.question || '').replace(/\\s+/g, ' ').slice(0, 140);
    return `
      <div class="search-result-item" onclick="startSingleQuestionPractice('${q.id}')">
        <div class="search-result-meta">
          <span class="q-badge ${q.type}">${q.type?.toUpperCase()}</span>
          <span class="q-badge ${q.difficulty}">${q.difficulty}</span>
          <span class="chip">${escapeHtml(q.subject || 'CS')}</span>
          ${q.topic ? `<span class="chip chip-info">${escapeHtml(q.topic)}</span>` : ''}
          <span style="margin-left:auto;color:var(--text-muted);font-size:10px">#${idx + 1}</span>
        </div>
        <div class="search-result-snippet">${escapeHtml(snippet)}...</div>
        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:6px">
          <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); openPlaylistModal('${q.id}')" style="padding:2px 8px;font-size:11px" type="button">
            🗂️ Playlist
          </button>
          <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); startSingleQuestionPractice('${q.id}')" style="padding:2px 8px;font-size:11px" type="button">
            ▶ Practice Now
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function startSingleQuestionPractice(qid) {
  closeGlobalSearch();
  const q = (state.questions || []).find(item => item.id === qid);
  if (!q) return;
  state.practiceQueue = [q];
  state.currentQuestion = 0;
  state.practiceMode = true;
  state.practiceAnswered = false;
  practiceSelectedOpts = new Set();
  const ov = document.getElementById('test-overlay');
  if (ov) {
    ov.classList.add('active');
    renderPracticeQuestion();
    renderMath(ov);
  }
}

// ─── 10-SPOKE SUBJECT MASTERY RADAR CHART (IIT MADRAS SPECIFICATION) ─────────
function buildMasteryRadarChartSVG() {
  const subjects10 = [
    { key: 'Engineering Mathematics', label: 'Engg Math & DM' },
    { key: 'Digital Logic', label: 'Digital Logic' },
    { key: 'Computer Organization', label: 'COA' },
    { key: 'Data Structures', label: 'C & Data Structures' },
    { key: 'Algorithms', label: 'Algorithms' },
    { key: 'Theory of Computation', label: 'TOC' },
    { key: 'Compiler Design', label: 'Compiler Design' },
    { key: 'Operating Systems', label: 'Operating Systems' },
    { key: 'DBMS', label: 'DBMS' },
    { key: 'Computer Networks', label: 'Networks' }
  ];

  const totalSpokes = subjects10.length;
  const cx = 200, cy = 200, R = 130;
  const rings = [0.2, 0.4, 0.6, 0.8, 1.0];

  const ringsSVG = rings.map(rPct => {
    const pts = [];
    for (let i = 0; i < totalSpokes; i++) {
      const angle = (Math.PI * 2 / totalSpokes) * i - Math.PI / 2;
      const x = cx + R * rPct * Math.cos(angle);
      const y = cy + R * rPct * Math.sin(angle);
      pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }
    return `<polygon points="${pts.join(' ')}" class="radar-grid-ring" />
            <text x="${cx + 4}" y="${(cy - R * rPct + 10).toFixed(1)}" fill="rgba(255,255,255,0.25)" font-size="8">${Math.round(rPct * 100)}%</text>`;
  }).join('');

  const spokesSVG = subjects10.map((s, i) => {
    const angle = (Math.PI * 2 / totalSpokes) * i - Math.PI / 2;
    const x = cx + R * Math.cos(angle);
    const y = cy + R * Math.sin(angle);
    const lx = cx + (R + 24) * Math.cos(angle);
    const ly = cy + (R + 18) * Math.sin(angle);
    return `
      <line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" class="radar-spoke" />
      <text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" class="radar-label">${s.label}</text>
    `;
  }).join('');

  const polygonPoints = [];
  const dataPoints = [];
  const legendRows = [];

  subjects10.forEach((s, i) => {
    const st = getSubjectStats(s.key);
    const acc = st.doneCount > 0 ? st.accuracy : 45;
    const rPct = Math.max(0.15, Math.min(1.0, acc / 100));
    const angle = (Math.PI * 2 / totalSpokes) * i - Math.PI / 2;
    const x = cx + R * rPct * Math.cos(angle);
    const y = cy + R * rPct * Math.sin(angle);
    polygonPoints.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    dataPoints.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5" class="radar-point"><title>${s.label}: ${acc}% Accuracy (${st.doneCount} Qs)</title></circle>`);
    
    const tierBadge = acc >= 75 ? '🟢 Strong' : acc >= 50 ? '🟡 Average' : '🔴 Focus Area';
    legendRows.push(`
      <div class="radar-legend-item">
        <span style="font-weight:600;color:var(--text-primary)">${s.label}</span>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-weight:800;color:var(--accent)">${acc}%</span>
          <span style="font-size:10px">${tierBadge}</span>
        </div>
      </div>
    `);
  });

  return `
    <div class="radar-chart-card">
      <div class="card-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
        <div class="card-title">🕸️ 10-Spoke Subject Mastery Radar (IIT Madras Curriculum)</div>
        <span class="badge" style="background:rgba(108,99,255,0.2);color:var(--accent)">360° Syllabus Depth</span>
      </div>
      <div class="radar-chart-container">
        <div class="radar-svg-wrap">
          <svg class="radar-svg" viewBox="0 0 400 400">
            ${ringsSVG}
            ${spokesSVG}
            <polygon points="${polygonPoints.join(' ')}" class="radar-polygon" />
            ${dataPoints.join('')}
          </svg>
        </div>
        <div class="radar-legend-list">
          <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px">Topic-by-topic accuracy profile:</div>
          ${legendRows.join('')}
        </div>
      </div>
    </div>
  `;
}

// ─── OPTION ELIMINATION & EXPECTED VALUE (E) RISK ANALYZER ────────────────────
function setQuestionConfidence(qid, level) {
  if (!state.confidenceTags) state.confidenceTags = {};
  if (state.confidenceTags[qid] === level) {
    delete state.confidenceTags[qid];
  } else {
    state.confidenceTags[qid] = level;
  }
  try {
    localStorage.setItem('gate_cse_confidence_tags', JSON.stringify(state.confidenceTags));
  } catch(e) {}

  const wrap = document.getElementById(`conf-selector-${qid}`);
  if (wrap) {
    wrap.outerHTML = buildConfidenceSelectorHTML(qid);
  }
}

function buildConfidenceSelectorHTML(qid) {
  const current = state.confidenceTags?.[qid] || '';
  return `
    <div class="confidence-selector" id="conf-selector-${qid}">
      <span class="conf-label">🎯 Confidence:</span>
      <div class="conf-btn-group">
        <button class="conf-btn conf-high ${current === 'high' ? 'active' : ''}" onclick="setQuestionConfidence('${qid}', 'high')" type="button" title="100% Sure / Confident">
          🟢 Sure
        </button>
        <button class="conf-btn conf-educated ${current === 'educated' ? 'active' : ''}" onclick="setQuestionConfidence('${qid}', 'educated')" type="button" title="Eliminated 1 or 2 options (50:50 guess)">
          🟡 50:50 Guess
        </button>
        <button class="conf-btn conf-blind ${current === 'blind' ? 'active' : ''}" onclick="setQuestionConfidence('${qid}', 'blind')" type="button" title="Blind Guess / Intuition">
          🔴 Blind Guess
        </button>
      </div>
    </div>
  `;
}

function getExpectedValueAnalysis(q) {
  const marks = q.marks || 1;
  const isMcq = q.type === 'mcq';
  const isMsqOrNat = q.type === 'msq' || q.type === 'nat';

  if (isMsqOrNat) {
    return {
      type: q.type.toUpperCase(),
      penalty: 0,
      ev0: (1 / 4) * marks,
      ev1: (1 / 3) * marks,
      ev2: (1 / 2) * marks,
      recommendation: '✅ ZERO NEGATIVE PENALTY: Guessing never loses marks in MSQs & NATs! Always attempt.'
    };
  }

  const neg = marks === 2 ? 2 / 3 : 1 / 3;
  const ev0 = (1 / 4) * marks - (3 / 4) * neg;
  const ev1 = (1 / 3) * marks - (2 / 3) * neg;
  const ev2 = (1 / 2) * marks - (1 / 2) * neg;

  return {
    type: 'MCQ',
    penalty: -neg,
    ev0: Number(ev0.toFixed(2)),
    ev1: Number(ev1.toFixed(2)),
    ev2: Number(ev2.toFixed(2)),
    recommendation: ev2 > 0 ? '💡 MATHEMATICAL EDGE: If you eliminate 2 options, Expected Value is +' + ev2.toFixed(2) + ' marks. Statistically you must attempt!' : 'Neutral expected value.'
  };
}

function buildExpectedValueCardHTML(q) {
  const ev = getExpectedValueAnalysis(q);
  return `
    <div class="ev-card">
      <div class="ev-header">
        <span class="ev-title">⚖️ Option Elimination & Expected Value (E) Analyzer</span>
        <span class="chip" style="font-size:10px">${escapeHtml(ev.type)} (${q.marks}M)</span>
      </div>
      <div style="font-size:11px;color:var(--text-secondary);line-height:1.4">
        ${escapeHtml(ev.recommendation)}
      </div>
      <div class="ev-matrix-grid">
        <div class="ev-stat-box">
          <div class="ev-stat-val" style="color:${ev.ev0 >= 0 ? '#4ade80' : '#f87171'}">${ev.ev0 >= 0 ? '+' : ''}${ev.ev0} M</div>
          <div class="ev-stat-lbl">Blind Guess (4 Choices)</div>
        </div>
        <div class="ev-stat-box">
          <div class="ev-stat-val" style="color:#facc15">+${ev.ev1} M</div>
          <div class="ev-stat-lbl">1 Option Eliminated</div>
        </div>
        <div class="ev-stat-box">
          <div class="ev-stat-val" style="color:#4ade80;font-weight:900">+${ev.ev2} M</div>
          <div class="ev-stat-lbl">2 Options Eliminated (50:50)</div>
        </div>
      </div>
    </div>
  `;
}

// ─── 60-SECOND FORMULA BLITZ SPEED RECALL MODE ──────────────────────────────
let blitzTimerInterval = null;
let blitzCurrentIndex = 0;
let blitzScore = 0;
let blitzStreak = 0;
let blitzTimeRemaining = 60;
let blitzDeck = [];

function startFormulaBlitz() {
  const modal = document.getElementById('flashcard-modal-card');
  if (!modal) return;
  
  blitzDeck = [...(window.FLASHCARDS || [])].sort(() => Math.random() - 0.5);
  if (!blitzDeck.length) {
    showToast('No flashcards loaded in deck', 'error');
    return;
  }
  blitzScore = 0;
  blitzStreak = 0;
  blitzTimeRemaining = 60;
  blitzCurrentIndex = 0;

  renderFormulaBlitzView();

  clearInterval(blitzTimerInterval);
  blitzTimerInterval = setInterval(() => {
    blitzTimeRemaining--;
    const timeFill = document.getElementById('blitz-timer-fill');
    const timeText = document.getElementById('blitz-time-text');
    if (timeFill) timeFill.style.width = `${(blitzTimeRemaining / 60) * 100}%`;
    if (timeText) timeText.textContent = `⏳ ${blitzTimeRemaining}s`;

    if (blitzTimeRemaining <= 0) {
      finishFormulaBlitz();
    }
  }, 1000);
}

function renderFormulaBlitzView() {
  const modal = document.getElementById('flashcard-modal-card');
  if (!modal) return;

  const card = blitzDeck[blitzCurrentIndex % blitzDeck.length] || { topic: 'Core Formula', formula: 'Formula Recall' };

  modal.innerHTML = `
    <div class="flashcard-modal-header">
      <div class="flashcard-modal-title">⚡ 60-Second Formula Blitz</div>
      <button class="shortcuts-close-btn" onclick="stopFormulaBlitz()" type="button">✕ Exit Blitz</button>
    </div>
    <div class="blitz-view-container">
      <div style="display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:700">
        <span id="blitz-time-text" style="color:#f87171">⏳ ${blitzTimeRemaining}s</span>
        <span style="color:#eab308">🔥 Streak: ${blitzStreak}</span>
        <span style="color:var(--accent)">Score: ${blitzScore} pts</span>
      </div>
      <div class="blitz-timer-bar">
        <div class="blitz-timer-fill" id="blitz-timer-fill" style="width:${(blitzTimeRemaining / 60) * 100}%"></div>
      </div>
      <div class="blitz-card-topic">${escapeHtml(card.topic)}</div>
      <div class="blitz-card-formula" id="blitz-formula-content">${escapeHtml(card.title || card.topic)}: Can you recall the invariant / formula?</div>
      <button class="btn btn-secondary btn-sm" onclick="revealBlitzFormula()" id="blitz-reveal-btn" type="button" style="align-self:center;padding:4px 12px">
        👁️ Peek Formula Solution
      </button>
      <div class="blitz-actions">
        <button class="btn btn-danger" onclick="advanceBlitzCard(false)" style="padding:10px 24px;font-weight:700" type="button">
          ❌ Blank / Forgot
        </button>
        <button class="btn btn-success" onclick="advanceBlitzCard(true)" style="padding:10px 24px;font-weight:700" type="button">
          ✅ Recalled It! (+10 pts)
        </button>
      </div>
    </div>
  `;
}

function revealBlitzFormula() {
  const card = blitzDeck[blitzCurrentIndex % blitzDeck.length];
  const box = document.getElementById('blitz-formula-content');
  const btn = document.getElementById('blitz-reveal-btn');
  if (box && card) {
    box.innerHTML = formatQuestionContent(card.formula || card.details || card.title);
    renderMath(box);
    if (btn) btn.style.display = 'none';
  }
}

function advanceBlitzCard(known) {
  if (known) {
    blitzScore += 10 + Math.min(blitzStreak * 2, 10);
    blitzStreak++;
  } else {
    blitzStreak = 0;
  }
  blitzCurrentIndex++;
  renderFormulaBlitzView();
}

function finishFormulaBlitz() {
  clearInterval(blitzTimerInterval);
  const modal = document.getElementById('flashcard-modal-card');
  if (!modal) return;
  modal.innerHTML = `
    <div class="flashcard-modal-header">
      <div class="flashcard-modal-title">🏁 Blitz Complete!</div>
      <button class="shortcuts-close-btn" onclick="stopFormulaBlitz()" type="button">✕</button>
    </div>
    <div class="blitz-view-container">
      <div class="blitz-score-badge">🏆 ${blitzScore} PTS</div>
      <div style="font-size:15px;color:var(--text-secondary);font-weight:600">
        You rapidly evaluated ${blitzCurrentIndex} core formulas in 60 seconds!
      </div>
      <div style="display:flex;justify-content:center;gap:12px;margin-top:12px">
        <button class="btn btn-primary" onclick="startFormulaBlitz()" type="button">🔄 Play Again</button>
        <button class="btn btn-secondary" onclick="stopFormulaBlitz()" type="button">Back to Deck</button>
      </div>
    </div>
  `;
}

function stopFormulaBlitz() {
  clearInterval(blitzTimerInterval);
  renderActiveFlashcard();
}

// ─── NAT PRECISION & ROUNDING TRAP INSPECTOR ─────────────────────────────────
function buildNatToleranceHTML(q) {
  if (q.type !== 'nat') return '';
  const range = q.natRange || { min: q.correct[0], max: q.correct[0] };
  const exact = q.correct[0];
  const isRange = range.min !== range.max;
  
  return `
    <div class="nat-tolerance-box">
      <div class="nat-tolerance-header">
        <span>🎯 Numerical Acceptance Bounds:</span>
        <span style="font-family:monospace;font-size:13px;font-weight:800;color:#38bdf8">
          ${isRange ? `[${range.min}, ${range.max}]` : `${exact}`}
        </span>
      </div>
      <div class="nat-trap-alert">
        <strong>⚠️ Rounding Trap Advisory:</strong> GATE marks strictly on acceptance boundaries. Never truncate or round intermediate floats; carry full machine precision and round only your final result.
      </div>
    </div>
  `;
}

// ─── 2-COLUMN PRINTABLE PRACTICE WORKSHEET GENERATOR ─────────────────────────
function generatePrintableWorksheet(questions, title = 'GATE CSE Practice Worksheet') {
  const container = document.getElementById('printable-worksheet-container');
  if (!container) return;

  const qs = questions || (state.questions || []).slice(0, 30);
  const labels = ['(A)', '(B)', '(C)', '(D)'];

  container.innerHTML = `
    <div class="ws-header">
      <div>
        <div class="ws-title">🎯 ${escapeHtml(title)}</div>
        <div class="ws-meta">GATE CSE Aspirant Platform • Organizing Institute Standards (IIT Madras) • Total Questions: ${qs.length}</div>
      </div>
      <div style="text-align:right">
        <div class="ws-meta"><strong>Date:</strong> ________________</div>
        <div class="ws-meta"><strong>Score:</strong> _____ / ${qs.reduce((acc, q) => acc + (q.marks || 1), 0)} M</div>
      </div>
    </div>

    <div class="ws-grid">
      ${qs.map((q, idx) => `
        <div class="ws-q-item">
          <div class="ws-q-num">Q${idx + 1}. [${q.type?.toUpperCase()} | ${q.marks} Mark${q.marks > 1 ? 's' : ''}] [${escapeHtml(q.subject || 'CS')}]</div>
          <div style="margin-bottom:6px">${formatQuestionContent(q.question)}</div>
          ${q.type === 'nat'
            ? `<div style="margin-top:6px;font-family:monospace">Answer: [ _______________ ]</div>`
            : `<div class="ws-options">
                ${(q.options || []).map((opt, oIdx) => `
                  <div class="ws-opt">
                    <span class="ws-box"></span>
                    <span>${labels[oIdx]} ${formatQuestionContent(opt)}</span>
                  </div>
                `).join('')}
               </div>`
          }
        </div>
      `).join('')}
    </div>

    <div class="ws-page-break"></div>

    <div class="ws-header">
      <div class="ws-title">📝 Answer Key & Solutions: ${escapeHtml(title)}</div>
      <div class="ws-meta">For Self-Evaluation Only</div>
    </div>

    <table class="ws-key-table">
      <thead>
        <tr>
          <th style="width:40px">Q#</th>
          <th style="width:60px">Type</th>
          <th style="width:80px">Correct</th>
          <th>Explanation Summary</th>
        </tr>
      </thead>
      <tbody>
        ${qs.map((q, idx) => {
          const corr = q.type === 'nat' ? `${q.correct[0]}` : q.correct.map(c => labels[c]).join(', ');
          const expl = (q.explanation || 'Direct derivation.').slice(0, 150);
          return `
            <tr>
              <td><strong>Q${idx + 1}</strong></td>
              <td>${q.type?.toUpperCase()}</td>
              <td style="font-weight:700">${corr}</td>
              <td>${escapeHtml(expl)}...</td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;

  renderMath(container);
  setTimeout(() => {
    window.print();
  }, 200);
}

function exportReviewWorksheetPDF() {
  if (state.activeTestResults?.questions) {
    generatePrintableWorksheet(state.activeTestResults.questions, 'GATE Mock Exam Review Worksheet');
  } else if (state.practiceQueue?.length) {
    generatePrintableWorksheet(state.practiceQueue, 'GATE CSE Practice Drill Worksheet');
  } else {
    generatePrintableWorksheet((state.questions || []).slice(0, 25), 'GATE CSE High-Yield Drill Worksheet');
  }
}
'''

# 2. Insert new functions right before // ─── EXPOSE FUNCTIONS TO GLOBAL SCOPE
export_header = '// ─── EXPOSE FUNCTIONS TO GLOBAL SCOPE'
if export_header in code:
    code = code.replace(export_header, new_functions + '\n' + export_header, 1)
    print("New functions inserted successfully!")
else:
    print("Export header not found!")

# 3. Add to Object.assign(window, { ... })
export_target = '  buildOfficialSyllabusGuideHTML,'
new_exports = '''  buildOfficialSyllabusGuideHTML,

  // Strategic Intelligence & Enhanced Mastery
  getExamCountdownData,
  initExamCountdownAndStreak,
  recordDailyAttemptForStreak,
  openGlobalSearch,
  closeGlobalSearch,
  handleGlobalSearchInput,
  setGlobalSearchFilter,
  executeGlobalSearch,
  startSingleQuestionPractice,
  buildMasteryRadarChartSVG,
  setQuestionConfidence,
  buildConfidenceSelectorHTML,
  getExpectedValueAnalysis,
  buildExpectedValueCardHTML,
  startFormulaBlitz,
  renderFormulaBlitzView,
  revealBlitzFormula,
  advanceBlitzCard,
  finishFormulaBlitz,
  stopFormulaBlitz,
  buildNatToleranceHTML,
  generatePrintableWorksheet,
  exportReviewWorksheetPDF,'''

if export_target in code:
    code = code.replace(export_target, new_exports, 1)
    print("New exports added successfully!")
else:
    print("export_target not found!")

# 4. Update submitPracticeAnswer to include EV card, Confidence, NAT tolerance, and recordDailyAttemptForStreak
practice_submit_target = """  const expBox=document.getElementById('explanation-box');
  if (expBox){
    expBox.classList.add('show');
    renderMath(expBox);
  }
  document.getElementById('q-actions').classList.add('hidden');
  document.getElementById('q-next-actions').classList.remove('hidden');
  await persistAttempt({questionId:q.id, correct:ok, timeMs:practiceSeconds*1000, date:Date.now(), uid:uid()});"""

practice_submit_replace = """  const expBox=document.getElementById('explanation-box');
  if (expBox){
    expBox.innerHTML = `
      ${buildConfidenceSelectorHTML(q.id)}
      ${buildExpectedValueCardHTML(q)}
      ${q.type === 'nat' ? buildNatToleranceHTML(q) : ''}
      ${buildMultiMethodExplanationHTML(q)}
      ${buildStudentShortcutNoteHTML(q.id)}
    `;
    expBox.classList.add('show');
    renderMath(expBox);
  }
  document.getElementById('q-actions').classList.add('hidden');
  document.getElementById('q-next-actions').classList.remove('hidden');
  await persistAttempt({questionId:q.id, correct:ok, timeMs:practiceSeconds*1000, date:Date.now(), uid:uid()});
  recordDailyAttemptForStreak();"""

if practice_submit_target in code:
    code = code.replace(practice_submit_target, practice_submit_replace, 1)
    print("submitPracticeAnswer updated successfully!")
else:
    print("practice_submit_target not found!")

# 5. Update renderPerformance to include buildMasteryRadarChartSVG()
perf_target = """function renderPerformance(c){
  const {attempted,correct,accuracy}=getStats();
  const subData=SUBJECTS.map(s=>({name:s.name,color:s.color,...getSubjectStats(s.name)})).filter(s=>s.total>0);
  c.innerHTML=`
    ${buildPredictorCardHTML(null, state.predictedCategory)}
    ${buildMasteryMatrixHTML()}"""

perf_replace = """function renderPerformance(c){
  const {attempted,correct,accuracy}=getStats();
  const subData=SUBJECTS.map(s=>({name:s.name,color:s.color,...getSubjectStats(s.name)})).filter(s=>s.total>0);
  c.innerHTML=`
    ${buildPredictorCardHTML(null, state.predictedCategory)}
    ${buildMasteryRadarChartSVG()}
    ${buildMasteryMatrixHTML()}"""

if perf_target in code:
    code = code.replace(perf_target, perf_replace, 1)
    print("renderPerformance updated successfully!")
else:
    print("perf_target not found!")

# 6. Update Test Review mode to include Worksheet action bar and EV / Confidence cards
review_top_target = """      ${buildLossDiagnosisHTML(session, questions, answers)}
      ${buildQuadrantAnalysisHTML()}
      <div class="section-title mb-4" style="margin-top:24px">Detailed Question Review</div>"""

review_top_replace = """      ${buildLossDiagnosisHTML(session, questions, answers)}
      ${buildQuadrantAnalysisHTML()}
      <div style="display:flex;gap:10px;margin:20px 0 16px 0;flex-wrap:wrap">
        <button class="btn btn-primary btn-sm" onclick="exportReviewWorksheetPDF()" type="button" style="display:inline-flex;align-items:center;gap:6px">
          📄 Print 2-Column PDF Practice Worksheet
        </button>
        <button class="btn btn-secondary btn-sm" onclick="printTestReport()" type="button" style="display:inline-flex;align-items:center;gap:6px">
          🖨️ Print Test Report
        </button>
      </div>
      <div class="section-title mb-4" style="margin-top:14px">Detailed Question Review</div>"""

if review_top_target in code:
    code = code.replace(review_top_target, review_top_replace, 1)
    print("Review action bar updated successfully!")
else:
    print("review_top_target not found!")

review_q_target = """          <div class="explanation-box show" style="display:block">
            ${buildMultiMethodExplanationHTML(q)}
            ${buildStudentShortcutNoteHTML(q.id)}
          </div>"""

review_q_replace = """          <div class="explanation-box show" style="display:block">
            ${buildConfidenceSelectorHTML(q.id)}
            ${buildExpectedValueCardHTML(q)}
            ${q.type === 'nat' ? buildNatToleranceHTML(q) : ''}
            ${buildMultiMethodExplanationHTML(q)}
            ${buildStudentShortcutNoteHTML(q.id)}
          </div>"""

if review_q_target in code:
    code = code.replace(review_q_target, review_q_replace, 1)
    print("Review question cards updated successfully!")
else:
    print("review_q_target not found!")

# 7. Update keyboard shortcuts for / and Escape
shortcut_escape_target = """    if (e.key === 'Escape') {
      if (flashcardModalOpen) { toggleFormulaFlashcards(false); return; }"""

shortcut_escape_replace = """    if (e.key === 'Escape') {
      if (document.getElementById('global-search-modal')?.classList.contains('active')) { closeGlobalSearch(); return; }
      if (flashcardModalOpen) { toggleFormulaFlashcards(false); return; }"""

if shortcut_escape_target in code:
    code = code.replace(shortcut_escape_target, shortcut_escape_replace, 1)
    print("Escape shortcut updated successfully!")
else:
    print("shortcut_escape_target not found!")

shortcut_slash_target = """    if (e.key === 'c' || e.key === 'C') {"""
shortcut_slash_replace = """    if (e.key === '/') {
      e.preventDefault();
      openGlobalSearch();
      return;
    }

    if (e.key === 'c' || e.key === 'C') {"""

if shortcut_slash_target in code:
    code = code.replace(shortcut_slash_target, shortcut_slash_replace, 1)
    print("Slash shortcut updated successfully!")
else:
    print("shortcut_slash_target not found!")

# 8. Update bootApp to initialize Countdown and Streak
boot_target = """  setupCalcDraggable();
  checkExamAutoSaveRecovery();
  navigate('dashboard');"""

boot_replace = """  setupCalcDraggable();
  initExamCountdownAndStreak();
  checkExamAutoSaveRecovery();
  navigate('dashboard');"""

if boot_target in code:
    code = code.replace(boot_target, boot_replace, 1)
    print("bootApp updated successfully!")
else:
    print("boot_target not found!")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("app.js patched with all improvements successfully!")
