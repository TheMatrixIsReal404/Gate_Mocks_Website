# -*- coding: utf-8 -*-
import json
import random

with open('previous_questions.json', 'r', encoding='utf-8') as f:
    pq = json.load(f)

strictly_valid = []
for q in pq:
    text = (q.get('question') or '').strip()
    t = q.get('type')
    opts = q.get('options', [])
    corr = q.get('correct')
    nat_range = q.get('natRange')
    
    if len(text) < 15:
        continue
    if t == 'mcq':
        if not opts or len(opts) < 2:
            continue
        if not corr or len(corr) != 1:
            continue
        c = corr[0]
        if not isinstance(c, int) or c < 0 or c >= len(opts):
            continue
        strictly_valid.append(q)
    elif t == 'msq':
        if not opts or len(opts) < 2:
            continue
        if not corr or len(corr) < 1:
            continue
        if any(not isinstance(c, int) or c < 0 or c >= len(opts) for c in corr):
            continue
        strictly_valid.append(q)
    elif t == 'nat':
        if nat_range and 'min' in nat_range and 'max' in nat_range:
            strictly_valid.append(q)
        elif corr and len(corr) > 0 and isinstance(corr[0], (int, float)):
            strictly_valid.append(q)

print(f"Strictly valid count: {len(strictly_valid)}")

random.seed(42)
samples = random.sample(strictly_valid, 15)

for i, q in enumerate(samples):
    print(f"\n--- Sample {i+1}: [{q['id']}] (Year: {q.get('year')}, Subject: {q.get('subject')}, Type: {q.get('type')}) ---")
    print("Q:", q.get('question'))
    if q.get('options'):
        print("Options:")
        for idx, opt in enumerate(q['options']):
            print(f"  [{idx}] {opt}")
    print("Correct:", q.get('correct'))
    if q.get('natRange'):
        print("natRange:", q.get('natRange'))
    print("Explanation:", repr(q.get('explanation')))
