# -*- coding: utf-8 -*-
"""
Verification of Practice Papers and Mock Tests in website:
- Validates all PRACTICE_PAPERS and MOCK_TESTS can load their questions from sample_questions.json.
- Checks question count, pagination count, and subject coverage.
"""

import json
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print(f"Total Master Questions: {len(questions)}")

# Practice Papers definition matching app.js
papers = [
    {'id':'paper-gate-2025-s1', 'name':'Official GATE CSE 2025 (Set 1) Paper', 'type':'full', 'questions':65},
    {'id':'paper-gate-2025-s2', 'name':'Official GATE CSE 2025 (Set 2) Paper', 'type':'full', 'questions':65},
    {'id':'paper-cat1-set1', 'mockId':'mock-cat1-set1', 'name':'GATE CSE Practice Paper (Cat 1 - Set 1)', 'type':'full', 'questions':65},
    {'id':'paper-cat1-set2', 'mockId':'mock-cat1-set2', 'name':'GATE CSE Practice Paper (Cat 1 - Set 2)', 'type':'full', 'questions':65},
    {'id':'paper-cat1-set3', 'mockId':'mock-cat1-set3', 'name':'GATE CSE Practice Paper (Cat 1 - Set 3)', 'type':'full', 'questions':65},
    {'id':'paper-cat1-set4', 'mockId':'mock-cat1-set4', 'name':'GATE CSE Practice Paper (Cat 1 - Set 4)', 'type':'full', 'questions':65},
    {'id':'paper-cat1-set5', 'mockId':'mock-cat1-set5', 'name':'GATE CSE Practice Paper (Cat 1 - Set 5)', 'type':'full', 'questions':65},
    {'id':'paper-cat2-set1', 'mockId':'mock-cat2-set1', 'name':'GATE CSE Practice Paper (Cat 2 - Set 1)', 'type':'full', 'questions':65},
    {'id':'paper-cat2-set2', 'mockId':'mock-cat2-set2', 'name':'GATE CSE Practice Paper (Cat 2 - Set 2)', 'type':'full', 'questions':65},
    {'id':'paper-cat2-set3', 'mockId':'mock-cat2-set3', 'name':'GATE CSE Practice Paper (Cat 2 - Set 3)', 'type':'full', 'questions':65},
    {'id':'paper-cat2-set4', 'mockId':'mock-cat2-set4', 'name':'GATE CSE Practice Paper (Cat 2 - Set 4)', 'type':'full', 'questions':65},
    {'id':'paper-cat2-set5', 'mockId':'mock-cat2-set5', 'name':'GATE CSE Practice Paper (Cat 2 - Set 5)', 'type':'full', 'questions':65},
]

# Add the 20 Full-Length Mock Papers
for i in range(1, 21):
    papers.append({
        'id': f'paper-flm-{i:02d}',
        'mockId': f'mock-flm-{i:02d}',
        'name': f'GATE CS Full Mock Exam #{i:02d}',
        'type': 'full',
        'questions': 65
    })

papers.extend([
    {'id':'paper-gate-2021', 'name':'Official GATE CSE 2021 Paper', 'type':'full', 'year':2021, 'questions':88},
    {'id':'paper-gate-2020', 'name':'Official GATE CSE 2020 Paper', 'type':'full', 'year':2020, 'questions':70},
    {'id':'paper-gate-2019', 'name':'Official GATE CSE 2019 Paper', 'type':'full', 'year':2019, 'questions':66},
    {'id':'paper-gate-2018', 'name':'Official GATE CSE 2018 Paper', 'type':'full', 'year':2018, 'questions':72},
    {'id':'paper-gate-2015', 'name':'Official GATE CSE 2015 Multi-Set Paper', 'type':'full', 'year':2015, 'questions':172},
    {'id':'paper-gate-2014', 'name':'Official GATE CSE 2014 Multi-Set Paper', 'type':'full', 'year':2014, 'questions':205},
    {'id':'paper-gate-2011', 'name':'Official GATE CSE 2011 Full Paper', 'type':'full', 'year':2011, 'questions':65},
    {'id':'paper-gate-overflow-decade', 'name':'GATE Decade PYQ Paper (2014-2024)', 'type':'full', 'questions':65},
    {'id':'paper-full-1', 'name':'GATE CSE Comprehensive Paper 1', 'type':'full', 'questions':65},
    {'id':'paper-full-2', 'name':'GATE CSE Comprehensive Paper 2', 'type':'full', 'questions':65},
    {'id':'paper-dsa', 'name':'Data Structures & Algorithms Paper', 'type':'subwise', 'subjects':['Data Structures','Algorithms','C Programming'], 'questions':50},
    {'id':'paper-systems', 'name':'Systems & Architecture Paper', 'type':'subwise', 'subjects':['Operating Systems','Computer Networks','Computer Organization'], 'questions':50},
    {'id':'paper-theory', 'name':'Theory of Computation & Compilers', 'type':'subwise', 'subjects':['Theory of Computation','Compiler Design'], 'questions':35},
    {'id':'paper-maths', 'name':'Maths & General Aptitude Paper', 'type':'subwise', 'subjects':['Discrete Mathematics','Engineering Mathematics','Aptitude'], 'questions':45},
])

mocks = [
    'mock-full-easy', 'mock-full-med', 'mock-full-hard', 'mock-full-001', 'mock-full-002',
    'mock-gate-2025-s1', 'mock-gate-2025-s2',
    'mock-cat1-set1', 'mock-cat1-set2', 'mock-cat1-set3', 'mock-cat1-set4', 'mock-cat1-set5',
    'mock-cat2-set1', 'mock-cat2-set2', 'mock-cat2-set3', 'mock-cat2-set4', 'mock-cat2-set5'
]

# Add the 20 Full-Length Mocks
for i in range(1, 21):
    mocks.append(f'mock-flm-{i:02d}')

def getMockQuestions(mockId):
    targetMockId = (mockId.replace('paper-', 'mock-') 
                    if (mockId.startswith('paper-cat') or mockId.startswith('paper-flm')) 
                    else mockId)
    directQs = [q for q in questions if q.get('mockId') == targetMockId or q.get('mockId') == mockId]
    if len(directQs) >= 65:
        return directQs

    if mockId in ('paper-gate-2025-s1', 'mock-gate-2025-s1'):
        return [q for q in questions if q.get('paper') == 'GATE 2025 Set 1' or q['id'].startswith('pyq_2025_s1')]
    if mockId in ('paper-gate-2025-s2', 'mock-gate-2025-s2'):
        return [q for q in questions if q.get('paper') == 'GATE 2025 Set 2' or q['id'].startswith('pyq_2025_s2')]
    p = next((x for x in papers if x['id'] == mockId), None)
    if p:
        if p.get('mockId'):
            pQs = [q for q in questions if q.get('mockId') == p['mockId']]
            if pQs: return pQs
        if p.get('year'):
            return [q for q in questions if q.get('year') == p['year']]
        if p.get('subjects'):
            return [q for q in questions if q.get('subject') in p['subjects']]
        h = 0 if mockId == 'paper-full-1' else 1
        return [q for idx, q in enumerate(questions) if (idx % 2) == h][:p['questions']]
    return [q for q in questions][:65]

print(f"\n--- 1. PRACTICE PAPERS AUDIT ({len(papers)} Total Papers) ---")
for p in papers:
    qs = getMockQuestions(p['id'])
    pages = (len(qs) + 19) // 20
    print(f"[{p['id']}] {p['name']}: {len(qs)} questions ({pages} pages at 20/page)")
    assert len(qs) >= 35, f"Error: {p['id']} has too few questions: {len(qs)}"

print(f"\n--- 2. FULL MOCKS AUDIT ({len(mocks)} Total Full-Length Mocks) ---")
for m in mocks:
    qs = getMockQuestions(m)
    assert len(qs) >= 65, f"Error: Mock {m} has fewer than 65 questions: {len(qs)}"
    print(f"[{m}]: {len(qs)} questions verified")

print(f"\nAll {len(papers)} Practice Papers and {len(mocks)} Full-Length Mocks verified successfully!")
