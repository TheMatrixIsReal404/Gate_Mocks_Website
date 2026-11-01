# -*- coding: utf-8 -*-
"""
Thorough duplicate detection across data/sample_questions.json.
Checks:
1. Exact ID duplicates
2. Normalized text duplicates
3. High Jaccard similarity (fuzzy duplicates > 80% word overlap)
4. Same-year duplicate questions
"""

import json
import re
from collections import defaultdict

def normalize(text):
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
    with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
        
    print(f"Total questions in database: {len(questions)}")
    
    # 1. Exact ID Duplicates
    id_counts = defaultdict(list)
    for q in questions:
        id_counts[q['id']].append(q)
    id_dups = {k: v for k, v in id_counts.items() if len(v) > 1}
    print(f"\n1. ID duplicates: {len(id_dups)}")
    for k, v in id_dups.items():
        print(f"   Duplicate ID: {k} (count={len(v)})")
        
    # 2. Normalized Text Duplicates
    text_counts = defaultdict(list)
    for q in questions:
        norm = normalize(q['question'])
        text_counts[norm].append(q)
    text_dups = {k: v for k, v in text_counts.items() if len(v) > 1}
    print(f"\n2. Normalized text exact duplicates: {len(text_dups)}")
    for k, v in text_dups.items():
        print(f"   Snippet: '{k[:70]}...'")
        for q in v:
            print(f"     -> ID: {q['id']}, Year: {q.get('year')}, Subject: {q.get('subject')}, Category: {q.get('category')}")
            
    # 3. Fuzzy Text Similarity (> 80% word overlap)
    print("\n3. Checking fuzzy similarity (> 80% word overlap across all pairs)...")
    word_sets = [(q, get_words(q['question'])) for q in questions]
    fuzzy_dups = []
    
    for i in range(len(word_sets)):
        q1, words1 = word_sets[i]
        if len(words1) < 4:
            continue
        for j in range(i + 1, len(word_sets)):
            q2, words2 = word_sets[j]
            if len(words2) < 4:
                continue
            sim = jaccard(words1, words2)
            if sim >= 0.80:
                fuzzy_dups.append((q1, q2, sim))
                
    print(f"   Fuzzy duplicates found: {len(fuzzy_dups)}")
    for q1, q2, sim in fuzzy_dups:
        print(f"   - Match ({sim:.2%}):")
        print(f"     A: [{q1['id']}] (Year: {q1.get('year')}, Subject: {q1.get('subject')}): {q1['question'][:65]}...")
        print(f"     B: [{q2['id']}] (Year: {q2.get('year')}, Subject: {q2.get('subject')}): {q2['question'][:65]}...")

if __name__ == '__main__':
    main()
