# -*- coding: utf-8 -*-
"""
scripts/audit_bank.py
Data quality audit & CI gate for GATE CSE Question Bank.
"""
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

DATA_PATH = r"data/sample_questions.json"

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    questions = json.load(f)

print("=" * 70)
print(f"📊 GATE CSE QUESTION BANK AUDIT REPORT ({len(questions)} Total Questions)")
print("=" * 70)

unkeyed = []
out_of_bounds = []
mcq_multi_keys = []
missing_canonical = []
has_explanation = 0

for q in questions:
    qid = q.get('id')
    qtype = q.get('type')
    correct = q.get('correct', [])
    nat_range = q.get('natRange')
    options = q.get('options', [])
    expl = q.get('explanation', '')
    cid = q.get('canonicalId')

    if not cid:
        missing_canonical.append(qid)

    if expl and len(expl.strip()) > 5:
        has_explanation += 1

    if qtype == 'nat':
        if not correct and not nat_range:
            unkeyed.append(qid)
    else:
        if not correct or len(correct) == 0:
            unkeyed.append(qid)
        else:
            for idx in correct:
                if isinstance(idx, int) and idx >= len(options):
                    out_of_bounds.append((qid, idx, len(options)))
            if qtype == 'mcq' and len(correct) > 1:
                mcq_multi_keys.append((qid, correct))

unique_canonical_ids = len(set(q.get('canonicalId', q.get('id')) for q in questions))

print(f"✓ Total questions in datastore: {len(questions)}")
print(f"✓ Unique canonical questions: {unique_canonical_ids}")
print(f"✓ Questions with explanation: {has_explanation} / {len(questions)} ({round(has_explanation/len(questions)*100, 1)}%)")
print(f"⚠️ Questions with pending answer key: {len(unkeyed)}")
print(f"⚠️ Questions with out-of-bounds key index: {len(out_of_bounds)}")
print(f"⚠️ MCQs with >1 key: {len(mcq_multi_keys)}")
print(f"✓ Missing canonicalId: {len(missing_canonical)}")

print("=" * 70)
if len(missing_canonical) == 0 and len(mcq_multi_keys) == 0:
    print("✅ AUDIT INTEGRITY GATE: PASSED (Canonical tagging & index deduplication clean)")
else:
    print(f"❌ AUDIT GATE ISSUES FOUND")
    sys.exit(1)
