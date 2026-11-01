# -*- coding: utf-8 -*-
import sys
import re

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Backup app.js
with open('app.js.bak_adv', 'w', encoding='utf-8') as f:
    f.write(code)

print("Original app.js length:", len(code))

# 1. Update titles in navigate()
old_titles = "dashboard:'Dashboard', subjects:'Subjects', practice:'Practice Questions',\n    mocks:'Mock Tests', 'pyq-exams':'Full-Length PYQ Exams', pyqs:'Topic-wise PYQs', performance:'Performance', upload:'Upload Questions',"
new_titles = "dashboard:'Dashboard', subjects:'Subjects', practice:'Practice Questions',\n    mocks:'Mock Tests', 'pyq-exams':'Full-Length PYQ Exams', pyqs:'Topic-wise PYQs', mistakes:'Mistake Vault & Revision', performance:'Performance', upload:'Upload Questions',"
assert old_titles in code, "old_titles not found"
code = code.replace(old_titles, new_titles, 1)

# 2. Update renderPage switch
old_switch = "case 'performance': renderPerformance(c);       break;"
new_switch = "case 'mistakes':    renderMistakes(c);          break;\n    case 'performance': renderPerformance(c);       break;"
assert old_switch in code, "old_switch not found"
code = code.replace(old_switch, new_switch, 1)

# 3. Update renderTestMode topbar right to include Fullscreen button
old_test_topbar_right = """      <div class="test-topbar-right">
        <button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()" type="button" title="GATE Virtual Calculator (C)">🧮 <span class="hide-xs">Calc</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleShortcutsModal()" type="button" title="Shortcuts (?)">⌨️</button>"""
new_test_topbar_right = """      <div class="test-topbar-right">
        <button class="btn btn-secondary btn-sm" id="exam-fullscreen-btn" onclick="toggleExamFullscreen()" type="button" title="Toggle Fullscreen Exam Mode (F)">⛶ <span class="hide-xs">Fullscreen</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()" type="button" title="GATE Virtual Calculator (C)">🧮 <span class="hide-xs">Calc</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleShortcutsModal()" type="button" title="Shortcuts (?)">⌨️</button>"""
assert old_test_topbar_right in code, "old_test_topbar_right not found"
code = code.replace(old_test_topbar_right, new_test_topbar_right, 1)

# 4. Update startMockTest to initialize timePerQ and tabSwitches
old_start_mock = """  state.activeTest={
    mockId,mock,questions,
    answers:new Array(questions.length).fill(null),
    marked:new Set(), currentQ:0, timeLeft:mock.duration*60, submitted:false,
  };"""
new_start_mock = """  state.activeTest={
    mockId,mock,questions,
    answers:new Array(questions.length).fill(null),
    marked:new Set(), currentQ:0, timeLeft:mock.duration*60, submitted:false,
    timePerQ:new Array(questions.length).fill(0),
    tabSwitches:0,
  };"""
assert old_start_mock in code, "old_start_mock not found"
code = code.replace(old_start_mock, new_start_mock, 1)

# 5. Update startMockTimer to accumulate timePerQ
old_timer = """  mockTimerInterval=setInterval(()=>{
    if(!state.activeTest||state.activeTest.submitted){stopMockTimer();return;}
    state.activeTest.timeLeft--;"""
new_timer = """  mockTimerInterval=setInterval(()=>{
    if(!state.activeTest||state.activeTest.submitted){stopMockTimer();return;}
    state.activeTest.timeLeft--;
    if (!state.activeTest.timePerQ) state.activeTest.timePerQ = new Array(state.activeTest.questions.length).fill(0);
    const curQ = state.activeTest.currentQ || 0;
    state.activeTest.timePerQ[curQ] = (state.activeTest.timePerQ[curQ] || 0) + 1;"""
assert old_timer in code, "old_timer not found"
code = code.replace(old_timer, new_timer, 1)

# 6. Update submitMockTest to record timeMs accurately and pass timePerQ to session
old_submit_att = """    answeredAttempts.push({
      questionId: q.id,
      correct: ok,
      timeMs: Math.round(((mock.duration * 60 - timeLeft) / Math.max(1, questions.length)) * 1000),
      date: Date.now(),
      uid: uid()
    });"""
new_submit_att = """    const qDwellSec = (state.activeTest.timePerQ && state.activeTest.timePerQ[i]) || Math.round((mock.duration * 60 - timeLeft) / Math.max(1, questions.length));
    answeredAttempts.push({
      questionId: q.id,
      correct: ok,
      timeMs: qDwellSec * 1000,
      date: Date.now(),
      uid: uid()
    });"""
assert old_submit_att in code, "old_submit_att not found"
code = code.replace(old_submit_att, new_submit_att, 1)

old_session = """  const session={mockId:mock.id,name:mock.name,date:Date.now(),score:Math.max(0,parseFloat(score.toFixed(2))),maxScore,percentage:pct,correct,wrong,skipped,timeTaken:mock.duration*60-timeLeft};"""
new_session = """  const session={mockId:mock.id,name:mock.name,date:Date.now(),score:Math.max(0,parseFloat(score.toFixed(2))),maxScore,percentage:pct,correct,wrong,skipped,timeTaken:mock.duration*60-timeLeft,timePerQ:[...(state.activeTest.timePerQ||[])],tabSwitches:state.activeTest.tabSwitches||0};"""
assert old_session in code, "old_session not found"
code = code.replace(old_session, new_session, 1)

# 7. Update keyboard shortcuts for Alt+S, Alt+M, Alt+C, and F (fullscreen)
old_shortcuts_block = """      if (e.key === 'Enter') {
        e.preventDefault();
        saveAndNextTestQ();
        return;
      }"""
new_shortcuts_block = """      if (e.key === 'Enter' || ((e.key === 's' || e.key === 'S') && e.altKey)) {
        e.preventDefault();
        saveAndNextTestQ();
        return;
      }
      if ((e.key === 'm' || e.key === 'M') && e.altKey) {
        e.preventDefault();
        markForReview();
        return;
      }
      if ((e.key === 'c' || e.key === 'C') && e.altKey) {
        e.preventDefault();
        clearTestResponse();
        return;
      }
      if (e.key === 'f' || e.key === 'F') {
        if (!e.ctrlKey && !e.metaKey && !e.altKey && !['INPUT','TEXTAREA'].includes(e.target?.tagName)) {
          e.preventDefault();
          toggleExamFullscreen();
          return;
        }
      }"""
assert old_shortcuts_block in code, "old_shortcuts_block not found"
code = code.replace(old_shortcuts_block, new_shortcuts_block, 1)

# 8. Enhance showTestResult with Pacing Analytics, Time Badges per question, Print Report & GATE Score Predictor
idx1 = code.find('function showTestResult(')
idx2 = code.find('function closeResult(')
assert idx1 != -1 and idx2 != -1, "showTestResult bounds not found"

new_show_result = """function showTestResult(session,questions,answers){
  const ov=document.getElementById('result-overlay');
  const pct=session.percentage;
  const grade=pct>=85?'🏆 Excellent':pct>=70?'🌟 Good':pct>=50?'📈 Average':'📚 Need More Practice';
  const labels=['A','B','C','D','E'];
  const times = session.timePerQ || new Array(questions.length).fill(0);
  const totalSec = session.timeTaken || times.reduce((a,b)=>a+b, 0) || 1;
  const avgSec = Math.round(totalSec / Math.max(1, questions.length));

  // Compute pacing stats
  let correctSec = 0, wrongSec = 0, skipSec = 0, overtimeCount = 0;
  questions.forEach((q, i) => {
    const a = answers[i];
    const isSkip = a === null || (Array.isArray(a) && !a.length);
    const qSec = times[i] || 0;
    if (qSec > 210) overtimeCount++;
    if (isSkip) {
      skipSec += qSec;
    } else {
      let isOk = false;
      if (q.type === 'nat') {
        const v = parseFloat(a), e = q.correct[0];
        isOk = v >= (q.natRange?.min ?? e) && v <= (q.natRange?.max ?? e);
      } else {
        const s = (Array.isArray(a) ? a : [a]).sort((x, y) => x - y), e = [...q.correct].sort((x, y) => x - y);
        isOk = s.length === e.length && s.every((v, idx) => v === e[idx]);
      }
      if (isOk) correctSec += qSec;
      else wrongSec += qSec;
    }
  });

  const avgCorrect = session.correct > 0 ? Math.round(correctSec / session.correct) : 0;
  const avgWrong = session.wrong > 0 ? Math.round(wrongSec / session.wrong) : 0;

  // Predictor calculation for this test
  const pred = calculateGatePrediction(session.score, state.predictedCategory || 'GEN');

  ov.innerHTML=`
    <div class="result-hero">
      <div class="result-score-ring" style="--pct:${pct}">
        <div class="result-score-inner">
          <div class="result-score-pct">${pct}%</div>
          <div class="result-score-label">Score</div>
        </div>
      </div>
      <div class="result-title">${grade}</div>
      <div class="result-subtitle">${session.name}</div>
      <div class="result-stats">
        <div class="result-stat"><div class="result-stat-value" style="color:var(--green)">${session.correct}</div><div class="result-stat-label">Correct</div></div>
        <div class="result-stat"><div class="result-stat-value" style="color:var(--red)">${session.wrong}</div><div class="result-stat-label">Wrong</div></div>
        <div class="result-stat"><div class="result-stat-value" style="color:var(--text-muted)">${session.skipped}</div><div class="result-stat-label">Skipped</div></div>
        <div class="result-stat"><div class="result-stat-value">${session.score}/${session.maxScore}</div><div class="result-stat-label">Marks</div></div>
        <div class="result-stat"><div class="result-stat-value">${fmtH(session.timeTaken)}</div><div class="result-stat-label">Time</div></div>
        ${session.tabSwitches > 0 ? `<div class="result-stat"><div class="result-stat-value" style="color:var(--red)">${session.tabSwitches}</div><div class="result-stat-label">Tab Switches</div></div>` : ''}
      </div>
      <div style="margin-top:20px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
        <button class="btn btn-white" onclick="closeResult()">🏠 Home</button>
        <button class="btn btn-outline-white" onclick="navigate('mocks')">🎯 All Tests</button>
        <button class="btn btn-secondary btn-sm" onclick="printTestReport()" style="background:rgba(255,255,255,0.15);color:#fff">🖨️ Print / Save PDF</button>
        <button class="btn btn-secondary btn-sm" onclick="navigate('mistakes')" style="background:rgba(239,68,68,0.2);color:#ff8888">📖 Review Mistakes</button>
      </div>
    </div>
    <div class="result-content">
      <!-- ── QUESTION-WISE TIME & PACING ANALYTICS ── -->
      <div class="section-title mb-2">⏱️ Question-Wise Pacing Analytics</div>
      <div class="pacing-analytics-grid">
        <div class="pacing-stat-card">
          <div class="pacing-stat-val">${fmtSec(avgSec)}</div>
          <div class="pacing-stat-lbl">Avg Time / Question</div>
        </div>
        <div class="pacing-stat-card">
          <div class="pacing-stat-val" style="color:var(--green)">${fmtSec(avgCorrect)}</div>
          <div class="pacing-stat-lbl">Avg on Correct Qs</div>
        </div>
        <div class="pacing-stat-card">
          <div class="pacing-stat-val" style="color:var(--red)">${fmtSec(avgWrong)}</div>
          <div class="pacing-stat-lbl">Avg on Incorrect Qs</div>
        </div>
        <div class="pacing-stat-card">
          <div class="pacing-stat-val" style="color:${overtimeCount > 5 ? 'var(--red)' : 'var(--accent)'}">${overtimeCount} Qs</div>
          <div class="pacing-stat-lbl">Pacing Warnings (>3.5m)</div>
        </div>
      </div>

      <!-- ── ESTIMATED GATE SCORE & RANK PREDICTION ── -->
      <div class="predictor-card" style="margin-top:16px">
        <div class="predictor-card-header">
          <div class="predictor-title">🎯 Estimated GATE Performance Predictor</div>
          <span class="badge" style="background:rgba(108,99,255,0.2);color:var(--accent)">Based on this Test</span>
        </div>
        <div class="predictor-output-grid">
          <div class="predictor-output-box">
            <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Estimated GATE Score</div>
            <div class="predictor-score-huge">${pred.score} <span style="font-size:14px;color:var(--text-muted);font-weight:600">/ 1000</span></div>
          </div>
          <div class="predictor-output-box">
            <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Estimated All India Rank (AIR)</div>
            <div class="predictor-air-huge" style="color:${pred.airBadgeClass}">${pred.air}</div>
          </div>
        </div>
        <div class="predictor-eligibility-badge">${pred.eligibility}</div>
      </div>

      <div class="section-title mb-4" style="margin-top:24px">Detailed Question Review</div>
      ${questions.map((q,i)=>{
        const a=answers[i]; const skip=a===null||(Array.isArray(a)&&!a.length);
        let ok=false;
        if(!skip){if(q.type==='nat'){const v=parseFloat(a),e=q.correct[0];ok=v>=(q.natRange?.min??e)&&v<=(q.natRange?.max??e);}else{const s=(Array.isArray(a)?a:[a]).sort((x,y)=>x-y),e=[...q.correct].sort((x,y)=>x-y);ok=s.length===e.length&&s.every((v,idx)=>v===e[idx]);}}
        const clr=skip?'var(--text-muted)':ok?'var(--green)':'var(--red)';
        const lbl=skip?'⚪ Skipped':ok?'✅ Correct':'❌ Wrong';
        const yourAns=skip?'Not attempted':q.type==='nat'?`${a}`:(Array.isArray(a)?a:[a]).map(i=>labels[i]+'.'+(q.options?.[i]||'')).join(', ');
        const corrAns=q.type==='nat'?`${q.correct[0]}`:q.correct.map(i=>labels[i]+'.'+(q.options?.[i]||'')).join(', ');
        const qSec = times[i] || 0;
        const timeCls = qSec <= 90 ? 'time-spent-fast' : qSec <= 210 ? 'time-spent-optimal' : 'time-spent-warning';
        const isBmk = state.bookmarks?.has(q.id);

        return `<div class="card mb-4" style="border-left:3px solid ${clr}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
            <div style="display:flex;align-items:center;gap:8px">
              <span class="chip">Q${i+1}</span>
              <span class="chip chip-info">${q.subject}</span>
              <span class="time-spent-badge ${timeCls}">⏱️ ${fmtSec(qSec)}${qSec > 210 ? ' • Overtime' : ''}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
              <button class="btn btn-secondary btn-sm" onclick="toggleBookmark('${q.id}'); this.innerHTML = state.bookmarks.has('${q.id}') ? '⭐ Bookmarked' : '☆ Star';" style="padding:2px 8px;font-size:11px" type="button">
                ${isBmk ? '⭐ Bookmarked' : '☆ Star'}
              </button>
              <span style="font-size:13px;font-weight:700;color:${clr}">${lbl}</span>
            </div>
          </div>
          <div style="font-size:14px;line-height:1.7;margin-bottom:12px;font-weight:500">${formatQuestionContent(q.question)}</div>
          <div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px">Your: <strong>${yourAns}</strong></div>
          ${!ok?`<div style="font-size:13px;color:var(--green);margin-bottom:8px">Correct: <strong>${corrAns}</strong></div>`:''}
          <div class="explanation-box show" style="display:block"><strong>💡 </strong>${formatQuestionContent(q.explanation||'No explanation.')}</div>
        </div>`;
      }).join('')}
    </div>`;
  ov.classList.add('active'); ov.scrollTop=0;
  renderMath(ov);
}
"""

code = code[:idx1] + new_show_result + "\n" + code[idx2:]

# 9. Append new helper functions, Mistake Vault, Predictor, Fullscreen, Draggable, and PWA logic
new_modules_code = """
// ── SECONDS FORMATTER HELPER ──
function fmtSec(sec) {
  sec = Math.max(0, parseInt(sec) || 0);
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  if (m === 0) return `${s}s`;
  return `${m}m ${s < 10 ? '0' : ''}${s}s`;
}

// ── FULLSCREEN EXAM MODE ──
function toggleExamFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen?.().then(() => {
      updateFullscreenBtn(true);
    }).catch(err => {
      console.warn('[Exam] Fullscreen request:', err);
    });
  } else {
    document.exitFullscreen?.().then(() => {
      updateFullscreenBtn(false);
    }).catch(err => {
      console.warn('[Exam] Exit fullscreen:', err);
    });
  }
}

function updateFullscreenBtn(isFull) {
  const btn = document.getElementById('exam-fullscreen-btn');
  if (btn) {
    btn.innerHTML = isFull
      ? '🗗 <span class="hide-xs">Exit Fullscreen</span>'
      : '⛶ <span class="hide-xs">Fullscreen</span>';
  }
}

document.addEventListener('fullscreenchange', () => {
  updateFullscreenBtn(!!document.fullscreenElement);
});

// Proctored Exam Focus / Tab Switch Alert
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden' && state.activeTest && !state.activeTest.submitted) {
    state.activeTest.tabSwitches = (state.activeTest.tabSwitches || 0) + 1;
    showToast(`⚠️ Exam Alert: Tab switch detected (#${state.activeTest.tabSwitches})! Maintain full focus on the exam.`, 'error');
  }
});

// ── PRINT / SAVE TEST REPORT ──
function printTestReport() {
  window.print();
}

// ── DRAGGABLE GATE CALCULATOR ──
function setupCalcDraggable() {
  const modal = document.getElementById('gate-calc-modal');
  const handle = document.getElementById('calc-drag-handle');
  if (!modal || !handle || modal._dragInitialized) return;
  modal._dragInitialized = true;

  let isDragging = false;
  let startX = 0, startY = 0, initialLeft = 0, initialTop = 0;

  handle.addEventListener('pointerdown', (e) => {
    if (e.target.closest('.calc-close-btn') || e.target.closest('button')) return;
    isDragging = true;
    modal.classList.add('is-dragging');
    const rect = modal.getBoundingClientRect();
    startX = e.clientX;
    startY = e.clientY;
    initialLeft = rect.left;
    initialTop = rect.top;
    modal.style.right = 'auto';
    modal.style.bottom = 'auto';
    modal.style.transform = 'none';
    modal.style.left = `${initialLeft}px`;
    modal.style.top = `${initialTop}px`;
    try { handle.setPointerCapture(e.pointerId); } catch(err) {}
  });

  window.addEventListener('pointermove', (e) => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    const newLeft = Math.max(10, Math.min(window.innerWidth - modal.offsetWidth - 10, initialLeft + dx));
    const newTop = Math.max(10, Math.min(window.innerHeight - modal.offsetHeight - 10, initialTop + dy));
    modal.style.left = `${newLeft}px`;
    modal.style.top = `${newTop}px`;
  });

  window.addEventListener('pointerup', () => {
    if (isDragging) {
      isDragging = false;
      modal.classList.remove('is-dragging');
    }
  });
}

// ── OFFICIAL GATE SCORE & AIR PREDICTOR ENGINE ──
function calculateGatePrediction(marks, category = 'GEN') {
  marks = Math.max(0, Math.min(100, parseFloat(marks) || 0));
  const Mq = category === 'SC' ? 20.0 : category === 'OBC' ? 26.5 : 29.5;
  const Mt = 78.5;
  const Sq = 350;
  const St = 900;
  let score = 0;
  if (marks < Mq) {
    score = Math.round(Sq * (marks / Mq));
  } else {
    score = Math.min(1000, Math.round(Sq + (St - Sq) * ((marks - Mq) / (Mt - Mq))));
  }

  let air = '';
  let eligibility = '';
  let airBadgeClass = '#22c55e';

  if (score >= 900) {
    air = 'AIR 1 – 100';
    eligibility = 'Top 100 Ranker! Direct interview-exempt admission to IISc Bangalore & IIT Bombay (M.Tech CSE / Direct PhD) and Top PSUs (IOCL, ONGC, NTPC).';
  } else if (score >= 800) {
    air = 'AIR 101 – 450';
    eligibility = 'Top Tier IIT CSE: IIT Delhi, IIT Madras, IIT Kanpur, IIT Kharagpur (M.Tech CSE / AI & Data Science). PSU Shortlisting Guaranteed.';
  } else if (score >= 700) {
    air = 'AIR 451 – 1,200';
    eligibility = 'Established IITs & Top NITs: IIT Roorkee, IIT Guwahati, IIT Hyderabad, NIT Trichy, NIT Surathkal, IIIT Bangalore / Hyderabad.';
  } else if (score >= 600) {
    air = 'AIR 1,201 – 2,800';
    eligibility = 'Top NITs & Newer IITs: NIT Warangal, NIT Calicut, VNIT, MNIT, IIT BHU, IIT Gandhinagar, IIT Ropar.';
  } else if (score >= 500) {
    air = 'AIR 2,801 – 5,500';
    eligibility = 'Good NITs & Central Universities: NIT Durgapur, NIT Jalandhar, NIT Silchar, BITS Pilani (Higher Degree).';
  } else if (score >= 350) {
    air = 'AIR 5,501 – 15,000';
    eligibility = 'GATE Qualified. Eligible for CCMT counseling across Tier-2/3 NITs, IIEST, State Engineering Colleges, and stipend M.Tech.';
    airBadgeClass = '#f59e0b';
  } else {
    air = 'Below Qualifying Cutoff';
    eligibility = 'Marks below estimated cutoff. Continue practicing foundational mocks and high-weightage core CS topics.';
    airBadgeClass = '#ef4444';
  }

  return { marks, score, air, eligibility, category, airBadgeClass, isQualified: marks >= Mq };
}

function buildPredictorCardHTML(marksVal, catVal) {
  const latestSession = state.testSessions?.[state.testSessions.length - 1];
  const defaultMarks = marksVal !== null && marksVal !== undefined ? marksVal : (latestSession ? latestSession.score : 55);
  const cat = catVal || state.predictedCategory || 'GEN';
  const pred = calculateGatePrediction(defaultMarks, cat);

  return `
    <div class="predictor-card" id="gate-predictor-container">
      <div class="predictor-card-header">
        <div class="predictor-title">
          <span>🎯 Official GATE Score & Rank Simulator</span>
          <span class="badge" style="background:rgba(108,99,255,0.2);color:var(--accent);font-size:11px">IISc/IIT Model</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <label style="font-size:12px;color:var(--text-secondary);font-weight:600">Category:</label>
          <select class="form-select form-select-sm" style="width:auto;padding:4px 8px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text-primary)" onchange="updatePredictorCategory(this.value)">
            <option value="GEN" ${cat==='GEN'?'selected':''}>General / EWS (Cutoff ~29.5)</option>
            <option value="OBC" ${cat==='OBC'?'selected':''}>OBC-NCL (Cutoff ~26.5)</option>
            <option value="SC" ${cat==='SC'?'selected':''}>SC / ST / PwD (Cutoff ~20.0)</option>
          </select>
        </div>
      </div>

      <div class="predictor-slider-container">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <span style="font-size:13px;font-weight:600;color:var(--text-secondary)">Target Exam Marks (out of 100):</span>
          <span style="font-size:18px;font-weight:900;color:var(--accent)">${pred.marks} / 100</span>
        </div>
        <input type="range" class="predictor-slider" min="0" max="100" step="0.5" value="${pred.marks}" oninput="updatePredictorMarks(this.value)" />
      </div>

      <div class="predictor-output-grid">
        <div class="predictor-output-box">
          <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Simulated GATE Score</div>
          <div class="predictor-score-huge">${pred.score} <span style="font-size:14px;color:var(--text-muted);font-weight:600">/ 1000</span></div>
        </div>
        <div class="predictor-output-box">
          <div style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase">Estimated All India Rank (AIR)</div>
          <div class="predictor-air-huge" style="color:${pred.airBadgeClass}">${pred.air}</div>
        </div>
      </div>
      <div class="predictor-eligibility-badge" style="background:${pred.isQualified ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)'};color:${pred.airBadgeClass}">
        ${pred.eligibility}
      </div>
    </div>`;
}

function updatePredictorMarks(val) {
  state.predictedMarks = parseFloat(val);
  const container = document.getElementById('gate-predictor-container');
  if (container) {
    container.outerHTML = buildPredictorCardHTML(state.predictedMarks, state.predictedCategory);
  }
}

function updatePredictorCategory(cat) {
  state.predictedCategory = cat;
  const container = document.getElementById('gate-predictor-container');
  if (container) {
    container.outerHTML = buildPredictorCardHTML(state.predictedMarks, state.predictedCategory);
  }
}

// ── MISTAKE VAULT & REVISION NOTEBOOK VIEW ──
function getMistakeData() {
  const latestAttemptMap = new Map();
  state.attempts.forEach(a => {
    if (!latestAttemptMap.has(a.questionId) || a.date > latestAttemptMap.get(a.questionId).date) {
      latestAttemptMap.set(a.questionId, a);
    }
  });

  const allMistakeQIds = new Set();
  state.attempts.filter(a => a.correct === false).forEach(a => allMistakeQIds.add(a.questionId));

  const unresolved = [];
  const resolved = [];

  allMistakeQIds.forEach(id => {
    const q = state.questions.find(x => x.id === id);
    if (!q) return;
    const latest = latestAttemptMap.get(id);
    if (latest && latest.correct === true) {
      resolved.push({ q, latest });
    } else {
      unresolved.push({ q, latest });
    }
  });

  const bookmarked = [];
  if (state.bookmarks) {
    state.bookmarks.forEach(id => {
      const q = state.questions.find(x => x.id === id);
      if (q) bookmarked.push(q);
    });
  }

  return { unresolved, resolved, bookmarked, totalMistakes: allMistakeQIds.size };
}

function renderMistakes(c) {
  const { unresolved, resolved, bookmarked, totalMistakes } = getMistakeData();
  const subFilter = state.mistakeSubject || 'all';
  const statusFilter = state.mistakeStatus || 'unresolved';
  const search = (state.mistakeSearch || '').trim().toLowerCase();

  let displayed = [];
  if (statusFilter === 'unresolved') {
    displayed = unresolved.map(item => item.q);
  } else if (statusFilter === 'resolved') {
    displayed = resolved.map(item => item.q);
  } else if (statusFilter === 'bookmarked') {
    displayed = bookmarked;
  } else {
    // all recorded mistakes
    const map = new Map();
    [...unresolved, ...resolved].forEach(item => map.set(item.q.id, item.q));
    displayed = Array.from(map.values());
  }

  if (subFilter !== 'all') {
    displayed = displayed.filter(q => q.subject === subFilter);
  }
  if (search) {
    displayed = displayed.filter(q =>
      (q.question && q.question.toLowerCase().includes(search)) ||
      (q.topic && q.topic.toLowerCase().includes(search)) ||
      (q.subject && q.subject.toLowerCase().includes(search))
    );
  }

  const subjectsWithMistakes = Array.from(new Set([...unresolved, ...resolved].map(item => item.q.subject))).sort();

  c.innerHTML = `
    <!-- ── MISTAKE HERO BANNER ── -->
    <div class="mistake-hero">
      <div class="mistake-hero-text">
        <h2>📖 Mistake Vault & Weakness Diagnostic</h2>
        <p>Every mistake in your mock exams and practice drills is recorded here automatically. Turn your past errors into guaranteed marks on exam day with targeted re-drills.</p>
      </div>
      <div class="mistake-stats-pills">
        <div class="mistake-stat-pill">
          <span class="mistake-stat-pill-val" style="color:#ef4444">${unresolved.length}</span>
          <span class="mistake-stat-pill-lbl">Unresolved</span>
        </div>
        <div class="mistake-stat-pill">
          <span class="mistake-stat-pill-val" style="color:#22c55e">${resolved.length}</span>
          <span class="mistake-stat-pill-lbl">Mastered</span>
        </div>
        <div class="mistake-stat-pill">
          <span class="mistake-stat-pill-val" style="color:#f59e0b">${bookmarked.length}</span>
          <span class="mistake-stat-pill-lbl">Starred</span>
        </div>
        <div class="mistake-stat-pill">
          <span class="mistake-stat-pill-val" style="color:var(--accent)">${totalMistakes}</span>
          <span class="mistake-stat-pill-lbl">Total Vault</span>
        </div>
      </div>
    </div>

    <!-- ── CONTROLS & ACTION BAR ── -->
    <div class="mistake-controls-bar">
      <div class="mistake-filters-group">
        <button class="btn btn-primary btn-sm" onclick="startMistakeReTest()" style="font-weight:700" type="button" ${!unresolved.length ? 'disabled' : ''}>
          🔥 Re-Test My Mistakes (${Math.min(15, unresolved.length)} Qs)
        </button>
        <div style="display:flex;align-items:center;gap:6px">
          <button class="btn btn-secondary btn-sm ${statusFilter==='unresolved'?'btn-primary':''}" onclick="setMistakeStatusFilter('unresolved')">Unresolved (${unresolved.length})</button>
          <button class="btn btn-secondary btn-sm ${statusFilter==='bookmarked'?'btn-primary':''}" onclick="setMistakeStatusFilter('bookmarked')">⭐ Starred (${bookmarked.length})</button>
          <button class="btn btn-secondary btn-sm ${statusFilter==='resolved'?'btn-primary':''}" onclick="setMistakeStatusFilter('resolved')">✅ Mastered (${resolved.length})</button>
          <button class="btn btn-secondary btn-sm ${statusFilter==='all'?'btn-primary':''}" onclick="setMistakeStatusFilter('all')">All (${totalMistakes})</button>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
        <input type="text" class="search-input" placeholder="Search mistakes by keyword..."
          style="padding:6px 12px;font-size:12px;width:200px"
          value="${escapeHtml(state.mistakeSearch || '')}"
          oninput="updateMistakeSearch(this.value)" />
        <select class="form-select form-select-sm" style="width:auto;padding:6px 10px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);border-radius:6px;color:var(--text-primary)" onchange="setMistakeSubjectFilter(this.value)">
          <option value="all" ${subFilter==='all'?'selected':''}>All Subjects (${subjectsWithMistakes.length})</option>
          ${subjectsWithMistakes.map(s => `<option value="${escapeHtml(s)}" ${subFilter===s?'selected':''}>${escapeHtml(s)}</option>`).join('')}
        </select>
      </div>
    </div>

    <!-- ── MISTAKE QUESTIONS LIST ── -->
    ${!displayed.length ? `
      <div class="empty-state">
        <div class="empty-state-icon">🎉</div>
        <div class="empty-state-title">No mistakes matching your filter</div>
        <div class="empty-state-sub">Keep solving full mock tests and practicing questions to track weak areas!</div>
      </div>
    ` : `
      <div class="mistake-list">
        ${displayed.map((q, idx) => {
          const isBmk = state.bookmarks?.has(q.id);
          const att = state.attempts.find(a => a.questionId === q.id);
          const timeSec = att?.timeMs ? Math.round(att.timeMs / 1000) : 0;
          const labels = ['A','B','C','D'];
          return `
            <div class="mistake-card">
              <div class="mistake-card-top">
                <div class="mistake-meta-tags">
                  <span class="mistake-tag mistake-tag-danger">Missed</span>
                  <span class="mistake-tag mistake-tag-subject">${escapeHtml(q.subject)}</span>
                  ${q.topic ? `<span class="chip" style="font-size:11px">${escapeHtml(q.topic)}</span>` : ''}
                  <span class="chip" style="font-size:11px">${q.type?.toUpperCase()} • ${q.marks} Mark${q.marks>1?'s':''}</span>
                  ${timeSec > 0 ? `<span class="mistake-tag mistake-tag-dwell">⏱️ ${fmtSec(timeSec)}</span>` : ''}
                </div>
                <div style="display:flex;align-items:center;gap:8px">
                  <button class="btn btn-secondary btn-sm" onclick="toggleBookmark('${q.id}'); renderMistakes(document.getElementById('page-content'));" style="padding:3px 8px;font-size:11px" type="button">
                    ${isBmk ? '⭐ Starred' : '☆ Star'}
                  </button>
                  <button class="btn btn-secondary btn-sm" onclick="markMistakeResolved('${q.id}')" style="padding:3px 8px;font-size:11px;color:#22c55e" type="button">
                    ✅ Mark Mastered
                  </button>
                </div>
              </div>
              <div style="font-size:14px;line-height:1.7;margin-bottom:12px;font-weight:500">
                <strong style="color:var(--accent);margin-right:6px">Q${idx + 1}.</strong>${formatQuestionContent(q.question)}
              </div>
              ${q.options && q.options.length ? `
                <div class="options-list mb-3">
                  ${q.options.map((opt, oIdx) => {
                    const isCorrect = q.correct?.includes(oIdx);
                    return `<div class="option-item ${isCorrect ? 'correct' : ''}" style="cursor:default">
                      <div class="option-marker">${labels[oIdx]}</div>
                      <div class="option-text">${formatQuestionContent(opt)}</div>
                    </div>`;
                  }).join('')}
                </div>
              ` : `
                <div style="font-size:13px;color:var(--green);margin-bottom:8px">
                  Correct Answer: <strong>${q.correct?.[0] !== undefined ? q.correct[0] : (q.natRange ? `${q.natRange.min} - ${q.natRange.max}` : '')}</strong>
                </div>
              `}
              <div class="mistake-solution-box">
                <div style="font-weight:700;color:var(--accent);margin-bottom:4px">💡 Step-by-Step Explanation:</div>
                ${formatQuestionContent(q.explanation || 'Refer to standard syllabus and core concepts.')}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `}
  `;
}

function setMistakeStatusFilter(st) {
  state.mistakeStatus = st;
  renderMistakes(document.getElementById('page-content'));
}

function setMistakeSubjectFilter(sub) {
  state.mistakeSubject = sub;
  renderMistakes(document.getElementById('page-content'));
}

function updateMistakeSearch(term) {
  state.mistakeSearch = term;
  renderMistakes(document.getElementById('page-content'));
}

async function markMistakeResolved(qId) {
  const att = {
    questionId: qId,
    correct: true,
    timeMs: 60000,
    date: Date.now(),
    uid: uid()
  };
  await persistAttempt(att);
  showToast('Question marked as mastered!', 'success');
  renderMistakes(document.getElementById('page-content'));
}

function startMistakeReTest() {
  const { unresolved } = getMistakeData();
  if (!unresolved.length) {
    showToast('No unresolved mistakes found! Great job!', 'info');
    return;
  }
  const pool = unresolved.map(item => item.q);
  const selected = shuffleArr([...pool]).slice(0, 15);
  state.practiceQueue = selected;
  state.currentQuestion = 0;
  state.practiceAnswered = false;
  state.practiceSelected = null;
  state.activeMockPaper = null;
  state.activeTest = null;
  navigate('practice');
  showToast(`Launched Mistake Drill with ${selected.length} questions!`, 'success');
}

// ── PWA INSTALLATION HELPER ──
window.deferredPwaPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  window.deferredPwaPrompt = e;
  const btn = document.getElementById('pwa-install-btn');
  if (btn) btn.style.display = 'inline-flex';
});

function triggerPwaInstall() {
  if (window.deferredPwaPrompt) {
    window.deferredPwaPrompt.prompt();
    window.deferredPwaPrompt.userChoice.then(choice => {
      if (choice.outcome === 'accepted') {
        showToast('Thank you for installing GATE CSE App!', 'success');
      }
      window.deferredPwaPrompt = null;
      const btn = document.getElementById('pwa-install-btn');
      if (btn) btn.style.display = 'none';
    });
  } else {
    showToast('Offline app is ready! Access offline practice anytime from browser menu.', 'info');
  }
}
"""

# Insert new modules before bootApp
bootapp_target = "async function bootApp(user) {"
assert bootapp_target in code, "bootApp target not found"
code = code.replace(bootapp_target, new_modules_code + "\n" + bootapp_target, 1)

# In bootApp, call setupCalcDraggable()
old_boot_call = "  setupMobileMenu();\n  setupKeyboardShortcuts();"
new_boot_call = "  setupMobileMenu();\n  setupKeyboardShortcuts();\n  setupCalcDraggable();"
assert old_boot_call in code, "old_boot_call not found"
code = code.replace(old_boot_call, new_boot_call, 1)

# Also in renderPerformance, insert the Predictor card
old_perf_grid = '  c.innerHTML=`\n    <div class="stats-grid" style="margin-bottom:28px">'
new_perf_grid = '  c.innerHTML=`\n    ${buildPredictorCardHTML(null, state.predictedCategory)}\n    <div class="stats-grid" style="margin-bottom:28px">'
assert old_perf_grid in code, "old_perf_grid not found"
code = code.replace(old_perf_grid, new_perf_grid, 1)

# 10. Update Object.assign(window, {...}) to export new functions
old_obj_assign = "  // Mock Paper & Practice Papers"
new_obj_exports = """  // Advanced Improvements & Simulators
  toggleExamFullscreen,
  printTestReport,
  setupCalcDraggable,
  calculateGatePrediction,
  buildPredictorCardHTML,
  updatePredictorMarks,
  updatePredictorCategory,
  renderMistakes,
  setMistakeStatusFilter,
  setMistakeSubjectFilter,
  updateMistakeSearch,
  markMistakeResolved,
  startMistakeReTest,
  triggerPwaInstall,

  // Mock Paper & Practice Papers"""
assert old_obj_assign in code, "old_obj_assign not found"
code = code.replace(old_obj_assign, new_obj_exports, 1)

# Write updated code
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully updated app.js! New length:", len(code))
