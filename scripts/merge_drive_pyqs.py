# -*- coding: utf-8 -*-
"""
Merges authentic PYQs from Google Drive / Gate Overflow Books into sample_questions.json.
Validates schema and confirms 0 duplicates.
"""

import os
import sys
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from pyqs_drive_expansion import get_drive_expansion_pyqs

VALID_SUBJECTS = {
    "Algorithms",
    "Aptitude",
    "General Aptitude",
    "C Programming",
    "Compiler Design",
    "Computer Networks",
    "Computer Organization",
    "DBMS",
    "Data Structures",
    "Digital Logic",
    "Discrete Mathematics",
    "Engineering Mathematics",
    "Operating Systems",
    "Theory of Computation"
}

def normalize_text(text):
    text = re.sub(r'[\$\`\*\_]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def validate_question(q):
    qid = q.get("id")
    assert qid, "Question missing id"
    assert q.get("type") in ["mcq", "msq", "nat"], f"{qid}: Invalid type {q.get('type')}"
    # Normalize 'General Aptitude' to 'Aptitude' if needed
    if q.get("subject") == "General Aptitude":
        q["subject"] = "Aptitude"
    assert q.get("subject") in VALID_SUBJECTS or q.get("subject") == "Aptitude", f"{qid}: Invalid subject {q.get('subject')}"
    assert q.get("difficulty") in ["easy", "medium", "hard"], f"{qid}: Invalid difficulty {q.get('difficulty')}"
    assert q.get("marks") in [1, 2], f"{qid}: Invalid marks {q.get('marks')}"
    assert q.get("question") and len(q["question"].strip()) > 5, f"{qid}: Empty question text"
    assert q.get("explanation") and len(q["explanation"].strip()) > 5, f"{qid}: Empty explanation"

    if q["type"] in ["mcq", "msq"]:
        opts = q.get("options", [])
        assert len(opts) >= 2, f"{qid}: Too few options ({len(opts)})"
        corrs = q.get("correct", [])
        assert len(corrs) >= 1, f"{qid}: Missing correct answer"
        for c in corrs:
            assert isinstance(c, int), f"{qid}: Correct answer index not int ({c})"
            assert 0 <= c < len(opts), f"{qid}: Correct index {c} out of bounds (len {len(opts)})"
    elif q["type"] == "nat":
        assert "natRange" in q, f"{qid}: NAT question missing natRange"
        nr = q["natRange"]
        assert "min" in nr and "max" in nr, f"{qid}: natRange missing min/max"

def main():
    db_path = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "sample_questions.json")
    with open(db_path, "r", encoding="utf-8") as f:
        existing_qs = json.load(f)

    print(f"Initial questions in database: {len(existing_qs)}")
    existing_ids = {q["id"] for q in existing_qs}
    existing_texts = {normalize_text(q["question"]) for q in existing_qs}

    new_candidates = get_drive_expansion_pyqs()
    print(f"Candidate questions to merge: {len(new_candidates)}")

    added_qs = []
    for q in new_candidates:
        validate_question(q)
        if q["id"] in existing_ids:
            print(f"Skipping duplicate ID: {q['id']}")
            continue
        norm = normalize_text(q["question"])
        if norm in existing_texts:
            print(f"Skipping duplicate text: {q['id']}")
            continue
        existing_ids.add(q["id"])
        existing_texts.add(norm)
        added_qs.append(q)

    print(f"Valid distinct questions added: {len(added_qs)}")
    final_qs = existing_qs + added_qs
    print(f"Total questions in database now: {len(final_qs)}")

    # Write merged database
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(final_qs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(final_qs)} questions to {db_path}")

    # Write separate copy of added batch
    added_path = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "gate_drive_pyqs_added.json")
    with open(added_path, "w", encoding="utf-8") as f:
        json.dump(added_qs, f, indent=2, ensure_ascii=False)
    print(f"Saved added questions backup to {added_path}")

if __name__ == "__main__":
    main()
