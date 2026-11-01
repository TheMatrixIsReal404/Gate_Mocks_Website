# -*- coding: utf-8 -*-
import json
from collections import Counter
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.test_pq_filtering import normalize, clean_question_text, clean_option

with open('previous_questions.json', 'r', encoding='utf-8') as f:
    pq = json.load(f)

with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
    sq = json.load(f)

sq_ids = {q['id'] for q in sq}
sq_texts = {normalize(q['question']) for q in sq}

new_candidates = []
seen_cand_texts = set()

for q in pq:
    qid = q.get('id')
    text = clean_question_text(q.get('question', ''))
    # Clean trailing leaked question if any
    import re
    m = re.search(r'[\r\n]+\s*Q\.?\s*(\d+)[\.\,\s]', text)
    if m:
        text = text[:m.start()].strip()
        
    norm = normalize(text)
    q_type = q.get('type')
    opts = [clean_option(o) for o in q.get('options', [])]
    corr = q.get('correct')
    nat_range = q.get('natRange')

    if qid in sq_ids or norm in sq_texts or norm in seen_cand_texts:
        continue

    if len(text) < 15:
        continue

    if q_type == 'mcq':
        if len(opts) < 2 or not corr or len(corr) != 1:
            continue
        c = corr[0]
        if not isinstance(c, int) or c < 0 or c >= len(opts):
            continue
    elif q_type == 'msq':
        if len(opts) < 2 or not corr or len(corr) < 1:
            continue
        if any(not isinstance(c, int) or c < 0 or c >= len(opts) for c in corr):
            continue
    elif q_type == 'nat':
        if not nat_range or 'min' not in nat_range or 'max' not in nat_range:
            if corr and len(corr) > 0 and isinstance(corr[0], (int, float)):
                val = corr[0]
                nat_range = {"min": val, "max": val}
            else:
                continue
    else:
        continue

    seen_cand_texts.add(norm)

    # Explanation formatting
    expl = q.get('explanation') or ""
    if not expl or len(expl.strip()) < 5:
        if q_type == 'mcq':
            opt_val = opts[corr[0]] if 0 <= corr[0] < len(opts) else ""
            expl = f"Official GATE {q.get('year')} Key: Option ({chr(65+corr[0])}) is the correct answer. {opt_val}"
        elif q_type == 'nat':
            expl = f"Official GATE {q.get('year')} Key: Numerical answer is {nat_range['min'] if nat_range['min'] == nat_range['max'] else str(nat_range['min']) + ' to ' + str(nat_range['max'])}."
        elif q_type == 'msq':
            opt_vals = [chr(65+c) for c in corr]
            expl = f"Official GATE {q.get('year')} Key: Options ({', '.join(opt_vals)}) are correct."

    paper_name = f"GATE {q.get('year')}"
    if 'CS1' in qid or 'S1' in qid:
        paper_name += " Set 1"
    elif 'CS2' in qid or 'S2' in qid:
        paper_name += " Set 2"
    elif 'S3' in qid:
        paper_name += " Set 3"

    clean_item = {
        "id": qid,
        "type": q_type,
        "category": "pyq",
        "subject": q.get('subject') if q.get('subject') != 'General Aptitude' else 'Aptitude',
        "topic": q.get('topic') or f"GATE {q.get('year')} PYQ",
        "difficulty": q.get('difficulty') or "medium",
        "year": q.get('year'),
        "paper": paper_name,
        "marks": q.get('marks') or (1 if q.get('difficulty') == 'easy' else 2),
        "question": text,
        "options": opts,
        "correct": corr,
        "explanation": expl
    }
    if q_type == 'nat':
        clean_item['natRange'] = nat_range

    new_candidates.append(clean_item)

print(f"Total new valid unique candidates: {len(new_candidates)}")
combined = sq + new_candidates
print(f"Total combined questions in database: {len(combined)}")

print("\nCombined Total by Year:")
by_year = Counter(q.get('year') for q in combined)
print(dict(sorted(by_year.items(), key=lambda x: str(x[0]))))

print("\nCombined Total by Subject:")
by_sub = Counter(q.get('subject') for q in combined)
print(dict(sorted(by_sub.items())))

print("\nCombined Total by Type:")
by_t = Counter(q.get('type') for q in combined)
print(dict(by_t))

print("\nCombined Total by Difficulty:")
by_d = Counter(q.get('difficulty') for q in combined)
print(dict(by_d))
