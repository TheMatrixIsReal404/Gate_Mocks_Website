# -*- coding: utf-8 -*-
"""
merge_all_testseries_questions.py
Merges deduplicated questions from PW Weekly Tests and Gate Overflow 2025
into data/sample_questions.json with schema normalization and validation.
"""
import json
import shutil
import os
import re

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

def classify_mock_question(q_text):
    t = q_text.lower()
    if any(k in t for k in ['relational', 'sql', 'transaction', 'acid', 'serializability', 'b-tree', 'b+ tree', 'functional dependency']):
        return 'DBMS'
    if any(k in t for k in ['cache', 'pipelining', 'pipeline', 'instruction', 'mips', 'addressing mode', 'tlb', 'interrupt']):
        return 'Computer Organization'
    if any(k in t for k in ['grammar', 'turing', 'cfg', 'dfa', 'nfa', 'pda', 'undecidable', 'decidable', 'regular expression', 'chomsky']):
        return 'Theory of Computation'
    if any(k in t for k in ['ip address', 'subnet', 'tcp', 'udp', 'routing', 'packet', 'sliding window', 'congestion', 'osi']):
        return 'Computer Networks'
    if any(k in t for k in ['process', 'thread', 'deadlock', 'semaphore', 'paging', 'virtual memory', 'page fault', 'fork()']):
        return 'Operating Systems'
    if any(k in t for k in ['sorting', 'binary search', 'greedy', 'dynamic programming', 'graph', 'mst', 'dijkstra', 'shortest path', 'recurrence', 'asymptotic', 'complexity']):
        return 'Algorithms'
    if any(k in t for k in ['tree', 'stack', 'queue', 'linked list', 'heap', 'hashing', 'binary tree', 'traversal']):
        return 'Data Structures'
    if any(k in t for k in ['printf', 'pointer', 'malloc', 'struct', 'sizeof', 'array index', 'recursion in c', 'main(']):
        return 'C Programming'
    if any(k in t for k in ['k-map', 'flip-flop', 'multiplexer', 'boolean', 'counter', 'logic gate', 'decoder', '2\'s complement']):
        return 'Digital Logic'
    if any(k in t for k in ['parser', 'parsing', 'lr(0)', 'lr(1)', 'slr', 'lalr', 'syntax directed', 'three address code', 'compiler', 'lexer', 'basic block']):
        return 'Compiler Design'
    if any(k in t for k in ['graph theory', 'eulerian', 'hamiltonian', 'relation', 'equivalence', 'group', 'monoid', 'poset', 'lattice', 'propositional', 'predicate', 'combinatorics']):
        return 'Discrete Mathematics'
    if any(k in t for k in ['matrix', 'eigenvalue', 'eigenvector', 'determinant', 'rank of', 'probability', 'poisson', 'normal distribution', 'bayes', 'derivative', 'integral', 'limit', 'calculus']):
        return 'Engineering Mathematics'
    if any(k in t for k in ['percentage', 'ratio', 'work', 'time and distance', 'speed', 'profit', 'loss', 'pie chart', 'passage', 'comprehension', 'syllogism', 'cube']):
        return 'Aptitude'
    return 'Engineering Mathematics'

def main():
    backup_path = 'data/sample_questions_backup_pre_ts.json'
    master_path = 'data/sample_questions.json'
    pw_path = 'data/pw_extracted_new_questions.json'
    go_path = 'data/go25_extracted_new_questions.json'
    
    print(f"Creating backup: {backup_path}...")
    shutil.copyfile(master_path, backup_path)
    print("Backup created successfully.")
    
    master_qs = json.load(open(master_path, encoding='utf-8'))
    pw_qs = json.load(open(pw_path, encoding='utf-8'))
    go_qs = json.load(open(go_path, encoding='utf-8'))
    
    print(f"Master questions count: {len(master_qs)}")
    print(f"PW questions count: {len(pw_qs)}")
    print(f"GO questions count: {len(go_qs)}")
    
    existing_ids = set(q['id'] for q in master_qs)
    
    # 1. Process PW Questions
    cleaned_pw = []
    for q in pw_qs:
        qid = q['id']
        if qid in existing_ids:
            continue
            
        subj = q.get('subject', '')
        topic = q.get('topic', '')
        
        # Normalize subject
        if subj == 'Operating System':
            subj = 'Operating Systems'
        elif subj == 'Databases':
            subj = 'DBMS'
        elif subj == 'Computer Organization and Architecture':
            subj = 'Computer Organization'
        elif subj == 'Programming and Data Structures':
            if topic in ['Recursion and arrays', 'Arrays and Pointers', 'Functions and Storage Classes']:
                subj = 'C Programming'
            else:
                subj = 'Data Structures'
                
        if subj not in CANONICAL_SUBJECTS:
            subj = 'Data Structures'
            
        q_type = q.get('type', 'mcq').lower()
        marks = int(q.get('marks', 1))
        options = q.get('options', [])
        correct = q.get('correct', [])
        has_key = bool(q.get('hasUsableKey', False)) and len(correct) > 0
        
        # Validate options for mcq/msq
        if q_type in ['mcq', 'msq']:
            if len(options) < 2:
                q_type = 'nat'
                options = []
            else:
                # If question has multiple correct options, it is an MSQ
                if q_type == 'mcq' and len(correct) > 1:
                    q_type = 'msq'
                # Validate key bounds
                if any(isinstance(k, int) and (k < 0 or k >= len(options)) for k in correct):
                    has_key = False
                    correct = []
                    
        item = {
            'id': qid,
            'canonicalId': q.get('canonicalId', qid),
            'type': q_type,
            'category': 'test_series',
            'subject': subj,
            'topic': topic or 'Subject Test',
            'difficulty': q.get('difficulty', 'medium').lower(),
            'year': q.get('year', 2026),
            'marks': marks,
            'question': q.get('question', '').strip(),
            'options': options,
            'correct': correct,
            'explanation': q.get('explanation', '').strip(),
            'hasUsableKey': has_key,
            'source': q.get('paper', 'PW Weekly Test Series')
        }
        cleaned_pw.append(item)
        existing_ids.add(qid)
        
    print(f"Cleaned and validated PW questions: {len(cleaned_pw)}")
    
    # 2. Process GO Questions
    cleaned_go = []
    filtered_bad_go = 0
    for q in go_qs:
        qid = q['id']
        if qid in existing_ids:
            continue
            
        subj = q.get('subject', '')
        q_text = q.get('question', '').strip()
        topic = q.get('topic', '')
        
        if subj == 'Mock' or subj not in CANONICAL_SUBJECTS:
            subj = classify_mock_question(q_text)
            
        q_type = q.get('type', 'mcq').lower()
        marks = int(q.get('marks', 1))
        options = q.get('options', [])
        correct = q.get('correct', [])
        
        # Check option integrity
        if q_type in ['mcq', 'msq']:
            if len(options) < 2:
                filtered_bad_go += 1
                continue
            if q_type == 'mcq' and len(correct) > 1:
                q_type = 'msq'
            if any(isinstance(k, int) and (k < 0 or k >= len(options)) for k in correct):
                # Corrupted / missing image options
                filtered_bad_go += 1
                continue
                
        has_key = bool(q.get('hasUsableKey', False)) and len(correct) > 0
        
        item = {
            'id': qid,
            'canonicalId': q.get('canonicalId', qid),
            'type': q_type,
            'category': 'test_series',
            'subject': subj,
            'topic': topic or 'Test Series Practice',
            'difficulty': q.get('difficulty', 'medium').lower(),
            'year': q.get('year', 2025),
            'marks': marks,
            'question': q_text,
            'options': options,
            'correct': correct,
            'explanation': q.get('explanation', '').strip(),
            'hasUsableKey': has_key,
            'source': q.get('source', 'Gate Overflow 2025 Test Series')
        }
        cleaned_go.append(item)
        existing_ids.add(qid)
        
    print(f"Cleaned and validated GO questions: {len(cleaned_go)} (Filtered corrupted/missing diagrams: {filtered_bad_go})")
    
    # Combine all
    unified_bank = master_qs + cleaned_pw + cleaned_go
    print(f"\n==========================================")
    print(f"Final Merged Datastore Summary:")
    print(f"Initial Questions: {len(master_qs)}")
    print(f"Added PW Unique Questions: {len(cleaned_pw)}")
    print(f"Added GO Unique Questions: {len(cleaned_go)}")
    print(f"Total Questions in Bank: {len(unified_bank)}")
    print(f"==========================================")
    
    # Validate newly added questions integrity
    new_questions = cleaned_pw + cleaned_go
    assert len(unified_bank) == len(set(q['id'] for q in unified_bank)), "CRITICAL: Duplicate IDs detected in unified bank!"
    for q in new_questions:
        assert 'id' in q and q['id'], "CRITICAL: Empty id"
        assert 'canonicalId' in q and q['canonicalId'], f"CRITICAL: Empty canonicalId in {q['id']}"
        assert q['subject'] in CANONICAL_SUBJECTS, f"CRITICAL: Unknown subject '{q['subject']}' in {q['id']}"
        assert q['type'] in ['mcq', 'msq', 'nat'], f"CRITICAL: Invalid type '{q['type']}' in {q['id']}"
        if q['type'] in ['mcq', 'msq']:
            assert len(q.get('options', [])) >= 2, f"CRITICAL: Options < 2 in {q['id']}"
            for k in q.get('correct', []):
                if isinstance(k, int):
                    assert 0 <= k < len(q['options']), f"CRITICAL: Out of bounds key {k} in {q['id']}"
                    
    print(f"ALL {len(new_questions)} NEW TEST SERIES QUESTIONS PASSED STRICT DATASTORE INTEGRITY ASSERTIONS!")
    
    # Write to data/sample_questions.json
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(unified_bank, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(unified_bank)} questions to {master_path}.")

if __name__ == '__main__':
    main()
