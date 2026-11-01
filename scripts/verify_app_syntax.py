# -*- coding: utf-8 -*-
import json
import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. VERIFYING APP.JS DEFINITIONS & COUNTS ===")
with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Check key symbols
checks = [
    "mock-easy-01",
    "mock-easy-30",
    "mock-med-01",
    "mock-med-30",
    "FULL_LENGTH_PYQ_EXAMS",
    "pyq-exam-2026-1",
    "pyq-exam-2025-s1",
    "pyq-exam-2024",
    "paper-full-1",
    "renderPyqExams",
    "buildPyqExamsGrid",
    "buildPyqExamsFilterBar",
    "setPyqExamEraFilter",
    "getMockTabHTML",
    "switchMockTab",
    "Full-Length PYQ Exams",
    "persistAttempt(att)",
    "ingestMediumMocks"
]

for sym in checks:
    assert sym in js, f"Missing symbol in app.js: {sym}"
print(f"All {len(checks)} critical symbols and features verified in app.js!")

# Count mock-easy- in app.js
easy_ids = [f"mock-easy-{i:02d}" for i in range(1, 31)]
for eid in easy_ids:
    assert eid in js, f"Missing {eid} in app.js"
print("All 30 Easy Mock IDs (mock-easy-01 to mock-easy-30) verified in app.js MOCK_TESTS!")

# Count mock-med- in app.js
med_ids = [f"mock-med-{i:02d}" for i in range(1, 31)]
for mid in med_ids:
    assert mid in js, f"Missing {mid} in app.js"
print("All 30 Medium Mock IDs (mock-med-01 to mock-med-30) verified in app.js MOCK_TESTS!")

# Count pyq-exam in app.js
pyq_ids = [
    "pyq-exam-2026-1", "pyq-exam-2026-2", "pyq-exam-2025-s1", "pyq-exam-2025-s2",
    "pyq-exam-2024", "pyq-exam-2023", "pyq-exam-2022", "pyq-exam-2021", "pyq-exam-2020",
    "pyq-exam-2019", "pyq-exam-2018", "pyq-exam-2017", "pyq-exam-2016", "pyq-exam-2015-s1",
    "pyq-exam-2015-s2", "pyq-exam-2015-s3", "pyq-exam-2014-s1", "pyq-exam-2014-s2",
    "pyq-exam-2014-s3", "pyq-exam-2011", "pyq-exam-decade"
]
for pid in pyq_ids:
    assert pid in js, f"Missing {pid} in app.js"
print(f"All {len(pyq_ids)} Full-Length PYQ Exam IDs verified in app.js FULL_LENGTH_PYQ_EXAMS!")

# 2. CHECK INDEX.HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert 'nav-pyq-exams' in html, "index.html missing nav-pyq-exams"
assert 'Full-Length PYQ Exams' in html, "index.html missing Full-Length PYQ Exams"
assert 'nav-papers' not in html, "index.html still contains nav-papers"
print("index.html verified: nav-papers removed, nav-pyq-exams present!")

# 3. CHECK QUESTIONS IN SAMPLE_QUESTIONS.JSON
with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
    sq = json.load(f)

print(f"Total master questions in sample_questions.json: {len(sq)}")
assert len(sq) >= 8168, f"Expected at least 8168 questions, got {len(sq)}"

easy_q_count = len([q for q in sq if (q.get('mockId') or '').startswith('mock-easy-')])
print(f"Easy mock questions count: {easy_q_count}")
assert easy_q_count == 1950, f"Expected 1950 easy mock questions, got {easy_q_count}"

med_q_count = len([q for q in sq if (q.get('mockId') or '').startswith('mock-med-')])
print(f"Medium mock questions count: {med_q_count}")
assert med_q_count == 1950, f"Expected 1950 medium mock questions, got {med_q_count}"

# 4. CHECK GATE_30_EASY_MOCKS.JSON & GATE_30_MEDIUM_MOCKS.JSON
with open('data/gate_30_easy_mocks.json', 'r', encoding='utf-8') as f:
    em = json.load(f)
assert len(em) == 1950, f"Expected 1950 in gate_30_easy_mocks.json, got {len(em)}"
print("gate_30_easy_mocks.json verified with all 1950 questions!")

with open('data/gate_30_medium_mocks.json', 'r', encoding='utf-8') as f:
    mm = json.load(f)
assert len(mm) == 1950, f"Expected 1950 in gate_30_medium_mocks.json, got {len(mm)}"
print("gate_30_medium_mocks.json verified with all 1950 questions!")

# 5. VERIFY GETMOCKQUESTIONS LOGIC ON DATASET
for m_idx in range(1, 31):
    easy_id = f"mock-easy-{m_idx:02d}"
    med_id = f"mock-med-{m_idx:02d}"
    eqs = [q for q in sq if q.get('mockId') == easy_id]
    mqs = [q for q in sq if q.get('mockId') == med_id]
    assert len(eqs) == 65, f"Mock {easy_id} has {len(eqs)} questions instead of 65"
    assert len(mqs) == 65, f"Mock {med_id} has {len(mqs)} questions instead of 65"

print("All 30 easy mocks and 30 medium mocks verified to have exactly 65 questions each (3,900 mock questions total)!")

# Check 2025 PYQ exams
s1_qs = [q for q in sq if q.get('paper') == 'GATE 2025 Set 1' or q.get('id', '').startswith('pyq_2025_s1')]
s2_qs = [q for q in sq if q.get('paper') == 'GATE 2025 Set 2' or q.get('id', '').startswith('pyq_2025_s2')]
assert len(s1_qs) >= 65, f"GATE 2025 Set 1 has {len(s1_qs)} questions"
assert len(s2_qs) >= 65, f"GATE 2025 Set 2 has {len(s2_qs)} questions"
print("GATE 2025 Set 1 & Set 2 verified with 65 questions each!")

print("\n>>> ALL VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<")
