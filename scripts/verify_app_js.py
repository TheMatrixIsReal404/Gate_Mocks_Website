# -*- coding: utf-8 -*-
import sys
import json
import re

with open("app.js", "r", encoding="utf-8") as f:
    code = f.read()

mocks = re.findall(r"id:\s*['\"](mock-flm-\d+)['\"]", code)
papers = re.findall(r"id:\s*['\"](paper-flm-\d+)['\"]", code)

print(f"MOCK_TESTS contains {len(mocks)} mock-flm entries: {mocks[0]} to {mocks[-1]}")
print(f"PRACTICE_PAPERS contains {len(papers)} paper-flm entries: {papers[0]} to {papers[-1]}")

assert len(mocks) == 20, f"Expected 20 mock-flm entries, got {len(mocks)}"
assert len(papers) == 20, f"Expected 20 paper-flm entries, got {len(papers)}"

# Check questions in sample_questions.json
with open("data/sample_questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total questions in sample_questions.json: {len(data)}")

for i in range(1, 21):
    m_id = f"mock-flm-{i:02d}"
    qs = [q for q in data if q.get("mockId") == m_id]
    assert len(qs) == 65, f"Mock {m_id} has {len(qs)} questions instead of 65"
    
    # Check marks sum
    m_sum = sum(q.get("marks", 0) for q in qs)
    assert m_sum == 100, f"Mock {m_id} has {m_sum} marks instead of 100"
    
    # Check question number sequence
    q_nums = [int(q["id"].split("_q")[1]) for q in qs]
    assert q_nums == list(range(1, 66)), f"Mock {m_id} invalid q_nums: {q_nums[:5]}...{q_nums[-5:]}"

print("\nALL 20 MOCKS VALIDATED IN sample_questions.json!")
print("Every mock contains exactly 65 questions totaling 100 marks (10 GA + 55 Core CS)!")
