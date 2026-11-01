# -*- coding: utf-8 -*-
"""
Ingestion & Merge Engine for GATE Easy-to-Medium Mock Tests (10 Full Papers, 650 Questions).
Parses docx files, validates question schemas, checks duplicates, and merges into sample_questions.json.
"""

import os
import sys
import json
import re
from collections import defaultdict, Counter
from parse_docx_mock import parse_mock_docx, map_subject

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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

def normalize(text):
    if not text:
        return ""
    text = re.sub(r'^(answer:\s*[^\.\n]+\.\s*)?Q\.?\s*\d+[\.\:\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def get_words(text):
    return set(normalize(text).split())

def jaccard(s1, s2):
    if not s1 or not s2:
        return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def main():
    folder = r'c:\Users\sahu1\Downloads\GATE(Easy_to_Medium_Mocks)'
    files = sorted([f for f in os.listdir(folder) if f.endswith('.docx')])
    print(f"=== INGESTING {len(files)} MOCK TEST DOCX FILES ===")
    
    mock_questions = []
    
    for f in files:
        m = re.search(r'Category(\d+)_Set(\d+)', f)
        cat_num = m.group(1) if m else '1'
        set_num = m.group(2) if m else '1'
        mock_id = f"mock-cat{cat_num}-set{set_num}"
        paper_name = f"GATE CSE Mock Cat {cat_num} Set {set_num}"
        
        path = os.path.join(folder, f)
        qs = parse_mock_docx(path)
        print(f"Parsing {f} -> {len(qs)} questions (Mock ID: {mock_id})")
        assert len(qs) == 65, f"Expected 65 questions in {f}, got {len(qs)}"
        
        for q in qs:
            qid = f"mock_c{cat_num}_s{set_num}_q{q['q_num']:02d}"
            
            # Format clean question object
            subj = q['subject']
            if subj not in VALID_SUBJECTS:
                subj = 'Engineering Mathematics'
                
            q_clean = {
                "id": qid,
                "type": q['type'],
                "category": "mock",
                "mockId": mock_id,
                "paper": paper_name,
                "subject": subj,
                "topic": q['topic'],
                "difficulty": q['difficulty'],
                "year": 2026,
                "marks": q['marks'],
                "question": q['question'].strip(),
                "options": q['options'],
                "correct": q['correct'],
                "explanation": q['explanation'].strip()
            }
            if q['type'] == 'nat' and 'natRange' in q:
                q_clean['natRange'] = q['natRange']
                
            mock_questions.append(q_clean)

    print(f"\nTotal new mock questions parsed: {len(mock_questions)}")
    
    # Validation against platform schema
    for q in mock_questions:
        qid = q['id']
        assert q['type'] in ('mcq', 'msq', 'nat'), f"{qid}: invalid type {q['type']}"
        assert q['subject'] in VALID_SUBJECTS or q['subject'] == 'Aptitude', f"{qid}: invalid subject {q['subject']}"
        assert q['difficulty'] in ('easy', 'medium', 'hard'), f"{qid}: invalid difficulty {q['difficulty']}"
        assert q['marks'] in (1, 2), f"{qid}: invalid marks {q['marks']}"
        assert len(q['question']) >= 10, f"{qid}: question text too short"
        assert len(q['explanation']) >= 5, f"{qid}: explanation too short"
        
        if q['type'] in ('mcq', 'msq'):
            assert len(q['options']) == 4, f"{qid}: options != 4 ({len(q['options'])})"
            for opt_idx, opt in enumerate(q['options']):
                assert len(str(opt).strip()) > 0, f"{qid}: empty option {opt_idx}"
            assert len(q['correct']) >= 1, f"{qid}: empty correct answer"
            for c in q['correct']:
                assert isinstance(c, int) and 0 <= c < 4, f"{qid}: invalid correct index {c}"
        elif q['type'] == 'nat':
            assert 'natRange' in q, f"{qid}: missing natRange"
            nr = q['natRange']
            assert 'min' in nr and 'max' in nr, f"{qid}: natRange missing min/max"
            assert isinstance(nr['min'], (int, float)) and isinstance(nr['max'], (int, float)), f"{qid}: non-numeric min/max"

    print("All 650 questions passed strict schema validation!")

    # Load existing database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sample_questions.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        existing_qs = json.load(f)
    print(f"Existing questions in database: {len(existing_qs)}")

    # Check for ID collisions
    existing_ids = {q['id'] for q in existing_qs}
    colliding_ids = [q['id'] for q in mock_questions if q['id'] in existing_ids]
    assert len(colliding_ids) == 0, f"ID collisions detected: {colliding_ids[:5]}"
    print("0 ID collisions with existing database.")

    # Save standalone copy of mock questions
    mocks_copy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'gate_easy_medium_mocks.json')
    with open(mocks_copy_path, 'w', encoding='utf-8') as f:
        json.dump(mock_questions, f, indent=2, ensure_ascii=False)
    print(f"Saved standalone mock questions archive: {mocks_copy_path}")

    # Merge into sample_questions.json
    final_qs = existing_qs + mock_questions
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(final_qs, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(final_qs)} questions to {db_path}!")

    # Metrics summary
    print("\n--- FINAL MASTER DATABASE STATS ---")
    print("Total Questions:", len(final_qs))
    print("By Category:", dict(Counter(q.get('category', 'pyq') for q in final_qs)))
    print("By Type:", dict(Counter(q['type'] for q in final_qs)))
    print("By Difficulty:", dict(Counter(q['difficulty'] for q in final_qs)))
    print("By Subject:", dict(sorted(Counter(q['subject'] for q in final_qs).items())))

if __name__ == '__main__':
    main()
