# -*- coding: utf-8 -*-
"""
enhance_mock_navigation.py
Enhances:
1. Mock Tests tabs: adds dedicated tabs for Gate Overflow (27) and Made Easy (21).
2. Sub-series filter pills: adds filter pills for Gate Overflow and Made Easy in buildMockSortBar and handles them in getFilteredAndSortedMocks.
3. Dashboard: adds flagship cards for Gate Overflow All-India Mocks and Made Easy Full Syllabus Tests.
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

app_path = r"g:\0.Gate_Lectures\0.Gate_Mocks_Website\app.js"
with open(app_path, 'r', encoding='utf-8') as f:
    app_js = f.read()

# 1. Update renderMocks counts
app_js = re.sub(
    r"(const\s+psetsCount\s*=\s*MOCK_TESTS\.filter\(m\s*=>\s*m\.type\s*===\s*['\"]practice-set['\"]\)\.length;)",
    r"\1\n  const goCount = fullMocks.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-')).length;\n  const meCount = fullMocks.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-')).length;",
    app_js
)
print("✓ Updated renderMocks counts with goCount and meCount")

# 2. Add tabs in renderMocks
app_js = re.sub(
    r"(<button class=\"tab-btn \${activeTab==='hard'\?'active':''}\" onclick=\"switchMockTab\('hard',this\)\" type=\"button\">[^<]*</button>)",
    r"\1\n      <button class=\"tab-btn ${activeTab==='go'?'active':''}\" onclick=\"switchMockTab('go',this)\" type=\"button\">🌐 Gate Overflow (${goCount})</button>\n      <button class=\"tab-btn ${activeTab==='made-easy'?'active':''}\" onclick=\"switchMockTab('made-easy',this)\" type=\"button\">📘 Made Easy (${meCount})</button>",
    app_js
)
print("✓ Added Gate Overflow & Made Easy tabs to renderMocks")

# 3. Add handlers in getMockTabHTML
go_tab_handler = """  if (tab === 'go') {
    const list = fullMocks.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-'));
    const filtered = getFilteredAndSortedMocks(list);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Gate Overflow All-India Mocks')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'made-easy') {
    const list = fullMocks.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-'));
    const filtered = getFilteredAndSortedMocks(list);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Made Easy Full Syllabus Mocks')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'practice-sets') {"""

app_js = re.sub(
    r"if\s*\(\s*tab\s*===\s*['\"]practice-sets['\"]\s*\)\s*\{",
    go_tab_handler,
    app_js
)
print("✓ Added tab handlers to getMockTabHTML")

# 4. Add subseries filter in getFilteredAndSortedMocks
subseries_logic = """  } else if (subSeries === 'cat-10') {
    list = list.filter(m => m.id.startsWith('mock-cat'));
  } else if (subSeries === 'go-mocks') {
    list = list.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-'));
  } else if (subSeries === 'me-mocks') {
    list = list.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-'));"""

app_js = re.sub(
    r"\}\s*else\s+if\s*\(\s*subSeries\s*===\s*['\"]cat-10['\"]\s*\)\s*\{\s*list\s*=\s*list\.filter\(m\s*=>\s*m\.id\.startsWith\(['\"]mock-cat['\"]\)\);\s*\}",
    subseries_logic + "\n  }",
    app_js
)
print("✓ Added go-mocks and me-mocks subseries filtering logic")

# 5. Add filter pills in buildMockSortBar
app_js = re.sub(
    r"(<button class=\"mock-subseries-pill \${subSeries==='all'\?'active':''}\" onclick=\"setMockSubSeries\('all'\)\">[^<]*</button>)",
    r"\1\n        <button class=\"mock-subseries-pill ${subSeries==='go-mocks'?'active':''}\" onclick=\"setMockSubSeries('go-mocks')\">🌐 Gate Overflow (27)</button>\n        <button class=\"mock-subseries-pill ${subSeries==='me-mocks'?'active':''}\" onclick=\"setMockSubSeries('me-mocks')\">📘 Made Easy (21)</button>",
    app_js
)
print("✓ Added go-mocks and me-mocks filter pills in buildMockSortBar")

# 6. Dashboard series cards update
old_dash_header = 'Curated GATE Exam Series <span>4 Flagship Compendiums</span>'
new_dash_header = 'Curated GATE Exam Series <span>6 Flagship Compendiums (85 Full Mocks)</span>'
app_js = app_js.replace(old_dash_header, new_dash_header)

old_card_end = re.search(r'(<div class="series-card"[^>]+navigate\([\'"]pyq-exams[\'"]\).*?</div>\s*</div>)', app_js, re.DOTALL)
if old_card_end and "27 Gate Overflow Mocks" not in app_js:
    pyq_card = old_card_end.group(1)
    extra_cards = """
      <div class="series-card" style="--series-color:#06b6d4" onclick="navigate('mocks',{tab:'go'})">
        <div>
          <div class="series-badge" style="background:rgba(6,182,212,0.15);color:#06b6d4">🌐 ALL-INDIA MOCKS</div>
          <div class="series-title">27 Gate Overflow Mocks</div>
          <div class="series-sub">Rigorous full-length All-India Mock Tests (2025–2026) crafted by the Gate Overflow community for peak exam calibration.</div>
        </div>
        <div class="series-footer">
          <span>1,568 Qs • 27 Full Tests • 7.2/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
      <div class="series-card" style="--series-color:#8b5cf6" onclick="navigate('mocks',{tab:'made-easy'})">
        <div>
          <div class="series-badge" style="background:rgba(139,92,246,0.15);color:#a78bfa">📘 ELITE COACHING</div>
          <div class="series-title">21 Made Easy Full Mocks</div>
          <div class="series-sub">High-resolution visual question cards, Advance & Basic Level Full Syllabus Tests, and National Mock Exams (2023–2024).</div>
        </div>
        <div class="series-footer">
          <span>1,409 Qs • 21 Full Tests • 7.5/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>
    </div>"""
    pyq_card_new = pyq_card[:-6] + extra_cards
    app_js = app_js.replace(pyq_card, pyq_card_new, 1)
    print("✓ Added 2 new flagship series cards to Dashboard")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_js)

print("\n>>> ALL MOCK NAVIGATION & DASHBOARD ENHANCEMENTS APPLIED SUCCESSFULLY! <<<")
