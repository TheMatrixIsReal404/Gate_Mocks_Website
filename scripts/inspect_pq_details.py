# -*- coding: utf-8 -*-
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('previous_questions.json', 'r', encoding='utf-8') as f:
    pq = json.load(f)

print("--- Inspecting pyq_2008_cs41, pyq_2008_cs42, pyq_2009_cs15, pyq_2021_CS1_ga02 ---")
for q in pq:
    if q['id'] in ['pyq_2008_cs41', 'pyq_2008_cs42', 'pyq_2009_cs15', 'pyq_2021_CS1_ga02']:
        print("ID:", q['id'])
        print("Year:", q.get('year'), "Subject:", q.get('subject'))
        print("Question:", repr(q.get('question')))
        print("Options:", q.get('options'))
        print("Correct:", q.get('correct'))
        print("needsReview:", q.get('needsReview'))
        print("-" * 50)

print("\n--- Summary of needsReview in PQ ---")
needs_review = [q for q in pq if q.get('needsReview')]
print(f"Total needsReview: {len(needs_review)} / {len(pq)}")

print("\n--- Summary of questions with valid options and correct answers ---")
valid_ready = []
needs_fixing = []

for q in pq:
    q_type = q.get('type')
    q_text = (q.get('question') or '').strip()
    opts = q.get('options', [])
    corr = q.get('correct')
    nat_range = q.get('natRange')
    
    # check validity
    is_valid = True
    reason = []
    
    if len(q_text) < 10:
        is_valid = False
        reason.append("text too short")
        
    if q_type in ('mcq', 'msq'):
        if not opts or len(opts) < 2:
            is_valid = False
            reason.append(f"options count {len(opts)}")
        if not corr or len(corr) == 0:
            is_valid = False
            reason.append("missing correct answer")
    elif q_type == 'nat':
        if corr is None and not nat_range:
            is_valid = False
            reason.append("NAT missing correct/natRange")
            
    if is_valid:
        valid_ready.append(q)
    else:
        needs_fixing.append((q, reason))

print(f"Valid and ready: {len(valid_ready)}")
print(f"Needs fixing / incomplete: {len(needs_fixing)}")

from collections import Counter
reasons = Counter()
for q, r in needs_fixing:
    for item in r:
        reasons[item] += 1
print("\nIncomplete breakdown:", dict(reasons))
