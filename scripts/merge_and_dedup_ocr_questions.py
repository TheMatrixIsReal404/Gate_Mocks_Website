# -*- coding: utf-8 -*-
"""
merge_and_dedup_ocr_questions.py
Comprehensive duplicate detection, canonicalId alignment, and datastore merger
for 1,143 high-fidelity OCR questions into data/sample_questions.json.
"""
import json
import shutil
import os
import re
import hashlib
from collections import defaultdict, Counter

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

def normalize_text(text):
    if not text:
        return ""
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'```c|```', ' ', t)
    t = t.replace('$', ' ')
    t = t.lower()
    t = re.sub(r'[\s\W_]+', ' ', t)
    return t.strip()

def tokenize(text):
    norm = normalize_text(text)
    return set([w for w in norm.split() if len(w) > 2])

def jaccard(s1, s2):
    if not s1 or not s2:
        return 0.0
    u = len(s1.union(s2))
    return len(s1.intersection(s2)) / u if u > 0 else 0.0

def main():
    master_path = 'data/sample_questions.json'
    alias_path = 'data/id_aliases.json'
    new_path = 'data/newly_extracted_core_cs_questions.json'
    audit_report_path = 'data/complete_ocr_duplicate_audit_report.json'
    
    print("=================================================================")
    print("STARTING OCR QUESTIONS DUPLICACY CHECK & DATASTORE INTEGRATION")
    print("=================================================================")
    
    # Read from pre-merge backup if exists to ensure idempotency
    backup_file = 'data/sample_questions_backup_19874.json'
    source_master_path = backup_file if os.path.exists(backup_file) else master_path
    
    master = json.load(open(source_master_path, encoding='utf-8'))
    new_qs = json.load(open(new_path, encoding='utf-8'))
    aliases = json.load(open(alias_path, encoding='utf-8')) if os.path.exists(alias_path) else {}
    
    print(f"Initial Master Questions: {len(master)}")
    print(f"New High-Fidelity Questions: {len(new_qs)}")
    print(f"Initial Aliases Count: {len(aliases)}")
    
    # -----------------------------------------------------------------
    # 1. Identify Old Low-Fidelity Zeal Questions to be Upgraded
    # -----------------------------------------------------------------
    old_zeal_sheet_sources = [
        'C Programming Language Questions.pdf',
        'DLD - Basic  Sheet.pdf',
        'Maths  Sheet_2022.pdf'
    ]
    
    old_zeal_to_replace = []
    retained_master = []
    for q in master:
        src = q.get('source', '')
        if any(s in src for s in old_zeal_sheet_sources):
            old_zeal_to_replace.append(q)
        else:
            retained_master.append(q)
            
    print(f"\n[Step 1] Master Partitioning:")
    print(f"  - Old raw Zeal questions being upgraded: {len(old_zeal_to_replace)}")
    print(f"  - Core Master Questions Retained (PYQ, Mocks, Other Test Series): {len(retained_master)}")
    
    # -----------------------------------------------------------------
    # 2. Map Old Zeal IDs to New High-Fidelity IDs for Aliasing
    # -----------------------------------------------------------------
    new_norm_map = {}
    for nq in new_qs:
        norm = normalize_text(nq['question'])
        if len(norm) > 10 and norm not in new_norm_map:
            new_norm_map[norm] = nq
            
    new_tokens = [(nq, tokenize(nq['question'])) for nq in new_qs if len(nq['question']) > 20]
    
    old_to_new_alias_count = 0
    for oq in old_zeal_to_replace:
        old_norm = normalize_text(oq['question'])
        matched_new = None
        if old_norm in new_norm_map:
            matched_new = new_norm_map[old_norm]
        else:
            otok = tokenize(oq['question'])
            if len(otok) >= 5:
                best_sim = 0.0
                best_match = None
                for nq, ntok in new_tokens:
                    if nq['subject'] == oq['subject']:
                        sim = jaccard(otok, ntok)
                        if sim > best_sim:
                            best_sim = sim
                            best_match = nq
                if best_sim >= 0.70:
                    matched_new = best_match
                    
        if matched_new:
            aliases[oq['id']] = matched_new['id']
            old_to_new_alias_count += 1
            
    print(f"  - Mapped {old_to_new_alias_count} legacy Zeal IDs to new high-fidelity canonical IDs.")
    
    # -----------------------------------------------------------------
    # 3. Check Cross-Paper Duplicates (New Questions vs PYQ / Mocks / PW / GO)
    # -----------------------------------------------------------------
    retained_norm_map = defaultdict(list)
    for q in retained_master:
        norm = normalize_text(q.get('question', ''))
        if len(norm) > 15:
            retained_norm_map[norm].append(q)
            
    cross_paper_duplicates = []
    canonical_unifications = 0
    
    for nq in new_qs:
        norm = normalize_text(nq.get('question', ''))
        if norm in retained_norm_map:
            matched_candidates = retained_norm_map[norm]
            category_rank = {'pyq': 1, 'mock': 2, 'subject': 3, 'test_series': 4}
            sorted_candidates = sorted(matched_candidates, key=lambda x: category_rank.get(x.get('category'), 5))
            primary_match = sorted_candidates[0]
            
            primary_cid = primary_match.get('canonicalId') or primary_match['id']
            nq['canonicalId'] = primary_cid
            aliases[nq['id']] = primary_cid
            canonical_unifications += 1
            
            cross_paper_duplicates.append({
                'new_id': nq['id'],
                'new_subject': nq['subject'],
                'canonical_primary_id': primary_cid,
                'primary_category': primary_match.get('category'),
                'primary_paper': primary_match.get('paper', primary_match.get('source', '')),
                'snippet': nq['question'][:100]
            })
        else:
            nq['canonicalId'] = nq['id']
            
    print(f"\n[Step 2] Cross-Paper Duplication Check:")
    print(f"  - Exact cross-paper duplicate matches detected: {len(cross_paper_duplicates)}")
    print(f"  - Canonical IDs unified to primary problems: {canonical_unifications}")
    for dup in cross_paper_duplicates[:5]:
        print(f"    * {dup['new_id']} ({dup['new_subject']}) -> Canonical: {dup['canonical_primary_id']} ({dup['primary_category']})")
        
    # -----------------------------------------------------------------
    # 4. Check Internal Duplicates within the New Batch
    # -----------------------------------------------------------------
    internal_norm_map = defaultdict(list)
    for nq in new_qs:
        norm = normalize_text(nq.get('question', ''))
        if len(norm) > 15:
            internal_norm_map[norm].append(nq)
            
    internal_duplicates = []
    for norm, q_group in internal_norm_map.items():
        if len(q_group) > 1:
            prim_cid = q_group[0]['canonicalId']
            for dup_q in q_group[1:]:
                dup_q['canonicalId'] = prim_cid
                aliases[dup_q['id']] = prim_cid
            internal_duplicates.append({
                'primary_id': q_group[0]['id'],
                'duplicate_ids': [x['id'] for x in q_group[1:]],
                'subject': q_group[0]['subject'],
                'snippet': q_group[0]['question'][:100]
            })
            
    print(f"\n[Step 3] Internal Duplication Check:")
    print(f"  - Internal duplicate clusters within new questions: {len(internal_duplicates)}")
    
    # -----------------------------------------------------------------
    # 5. Schema Validation & Normalization for All New Questions
    # -----------------------------------------------------------------
    cleaned_new = []
    for q in new_qs:
        subj = q['subject']
        assert subj in CANONICAL_SUBJECTS, f"Invalid subject: {subj}"
        
        q_type = q.get('type', 'mcq').lower()
        options = q.get('options', [])
        correct = q.get('correct', [])
        
        if q_type in ['mcq', 'msq']:
            if len(options) < 2 and not ('<figure' in q['question']):
                q_type = 'nat'
                options = []
            elif any(isinstance(k, int) and (k < 0 or (options and k >= len(options))) for k in correct):
                correct = []
                
        if q_type == 'mcq' and len(correct) > 1:
            q_type = 'msq'
            
        has_key = bool(q.get('hasUsableKey', False)) and len(correct) > 0
        
        # Paper assignment
        paper_title = q.get('paper', '')
        if not paper_title or len(paper_title) > 65:
            if 'zeal_cp_' in q['id']:
                paper_title = 'Zeal Practice Sheet 2023 - C Programming'
            elif 'zeal_dld_' in q['id']:
                paper_title = 'Zeal Practice Sheet 2023 - DLD Basic'
            elif 'zeal_em_' in q['id']:
                paper_title = 'Zeal Practice Sheet 2023 - Engineering Mathematics'
            elif 'me24_' in q['id']:
                paper_title = 'Made Easy 2024 - Programming and Data Structures'
                
        item = {
            'id': q['id'],
            'canonicalId': q.get('canonicalId', q['id']),
            'type': q_type,
            'category': 'test_series',
            'subject': subj,
            'topic': q.get('topic', 'Practice Problems'),
            'paper': paper_title,
            'difficulty': q.get('difficulty', 'medium'),
            'year': q.get('year', 2023),
            'marks': q.get('marks', 1),
            'question': q['question'].strip(),
            'options': options,
            'correct': correct,
            'explanation': q.get('explanation', '').strip(),
            'hasUsableKey': has_key,
            'source': q.get('source', 'GATE Coaching Test Series')
        }
        cleaned_new.append(item)
        
    # -----------------------------------------------------------------
    # 6. Assemble Unified Datastore
    # -----------------------------------------------------------------
    unified_datastore = retained_master + cleaned_new
    print(f"\n[Step 4] Datastore Assembly:")
    print(f"  - Initial Master Count: {len(master)}")
    print(f"  - Upgraded/Replaced Old Zeal Questions: {len(old_zeal_to_replace)}")
    print(f"  - Added High-Fidelity Questions: {len(cleaned_new)}")
    print(f"  - Final Unified Datastore Count: {len(unified_datastore)}")
    print(f"  - Net Expansion: +{len(unified_datastore) - len(master)} questions")
    
    # -----------------------------------------------------------------
    # 7. Strict Datastore Integrity Assertions
    # -----------------------------------------------------------------
    print(f"\n[Step 5] Running Strict Datastore Integrity Assertions...")
    all_ids = [q['id'] for q in unified_datastore]
    assert len(all_ids) == len(set(all_ids)), f"CRITICAL: Found duplicate IDs in unified datastore! {len(all_ids) - len(set(all_ids))} duplicates"
    
    for q in unified_datastore:
        assert q['subject'] in CANONICAL_SUBJECTS, f"Invalid subject {q['subject']} in {q['id']}"
        assert q['type'] in ['mcq', 'msq', 'nat'], f"Invalid type {q['type']} in {q['id']}"
        
    missing_assets = []
    for q in cleaned_new:
        imgs = re.findall(r'src="([^"]+)"', q['question'])
        for img in imgs:
            if not os.path.exists(img):
                missing_assets.append((q['id'], img))
    assert len(missing_assets) == 0, f"Missing asset images: {missing_assets}"
    print("  -> ALL 100% INTEGRITY ASSERTIONS PASSED PERFECTLY!")
    
    # -----------------------------------------------------------------
    # 8. Save Backup, Datastore, Aliases & Audit Report
    # -----------------------------------------------------------------
    print(f"\n[Step 6] Persisting Changes:")
    if not os.path.exists(backup_file):
        print(f"  - Creating backup at {backup_file}...")
        shutil.copyfile(master_path, backup_file)
        
    print(f"  - Saving unified {master_path}...")
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(unified_datastore, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saving updated {alias_path} ({len(aliases)} mappings)...")
    with open(alias_path, 'w', encoding='utf-8') as f:
        json.dump(aliases, f, ensure_ascii=False, indent=2)
        
    audit_report = {
        'initial_master_count': len(master),
        'upgraded_old_raw_zeal_questions': len(old_zeal_to_replace),
        'new_high_fidelity_added': len(cleaned_new),
        'final_master_count': len(unified_datastore),
        'net_expansion': len(unified_datastore) - len(master),
        'total_aliases_registered': len(aliases),
        'cross_paper_duplicates_count': len(cross_paper_duplicates),
        'cross_paper_duplicates': cross_paper_duplicates,
        'internal_duplicates_count': len(internal_duplicates),
        'internal_duplicates': internal_duplicates,
        'subject_breakdown': dict(Counter(q['subject'] for q in unified_datastore)),
        'category_breakdown': dict(Counter(q['category'] for q in unified_datastore))
    }
    with open(audit_report_path, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, ensure_ascii=False, indent=2)
        
    print(f"  - Audit report saved to {audit_report_path}")
    print("\n=================================================================")
    print("ALL OCR QUESTIONS SUCCESSFULLY MERGED & DEDUPLICATED!")
    print("=================================================================")

if __name__ == '__main__':
    main()
