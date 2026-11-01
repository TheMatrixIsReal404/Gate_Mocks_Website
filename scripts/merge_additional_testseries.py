# -*- coding: utf-8 -*-
"""
merge_additional_testseries.py
Merges the 2,372 newly extracted, deduplicated test series questions into data/sample_questions.json.
"""
import json
import shutil

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
    backup_path = 'data/sample_questions_backup_10060.json'
    new_path = 'data/newly_extracted_testseries_questions.json'
    
    print(f"Creating backup: {backup_path}...")
    shutil.copyfile(master_path, backup_path)
    
    master = json.load(open(master_path, encoding='utf-8'))
    new_qs = json.load(open(new_path, encoding='utf-8'))
    
    print(f"Current master count: {len(master)}")
    print(f"New test series count to add: {len(new_qs)}")
    
    existing_ids = set(q['id'] for q in master)
    added = []
    
    for q in new_qs:
        qid = q['id']
        if qid in existing_ids:
            continue
            
        subj = q['subject']
        if subj not in CANONICAL_SUBJECTS:
            subj = 'Engineering Mathematics'
            
        q_type = q['type']
        options = q.get('options', [])
        correct = q.get('correct', [])
        
        # Double check key bounds
        if q_type in ['mcq', 'msq']:
            if len(options) < 2:
                continue
            if any(isinstance(k, int) and (k < 0 or k >= len(options)) for k in correct):
                continue
                
        if q_type == 'mcq' and len(correct) > 1:
            q_type = 'msq'
            
        item = {
            'id': qid,
            'canonicalId': q.get('canonicalId', qid),
            'type': q_type,
            'category': 'test_series',
            'subject': subj,
            'topic': q.get('topic', 'Test Series Practice'),
            'difficulty': q.get('difficulty', 'medium'),
            'year': q.get('year', 2025),
            'marks': q.get('marks', 1),
            'question': q['question'].strip(),
            'options': options,
            'correct': correct,
            'explanation': q.get('explanation', '').strip(),
            'hasUsableKey': bool(q.get('hasUsableKey', False)) and len(correct) > 0,
            'source': q.get('source', 'GATE Test Series')
        }
        added.append(item)
        existing_ids.add(qid)
        
    print(f"Validated and prepared {len(added)} new questions.")
    
    combined = master + added
    print(f"\nTotal Unified Bank: {len(combined)} questions.")
    
    # Assertions
    assert len(combined) == len(set(q['id'] for q in combined)), "CRITICAL: Duplicate IDs in combined bank!"
    for q in added:
        assert q['subject'] in CANONICAL_SUBJECTS, f"Unknown subject {q['subject']}"
        assert q['type'] in ['mcq', 'msq', 'nat'], f"Invalid type {q['type']}"
        if q['type'] in ['mcq', 'msq']:
            assert len(q['options']) >= 2, f"Options < 2 in {q['id']}"
            assert not any(isinstance(k, int) and (k < 0 or k >= len(q['options'])) for k in q['correct'])
            
    print("ALL NEW QUESTIONS PASSED STRICT DATASTORE INTEGRITY ASSERTIONS!")
    
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(combined)} questions to {master_path}.")

if __name__ == '__main__':
    main()
