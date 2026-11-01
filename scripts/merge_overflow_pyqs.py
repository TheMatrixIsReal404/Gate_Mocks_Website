# -*- coding: utf-8 -*-
"""
Merges and validates authentic GATE CSE questions from Gate Overflow books & official papers.
Expands the database to 510 questions.
"""

import os
import sys
import json

# Ensure scripts directory is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from pyqs_2007_2010 import get_2007_2010_pyqs
from pyqs_2011_2015 import get_2011_2015_pyqs
from pyqs_2017_2024 import get_2017_2024_pyqs
from pyqs_subjects_expansion import get_expansion_pyqs
from pyqs_milestone_500 import get_milestone_500_pyqs

VALID_SUBJECTS = {
    "Algorithms",
    "Aptitude",
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

def validate_question(q):
    qid = q.get("id")
    assert qid, "Question missing id"
    assert q.get("type") in ["mcq", "msq", "nat"], f"{qid}: Invalid type {q.get('type')}"
    assert q.get("category") in ["pyq", "mock", "subject"], f"{qid}: Invalid category {q.get('category')}"
    assert q.get("subject") in VALID_SUBJECTS, f"{qid}: Invalid subject {q.get('subject')}"
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
        assert nr["min"] <= nr["max"], f"{qid}: natRange min {nr['min']} > max {nr['max']}"

def main():
    root_dir = os.path.dirname(SCRIPT_DIR)
    target_path = os.path.join(root_dir, "data", "sample_questions.json")
    
    with open(target_path, "r", encoding="utf-8") as f:
        existing = json.load(f)
        
    print(f"[*] Loaded {len(existing)} existing questions from {target_path}")
    
    new_batches = [
        ("2007-2010 PYQs", get_2007_2010_pyqs()),
        ("2011-2015 PYQs", get_2011_2015_pyqs()),
        ("2017-2024 PYQs", get_2017_2024_pyqs()),
        ("Subjects Expansion PYQs", get_expansion_pyqs()),
        ("Milestone 500 PYQs", get_milestone_500_pyqs())
    ]
    
    all_new = []
    seen_ids = set(q["id"] for q in existing)
    
    for batch_name, q_list in new_batches:
        print(f"[*] Validating {batch_name}: {len(q_list)} questions...")
        for q in q_list:
            validate_question(q)
            assert q["id"] not in seen_ids, f"Duplicate ID detected: {q['id']}"
            seen_ids.add(q["id"])
            all_new.append(q)
            
    print(f"[+] All {len(all_new)} new questions passed schema validation!")
    
    # Save standalone export of new additions
    export_path = os.path.join(root_dir, "data", "gate_overflow_pyqs_added.json")
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(all_new, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved standalone batch of {len(all_new)} questions to {export_path}")
    
    # Merge and validate final collection
    combined = existing + all_new
    print(f"[*] Validating combined collection of {len(combined)} questions...")
    combined_ids = set()
    for q in combined:
        validate_question(q)
        assert q["id"] not in combined_ids, f"Collision in combined collection: {q['id']}"
        combined_ids.add(q["id"])
        
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
        
    print(f"\n[SUCCESS] Successfully merged and wrote {len(combined)} questions to {target_path}!")

if __name__ == "__main__":
    main()
