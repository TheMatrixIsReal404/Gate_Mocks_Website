# -*- coding: utf-8 -*-
import json
import os
import re
from collections import defaultdict, Counter

def normalize_text(text):
    if not text:
        return ""
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'```c|```', ' ', t)
    t = t.replace('$', ' ')
    t = t.lower()
    t = re.sub(r'[\s\W_]+', ' ', t)
    return t.strip()

def check_images(questions):
    imgs = []
    missing = []
    for q in questions:
        matches = re.findall(r'src="([^"]+)"', q.get('question', ''))
        for m in matches:
            imgs.append(m)
            if not os.path.exists(m):
                missing.append((q['id'], m))
    return imgs, missing

def main():
    with open('data/newly_extracted_core_cs_questions.json', 'r', encoding='utf-8') as f:
        new_qs = json.load(f)

    with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
        master = json.load(f)

    print("=================================================================")
    print("1. IMAGE INTEGRITY CHECK")
    imgs, missing = check_images(new_qs)
    print(f"Total embedded images: {len(imgs)}")
    print(f"Missing images: {len(missing)}")
    if missing:
        print(f"Sample missing: {missing[:5]}")
    print("=================================================================")

    print("\n2. ID UNIQUENESS IN NEW QUESTIONS")
    id_counts = Counter(q['id'] for q in new_qs)
    dup_ids = {k: v for k, v in id_counts.items() if v > 1}
    print(f"Total new questions: {len(new_qs)}")
    print(f"Unique IDs: {len(id_counts)}")
    print(f"Duplicated IDs: {len(dup_ids)}")
    print("=================================================================")

    print("\n3. SUBJECT & TOPIC NORMALIZATION")
    subjs = Counter(q.get('subject') for q in new_qs)
    print("Subjects present:", subjs)
    print("=================================================================")

    print("\n4. ANSWER KEY & TYPE VALIDATION")
    types = Counter(q.get('type') for q in new_qs)
    print("Types present:", types)
    invalid_keys = []
    for q in new_qs:
        t = q.get('type')
        opts = q.get('options', [])
        cor = q.get('correct', [])
        if t in ['mcq', 'msq']:
            if len(opts) < 2 and t == 'mcq' and not opts:
                pass # card without text options
            for k in cor:
                if isinstance(k, int) and (k < 0 or (opts and k >= len(opts))):
                    invalid_keys.append((q['id'], cor, len(opts)))
    print(f"Questions with out-of-bound keys: {len(invalid_keys)}")
    print("=================================================================")

if __name__ == '__main__':
    main()
