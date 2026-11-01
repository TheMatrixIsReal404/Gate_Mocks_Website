# -*- coding: utf-8 -*-
import re

# ─────────────────────────────────────────────────────────────────────────────
# 1. UPDATE APP.JS
# ─────────────────────────────────────────────────────────────────────────────
with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix getFilteredAndSortedMocks
old_filter_sort_pat = r'function getFilteredAndSortedMocks\(fullMocks\) \{[\s\S]*?return list;\r?\n\}'
new_filter_sort = '''function getFilteredAndSortedMocks(mockList) {
  const currentSort = state.mockSort || 'default';
  let list = (mockList || []).slice();

  const diffRank = { 'easy': 1, 'medium': 2, 'hard': 3 };

  if (currentSort === 'easy-first') {
    list.sort((a, b) => {
      const da = diffRank[a.difficulty] || 2;
      const db = diffRank[b.difficulty] || 2;
      if (da !== db) return da - db;
      return (a.rating || 5) - (b.rating || 5);
    });
  } else if (currentSort === 'hard-first') {
    list.sort((a, b) => {
      const da = diffRank[a.difficulty] || 2;
      const db = diffRank[b.difficulty] || 2;
      if (da !== db) return db - da;
      return (b.rating || 5) - (a.rating || 5);
    });
  } else if (currentSort === 'rating-desc') {
    list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
  } else if (currentSort === 'rating-asc') {
    list.sort((a, b) => (a.rating || 0) - (b.rating || 0));
  } else if (currentSort === 'name-asc') {
    list.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' }));
  }

  return list;
}'''

assert re.search(old_filter_sort_pat, code), "Could not find getFilteredAndSortedMocks in app.js"
code = re.sub(old_filter_sort_pat, new_filter_sort, code, count=1)
print("✅ 1. getFilteredAndSortedMocks updated.")

# Fix setMockSort and toggleCalibrationTable
old_set_mock_sort_pat = r'function setMockSort\(sortVal\) \{[\s\S]*?renderMath\(c\);\r?\n  \}\r?\n\}'
new_set_mock_sort = '''function setMockSort(sortVal) {
  state.mockSort = sortVal;
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}'''

assert re.search(old_set_mock_sort_pat, code), "Could not find setMockSort in app.js"
code = re.sub(old_set_mock_sort_pat, new_set_mock_sort, code, count=1)
print("✅ 2. setMockSort updated.")

old_toggle_cal_pat = r'function toggleCalibrationTable\(\) \{[\s\S]*?renderMath\(c\);\r?\n  \}\r?\n\}'
new_toggle_cal = '''function toggleCalibrationTable() {
  state.showCalibrationTable = !state.showCalibrationTable;
  const c = document.getElementById('mock-tab-content');
  if (c) {
    const tab = state.mockTab || 'all';
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
    c.innerHTML = getMockTabHTML(tab, fullMocks);
    renderMath(c);
  }
}'''

assert re.search(old_toggle_cal_pat, code), "Could not find toggleCalibrationTable in app.js"
code = re.sub(old_toggle_cal_pat, new_toggle_cal, code, count=1)
print("✅ 3. toggleCalibrationTable updated.")

# Fix switchMockTab to guarantee active class toggling and re-render
old_switch_tab_pat = r'function switchMockTab\(tab, btn\)\{[\s\S]*?renderMath\(c\);\r?\n\}'
new_switch_tab = '''function switchMockTab(tab, btn){
  state.mockTab = tab;
  document.querySelectorAll('#mock-tabs .tab-btn').forEach(b => {
    const isTarget = btn ? (b === btn) : (b.getAttribute('onclick') || '').includes(`'${tab}'`);
    b.classList.toggle('active', !!isTarget);
  });
  const c = document.getElementById('mock-tab-content');
  if (!c) return;
  const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
  c.innerHTML = getMockTabHTML(tab, fullMocks);
  renderMath(c);
}'''

assert re.search(old_switch_tab_pat, code), "Could not find switchMockTab in app.js"
code = re.sub(old_switch_tab_pat, new_switch_tab, code, count=1)
print("✅ 4. switchMockTab updated.")

# Write updated app.js
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)
print("🎉 app.js written successfully!")

# ─────────────────────────────────────────────────────────────────────────────
# 2. UPDATE STYLE.CSS FOR .CHIP.ACTIVE AND FILTER INTERACTION
# ─────────────────────────────────────────────────────────────────────────────
with open('style.css', 'r', encoding='utf-8') as f:
    css = f.read()

old_chip_css = '''.chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}'''

new_chip_css = '''.chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.chip:hover {
  border-color: var(--accent);
  color: var(--text-primary);
  background: var(--bg-card-hover);
}
.chip.active {
  background: var(--accent) !important;
  color: #ffffff !important;
  border-color: var(--accent) !important;
  box-shadow: 0 0 12px rgba(108, 99, 255, 0.4);
}'''

if old_chip_css in css:
    css = css.replace(old_chip_css, new_chip_css, 1)
    with open('style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("✅ 5. style.css updated with active chip styles.")
else:
    print("ℹ️ style.css chip style already modified.")

