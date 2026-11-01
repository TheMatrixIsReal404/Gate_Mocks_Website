# -*- coding: utf-8 -*-
"""
Script to apply rigorous difficulty ratings (Medium vs Hard) to all 20 Full-Length Mocks
in app.js, data/gate_20_full_mocks.json, data/sample_questions.json, and mocks.md.
"""

import os
import sys
import json
import re

MOCK_RATINGS = {
    1:  {'rating': 4.5, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '31-33', 'air100': '74-78', 'desc': 'Foundational-to-standard baseline paper with clean arithmetic bounds, classic cache and pipelining parameters, and standard scoring problems.'},
    2:  {'rating': 5.0, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '30-32', 'air100': '73-77', 'desc': 'Standard GATE difficulty featuring Peirce’s law, modulo 13 exponentiation, 4-element derangements, and 10-vertex planar graph faces.'},
    3:  {'rating': 5.5, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '29-31', 'air100': '72-76', 'desc': 'Standard GATE paper testing 5-iteration fork() trees (31 children), modulo 17 arithmetic, and 4-way set-associative cache tags.'},
    4:  {'rating': 5.4, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '29-31', 'air100': '72-76', 'desc': 'Standard GATE simulation covering self-dual Boolean functions (256), modulo 19 arithmetic, and sliding-window DFA state construction.'},
    5:  {'rating': 5.2, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '30-32', 'air100': '73-77', 'desc': 'Standard GATE paper testing modulo 23 modular arithmetic, 3-ary tree leaf invariants (47 leaves), and 4-to-1 MUX Shannon expansions.'},
    6:  {'rating': 5.8, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '28-30', 'air100': '71-75', 'desc': 'Standard-Plus GATE paper testing modulo 29 exponentiation, 18-vertex planar graphs, cyclic K-maps, and cascaded counter frequency division.'},
    7:  {'rating': 5.6, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '28-30', 'air100': '71-75', 'desc': 'Standard-Plus paper with modulo 31 arithmetic, 20-vertex planar graph faces, 8-element surjections (5,796), and TCP congestion milestones.'},
    8:  {'rating': 6.0, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '27-29', 'air100': '70-74', 'desc': 'Upper-Standard GATE paper featuring modulo 37 exponentiation, 22-vertex planar graphs, 7-element derangements (1,855), and 280ms TCP windows.'},
    9:  {'rating': 6.1, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '27-29', 'air100': '70-74', 'desc': 'Upper-Standard paper with modulo 41 arithmetic, 24-vertex planar graphs, 5-variable directed FD cycles, and 32.0% sliding window utilization.'},
    10: {'rating': 5.9, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '28-30', 'air100': '71-75', 'desc': 'Balanced Standard GATE paper testing modulo 43 arithmetic, 26-vertex planar graphs, cyclic candidate keys, and 180 Cayley trace calculations.'},
    11: {'rating': 6.8, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '25-27', 'air100': '66-70', 'desc': 'Advanced Rank Booster featuring modulo 47 arithmetic, 28-vertex planar graphs, 141-leaf 5-ary trees, and 330ms TCP slow-start calculations.'},
    12: {'rating': 7.5, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '24-26', 'air100': '65-69', 'desc': 'Advanced Rank Booster testing modulo 53 exponentiation, 30-vertex planar graphs, 186-leaf 6-ary trees, and 420ms TCP congestion windows.'},
    13: {'rating': 7.0, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '25-27', 'air100': '66-70', 'desc': 'Advanced Rank Booster with modulo 59 arithmetic, 32-vertex planar graphs, 8-element BST postorder reconstructions, and 270 Cayley trace.'},
    14: {'rating': 7.4, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '24-26', 'air100': '65-69', 'desc': 'Advanced Rank Booster testing modulo 61 exponentiation, 34-vertex planar graphs, 8-fragment IPv4 splitting, 304 trace, and 25% DMA overhead.'},
    15: {'rating': 8.0, 'level': 'hard',   'title_tier': 'High Difficulty',     'cutoff': '23-25', 'air100': '63-67', 'desc': 'High Difficulty Rank Booster with modulo 67 arithmetic, 36-vertex planar graphs, 173-leaf 5-ary trees, and 144,000-cost matrix chains.'},
    16: {'rating': 7.8, 'level': 'hard',   'title_tier': 'High Difficulty',     'cutoff': '23-25', 'air100': '63-67', 'desc': 'High Difficulty paper testing modulo 71 exponentiation, 38-vertex planar graphs, 226-leaf 6-ary trees, 6th-symbol DFA (64 states), and 378 trace.'},
    17: {'rating': 7.9, 'level': 'hard',   'title_tier': 'High Difficulty',     'cutoff': '23-25', 'air100': '63-67', 'desc': 'High Difficulty paper with modulo 73 exponentiation, 40-vertex planar graphs, 164ns paging EMAT, 418 trace, and 15% DMA cycle stealing.'},
    18: {'rating': 8.4, 'level': 'hard',   'title_tier': 'Advanced Hard',       'cutoff': '22-24', 'air100': '62-66', 'desc': 'Advanced Hard paper featuring modulo 79 exponentiation, 42-vertex planar graphs, 148-leaf 4-ary trees, 6-bit Kernighan loop, and 460 trace.'},
    19: {'rating': 8.6, 'level': 'hard',   'title_tier': 'Advanced Hard',       'cutoff': '21-23', 'air100': '60-65', 'desc': 'Advanced Hard paper with modulo 83 exponentiation, 44-vertex planar graphs, 205-leaf 5-ary trees, 504 IPv4 offset, and 504 Cayley trace.'},
    20: {'rating': 9.2, 'level': 'hard',   'title_tier': 'Capstone Challenge', 'cutoff': '20-22', 'air100': '58-63', 'desc': 'Capstone Challenge mock exam featuring modulo 89 exponentiation, 46-vertex planar graphs, 266-leaf 6-ary trees, 6th-symbol DFA (64 states), and 550 trace.'}
}

# 1. Update data/gate_20_full_mocks.json and data/sample_questions.json
with open('data/gate_20_full_mocks.json', 'r', encoding='utf-8') as f:
    mocks_qs = json.load(f)

for q in mocks_qs:
    m_num = int(q['mockId'].replace('mock-flm-', ''))
    cfg = MOCK_RATINGS[m_num]
    paper_name = f"GATE CS Full Mock Exam #{m_num:02d} ({cfg['title_tier']} — Rating: {cfg['rating']}/10)"
    q['paper'] = paper_name
    
    # Adjust question level difficulty
    if cfg['level'] == 'medium':
        q['difficulty'] = 'easy' if q['marks'] == 1 else 'medium'
    else:
        q['difficulty'] = 'medium' if q['marks'] == 1 else 'hard'

with open('data/gate_20_full_mocks.json', 'w', encoding='utf-8') as f:
    json.dump(mocks_qs, f, indent=2, ensure_ascii=False)
print("Updated data/gate_20_full_mocks.json")

# Update sample_questions.json
with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
    sq = json.load(f)

sq_filtered = [q for q in sq if not (q.get('mockId') or '').startswith('mock-flm-')]
sq_merged = sq_filtered + mocks_qs

with open('data/sample_questions.json', 'w', encoding='utf-8') as f:
    json.dump(sq_merged, f, indent=2, ensure_ascii=False)
print(f"Updated data/sample_questions.json ({len(sq_merged)} total questions)")

# 2. Update app.js
app_js_path = 'app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace MOCK_TESTS entries for mock-flm-
old_flm_pattern = r'  // ─── 20 FULL-LENGTH GATE CS MOCK EXAMS \(Compendium Series\) ───.*?  // ─── SUBJECT-WISE MOCKS'
new_mocks_code = "  // ─── 20 FULL-LENGTH GATE CS MOCK EXAMS (Compendium Series) ─────────────────\n"
for i in range(1, 21):
    cfg = MOCK_RATINGS[i]
    new_mocks_code += f"""  {{
    id: 'mock-flm-{i:02d}',
    type: 'full',
    difficulty: '{cfg['level']}',
    name: 'GATE CS Full Mock Exam #{i:02d} ({cfg['title_tier']} — Rating: {cfg['rating']}/10)',
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: 'Mock #{i:02d} [{cfg['title_tier']} | Rating: {cfg['rating']}/10 | Est. Cutoff: {cfg['cutoff']}M]: {cfg['desc']}'
  }},\n"""
new_mocks_code += "\n  // ─── SUBJECT-WISE MOCKS"

code = re.sub(old_flm_pattern, new_mocks_code, code, flags=re.DOTALL)

# Replace PRACTICE_PAPERS entries for paper-flm-
old_papers_pattern = r'  // ─── 20 FULL-LENGTH GATE CS PRACTICE PAPERS ───.*?(?=\{ id:\'paper-gate-2021\')'
new_papers_code = "  // ─── 20 FULL-LENGTH GATE CS PRACTICE PAPERS ───────────────────────────────\n"
for i in range(1, 21):
    cfg = MOCK_RATINGS[i]
    new_papers_code += f"""  {{ id:'paper-flm-{i:02d}', mockId:'mock-flm-{i:02d}', name:'GATE CS Full Mock Exam #{i:02d} ({cfg['title_tier']} — Rating: {cfg['rating']}/10)', type:'full', questions:65, marks:100, desc:'Full Mock Paper #{i:02d} [{cfg['title_tier']} | Rating: {cfg['rating']}/10 | Est. Cutoff: {cfg['cutoff']}M]: {cfg['desc']}' }},\n"""
new_papers_code += "\n  "

code = re.sub(old_papers_pattern, new_papers_code, code, flags=re.DOTALL)

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated app.js with calibrated ratings and titles")

print("All files updated successfully!")
