# -*- coding: utf-8 -*-
"""
unify_canonical_duplicates.py
Unifies canonicalId across all exact duplicate groups in data/sample_questions.json
and synchronizes data/id_aliases.json so deduplication in Practice Mode is 100% airtight.
"""
import json
import hashlib
import re
from collections import defaultdict

def normalize_text(text):
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r'[\s\W_]+', ' ', t)
    return t.strip()

def pick_primary_question(questions_group):
    # Sort key priority:
    # 1. pyq > subject > test_series > mock
    # 2. hasUsableKey (True > False)
    # 3. has explanation (len > 0)
    # 4. shorter or standard ID length
    category_rank = {'pyq': 1, 'subject': 2, 'test_series': 3, 'mock': 4, 'unknown': 5}
    def sort_key(q):
        cat = category_rank.get(q.get('category', 'unknown'), 5)
        has_key = 0 if q.get('hasUsableKey') else 1
        has_expl = 0 if len(q.get('explanation', '').strip()) > 0 else 1
        return (cat, has_key, has_expl, len(q.get('id', '')))
    
    sorted_group = sorted(questions_group, key=sort_key)
    return sorted_group[0]

def main():
    master_path = 'data/sample_questions.json'
    alias_path = 'data/id_aliases.json'
    
    questions = json.load(open(master_path, encoding='utf-8'))
    print(f"Loaded {len(questions)} questions from {master_path}.")
    
    # Group by exact normalized text
    hash_to_qs = defaultdict(list)
    for q in questions:
        norm = normalize_text(q.get('question', ''))
        h = hashlib.sha256(norm.encode('utf-8')).hexdigest()
        hash_to_qs[h].append(q)
        
    exact_groups = [qs for qs in hash_to_qs.values() if len(qs) > 1]
    print(f"Total exact duplicate groups: {len(exact_groups)}")
    
    aliases = {}
    updated_cids = 0
    
    for g in exact_groups:
        primary = pick_primary_question(g)
        primary_id = primary['id']
        primary_cid = primary.get('canonicalId') or primary_id
        
        for q in g:
            old_cid = q.get('canonicalId')
            if old_cid != primary_cid:
                q['canonicalId'] = primary_cid
                updated_cids += 1
            if q['id'] != primary_cid:
                aliases[q['id']] = primary_cid
                
    print(f"Updated canonicalId on {updated_cids} questions.")
    print(f"Total alias mappings registered: {len(aliases)}")
    
    # Save sample_questions.json
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Saved updated {master_path}.")
    
    # Save id_aliases.json
    with open(alias_path, 'w', encoding='utf-8') as f:
        json.dump(aliases, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(aliases)} aliases to {alias_path}.")
    
    # Count unique canonical IDs now
    unique_cids = len(set(q.get('canonicalId', q['id']) for q in questions))
    print(f"\n=======================================================")
    print(f"DEDUPLICATION ALIGNMENT COMPLETE:")
    print(f"Total Datastore Questions: {len(questions)}")
    print(f"Total Unique Canonical Problems: {unique_cids}")
    print(f"Exact Duplicate Instances Tagged: {len(questions) - unique_cids}")
    print(f"=======================================================")

if __name__ == '__main__':
    main()
