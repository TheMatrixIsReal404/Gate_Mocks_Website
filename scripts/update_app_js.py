# -*- coding: utf-8 -*-
import sys, re

app_js_path = r"g:\0.Gate_Lectures\0.Gate_Mocks_Website\app.js"

with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Generate MOCK_TESTS entries for the 20 Full-Length Mocks
flm_mocks_code = "  // ─── 20 FULL-LENGTH GATE CS MOCK EXAMS (Compendium Series) ─────────────────\n"
for i in range(1, 21):
    diff = 'medium' if i <= 14 else 'hard'
    lvl_label = "Standard GATE Exam" if i <= 14 else "Advanced Rank Booster"
    flm_mocks_code += f"""  {{
    id: 'mock-flm-{i:02d}',
    type: 'full',
    difficulty: '{diff}',
    name: 'GATE CS Full-Length Mock Exam #{i:02d}',
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: 'Mock #{i:02d} ({lvl_label}): Official IISc/IIT pattern mock exam containing 65 questions (10 General Aptitude + 55 Core CS) across all 13 subjects with complete step-by-step derivations.'
  }},\n"""

# Insert before '// ─── SUBJECT-WISE MOCKS'
if 'mock-flm-01' not in content:
    target = "  // ─── SUBJECT-WISE MOCKS ──────────────────────────────────────────────────"
    assert target in content, "Target comment for MOCK_TESTS not found"
    content = content.replace(target, flm_mocks_code + "\n" + target, 1)
    print("Added 20 mock tests to MOCK_TESTS")
else:
    print("Mocks already in MOCK_TESTS, skipping")

# 2. Generate PRACTICE_PAPERS entries for the 20 Full-Length Mocks
flm_papers_code = "  // ─── 20 FULL-LENGTH GATE CS PRACTICE PAPERS ───────────────────────────────\n"
for i in range(1, 21):
    flm_papers_code += f"""  {{ id:'paper-flm-{i:02d}', mockId:'mock-flm-{i:02d}', name:'GATE CS Full Mock Exam #{i:02d}', type:'full', questions:65, marks:100, desc:'Full-Length Mock Paper #{i:02d}: Complete 65-question paper (10 GA + 55 Core CS) with detailed step-by-step mathematical solutions.' }},\n"""

# Insert after paper-cat2-set5
if 'paper-flm-01' not in content:
    target_p = "{ id:'paper-cat2-set5', mockId:'mock-cat2-set5', name:'GATE CSE Practice Paper (Cat 2 — Set 5)', type:'full', questions:65, marks:100, desc:'Category 2 Set 5: Advanced mock paper with 25 rank-boosting numerical and conceptual questions (Rating: 5.5/10).' },"
    assert target_p in content, "Target paper-cat2-set5 not found"
    content = content.replace(target_p, target_p + "\n\n" + flm_papers_code, 1)
    print("Added 20 practice papers to PRACTICE_PAPERS")
else:
    print("Papers already in PRACTICE_PAPERS, skipping")

# 3. Update getMockQuestions to handle paper-flm
old_target_mock_id = "const targetMockId = mockId.startsWith('paper-cat') ? mockId.replace('paper-', 'mock-') : mockId;"
new_target_mock_id = "const targetMockId = (mockId.startsWith('paper-cat') || mockId.startsWith('paper-flm')) ? mockId.replace('paper-', 'mock-') : mockId;"

if old_target_mock_id in content:
    content = content.replace(old_target_mock_id, new_target_mock_id, 1)
    print("Updated targetMockId in getMockQuestions")

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"app.js updated successfully! New file size: {len(content)} characters.")
