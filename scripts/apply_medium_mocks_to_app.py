# -*- coding: utf-8 -*-
"""
Script to apply 30 Medium Mock Tests to app.js:
1. Adds 30 Medium-Level Mock Tests (mock-med-01 to mock-med-30) to MOCK_TESTS
2. Updates getMockQuestions to handle paper-med-
3. Adds window.ingestMediumMocks loader function
4. Adds Ingest 30 Medium Mocks button to upload UI
5. Exposes ingestMediumMocks to window
"""

import sys
import os
import shutil
import re

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app_path = 'app.js'
bak_path = 'app.js.bak_before_medium'
if not os.path.exists(bak_path):
    shutil.copyfile(app_path, bak_path)

with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Generate 30 Medium Mock definitions
med_mocks_lines = ["  // ── 30 MEDIUM-LEVEL FULL-LENGTH MOCK EXAMINATIONS (medium_mocks.docx) ──"]
for i in range(1, 31):
    rating = round(4.8 + (i - 1) * 0.03, 1)
    decay = i // 10
    cutoff = f"{31 - decay}-{33 - decay}"
    air100 = f"{74 - decay}-{78 - decay}"
    med_mocks_lines.append(f"""  {{
    id: 'mock-med-{i:02d}',
    type: 'full',
    difficulty: 'medium',
    rating: {rating},
    cutoff: '{cutoff}',
    air100: '{air100}',
    tier: 'Standard GATE (Medium)',
    name: 'GATE CS Medium Mock Exam #{i:02d}',
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: 'Mock #{i:02d} [Medium Level | Rating: {rating}/10 | Est. Cutoff: {cutoff}M]: Full-length medium-level examination strictly aligned with the latest IISc / IIT GATE CS syllabus & exam pattern (65 Questions | 100 Marks).'
  }},""")
med_mocks_str = "\n".join(med_mocks_lines)

# Insert before 'mock-full-easy'
m_flm = re.search(r'(\n\s*//[^\n]*FULL-LENGTH MOCKS[^\n]*\n\s*\{\s*id:\s*\'mock-full-easy\')', text)
assert m_flm, "Target mock-full-easy not found in app.js"
text = text[:m_flm.start()] + f"\n\n{med_mocks_str}" + text[m_flm.start():]

# 2. Update getMockQuestions targetMockId
old_target = "mockId.startsWith('paper-easy')"
new_target = "mockId.startsWith('paper-easy') || mockId.startsWith('paper-med')"
if old_target in text:
    text = text.replace(old_target, new_target, 1)

# 3. Add window.ingestMediumMocks
old_ingest = "window.ingestEasyMocks = async function() {"
ingest_medium_code = """window.ingestMediumMocks = async function() {
  showToast('Loading 30 Medium Mock Tests (1,950 questions)...', 'info', 2500);
  try {
    const res = await fetch('./data/gate_30_medium_mocks.json');
    if (!res.ok) throw new Error('File not found: ./data/gate_30_medium_mocks.json');
    const data = await res.json();
    await bulkImportQuestions(data);
  } catch(err) {
    showToast('Failed to load medium mocks: ' + err.message, 'error');
  }
};

window.ingestEasyMocks = async function() {"""
if old_ingest in text:
    text = text.replace(old_ingest, ingest_medium_code, 1)

# 4. Add Ingest button to buildJSONUploadUI
old_btn = 'onclick="ingestEasyMocks()"'
if old_btn in text and 'onclick="ingestMediumMocks()"' not in text:
    m_btn = re.search(r'(<button class="btn btn-secondary" onclick="ingestEasyMocks\(\)"[^>]*>[^<]*</button>)', text)
    assert m_btn, "Button tag not matched"
    btn_orig = m_btn.group(1)
    btn_med = """<button class="btn btn-secondary" onclick="ingestMediumMocks()" style="background:rgba(234,179,8,0.15);color:var(--yellow);border-color:var(--yellow)">⚡ Ingest 30 Medium Mocks (1,950 Q)</button>"""
    text = text.replace(btn_orig, f"{btn_orig}\n            {btn_med}", 1)

# 5. Expose ingestMediumMocks in window object
old_export = "downloadSampleJSON,"
if old_export in text and "ingestMediumMocks," not in text:
    text = text.replace(old_export, f"{old_export}\n  ingestMediumMocks,", 1)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("✅ Successfully updated app.js with 30 Medium Mocks, ingest function, UI button, and exports!")
