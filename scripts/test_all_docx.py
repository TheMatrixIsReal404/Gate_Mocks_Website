# -*- coding: utf-8 -*-
import os
import sys
import io
from collections import Counter
from parse_docx_mock import parse_mock_docx

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

folder = r'c:\Users\sahu1\Downloads\GATE(Easy_to_Medium_Mocks)'
files = sorted([f for f in os.listdir(folder) if f.endswith('.docx')])

total_parsed = 0
all_questions = []

for f in files:
    path = os.path.join(folder, f)
    qs = parse_mock_docx(path)
    print(f"{f}: parsed {len(qs)} questions")
    assert len(qs) == 65, f"Expected 65 questions in {f}, got {len(qs)}"
    
    # Validate each question
    for q in qs:
        # Check type
        assert q['type'] in ('mcq', 'msq', 'nat')
        # Check text
        assert len(q['question'].strip()) > 5, f"Short question in {f} Q{q['q_num']}"
        # Check options
        if q['type'] in ('mcq', 'msq'):
            assert len(q['options']) == 4, f"Options != 4 in {f} Q{q['q_num']} (got {len(q['options'])})"
            for opt_idx, opt in enumerate(q['options']):
                assert len(opt.strip()) > 0, f"Empty option {opt_idx} in {f} Q{q['q_num']}"
            assert len(q['correct']) >= 1, f"No correct in {f} Q{q['q_num']}"
            for c in q['correct']:
                assert 0 <= c < 4, f"Invalid correct index {c} in {f} Q{q['q_num']}"
        elif q['type'] == 'nat':
            assert 'natRange' in q, f"No natRange in {f} Q{q['q_num']}"
            assert len(q['correct']) >= 1, f"No correct in NAT {f} Q{q['q_num']}"
        # Check explanation
        assert len(q['explanation'].strip()) > 5, f"Short explanation in {f} Q{q['q_num']}"
        
        all_questions.append((f, q))
    total_parsed += len(qs)

print(f"\nSUCCESS! All 10 files parsed cleanly: {total_parsed} questions validated.")

types = Counter(q['type'] for f, q in all_questions)
diffs = Counter(q['difficulty'] for f, q in all_questions)
subjs = Counter(q['subject'] for f, q in all_questions)

print("\nQuestion Types:", dict(types))
print("Difficulties:", dict(diffs))
print("Subjects:", dict(sorted(subjs.items())))
