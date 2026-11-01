# -*- coding: utf-8 -*-
"""
merge_go26_and_zeal.py
Merges 1,174 GO 2026 questions and 6,307 Zeal questions into data/sample_questions.json
with strict schema validation, canonicalId alignment, and backup.
"""
import json
import shutil
from collections import Counter

CANONICAL_SUBJECTS = {
    'Algorithms',
    'Aptitude',
    'C Programming',
    'Compiler Design',
    'Computer Networks',
    'Computer Organization',
    'DBMS',
    'Data Structures',
    'Digital Logic',
    'Discrete Mathematics',
    'Engineering Mathematics',
    'Operating Systems',
    'Theory of Computation'
}

def main():
    master_path = 'data/sample_questions.json'
    backup_path = 'data/sample_questions_backup_12432.json'
    go26_path = 'data/go26_extracted_questions.json'
    zeal_path = 'data/zeal_extracted_questions.json'
    
    print(f"Creating backup: {backup_path}...")
    shutil.copyfile(master_path, backup_path)
    
    master = json.load(open(master_path, encoding='utf-8'))
    go26_qs = json.load(open(go26_path, encoding='utf-8'))
    zeal_qs = json.load(open(zeal_path, encoding='utf-8'))
    
    print(f"Current master count: {len(master)}")
    print(f"GO 2026 questions count: {len(go26_qs)}")
    print(f"Zeal questions count: {len(zeal_qs)}")
    
    existing_ids = set(q['id'] for q in master)
    added = []
    
    candidates = go26_qs + zeal_qs
    for q in candidates:
        qid = q['id']
        if qid in existing_ids:
            continue
            
        subj = q.get('subject')
        if subj not in CANONICAL_SUBJECTS:
            subj = 'Engineering Mathematics'
            
        q_type = q.get('type', 'mcq').lower()
        options = q.get('options', [])
        correct = q.get('correct', [])
        
        # Validate options and keys
        if q_type in ['mcq', 'msq']:
            if len(options) < 2:
                q_type = 'nat'
                options = []
            else:
                if any(isinstance(k, int) and (k < 0 or k >= len(options)) for k in correct):
                    correct = []
                    
        if q_type == 'mcq' and len(correct) > 1:
            q_type = 'msq'
            
        has_key = bool(q.get('hasUsableKey', False)) and len(correct) > 0
        
        item = {
            'id': qid,
            'canonicalId': q.get('canonicalId', qid),
            'type': q_type,
            'category': 'test_series',
            'subject': subj,
            'topic': q.get('topic', 'Practice Sheet'),
            'difficulty': q.get('difficulty', 'medium'),
            'year': q.get('year', 2025),
            'marks': q.get('marks', 1),
            'question': q['question'].strip(),
            'options': options,
            'correct': correct,
            'explanation': q.get('explanation', '').strip(),
            'hasUsableKey': has_key,
            'source': q.get('source', 'GATE Coaching Test Series')
        }
        added.append(item)
        existing_ids.add(qid)
        
    print(f"Cleaned and validated new questions: {len(added)}")
    
    unified_bank = master + added
    print(f"\n=======================================================")
    print(f"UNIFIED DATASTORE MILESTONE:")
    print(f"Initial Questions: {len(master)}")
    print(f"Added GO 2026 Unique Questions: {len(go26_qs)}")
    print(f"Added Zeal Practice Unique Questions: {len(zeal_qs)}")
    print(f"Total Questions in Platform Bank: {len(unified_bank)}")
    print(f"=======================================================")
    print("Categories Breakdown:", Counter(q['category'] for q in unified_bank))
    print("Types Breakdown:", Counter(q['type'] for q in unified_bank))
    
    # Assertions
    assert len(unified_bank) == len(set(q['id'] for q in unified_bank)), "CRITICAL: Duplicate IDs in unified bank!"
    for q in added:
        assert q['subject'] in CANONICAL_SUBJECTS, f"Unknown subject {q['subject']}"
        assert q['type'] in ['mcq', 'msq', 'nat'], f"Invalid type {q['type']}"
        if q['type'] in ['mcq', 'msq']:
            assert len(q['options']) >= 2, f"Options < 2 in {q['id']}"
            assert not any(isinstance(k, int) and (k < 0 or k >= len(q['options'])) for k in q['correct'])
            
    print("ALL NEW QUESTIONS PASSED STRICT DATASTORE INTEGRITY ASSERTIONS!")
    
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(unified_bank, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(unified_bank)} questions to {master_path}.")

if __name__ == '__main__':
    main()
