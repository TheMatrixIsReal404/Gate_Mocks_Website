# -*- coding: utf-8 -*-
import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. State properties
state_needle = "mockSort:         'default',"
state_repl = """mockSort:         'default',
  mockViewMode:     (typeof localStorage !== 'undefined' && localStorage.getItem('gate_mock_view_mode')) || 'grid',
  pinnedMocks:      new Set(JSON.parse((typeof localStorage !== 'undefined' && localStorage.getItem('gate_pinned_mocks')) || '[]')),"""

assert state_needle in code, "state_needle not found"
code = code.replace(state_needle, state_repl, 1)

# 2. subSeries === 'pinned' filter in getFilteredAndSortedMocks
subseries_needle = "  // 1. Sub-series filter\n  if (subSeries === 'med-30') {"
subseries_repl = """  // 1. Sub-series filter
  if (subSeries === 'pinned') {
    list = list.filter(m => state.pinnedMocks && state.pinnedMocks.has(m.id));
  } else if (subSeries === 'med-30') {"""

if subseries_needle not in code:
    subseries_needle = "  // 1. Sub-series filter\r\n  if (subSeries === 'med-30') {"
    subseries_repl = subseries_repl.replace("\n", "\r\n")

assert subseries_needle in code, "subseries_needle not found"
code = code.replace(subseries_needle, subseries_repl, 1)

# 3. Add helper functions before setMockSort
helper_funcs = """
function setMockViewMode(mode) {
  state.mockViewMode = mode;
  try { localStorage.setItem('gate_mock_view_mode', mode); } catch(e) {}
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}

function togglePinMock(mockId, evt) {
  if (evt) evt.stopPropagation();
  if (!state.pinnedMocks) state.pinnedMocks = new Set();
  if (state.pinnedMocks.has(mockId)) {
    state.pinnedMocks.delete(mockId);
    showToast('Mock removed from target list', 'info');
  } else {
    state.pinnedMocks.add(mockId);
    showToast('Mock added to ⭐ Target Mocks!', 'success');
  }
  try {
    localStorage.setItem('gate_pinned_mocks', JSON.stringify([...state.pinnedMocks]));
  } catch(e) {}
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}

function openMockRetakeCompare(mockId, evt) {
  if (evt) evt.stopPropagation();
  const matchingIndices = [];
  state.testSessions.forEach((s, idx) => {
    if (s.mockId === mockId) matchingIndices.push(idx);
  });
  if (matchingIndices.length < 2) {
    showToast('Complete this mock at least twice to compare retake progress!', 'info');
    return;
  }
  openCompareModal();
  const selectA = document.getElementById('compare-test-a');
  const selectB = document.getElementById('compare-test-b');
  if (selectA && selectB) {
    selectA.value = matchingIndices[0];
    selectB.value = matchingIndices[matchingIndices.length - 1];
    updateComparisonView();
  }
}

function buildMockCompactList(mocks) {
  return `<div class="mock-compact-list">${mocks.map(m => {
    const past = state.testSessions.filter(s => s.mockId === m.id);
    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const diffLabel = (m.difficulty || 'medium').toUpperCase();
    const isPinned = state.pinnedMocks && state.pinnedMocks.has(m.id);

    let providerBadge = '';
    const provName = m.provider || (m.tier && m.tier.includes('Made Easy') ? 'Made Easy' : (m.tier && (m.tier.includes('Gate Overflow') || m.tier.includes('GO Classes')) ? 'GO Classes & Gate Overflow' : null));
    if (provName) {
      let icon = provName.includes('Made Easy') ? '📘' : provName.includes('GO') ? '🌐' : '🏆';
      providerBadge = `<span class="q-badge" style="font-size:10px;padding:2px 6px;font-weight:600">${icon} ${provName}</span>`;
    }

    return `<div class="mock-compact-row" onclick="viewMockPaper('${m.id}')">
      <div class="mock-compact-main">
        <button class="mock-pin-btn ${isPinned ? 'pinned' : 'unpinned'}" onclick="togglePinMock('${m.id}', event)" title="${isPinned ? 'Unpin Mock' : 'Pin to Target Mocks'}" type="button">
          ${isPinned ? '⭐' : '☆'}
        </button>
        <div style="min-width:65px">
          <span class="mock-compact-title">${m.name}</span>
        </div>
        ${providerBadge}
        <span class="q-badge ${m.difficulty || 'medium'}" style="font-size:10px;padding:2px 6px">${diffLabel}${m.rating ? ` ${m.rating.toFixed(1)}/10` : ''}</span>
        <span class="mock-compact-desc" title="${escapeHtml(m.desc)}">${m.desc}</span>
      </div>
      <div class="mock-compact-meta">
        <span>📚 ${questionsCount} Qs</span>
        <span>⏱️ ${m.duration}m</span>
        <span>🏅 ${m.marks} M</span>
        ${best !== null ? `<span style="color:var(--green);font-weight:700">🏆 ${best}%</span>` : ''}
        ${past.length >= 2 ? `<button class="btn btn-secondary btn-sm" onclick="openMockRetakeCompare('${m.id}', event)" title="Compare your ${past.length} attempts" style="font-size:10px;padding:2px 6px" type="button">📊 Retakes (${past.length})</button>` : ''}
      </div>
      <div class="mock-compact-actions" onclick="event.stopPropagation()">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" style="font-size:11px;padding:4px 8px" type="button">📄 Paper</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" style="font-size:11px;padding:4px 10px" type="button">▶ Start</button>
      </div>
    </div>`;
  }).join('')}</div>`;
}

"""

set_mock_sort_needle = "function setMockSort(sortVal) {"
assert set_mock_sort_needle in code, "setMockSort not found"
code = code.replace(set_mock_sort_needle, helper_funcs + set_mock_sort_needle, 1)

# 4. In buildMockSortBar: Add Target Mocks pill to each pills group and add View Mode Switcher
# Add target pill to medium tab
code = code.replace(
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Medium (${list.length})</button>""",
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Medium (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>"""
)

# Add target pill to hard tab
code = code.replace(
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Hard (${list.length})</button>""",
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Hard (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>"""
)

# Add target pill to easy tab
code = code.replace(
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Easy (${list.length})</button>""",
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Easy (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>"""
)

# Add target pill to go tab
code = code.replace(
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All GO Tests (${list.length})</button>""",
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All GO Tests (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>"""
)

# Add target pill to made-easy tab
code = code.replace(
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Made Easy (${list.length})</button>""",
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Made Easy (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>"""
)

# Add target pill to all tab
code = code.replace(
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All (${list.length})</button>""",
    """<button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='pinned'?'active':''}" onclick="setMockSubSeries('pinned')">⭐ Target Mocks (${(state.pinnedMocks||new Set()).size})</button>"""
)

# Add View Mode Switcher next to Sort by in buildMockSortBar
sort_bar_needle = """        <div style="display:flex;align-items:center;gap:8px">

          <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>"""

sort_bar_repl = """        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">

          <div class="btn-group" style="display:inline-flex;border:1px solid var(--border);border-radius:6px;overflow:hidden">
            <button class="btn btn-sm ${state.mockViewMode==='compact'?'btn-secondary':'btn-primary'}" style="padding:4px 9px;font-size:12px" onclick="setMockViewMode('grid')" title="Detailed Grid View" type="button">⊞ Grid</button>
            <button class="btn btn-sm ${state.mockViewMode==='compact'?'btn-primary':'btn-secondary'}" style="padding:4px 9px;font-size:12px" onclick="setMockViewMode('compact')" title="Compact List View" type="button">☰ List</button>
          </div>

          <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>"""

assert sort_bar_needle in code, "sort_bar_needle not found"
code = code.replace(sort_bar_needle, sort_bar_repl, 1)

# 5. In buildMockGrid: compact check + card pin button + retake button
grid_top_needle = "function buildMockGrid(mocks){\n  if (!mocks.length) return '<div class=\"empty-state\"><div class=\"empty-state-icon\">📭</div><div class=\"empty-state-title\">No tests available for selected filter</div><div class=\"empty-state-sub\">Try selecting \"All\" or another tab.</div></div>';"
grid_top_repl = """function buildMockGrid(mocks){
  if (!mocks.length) return '<div class=\"empty-state\"><div class=\"empty-state-icon\">📭</div><div class=\"empty-state-title\">No tests available for selected filter</div><div class=\"empty-state-sub\">Try selecting \"All\" or another tab.</div></div>';

  if (state.mockViewMode === 'compact') {
    return buildMockCompactList(mocks);
  }"""

if grid_top_needle not in code:
    grid_top_needle = grid_top_needle.replace("\n", "\r\n")
    grid_top_repl = grid_top_repl.replace("\n", "\r\n")

assert grid_top_needle in code, "grid_top_needle not found"
code = code.replace(grid_top_needle, grid_top_repl, 1)

# Inside mock-card mapping: add isPinned
card_head_needle = """          <div style="display:flex;align-items:center;gap:6px">
            <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
            ${ratingBadge}
          </div>"""

card_head_repl = """          <div style="display:flex;align-items:center;gap:6px">
            <button class="mock-pin-btn ${state.pinnedMocks && state.pinnedMocks.has(m.id) ? 'pinned' : 'unpinned'}" onclick="togglePinMock('${m.id}', event)" title="${state.pinnedMocks && state.pinnedMocks.has(m.id) ? 'Unpin Mock' : 'Pin to Target Mocks'}" type="button">
              ${state.pinnedMocks && state.pinnedMocks.has(m.id) ? '⭐' : '☆'}
            </button>
            <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
            ${ratingBadge}
          </div>"""

assert card_head_needle in code, "card_head_needle not found"
code = code.replace(card_head_needle, card_head_repl, 1)

# Inside mock-card meta: add retake button
meta_best_needle = """${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}"""
meta_best_repl = """${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}
          ${past.length >= 2 ? `<button class="btn btn-secondary btn-sm" onclick="openMockRetakeCompare('${m.id}', event)" title="Compare your ${past.length} attempts" style="font-size:11px;padding:2px 7px;margin-left:4px" type="button">📊 Retakes (${past.length})</button>` : ''}"""

assert meta_best_needle in code, "meta_best_needle not found"
code = code.replace(meta_best_needle, meta_best_repl, 1)

# 6. Multi-token compound search in renderPractice
search_needle = """  if (state.practiceSearch && state.practiceSearch.trim()) {

    const term = state.practiceSearch.trim().toLowerCase();

    filtered = filtered.filter(q =>

      (q.question && q.question.toLowerCase().includes(term)) ||

      (q.topic && q.topic.toLowerCase().includes(term)) ||

      (q.subject && q.subject.toLowerCase().includes(term))

    );

  }"""

search_repl = """  if (state.practiceSearch && state.practiceSearch.trim()) {

    const pTerms = state.practiceSearch.trim().toLowerCase().split(/\\s+/).filter(Boolean);

    filtered = filtered.filter(q => {

      const hay = ((q.question || '') + ' ' + (q.subject || '') + ' ' + (q.topic || '') + ' ' + (q.explanation || '')).toLowerCase();

      return pTerms.every(t => hay.includes(t));

    });

  }"""

assert search_needle in code, "search_needle not found"
code = code.replace(search_needle, search_repl, 1)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("app.js successfully updated with all features!")
