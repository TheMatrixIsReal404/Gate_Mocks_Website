# -*- coding: utf-8 -*-
import json
import re
import sys
from collections import defaultdict, Counter

def normalize(text):
    if not text:
        return ""
    text = re.sub(r'[\$\`\#\*\_\{\}\\\(\)\[\]\:\,\.\?\!\;\"]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def get_words(text):
    return set(normalize(text).split())

def jaccard(s1, s2):
    if not s1 or not s2:
        return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def main():
    with open('previous_questions.json', 'r', encoding='utf-8') as f:
        pq = json.load(f)

    with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
        sq = json.load(f)

    print(f"Total PQ count: {len(pq)}")
    print(f"Total SQ count: {len(sq)}")

    # 1. ID Overlap
    sq_ids = {q['id']: q for q in sq}
    pq_ids = {q['id']: q for q in pq}
    common_ids = set(sq_ids.keys()).intersection(set(pq_ids.keys()))
    print(f"\n1. ID Overlap between SQ and PQ: {len(common_ids)}")
    if common_ids:
        print(f"   Sample common IDs: {list(common_ids)[:10]}")

    # 2. Duplicate IDs within PQ
    id_counts = Counter(q['id'] for q in pq)
    dup_ids = {k: v for k, v in id_counts.items() if v > 1}
    print(f"\n2. Duplicate IDs inside PQ: {len(dup_ids)}")

    # 3. Exact text duplicates inside PQ
    norm_pq = defaultdict(list)
    for q in pq:
        norm_pq[normalize(q.get('question', ''))].append(q)
    pq_text_dups = {k: v for k, v in norm_pq.items() if len(v) > 1}
    print(f"\n3. Exact text duplicates inside PQ: {len(pq_text_dups)}")
    for k, v in list(pq_text_dups.items())[:10]:
        print(f"   Snippet: '{k[:70]}...' (count={len(v)})")
        for item in v:
            print(f"     -> id: {item['id']}, year: {item.get('year')}, subject: {item.get('subject')}")

    # 4. Exact text matches between SQ and PQ
    sq_norm_map = defaultdict(list)
    for q in sq:
        sq_norm_map[normalize(q.get('question', ''))].append(q)

    exact_cross = []
    for q in pq:
        n = normalize(q.get('question', ''))
        if n in sq_norm_map:
            exact_cross.append((q, sq_norm_map[n]))

    print(f"\n4. Exact text matches between PQ and SQ: {len(exact_cross)}")
    for pq_item, sq_matches in exact_cross[:10]:
        sq_item = sq_matches[0]
        print(f"   PQ [{pq_item['id']}] (Year {pq_item.get('year')}, {pq_item.get('subject')})")
        print(f"   == SQ [{sq_item['id']}] (Year {sq_item.get('year')}, {sq_item.get('subject')})")
        print(f"   Text: {pq_item['question'][:80]}...\n")

    # 5. Fuzzy text matches (> 80% similarity) between PQ and SQ
    print("\n5. Checking high fuzzy similarity (> 85%) between PQ and SQ...")
    sq_words = [(q, get_words(q.get('question', ''))) for q in sq]
    pq_words = [(q, get_words(q.get('question', ''))) for q in pq]

    fuzzy_matches = []
    for pq_item, pw in pq_words:
        if len(pw) < 6:
            continue
        # Only check against SQ if not already an exact match
        n = normalize(pq_item.get('question', ''))
        if n in sq_norm_map:
            continue
        for sq_item, sw in sq_words:
            if len(sw) < 6:
                continue
            sim = jaccard(pw, sw)
            if sim >= 0.85:
                fuzzy_matches.append((pq_item, sq_item, sim))

    print(f"   Fuzzy matches (> 85%) found between PQ and SQ: {len(fuzzy_matches)}")
    for pq_item, sq_item, sim in fuzzy_matches[:10]:
        print(f"   Sim: {sim:.2%}")
        print(f"   PQ [{pq_item['id']}] ({pq_item.get('year')} {pq_item.get('subject')}): {pq_item['question'][:70]}...")
        print(f"   SQ [{sq_item['id']}] ({sq_item.get('year')} {sq_item.get('subject')}): {sq_item['question'][:70]}...")
        print()

    # 6. Quality & Schema validation of PQ
    print("\n6. PQ Schema & Quality Checks:")
    empty_q = [q['id'] for q in pq if not q.get('question') or len(q['question'].strip()) < 5]
    print(f"   Empty or very short questions: {len(empty_q)}")
    
    missing_correct = []
    invalid_type = []
    nat_without_range = []
    mcq_bad_options = []

    for q in pq:
        t = q.get('type')
        if t not in ('mcq', 'msq', 'nat'):
            invalid_type.append(q['id'])
        if t in ('mcq', 'msq'):
            opts = q.get('options', [])
            if not opts or len(opts) < 2:
                mcq_bad_options.append((q['id'], len(opts)))
            corr = q.get('correct', [])
            if not isinstance(corr, list) or len(corr) == 0:
                missing_correct.append(q['id'])
        elif t == 'nat':
            corr = q.get('correct')
            natR = q.get('natRange')
            if corr is None and not natR:
                nat_without_range.append(q['id'])

    print(f"   Invalid type: {len(invalid_type)}")
    print(f"   MCQ/MSQ with bad options (< 2): {len(mcq_bad_options)}")
    if mcq_bad_options:
        print(f"     Sample: {mcq_bad_options[:5]}")
    print(f"   MCQ/MSQ with missing correct answer: {len(missing_correct)}")
    if missing_correct:
        print(f"     Sample: {missing_correct[:5]}")
    print(f"   NAT missing both correct and natRange: {len(nat_without_range)}")
    if nat_without_range:
        print(f"     Sample: {nat_without_range[:5]}")

    # Check needsReview flag in PQ
    needs_review = [q['id'] for q in pq if q.get('needsReview')]
    print(f"   Questions marked needsReview: {len(needs_review)}")

if __name__ == '__main__':
    main()
