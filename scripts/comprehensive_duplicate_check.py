# -*- coding: utf-8 -*-
import json
import re
from collections import defaultdict, Counter

def normalize(text):
    if not text:
        return ""
    # remove preamble like "answer: - 1/3). Q1"
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
    with open('previous_questions.json', 'r', encoding='utf-8') as f:
        pq = json.load(f)

    with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
        sq = json.load(f)

    print(f"============================================================")
    print(f"MASTER DUPLICATE AUDIT REPORT")
    print(f"Total in previous_questions.json: {len(pq)}")
    print(f"Total in data/sample_questions.json: {len(sq)}")
    print(f"============================================================\n")

    # 1. Duplicates inside previous_questions.json
    id_map = defaultdict(list)
    for q in pq:
        id_map[q['id']].append(q)
    dup_ids = {k: v for k, v in id_map.items() if len(v) > 1}
    print(f"1. ID Duplicates within previous_questions.json: {len(dup_ids)}")

    # Text duplicates inside PQ (excluding empty text)
    text_map = defaultdict(list)
    empty_count = 0
    for q in pq:
        norm = normalize(q.get('question', ''))
        if len(norm) < 10:
            empty_count += 1
            continue
        text_map[norm].append(q)

    pq_text_dups = {k: v for k, v in text_map.items() if len(v) > 1}
    print(f"2. Non-empty text duplicates within previous_questions.json: {len(pq_text_dups)}")
    print(f"   (Empty or trivial text count in PQ: {empty_count})")
    
    dup_pairs_pq = []
    for k, v in pq_text_dups.items():
        # filter out generic phrases like 'which of the following is true'
        if len(k.split()) < 8 and ('which' in k or 'following' in k or 'true' in k or 'false' in k):
            continue
        dup_pairs_pq.append((k, v))
        
    print(f"   Genuine internal text duplicate clusters: {len(dup_pairs_pq)}")
    for k, v in dup_pairs_pq[:10]:
        print(f"   - Cluster text: '{k[:70]}...'")
        for item in v:
            print(f"     ID: {item['id']} | Year: {item.get('year')} | Subj: {item.get('subject')} | Type: {item.get('type')}")

    # 2. Cross-duplicates: PQ vs SQ
    sq_norm_map = defaultdict(list)
    for q in sq:
        sq_norm_map[normalize(q.get('question', ''))].append(q)

    sq_ids = {q['id'] for q in sq}
    common_ids = [q['id'] for q in pq if q['id'] in sq_ids]
    print(f"\n3. Exact ID overlap between PQ and SQ: {len(common_ids)}")
    if common_ids:
        print(f"   Sample common IDs: {common_ids[:5]}")

    exact_cross_matches = []
    for q in pq:
        norm = normalize(q.get('question', ''))
        if len(norm) >= 15 and norm in sq_norm_map:
            exact_cross_matches.append((q, sq_norm_map[norm]))

    print(f"\n4. Exact text matches between PQ and SQ: {len(exact_cross_matches)}")
    for pq_item, sq_matches in exact_cross_matches[:10]:
        sq_item = sq_matches[0]
        print(f"   PQ [{pq_item['id']}] (Year {pq_item.get('year')}) == SQ [{sq_item['id']}] (Year {sq_item.get('year')})")
        print(f"   Snippet: {pq_item['question'][:80]}...\n")

    # 5. High fuzzy matches (> 85%) between PQ and SQ
    sq_word_list = [(q, get_words(q.get('question', ''))) for q in sq]
    pq_word_list = [(q, get_words(q.get('question', ''))) for q in pq]

    fuzzy_cross_matches = []
    for pq_item, pw in pq_word_list:
        if len(pw) < 8:
            continue
        norm = normalize(pq_item.get('question', ''))
        if norm in sq_norm_map:
            continue
        for sq_item, sw in sq_word_list:
            if len(sw) < 8:
                continue
            sim = jaccard(pw, sw)
            if sim >= 0.82:
                fuzzy_cross_matches.append((pq_item, sq_item, sim))

    print(f"\n5. Fuzzy cross-matches (>= 82% word overlap) between PQ and SQ: {len(fuzzy_cross_matches)}")
    for pq_item, sq_item, sim in fuzzy_cross_matches[:10]:
        print(f"   Sim {sim:.1%} | PQ [{pq_item['id']}] ({pq_item.get('year')} {pq_item.get('subject')}) vs SQ [{sq_item['id']}] ({sq_item.get('year')} {sq_item.get('subject')})")
        print(f"   PQ: {pq_item['question'][:75]}...")
        print(f"   SQ: {sq_item['question'][:75]}...\n")

if __name__ == '__main__':
    main()
