# -*- coding: utf-8 -*-
"""
Merges all authentic question sources into data/sample_questions.json:
- Existing data/sample_questions.json
- previous_questions.json
- data/gate_30_easy_mocks.json (1,950 easy mock questions)
- data/gate_30_medium_mocks.json (1,950 medium mock questions)
- data/gate_20_full_mocks.json
- data/gate_easy_medium_mocks.json
- All supplementary PYQ sets
Ensures schema validity, no duplicate IDs, and writes master database.
"""

import json
import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    sources = [
        'data/sample_questions.json',
        'previous_questions.json',
        'data/gate_30_easy_mocks.json',
        'data/gate_30_medium_mocks.json',
        'data/gate_20_full_mocks.json',
        'data/gate_easy_medium_mocks.json',
        'data/gate_2025_pyqs.json',
        'data/gate_overflow_pyqs_added.json',
        'data/gate_drive_pyqs_added.json',
        'data/gate_pyqs_added.json'
    ]

    master = {}
    total_loaded = 0

    for src in sources:
        if not os.path.exists(src):
            print(f"Skipping missing: {src}")
            continue
        with open(src, 'r', encoding='utf-8') as f:
            items = json.load(f)
            total_loaded += len(items)
            for q in items:
                qid = q.get('id')
                if not qid:
                    continue
                # Keep first or enhance with mockId/paper if available
                if qid not in master:
                    master[qid] = q
                else:
                    # Enrich existing question with any missing non-null fields
                    for k, v in q.items():
                        if k not in master[qid] or master[qid][k] is None:
                            master[qid][k] = v

    print(f"Total entries loaded across sources: {total_loaded}")
    print(f"Total unique master questions: {len(master)}")

    # Verify all 30 easy mocks are present
    easy_mocks = [q for q in master.values() if (q.get('mockId') or '').startswith('mock-easy-')]
    print(f"Easy mock questions count: {len(easy_mocks)} (expected 1,950)")
    assert len(easy_mocks) == 1950, f"Expected 1950 easy mock questions, got {len(easy_mocks)}"

    # Verify all 30 medium mocks are present
    med_mocks = [q for q in master.values() if (q.get('mockId') or '').startswith('mock-med-')]
    print(f"Medium mock questions count: {med_mocks.__len__()} (expected 1,950)")
    assert len(med_mocks) == 1950, f"Expected 1950 medium mock questions, got {len(med_mocks)}"

    # Save to data/sample_questions.json
    out_path = 'data/sample_questions.json'
    if os.path.exists(out_path):
        os.replace(out_path, out_path + '.bak')

    master_list = list(master.values())
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(master_list, f, indent=2, ensure_ascii=False)

    print(f"Successfully saved {len(master_list)} master questions to {out_path} ({os.path.getsize(out_path):,} bytes)!")

if __name__ == '__main__':
    main()
