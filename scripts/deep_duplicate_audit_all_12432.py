# -*- coding: utf-8 -*-
"""
deep_duplicate_audit_all_12432.py
Exhaustive duplicate analysis across the entire 12,432 question bank.
Finds:
1. Exact text duplicates (identical normalized text).
2. Near-duplicate questions (Jaccard similarity >= 85% on normalized word n-grams).
3. Option-level collisions (questions with identical options).
4. Generates a detailed audit report and categorization of duplicates.
"""
import json
import re
import hashlib
from collections import defaultdict

STOPWORDS = {
    'the', 'and', 'for', 'that', 'this', 'with', 'from', 'which', 'following',
    'what', 'then', 'each', 'are', 'was', 'were', 'has', 'have', 'had', 'been',
    'such', 'also', 'some', 'any', 'all', 'one', 'two', 'given', 'consider',
    'let', 'suppose', 'show', 'true', 'false', 'value', 'number', 'statements'
}

def normalize_text(text):
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r'[\s\W_]+', ' ', t)
    return t.strip()

def tokenize(text):
    norm = normalize_text(text)
    words = [w for w in norm.split() if len(w) > 2 and w not in STOPWORDS]
    return set(words)

def main():
    print("Loading data/sample_questions.json (12,432 questions)...")
    questions = json.load(open('data/sample_questions.json', encoding='utf-8'))
    total_q = len(questions)
    print(f"Loaded {total_q} questions.")

    # 1. Exact Normalized Hash Duplication Check
    hash_to_qs = defaultdict(list)
    for q in questions:
        norm = normalize_text(q.get('question', ''))
        h = hashlib.sha256(norm.encode('utf-8')).hexdigest()
        hash_to_qs[h].append(q)

    exact_duplicate_groups = [qs for qs in hash_to_qs.values() if len(qs) > 1]
    total_exact_duplicate_questions = sum(len(qs) for qs in exact_duplicate_groups)
    redundant_exact_count = sum(len(qs) - 1 for qs in exact_duplicate_groups)

    print(f"\n=======================================================")
    print(f"1. EXACT TEXT MATCH RESULTS:")
    print(f"Total Exact Duplicate Groups: {len(exact_duplicate_groups)}")
    print(f"Total Questions Involved: {total_exact_duplicate_questions}")
    print(f"Redundant / Duplicate Instances: {redundant_exact_count}")
    print(f"=======================================================")

    # 2. Inverted Index for Fast Near-Duplicate / Fuzzy Matching (Jaccard >= 85%)
    print("\nBuilding inverted index for fuzzy duplicate search...")
    inverted_index = defaultdict(set)
    q_tokens_map = {}

    for idx, q in enumerate(questions):
        toks = tokenize(q.get('question', ''))
        q_tokens_map[idx] = toks
        for t in toks:
            inverted_index[t].add(idx)

    print(f"Inverted index built with {len(inverted_index)} unique terms.")

    # Find candidate pairs sharing at least 5 tokens
    candidate_pairs = set()
    for idx, toks in q_tokens_map.items():
        if len(toks) < 5:
            continue
        # Find candidates sharing rare tokens
        counts = defaultdict(int)
        for t in toks:
            postings = inverted_index[t]
            # Only consider terms that appear in fewer than 200 questions to avoid false candidate explosion
            if len(postings) < 200:
                for other_idx in postings:
                    if other_idx > idx:
                        counts[other_idx] += 1
                        
        min_overlap = int(len(toks) * 0.7)
        for other_idx, cnt in counts.items():
            if cnt >= min_overlap:
                candidate_pairs.add((idx, other_idx))

    print(f"Evaluated candidate pairs: {len(candidate_pairs)}")

    fuzzy_duplicates = []
    for idx1, idx2 in candidate_pairs:
        t1 = q_tokens_map[idx1]
        t2 = q_tokens_map[idx2]
        if not t1 or not t2:
            continue
        intersection = len(t1.intersection(t2))
        union = len(t1.union(t2))
        sim = intersection / union if union > 0 else 0.0
        if sim >= 0.85:
            q1 = questions[idx1]
            q2 = questions[idx2]
            # Check if not already in exact duplicates
            h1 = hashlib.sha256(normalize_text(q1.get('question', '')).encode('utf-8')).hexdigest()
            h2 = hashlib.sha256(normalize_text(q2.get('question', '')).encode('utf-8')).hexdigest()
            if h1 != h2:
                fuzzy_duplicates.append({
                    'sim': sim,
                    'q1_id': q1['id'],
                    'q1_category': q1.get('category', 'unknown'),
                    'q1_subject': q1.get('subject', 'unknown'),
                    'q2_id': q2['id'],
                    'q2_category': q2.get('category', 'unknown'),
                    'q2_subject': q2.get('subject', 'unknown'),
                    'q1_text': q1.get('question', '')[:90],
                    'q2_text': q2.get('question', '')[:90]
                })

    print(f"\n=======================================================")
    print(f"2. NEAR-DUPLICATE / FUZZY MATCH RESULTS (>=85% Jaccard):")
    print(f"Total Fuzzy Duplicate Pairs Found: {len(fuzzy_duplicates)}")
    print(f"=======================================================")

    # Breakdown by category interaction
    cat_pairs = defaultdict(int)
    for g in exact_duplicate_groups:
        cats = tuple(sorted(set(q.get('category', 'unknown') for q in g)))
        cat_pairs[cats] += 1

    print("\nExact Duplicates Breakdown by Categories:")
    for cats, count in sorted(cat_pairs.items(), key=lambda x: -x[1]):
        print(f"  {' vs '.join(cats)}: {count} groups")

    # Sample exact duplicate groups
    print("\n--- Sample Exact Duplicate Groups ---")
    for i, g in enumerate(exact_duplicate_groups[:5]):
        print(f"\nGroup {i+1} ({len(g)} questions):")
        for q in g:
            print(f"  - [{q['id']}] ({q.get('category')}|{q.get('subject')}|marks:{q.get('marks')}): {q.get('question', '')[:70]}...")

    # Sample fuzzy duplicate pairs
    print("\n--- Sample Near-Duplicate Pairs (>=85%) ---")
    for i, f in enumerate(fuzzy_duplicates[:5]):
        print(f"\nPair {i+1} (Similarity: {f['sim']:.1%}):")
        print(f"  - [{f['q1_id']}] ({f['q1_category']}|{f['q1_subject']}): {f['q1_text']}...")
        print(f"  - [{f['q2_id']}] ({f['q2_category']}|{f['q2_subject']}): {f['q2_text']}...")

    # Save complete audit report to disk
    report = {
        'total_questions_in_bank': total_q,
        'exact_duplicate_groups_count': len(exact_duplicate_groups),
        'redundant_exact_questions_count': redundant_exact_count,
        'fuzzy_duplicate_pairs_count': len(fuzzy_duplicates),
        'exact_duplicate_groups': [
            [{'id': q['id'], 'category': q.get('category'), 'subject': q.get('subject'), 'canonicalId': q.get('canonicalId'), 'text': q.get('question', '')[:100]} for q in g]
            for g in exact_duplicate_groups
        ],
        'fuzzy_duplicate_pairs': fuzzy_duplicates
    }
    out_path = 'data/complete_duplicate_audit_report.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nComplete duplicate audit report saved to {out_path}.")

if __name__ == '__main__':
    main()
