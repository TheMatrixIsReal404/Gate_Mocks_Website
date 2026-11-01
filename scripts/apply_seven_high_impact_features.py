# -*- coding: utf-8 -*-
import sys
import re

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Backup app.js
with open('app.js.bak_seven', 'w', encoding='utf-8') as f:
    f.write(code)

print("Original app.js length:", len(code))

# 1. Add questionNotes to state
old_state_def = "  mockLevelFilter:  'all',"
new_state_def = "  mockLevelFilter:  'all',\n  questionNotes:    {},"
assert old_state_def in code, "old_state_def not found"
code = code.replace(old_state_def, new_state_def, 1)

# 2. Add questionNotes to loadCache and saveCache
old_load_cache = "    state.testSessions = d.testSessions || [];\n    loadBookmarks();"
new_load_cache = """    state.testSessions = d.testSessions || [];
    try { state.questionNotes = JSON.parse(localStorage.getItem('gate_question_notes') || '{}'); } catch(e){ state.questionNotes = {}; }
    loadBookmarks();"""
assert old_load_cache in code, "old_load_cache not found"
code = code.replace(old_load_cache, new_load_cache, 1)

old_save_cache = "    saveBookmarks();"
new_save_cache = """    saveBookmarks();
    try { localStorage.setItem('gate_question_notes', JSON.stringify(state.questionNotes || {})); } catch(e){}"""
assert old_save_cache in code, "old_save_cache not found"
code = code.replace(old_save_cache, new_save_cache, 1)

# 3. Update startMockTest to include visited Set and auto-save
old_start_mock = """  state.activeTest={
    mockId,mock,questions,
    answers:new Array(questions.length).fill(null),
    marked:new Set(), currentQ:0, timeLeft:mock.duration*60, submitted:false,
    timePerQ:new Array(questions.length).fill(0),
    tabSwitches:0,
  };"""
new_start_mock = """  state.activeTest={
    mockId,mock,questions,
    answers:new Array(questions.length).fill(null),
    marked:new Set(),
    visited:new Set([0]),
    currentQ:0, timeLeft:mock.duration*60, submitted:false,
    timePerQ:new Array(questions.length).fill(0),
    tabSwitches:0,
  };
  saveExamAutoSaveState();"""
assert old_start_mock in code, "old_start_mock not found"
code = code.replace(old_start_mock, new_start_mock, 1)

# 4. Update renderTestMode to include:
# - Chime toggle button
# - 5-state TCS iON Legend
# - Calling updatePaletteStates()
idx_rtm = code.find('function renderTestMode(){')
end_rtm = code.find('function renderTestQuestion(){')
assert idx_rtm != -1 and end_rtm != -1, "renderTestMode bounds not found"

new_render_test = """function renderTestMode(){
  const {mock,questions,timeLeft}=state.activeTest;
  const ov=document.getElementById('test-overlay');
  ov.innerHTML=`
    <div class="test-topbar">
      <div class="test-topbar-left">
        <button class="btn btn-danger btn-sm" onclick="confirmSubmitTest()">Submit Test</button>
        <div class="test-title" title="${mock.name}">${mock.name}</div>
      </div>
      <div class="test-topbar-right">
        <button class="btn btn-secondary btn-sm" id="exam-fullscreen-btn" onclick="toggleExamFullscreen()" type="button" title="Toggle Fullscreen Exam Mode (F)">⛶ <span class="hide-xs">Fullscreen</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()" type="button" title="GATE Virtual Calculator (C)">🧮 <span class="hide-xs">Calc</span></button>
        <button class="btn btn-secondary btn-sm" id="exam-chime-btn" onclick="toggleExamChimes()" type="button" title="Toggle Exam Countdown Chimes">${chimesEnabled ? '🔔' : '🔕'} <span class="hide-xs">Chimes</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleShortcutsModal()" type="button" title="Shortcuts (?)">⌨️</button>
        <div id="test-timer-display" class="test-timer-display">${fmtH(timeLeft)}</div>
        <button class="btn btn-secondary btn-sm test-palette-toggle" onclick="toggleTestPalette()" type="button" title="Question Palette">
          🎨 <span class="hide-xs">Palette</span>
        </button>
      </div>
    </div>
    <div class="test-content">
      <div class="palette-backdrop" id="palette-backdrop" onclick="toggleTestPalette()"></div>
      <div class="test-sidebar" id="test-sidebar">
        <div class="test-sidebar-header">
          <div class="section-title" style="font-size:13px">TCS iON Question Palette</div>
          <button class="palette-close-btn" onclick="toggleTestPalette()" type="button">✕</button>
        </div>
        <div class="palette-legend-5" id="palette-legend-container">
          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#22c55e"></div>Answered (<span id="cnt-ans">0</span>)</div>
          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#ef4444"></div>Not Answered (<span id="cnt-notans">0</span>)</div>
          <div class="palette-legend-item-5"><div class="legend-shape" style="background:var(--bg-input);border:1px solid var(--border)"></div>Not Visited (<span id="cnt-notvis">0</span>)</div>
          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#8b5cf6"></div>Marked (<span id="cnt-marked">0</span>)</div>
          <div class="palette-legend-item-5"><div class="legend-shape" style="background:#8b5cf6;border:2px solid #22c55e"></div>Ans & Marked (<span id="cnt-ansmarked">0</span>)</div>
        </div>
        <div class="question-palette" id="q-palette">
          ${questions.map((_,i)=>`<button class="palette-btn not-visited" id="pb-${i}" onclick="jumpToTestQ(${i})">${i+1}</button>`).join('')}
        </div>
      </div>
      <div class="test-main" id="test-q-main"></div>
    </div>`;
  ov.classList.add('active');
  renderTestQuestion();
  updatePaletteStates();
  startMockTimer();
  saveExamAutoSaveState();
}"""

code = code[:idx_rtm] + new_render_test + "\n\n" + code[end_rtm:]

# 5. Update saveAndNextTestQ, markForReview, clearTestResponse, jumpToTestQ
old_save_next = """function saveAndNextTestQ(){
  const {questions,currentQ}=state.activeTest; const q=questions[currentQ];
  if (q.type==='nat'){const inp=document.getElementById('nat-answer');state.activeTest.answers[currentQ]=inp?.value?.trim()!==''?parseFloat(inp.value):null;}
  else{const a=[...practiceSelectedOpts];state.activeTest.answers[currentQ]=a.length?a:null;}
  const a=state.activeTest.answers[currentQ];
  updatePaletteBtn(currentQ,state.activeTest.marked.has(currentQ)?'marked':a!==null?'attempted':'');
  if (currentQ<questions.length-1){state.activeTest.currentQ++;renderTestQuestion();}else confirmSubmitTest();
}"""
new_save_next = """function saveAndNextTestQ(){
  if (!state.activeTest) return;
  const {questions,currentQ}=state.activeTest; const q=questions[currentQ];
  if (q.type==='nat'){const inp=document.getElementById('nat-answer');state.activeTest.answers[currentQ]=inp?.value?.trim()!==''?parseFloat(inp.value):null;}
  else{const a=[...practiceSelectedOpts];state.activeTest.answers[currentQ]=a.length?a:null;}
  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);
  state.activeTest.visited.add(currentQ);
  if (currentQ<questions.length-1){
    state.activeTest.currentQ++;
    state.activeTest.visited.add(state.activeTest.currentQ);
    renderTestQuestion();
  } else {
    confirmSubmitTest();
  }
  updatePaletteStates();
  saveExamAutoSaveState();
}"""
assert old_save_next in code, "old_save_next not found"
code = code.replace(old_save_next, new_save_next, 1)

old_mark = """function markForReview(){
  if (!state.activeTest) return;
  const {currentQ,marked}=state.activeTest;
  if (marked.has(currentQ)) marked.delete(currentQ); else marked.add(currentQ);
  updatePaletteBtn(currentQ,marked.has(currentQ)?'marked':state.activeTest.answers[currentQ]!==null?'attempted':'');
}"""
new_mark = """function markForReview(){
  if (!state.activeTest) return;
  const {currentQ,marked}=state.activeTest;
  if (marked.has(currentQ)) marked.delete(currentQ); else marked.add(currentQ);
  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);
  state.activeTest.visited.add(currentQ);
  updatePaletteStates();
  saveExamAutoSaveState();
}"""
assert old_mark in code, "old_mark not found"
code = code.replace(old_mark, new_mark, 1)

old_clear = """function clearTestResponse(){
  state.activeTest.answers[state.activeTest.currentQ]=null; practiceSelectedOpts=new Set();
  document.querySelectorAll('.option-item').forEach(i=>i.classList.remove('selected'));
  const n=document.getElementById('nat-answer'); if(n) n.value='';
  updatePaletteBtn(state.activeTest.currentQ,'');
}"""
new_clear = """function clearTestResponse(){
  if (!state.activeTest) return;
  state.activeTest.answers[state.activeTest.currentQ]=null; practiceSelectedOpts=new Set();
  document.querySelectorAll('.option-item').forEach(i=>i.classList.remove('selected'));
  const n=document.getElementById('nat-answer'); if(n) n.value='';
  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);
  state.activeTest.visited.add(state.activeTest.currentQ);
  updatePaletteStates();
  saveExamAutoSaveState();
}"""
assert old_clear in code, "old_clear not found"
code = code.replace(old_clear, new_clear, 1)

old_jump = """function jumpToTestQ(i){
  const {currentQ,questions,answers}=state.activeTest; const q=questions[currentQ];
  if(q.type!=='nat'){const a=[...practiceSelectedOpts];state.activeTest.answers[currentQ]=a.length?a:null;}
  updatePaletteBtn(currentQ,answers[currentQ]!==null?'attempted':state.activeTest.marked.has(currentQ)?'marked':'');
  state.activeTest.currentQ=i;
  renderTestQuestion();
  if (window.innerWidth <= 768) {
    document.getElementById('test-sidebar')?.classList.remove('mobile-open');
    document.getElementById('palette-backdrop')?.classList.remove('active');
  }
}"""
new_jump = """function jumpToTestQ(i){
  if (!state.activeTest || i < 0 || i >= state.activeTest.questions.length) return;
  const {currentQ,questions}=state.activeTest; const q=questions[currentQ];
  if(q && q.type!=='nat'){const a=[...practiceSelectedOpts];state.activeTest.answers[currentQ]=a.length?a:null;}
  if (!state.activeTest.visited) state.activeTest.visited = new Set([0]);
  state.activeTest.visited.add(currentQ);
  state.activeTest.currentQ=i;
  state.activeTest.visited.add(i);
  renderTestQuestion();
  updatePaletteStates();
  saveExamAutoSaveState();
  if (window.innerWidth <= 768) {
    document.getElementById('test-sidebar')?.classList.remove('mobile-open');
    document.getElementById('palette-backdrop')?.classList.remove('active');
  }
}"""
assert old_jump in code, "old_jump not found"
code = code.replace(old_jump, new_jump, 1)

# 6. In startMockTimer, add Chimes checks & auto-save
old_timer_block = """    if (!state.activeTest.timePerQ) state.activeTest.timePerQ = new Array(state.activeTest.questions.length).fill(0);
    const curQ = state.activeTest.currentQ || 0;
    state.activeTest.timePerQ[curQ] = (state.activeTest.timePerQ[curQ] || 0) + 1;
    const el=document.getElementById('test-timer-display');
    if(el){el.textContent=fmtH(state.activeTest.timeLeft);el.className='test-timer-display';if(state.activeTest.timeLeft<=300)el.classList.add('warning');if(state.activeTest.timeLeft<=60)el.classList.add('danger');}
    if(state.activeTest.timeLeft<=0) submitMockTest();"""
new_timer_block = """    if (!state.activeTest.timePerQ) state.activeTest.timePerQ = new Array(state.activeTest.questions.length).fill(0);
    const curQ = state.activeTest.currentQ || 0;
    state.activeTest.timePerQ[curQ] = (state.activeTest.timePerQ[curQ] || 0) + 1;
    
    // Auto-save exam every 5 seconds
    if (state.activeTest.timeLeft % 5 === 0) saveExamAutoSaveState();

    // Exam pacing countdown chimes
    if (state.activeTest.timeLeft === 3600) { triggerPacingChime('60min'); showToast('🔔 1 Hour Remaining: Begin final section review', 'info'); }
    else if (state.activeTest.timeLeft === 1800) { triggerPacingChime('30min'); showToast('🔔 30 Minutes Remaining: Save your responses', 'warning'); }
    else if (state.activeTest.timeLeft === 300) { triggerPacingChime('5min'); showToast('⚠️ 5 Minutes Remaining: Final review time!', 'error'); }

    const el=document.getElementById('test-timer-display');
    if(el){el.textContent=fmtH(state.activeTest.timeLeft);el.className='test-timer-display';if(state.activeTest.timeLeft<=300)el.classList.add('warning');if(state.activeTest.timeLeft<=60)el.classList.add('danger');}
    if(state.activeTest.timeLeft<=0) submitMockTest();"""
assert old_timer_block in code, "old_timer_block not found"
code = code.replace(old_timer_block, new_timer_block, 1)

# 7. In submitMockTest, clear exam auto-save
old_submit_start = """async function submitMockTest(){
  stopMockTimer();"""
new_submit_start = """async function submitMockTest(){
  stopMockTimer();
  clearExamAutoSave();"""
assert old_submit_start in code, "old_submit_start not found"
code = code.replace(old_submit_start, new_submit_start, 1)

# 8. Add Question Notes button and callout in showTestResult
old_note_anchor = """            <div style="display:flex;align-items:center;gap:8px">
              <button class="btn btn-secondary btn-sm" onclick="toggleBookmark('${q.id}'); this.innerHTML = state.bookmarks.has('${q.id}') ? '⭐ Bookmarked' : '☆ Star';" style="padding:2px 8px;font-size:11px" type="button">
                ${isBmk ? '⭐ Bookmarked' : '☆ Star'}
              </button>
              <span style="font-size:13px;font-weight:700;color:${clr}">${lbl}</span>
            </div>"""
new_note_anchor = """            <div style="display:flex;align-items:center;gap:8px">
              <button class="btn btn-secondary btn-sm" onclick="promptQuestionNote('${q.id}')" style="padding:2px 8px;font-size:11px" type="button">
                📝 ${state.questionNotes?.[q.id] ? 'Edit Note' : 'Add Note'}
              </button>
              <button class="btn btn-secondary btn-sm" onclick="toggleBookmark('${q.id}'); this.innerHTML = state.bookmarks.has('${q.id}') ? '⭐ Bookmarked' : '☆ Star';" style="padding:2px 8px;font-size:11px" type="button">
                ${isBmk ? '⭐ Bookmarked' : '☆ Star'}
              </button>
              <span style="font-size:13px;font-weight:700;color:${clr}">${lbl}</span>
            </div>"""
assert old_note_anchor in code, "old_note_anchor not found"
code = code.replace(old_note_anchor, new_note_anchor, 1)

old_expl_box = """<div class="explanation-box show" style="display:block"><strong>💡 </strong>${formatQuestionContent(q.explanation||'No explanation.')}</div>
        </div>`;"""
new_expl_box = """<div class="explanation-box show" style="display:block"><strong>💡 </strong>${formatQuestionContent(q.explanation||'No explanation.')}</div>
          ${state.questionNotes?.[q.id] ? `
            <div class="question-note-box">
              <div class="question-note-header">
                <span>📌 PERSONAL REVISION NOTE:</span>
                <button class="btn btn-secondary btn-sm" onclick="promptQuestionNote('${q.id}')" style="padding:1px 6px;font-size:10px">Edit</button>
              </div>
              <div>${escapeHtml(state.questionNotes[q.id])}</div>
            </div>` : ''}
        </div>`;"""
assert old_expl_box in code, "old_expl_box not found"
code = code.replace(old_expl_box, new_expl_box, 1)

# 9. In renderPerformance, insert GATE Syllabus Mastery Matrix & Data Portability Card
old_perf_insert = "${buildPredictorCardHTML(null, state.predictedCategory)}"
new_perf_insert = "${buildPredictorCardHTML(null, state.predictedCategory)}\n    ${buildMasteryMatrixHTML()}\n    ${buildDataPortabilityCardHTML()}"
assert old_perf_insert in code, "old_perf_insert not found"
code = code.replace(old_perf_insert, new_perf_insert, 1)

# 10. In renderPractice, add Custom Drill Generator quick launch button in header
old_practice_header = '<button class="btn btn-primary btn-sm" onclick="startPracticeMode()" ${!filtered.length ? \'disabled\' : \'\'}>▶ Start Practice</button>'
new_practice_header = """<div style="display:flex;gap:8px;align-items:center">
        <button class="btn btn-secondary btn-sm" onclick="toggleCustomDrillModal(true)" style="border-color:var(--accent);color:var(--accent);font-weight:700" type="button">🎛️ Custom Drill</button>
        <button class="btn btn-primary btn-sm" onclick="startPracticeMode()" ${!filtered.length ? 'disabled' : ''}>▶ Start Practice</button>
      </div>"""
assert old_practice_header in code, "old_practice_header not found"
code = code.replace(old_practice_header, new_practice_header, 1)

# 11. Append the new modules:
# - Exam Crash Protection Engine
# - 5-State TCS iON Question Palette Logic
# - GATE Weightage & Topic Mastery Matrix
# - Custom Drill Generator Engine
# - User Data Portability (Export / Restore)
# - Personal Notes Scratchpad
# - Web Audio Exam Countdown Chimes
new_seven_code = """
// ═════════════════════════════════════════════════════════════════════════════
// ── SEVEN HIGH-IMPACT ENGINE UPGRADES ──
// ═════════════════════════════════════════════════════════════════════════════

// ── 1. EXAM CRASH PROTECTION & AUTO-SAVE RECOVERY ──
const AUTOSAVE_TEST_KEY = 'gate_active_test_autosave_v1';

function saveExamAutoSaveState() {
  if (!state.activeTest || state.activeTest.submitted) return;
  try {
    const copy = {
      mockId: state.activeTest.mockId,
      mock: state.activeTest.mock,
      answers: state.activeTest.answers,
      marked: Array.from(state.activeTest.marked || []),
      visited: Array.from(state.activeTest.visited || [state.activeTest.currentQ || 0]),
      currentQ: state.activeTest.currentQ || 0,
      timeLeft: state.activeTest.timeLeft,
      timePerQ: state.activeTest.timePerQ || [],
      tabSwitches: state.activeTest.tabSwitches || 0,
      savedAt: Date.now()
    };
    localStorage.setItem(AUTOSAVE_TEST_KEY, JSON.stringify(copy));
  } catch(e) {}
}

function clearExamAutoSave() {
  try { localStorage.removeItem(AUTOSAVE_TEST_KEY); } catch(e) {}
}

function checkExamAutoSaveRecovery() {
  try {
    const raw = localStorage.getItem(AUTOSAVE_TEST_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    if (!data || !data.mockId || data.timeLeft <= 10) {
      clearExamAutoSave();
      return;
    }
    showResumeExamModal(data);
  } catch(e) {}
}

function showResumeExamModal(data) {
  let modal = document.getElementById('resume-exam-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'resume-exam-modal';
    modal.className = 'resume-modal-backdrop';
    document.body.appendChild(modal);
  }
  const mockName = data.mock?.name || 'In-Progress Exam';
  const minLeft = Math.round(data.timeLeft / 60);
  const agoMin = Math.max(1, Math.round((Date.now() - (data.savedAt || Date.now())) / 60000));
  modal.innerHTML = `
    <div class="resume-modal-card">
      <div class="resume-modal-title">
        <span>🔄 Unfinished Exam Detected</span>
      </div>
      <div class="resume-modal-body">
        You have an active in-progress attempt for <strong>${escapeHtml(mockName)}</strong> with <strong>${minLeft} minutes</strong> remaining (saved ${agoMin} minute${agoMin>1?'s':''} ago). Would you like to resume where you left off?
      </div>
      <div class="resume-modal-actions">
        <button class="btn btn-secondary btn-sm" onclick="discardSavedExam()" type="button">Discard</button>
        <button class="btn btn-primary btn-sm" onclick="resumeSavedExam()" type="button" style="font-weight:700">Resume Exam</button>
      </div>
    </div>
  `;
  modal.style.display = 'flex';
}

function resumeSavedExam() {
  try {
    const raw = localStorage.getItem(AUTOSAVE_TEST_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    document.getElementById('resume-exam-modal')?.remove();
    const mock = data.mock || MOCK_TESTS.find(m => m.id === data.mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === data.mockId);
    const questions = getMockQuestions(data.mockId);
    if (!questions.length) { showToast('Unable to resume: questions not found', 'error'); clearExamAutoSave(); return; }
    state.activeTest = {
      mockId: data.mockId,
      mock,
      questions,
      answers: data.answers || new Array(questions.length).fill(null),
      marked: new Set(data.marked || []),
      visited: new Set(data.visited || [data.currentQ || 0]),
      currentQ: data.currentQ || 0,
      timeLeft: data.timeLeft,
      timePerQ: data.timePerQ || new Array(questions.length).fill(0),
      tabSwitches: data.tabSwitches || 0,
      submitted: false
    };
    renderTestMode();
    showToast('Resumed in-progress exam successfully!', 'success');
  } catch(e) {
    console.error(e);
    clearExamAutoSave();
  }
}

function discardSavedExam() {
  clearExamAutoSave();
  document.getElementById('resume-exam-modal')?.remove();
  showToast('Unfinished exam discarded.', 'info');
}

// ── 2. TCS iON 5-STATE QUESTION PALETTE ENGINE ──
function updatePaletteStates() {
  if (!state.activeTest) return;
  const { questions, currentQ, answers, marked, visited } = state.activeTest;
  let ansCount = 0, notAnsCount = 0, notVisCount = 0, markedCount = 0, ansMarkedCount = 0;

  for (let i = 0; i < questions.length; i++) {
    const a = answers[i];
    const hasAns = a !== null && a !== undefined && (!Array.isArray(a) || a.length > 0);
    const isMarked = marked.has(i);
    const isVisited = visited ? visited.has(i) : true;
    const btn = document.getElementById(`pb-${i}`);

    let stateCls = 'not-visited';
    if (hasAns && isMarked) {
      stateCls = 'ans-marked';
      ansMarkedCount++;
    } else if (isMarked) {
      stateCls = 'marked';
      markedCount++;
    } else if (hasAns) {
      stateCls = 'answered';
      ansCount++;
    } else if (isVisited) {
      stateCls = 'not-answered';
      notAnsCount++;
    } else {
      stateCls = 'not-visited';
      notVisCount++;
    }

    if (btn) {
      btn.className = `palette-btn ${stateCls}${i === currentQ ? ' current' : ''}`;
    }
  }

  const cAns = document.getElementById('cnt-ans');
  const cNotAns = document.getElementById('cnt-notans');
  const cNotVis = document.getElementById('cnt-notvis');
  const cMarked = document.getElementById('cnt-marked');
  const cAnsMarked = document.getElementById('cnt-ansmarked');
  if (cAns) cAns.textContent = ansCount;
  if (cNotAns) cNotAns.textContent = notAnsCount;
  if (cNotVis) cNotVis.textContent = notVisCount;
  if (cMarked) cMarked.textContent = markedCount;
  if (cAnsMarked) cAnsMarked.textContent = ansMarkedCount;
}

// ── 3. GATE SYLLABUS MASTERY MATRIX & WEIGHTAGE HEATMAP ──
function buildMasteryMatrixHTML() {
  const map = new Map(state.attempts.map(a => [a.questionId, a]));

  function getPillarStats(predicate) {
    const qs = state.questions.filter(predicate);
    const attempted = qs.filter(q => map.has(q.id));
    const correct = attempted.filter(q => map.get(q.id)?.correct);
    const acc = attempted.length > 0 ? Math.round((correct.length / attempted.length) * 100) : 0;
    return { total: qs.length, attempted: attempted.length, correct: correct.length, acc };
  }

  const gaStats = getPillarStats(q => q.subject === 'General Aptitude');
  const emStats = getPillarStats(q => ['Engineering Mathematics', 'Discrete Mathematics'].includes(q.subject));
  const csStats = getPillarStats(q => q.subject !== 'General Aptitude' && !['Engineering Mathematics', 'Discrete Mathematics'].includes(q.subject));

  // Compute Projected Marks
  const gaProj = ((gaStats.acc / 100) * 15).toFixed(1);
  const emProj = ((emStats.acc / 100) * 13).toFixed(1);
  const csProj = ((csStats.acc / 100) * 72).toFixed(1);
  const totalProj = (parseFloat(gaProj) + parseFloat(emProj) + parseFloat(csProj)).toFixed(1);

  function getBadge(acc, att) {
    if (att === 0) return `<span class="mastery-status-badge" style="background:rgba(255,255,255,0.08);color:var(--text-muted)">Unattempted</span>`;
    if (acc >= 75) return `<span class="mastery-status-badge mastery-strong">🟢 Strong Mastery</span>`;
    if (acc >= 50) return `<span class="mastery-status-badge mastery-mod">🟡 Moderate</span>`;
    return `<span class="mastery-status-badge mastery-risk">🔴 High-Risk Area</span>`;
  }

  return `
    <div class="mastery-matrix-card">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:12px">
        <div>
          <div style="font-size:16px;font-weight:800;color:#fff">🗺️ GATE Syllabus Mastery Matrix & Weightage Heatmap</div>
          <div class="text-sm text-muted">Accuracy mapped against standard 100-mark GATE CS distribution.</div>
        </div>
        <div style="background:rgba(108,99,255,0.15);padding:6px 14px;border-radius:20px;border:1px solid rgba(108,99,255,0.3);font-size:13px;font-weight:700;color:var(--accent)">
          Projected GATE Marks: <span style="font-size:16px;color:#fff">${totalProj}</span> / 100
        </div>
      </div>

      <div class="mastery-pillars-grid">
        <!-- Pillar 1: General Aptitude -->
        <div class="mastery-pillar-box">
          <div class="mastery-pillar-top">
            <span class="mastery-pillar-title">1. General Aptitude (GA)</span>
            <span class="mastery-pillar-weight">15 Marks Weight</span>
          </div>
          <div class="mastery-pillar-meter">
            <div class="mastery-pillar-fill" style="width:${gaStats.acc}%;background:#22c55e"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px">
            <span class="text-muted">${gaStats.attempted}/${gaStats.total} Qs Attempted</span>
            <span style="font-weight:700;color:${gaStats.acc>=75?'#22c55e':gaStats.acc>=50?'#f59e0b':'#ef4444'}">${gaStats.acc}% Accuracy</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            ${getBadge(gaStats.acc, gaStats.attempted)}
            <span style="font-size:11.5px;color:var(--text-secondary)">Proj: <strong>${gaProj}</strong>/15 M</span>
          </div>
        </div>

        <!-- Pillar 2: Engineering & Discrete Math -->
        <div class="mastery-pillar-box">
          <div class="mastery-pillar-top">
            <span class="mastery-pillar-title">2. Engg & Discrete Math</span>
            <span class="mastery-pillar-weight">13 Marks Weight</span>
          </div>
          <div class="mastery-pillar-meter">
            <div class="mastery-pillar-fill" style="width:${emStats.acc}%;background:#3b82f6"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px">
            <span class="text-muted">${emStats.attempted}/${emStats.total} Qs Attempted</span>
            <span style="font-weight:700;color:${emStats.acc>=75?'#22c55e':emStats.acc>=50?'#f59e0b':'#ef4444'}">${emStats.acc}% Accuracy</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            ${getBadge(emStats.acc, emStats.attempted)}
            <span style="font-size:11.5px;color:var(--text-secondary)">Proj: <strong>${emProj}</strong>/13 M</span>
          </div>
        </div>

        <!-- Pillar 3: Core Computer Science -->
        <div class="mastery-pillar-box">
          <div class="mastery-pillar-top">
            <span class="mastery-pillar-title">3. Core Computer Science</span>
            <span class="mastery-pillar-weight">72 Marks Weight</span>
          </div>
          <div class="mastery-pillar-meter">
            <div class="mastery-pillar-fill" style="width:${csStats.acc}%;background:var(--accent)"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px">
            <span class="text-muted">${csStats.attempted}/${csStats.total} Qs Attempted</span>
            <span style="font-weight:700;color:${csStats.acc>=75?'#22c55e':csStats.acc>=50?'#f59e0b':'#ef4444'}">${csStats.acc}% Accuracy</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            ${getBadge(csStats.acc, csStats.attempted)}
            <span style="font-size:11.5px;color:var(--text-secondary)">Proj: <strong>${csProj}</strong>/72 M</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

// ── 4. CUSTOM MOCK EXAM & PRACTICE DRILL GENERATOR ──
function toggleCustomDrillModal(open) {
  let modal = document.getElementById('custom-drill-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'custom-drill-modal';
    modal.className = 'drill-modal-backdrop';
    document.body.appendChild(modal);
  }
  if (!open) {
    modal.style.display = 'none';
    return;
  }
  const allSubs = Array.from(new Set(state.questions.map(q => q.subject).filter(Boolean))).sort();
  modal.innerHTML = `
    <div class="drill-modal-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:17px;font-weight:800;color:#fff">🎛️ Custom Drill & Exam Generator</div>
        <button class="btn btn-secondary btn-sm" onclick="toggleCustomDrillModal(false)" type="button">✕</button>
      </div>
      <p class="text-sm text-muted" style="margin-bottom:14px">
        Craft your own personalized test session from our database of 8,168 authentic questions.
      </p>

      <div style="margin-bottom:14px">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <label style="font-size:12px;font-weight:700;color:var(--text-secondary)">Select Target Subjects:</label>
          <button class="btn btn-secondary btn-sm" onclick="toggleSelectAllDrillSubjects()" style="padding:2px 8px;font-size:11px" type="button">Toggle All</button>
        </div>
        <div class="drill-subject-grid" id="drill-subject-grid">
          ${allSubs.map(s => `
            <div class="drill-subject-item selected" data-sub="${escapeHtml(s)}" onclick="this.classList.toggle('selected')">
              <span>📚</span><span>${escapeHtml(s)}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
        <div>
          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Question Type:</label>
          <select class="form-select form-select-sm" id="drill-type" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">
            <option value="all">All Types (MCQ, MSQ, NAT)</option>
            <option value="mcq">MCQs Only</option>
            <option value="msq">MSQs Only</option>
            <option value="nat">NATs Only</option>
          </select>
        </div>
        <div>
          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Difficulty Tier:</label>
          <select class="form-select form-select-sm" id="drill-diff" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">
            <option value="all">Mixed (Balanced GATE CS)</option>
            <option value="easy">Easy (Foundational)</option>
            <option value="medium">Medium (Standard GATE)</option>
            <option value="hard">Hard (Rank Booster)</option>
          </select>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px">
        <div>
          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Number of Questions:</label>
          <select class="form-select form-select-sm" id="drill-count" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">
            <option value="15">15 Questions (Quick Drill)</option>
            <option value="30">30 Questions (Half-Length)</option>
            <option value="65">65 Questions (Full-Length Exam)</option>
          </select>
        </div>
        <div>
          <label style="font-size:12px;font-weight:700;color:var(--text-secondary);display:block;margin-bottom:4px">Mode:</label>
          <select class="form-select form-select-sm" id="drill-mode" style="width:100%;padding:6px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:#fff">
            <option value="timed">Timed Exam Mode (Countdown)</option>
            <option value="practice">Practice Mode (Instant Solutions)</option>
          </select>
        </div>
      </div>

      <div style="display:flex;justify-content:flex-end;gap:10px">
        <button class="btn btn-secondary btn-sm" onclick="toggleCustomDrillModal(false)" type="button">Cancel</button>
        <button class="btn btn-primary btn-sm" onclick="launchCustomDrill()" style="font-weight:700" type="button">🚀 Launch Custom Session</button>
      </div>
    </div>
  `;
  modal.style.display = 'flex';
}

function toggleSelectAllDrillSubjects() {
  const items = document.querySelectorAll('.drill-subject-item');
  const allSel = Array.from(items).every(i => i.classList.contains('selected'));
  items.forEach(i => i.classList.toggle('selected', !allSel));
}

function launchCustomDrill() {
  const selectedSubs = Array.from(document.querySelectorAll('.drill-subject-item.selected')).map(i => i.dataset.sub);
  if (!selectedSubs.length) {
    showToast('Please select at least one subject!', 'error');
    return;
  }
  const type = document.getElementById('drill-type')?.value || 'all';
  const diff = document.getElementById('drill-diff')?.value || 'all';
  const count = parseInt(document.getElementById('drill-count')?.value || '15', 10);
  const mode = document.getElementById('drill-mode')?.value || 'timed';

  let pool = state.questions.filter(q => selectedSubs.includes(q.subject));
  if (type !== 'all') pool = pool.filter(q => q.type === type);
  if (diff !== 'all') pool = pool.filter(q => q.difficulty === diff);

  if (!pool.length) {
    showToast('No questions match this combination! Try relaxing the filters.', 'error');
    return;
  }

  const selectedQs = shuffleArr([...pool]).slice(0, count);
  toggleCustomDrillModal(false);

  if (mode === 'practice') {
    state.practiceQueue = selectedQs;
    state.currentQuestion = 0;
    state.practiceAnswered = false;
    state.activeMockPaper = null;
    state.activeTest = null;
    navigate('practice');
    showToast(`Started custom practice drill with ${selectedQs.length} questions!`, 'success');
  } else {
    const customMock = {
      id: `custom-mock-${Date.now()}`,
      name: `Custom Drill (${selectedQs.length} Qs)`,
      duration: Math.max(20, Math.round(selectedQs.length * 2.75)),
      marks: selectedQs.reduce((s, q) => s + (q.marks || 1), 0),
      difficulty: diff === 'all' ? 'medium' : diff,
      type: 'full'
    };
    state.activeTest = {
      mockId: customMock.id,
      mock: customMock,
      questions: selectedQs,
      answers: new Array(selectedQs.length).fill(null),
      marked: new Set(),
      visited: new Set([0]),
      currentQ: 0,
      timeLeft: customMock.duration * 60,
      submitted: false,
      timePerQ: new Array(selectedQs.length).fill(0),
      tabSwitches: 0
    };
    renderTestMode();
    showToast(`Started custom timed exam (${customMock.duration} min)!`, 'success');
  }
}

// ── 5. USER DATA PORTABILITY (EXPORT & RESTORE PROGRESS) ──
function buildDataPortabilityCardHTML() {
  return `
    <div class="data-portability-card">
      <div>
        <div style="font-size:15px;font-weight:800;color:#fff">💾 1-Click Data Backup & Device Portability</div>
        <div class="text-sm text-muted" style="margin-top:2px">
          Export your test sessions, accuracy history, bookmarks, and revision notes to backup or transfer across devices.
        </div>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <button class="btn btn-secondary btn-sm" onclick="exportUserData()" style="font-weight:700" type="button">
          📥 Export Progress (JSON)
        </button>
        <button class="btn btn-secondary btn-sm" onclick="triggerRestoreFilePrompt()" style="font-weight:700;border-color:var(--accent);color:var(--accent)" type="button">
          📤 Restore From File
        </button>
      </div>
    </div>
  `;
}

function exportUserData() {
  try {
    const payload = {
      app: 'GATE CSE Platform',
      version: 'v5.5',
      exportDate: new Date().toISOString(),
      testSessions: state.testSessions || [],
      attempts: state.attempts || [],
      bookmarks: Array.from(state.bookmarks || []),
      questionNotes: state.questionNotes || {}
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gate_cse_progress_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Progress exported successfully! File downloaded.', 'success');
  } catch(e) {
    showToast('Export failed: ' + e.message, 'error');
  }
}

function triggerRestoreFilePrompt() {
  document.getElementById('restore-progress-file-input')?.click();
}

function handleRestoreProgressFile(event) {
  const file = event.target?.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      if (!data || !Array.isArray(data.attempts)) {
        showToast('Invalid backup file format.', 'error');
        return;
      }
      // Merge test sessions
      const existingSesIds = new Set((state.testSessions || []).map(s => s.id));
      (data.testSessions || []).forEach(s => {
        if (!existingSesIds.has(s.id)) state.testSessions.push(s);
      });

      // Merge attempts
      const attMap = new Map(state.attempts.map(a => [a.questionId, a]));
      (data.attempts || []).forEach(a => {
        if (!attMap.has(a.questionId) || a.date > attMap.get(a.questionId).date) {
          attMap.set(a.questionId, a);
        }
      });
      state.attempts = Array.from(attMap.values());

      // Merge bookmarks
      (data.bookmarks || []).forEach(b => state.bookmarks.add(b));

      // Merge notes
      state.questionNotes = Object.assign({}, state.questionNotes || {}, data.questionNotes || {});

      saveCache();
      showToast(`Restored ${data.attempts.length} attempts and ${data.testSessions?.length || 0} sessions!`, 'success');
      renderPage(state.currentPage || 'performance', state.currentParams || {});
    } catch(err) {
      showToast('Error parsing file: ' + err.message, 'error');
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// ── 6. PERSONAL QUESTION REVISION NOTES (SCRATCHPAD) ──
function promptQuestionNote(qId) {
  if (!state.questionNotes) state.questionNotes = {};
  const current = state.questionNotes[qId] || '';
  const note = prompt('Enter your personal revision note or mnemonic for this question:', current);
  if (note === null) return; // User cancelled
  saveQuestionNote(qId, note);
  if (state.currentPage === 'mistakes') {
    renderMistakes(document.getElementById('page-content'));
  } else if (state.currentPage === 'practice') {
    renderPractice(document.getElementById('page-content'));
  }
}

function saveQuestionNote(qId, noteText) {
  if (!state.questionNotes) state.questionNotes = {};
  if (noteText && noteText.trim()) {
    state.questionNotes[qId] = noteText.trim();
    showToast('Personal revision note saved!', 'success');
  } else {
    delete state.questionNotes[qId];
    showToast('Personal revision note deleted.', 'info');
  }
  try {
    localStorage.setItem('gate_question_notes', JSON.stringify(state.questionNotes));
  } catch(e) {}
}

// ── 7. EXAM PACING WEB AUDIO COUNTDOWN CHIMES ──
let examAudioCtx = null;
let chimesEnabled = localStorage.getItem('gate_exam_chimes') !== 'false';

function getExamAudioCtx() {
  if (!examAudioCtx) {
    examAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return examAudioCtx;
}

function toggleExamChimes() {
  chimesEnabled = !chimesEnabled;
  try { localStorage.setItem('gate_exam_chimes', chimesEnabled ? 'true' : 'false'); } catch(e) {}
  const btn = document.getElementById('exam-chime-btn');
  if (btn) btn.innerHTML = `${chimesEnabled ? '🔔' : '🔕'} <span class="hide-xs">Chimes</span>`;
  showToast(chimesEnabled ? '🔔 Exam Countdown Chimes Enabled' : '🔕 Exam Countdown Chimes Muted', 'info');
}

function playChimeTone(freq, duration, delay = 0) {
  if (!chimesEnabled) return;
  try {
    const ctx = getExamAudioCtx();
    if (ctx.state === 'suspended') ctx.resume();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, ctx.currentTime + delay);
    gain.gain.setValueAtTime(0.12, ctx.currentTime + delay);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(ctx.currentTime + delay);
    osc.stop(ctx.currentTime + delay + duration);
  } catch(e) {}
}

function triggerPacingChime(type) {
  if (type === '60min') {
    playChimeTone(520, 0.4);
  } else if (type === '30min') {
    playChimeTone(659, 0.3, 0);
    playChimeTone(520, 0.4, 0.35);
  } else if (type === '5min') {
    playChimeTone(880, 0.25, 0);
    playChimeTone(659, 0.25, 0.28);
    playChimeTone(880, 0.35, 0.56);
  }
}
"""

# Insert new code before bootApp
bootapp_target = "async function bootApp(user) {"
assert bootapp_target in code, "bootApp target not found"
code = code.replace(bootapp_target, new_seven_code + "\n" + bootapp_target, 1)

# In bootApp, call checkExamAutoSaveRecovery()
old_boot_init = "  setupMobileMenu();\n  setupKeyboardShortcuts();\n  setupCalcDraggable();"
new_boot_init = "  setupMobileMenu();\n  setupKeyboardShortcuts();\n  setupCalcDraggable();\n  checkExamAutoSaveRecovery();"
assert old_boot_init in code, "old_boot_init not found"
code = code.replace(old_boot_init, new_boot_init, 1)

# Export all new functions in Object.assign(window, {...})
old_exports_point = "  // Advanced Improvements & Simulators"
new_exports = """  // Seven High-Impact Upgrades
  saveExamAutoSaveState,
  clearExamAutoSave,
  resumeSavedExam,
  discardSavedExam,
  updatePaletteStates,
  buildMasteryMatrixHTML,
  buildDataPortabilityCardHTML,
  toggleCustomDrillModal,
  toggleSelectAllDrillSubjects,
  launchCustomDrill,
  exportUserData,
  triggerRestoreFilePrompt,
  handleRestoreProgressFile,
  promptQuestionNote,
  saveQuestionNote,
  toggleExamChimes,

  // Advanced Improvements & Simulators"""
assert old_exports_point in code, "old_exports_point not found"
code = code.replace(old_exports_point, new_exports, 1)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully integrated Seven High-Impact features! New length:", len(code))
