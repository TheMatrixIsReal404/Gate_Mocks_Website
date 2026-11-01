# -*- coding: utf-8 -*-
import os
import sys
import json
import re
from collections import defaultdict, Counter
from parse_docx_mock import parse_mock_docx

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
    
    mock_questions = []
    for f in files:
        # e.g. GATE_CSE_Mock_Category1_Set1.docx -> cat1_set1
        m = re.search(r'Category(\d+)_Set(\d+)', f)
        cat_num = m.group(1) if m else '1'
        set_num = m.group(2) if m else '1'
        mock_id = f"mock-cat{cat_num}-set{set_num}"
        
        qs = parse_mock_docx(os.path.join(folder, f))
        for q in qs:
            qid = f"cat{cat_num}_s{set_num}_q{q['q_num']:02d}"
            q['id'] = qid
            q['mockId'] = mock_id
            q['paper'] = f"GATE CSE Mock Cat {cat_num} Set {set_num}"
            mock_questions.append((f, q))

    print(f"Total parsed mock questions: {len(mock_questions)}")
    
    # 1. Duplicates WITHIN the 650 mock questions
    print("\n--- 1. Checking Duplicates WITHIN Mock Questions (650 Qs) ---")
    mock_norm_map = defaultdict(list)
    for f, q in mock_questions:
        norm = normalize(q['question'])
        mock_norm_map[norm].append((f, q))
        
    internal_dups = {k: v for k, v in mock_norm_map.items() if len(v) > 1}
    print(f"Exact text duplicate clusters within mocks: {len(internal_dups)}")
    for k, v in internal_dups.items():
        print(f"Snippet: {k[:60]}... (count={len(v)})")
        for f, q in v:
            print(f"  [{f}] Q{q['q_num']} ({q['subject']}): {q['question'][:50]}")

    # Fuzzy similarity within mock questions
    print("\nChecking fuzzy similarity (> 82%) within mock questions...")
    fuzzy_internal = []
    for i in range(len(mock_questions)):
        f1, q1 = mock_questions[i]
        w1 = get_words(q1['question'])
        if len(w1) < 6: continue
        for j in range(i + 1, len(mock_questions)):
            f2, q2 = mock_questions[j]
            w2 = get_words(q2['question'])
            if len(w2) < 6: continue
            sim = jaccard(w1, w2)
            if sim >= 0.82:
                fuzzy_internal.append((f1, q1, f2, q2, sim))
    print(f"Fuzzy matches within mocks: {len(fuzzy_internal)}")
    for f1, q1, f2, q2, sim in fuzzy_internal[:5]:
        print(f"Sim {sim:.1%}: [{f1} Q{q1['q_num']}] vs [{f2} Q{q2['q_num']}]")

    # 2. Duplicates between mock questions and existing sample_questions.json
    print("\n--- 2. Checking Overlap with Existing Database (1,140 Qs) ---")
    with open('data/sample_questions.json', 'r', encoding='utf-8') as db_file:
        existing_qs = json.load(db_file)
    print(f"Existing questions in database: {len(existing_qs)}")

    sq_norm_map = defaultdict(list)
    for q in existing_qs:
        sq_norm_map[normalize(q['question'])].append(q)

    exact_cross = []
    for f, q in mock_questions:
        norm = normalize(q['question'])
        if norm in sq_norm_map:
            exact_cross.append((f, q, sq_norm_map[norm]))

    print(f"Exact text matches with existing database: {len(exact_cross)}")
    for f, q, matches in exact_cross:
        print(f"Match: [{f} Q{q['q_num']}] ({q['subject']}) matches existing [{matches[0]['id']}]")
        print(f"  Mock: {q['question'][:65]}...")
        print(f"  DB:   {matches[0]['question'][:65]}...")

    # Fuzzy matches with existing database
    print("\nChecking fuzzy similarity (> 82%) with existing database...")
    sq_words = [(q, get_words(q['question'])) for q in existing_qs]
    fuzzy_cross = []
    for f, q in mock_questions:
        qw = get_words(q['question'])
        if len(qw) < 6: continue
        norm = normalize(q['question'])
        if norm in sq_norm_map: continue
        for eq, ew in sq_words:
            if len(ew) < 6: continue
            sim = jaccard(qw, ew)
            if sim >= 0.82:
                fuzzy_cross.append((f, q, eq, sim))

    print(f"Fuzzy cross matches (> 82% overlap): {len(fuzzy_cross)}")
    for f, q, eq, sim in fuzzy_cross[:10]:
        print(f"Sim {sim:.1%}: [{f} Q{q['q_num']}] ({q['subject']}) vs [{eq['id']}] ({eq.get('subject')})")
        print(f"  Mock: {q['question'][:65]}...")
        print(f"  DB:   {eq['question'][:65]}...")

if __name__ == '__main__':
    main()
