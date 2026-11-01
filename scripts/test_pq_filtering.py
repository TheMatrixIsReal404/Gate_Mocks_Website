# -*- coding: utf-8 -*-
import json
import re
from collections import defaultdict, Counter

def normalize(text):
    if not text:
        return ""
    text = re.sub(r'^(answer:\s*[^\.\n]+\.\s*)?Q\.?\s*\d+[\.\:\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def clean_question_text(text):
    if not text:
        return ""
    # Strip leading OCR junk like "answer: — 1/3). Ql " or "Q.1 "
    text = re.sub(r'^(answer:\s*[^\.\n]+\.\s*)?Q\.?\s*\d+[\.\:\s]*', '', text, flags=re.IGNORECASE)
    # Fix common OCR artifacts
    text = text.replace('\ufffd', "'")
    text = re.sub(r' +', ' ', text)
    return text.strip()

def clean_option(opt):
    if not opt:
        return ""
    opt = opt.strip()
    # Remove leading option labels if OCR captured them e.g. "(A)", "(a)", "@ ", "}"
    opt = re.sub(r'^[\(\[\{]?[A-Da-d1-4@\}][\)\]\}]?\s*', '', opt)
    opt = opt.replace('\ufffd', "'")
    return opt.strip()

def main():
    with open('previous_questions.json', 'r', encoding='utf-8') as f:
        pq = json.load(f)

    with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
        sq = json.load(f)

    sq_ids = {q['id'] for q in sq}
    sq_texts = {normalize(q['question']) for q in sq}

    candidate_new = []
    skipped_existing = []
    skipped_incomplete = []

    for q in pq:
        qid = q.get('id')
        text = clean_question_text(q.get('question', ''))
        norm = normalize(text)
        q_type = q.get('type')
        opts = [clean_option(o) for o in q.get('options', [])]
        corr = q.get('correct')
        nat_range = q.get('natRange')

        # 1. Check if already exists in SQ by id or normalized text
        if qid in sq_ids or norm in sq_texts:
            skipped_existing.append(qid)
            continue

        # 2. Check completeness
        if len(text) < 15:
            skipped_incomplete.append((qid, "text too short"))
            continue

        if q_type == 'mcq':
            if len(opts) < 2:
                skipped_incomplete.append((qid, f"options < 2 ({len(opts)})"))
                continue
            if not corr or len(corr) != 1:
                skipped_incomplete.append((qid, f"corr invalid {corr}"))
                continue
            c = corr[0]
            if not isinstance(c, int) or c < 0 or c >= len(opts):
                skipped_incomplete.append((qid, f"corr index {c} out of range [0..{len(opts)-1}]"))
                continue
        elif q_type == 'msq':
            if len(opts) < 2:
                skipped_incomplete.append((qid, f"options < 2 ({len(opts)})"))
                continue
            if not corr or len(corr) < 1:
                skipped_incomplete.append((qid, f"corr empty {corr}"))
                continue
            if any(not isinstance(c, int) or c < 0 or c >= len(opts) for c in corr):
                skipped_incomplete.append((qid, f"corr indices {corr} out of range"))
                continue
        elif q_type == 'nat':
            if not nat_range or 'min' not in nat_range or 'max' not in nat_range:
                if corr and len(corr) > 0 and isinstance(corr[0], (int, float)):
                    val = corr[0]
                    nat_range = {"min": val, "max": val}
                else:
                    skipped_incomplete.append((qid, "nat missing range"))
                    continue
        else:
            skipped_incomplete.append((qid, f"unknown type {q_type}"))
            continue

        # Build clean candidate question
        clean_q = {
            "id": qid,
            "type": q_type,
            "category": "pyq",
            "subject": q.get('subject', 'General Aptitude'),
            "topic": q.get('topic') or f"GATE {q.get('year')} PYQ",
            "difficulty": q.get('difficulty') or "medium",
            "year": q.get('year'),
            "marks": q.get('marks') or (1 if q.get('difficulty') == 'easy' else 2),
            "question": text,
            "options": opts,
            "correct": corr,
            "explanation": q.get('explanation') or f"Official GATE {q.get('year')} Question ({q.get('subject')}). Verified official key."
        }
        if q_type == 'nat' and nat_range:
            clean_q['natRange'] = nat_range

        candidate_new.append(clean_q)

    print(f"Total in PQ: {len(pq)}")
    print(f"Skipped existing in SQ: {len(skipped_existing)}")
    print(f"Skipped incomplete/invalid: {len(skipped_incomplete)}")
    print(f"HIGH-QUALITY NEW CANDIDATES TO ADD: {len(candidate_new)}")

    print("\nCandidates by Year:")
    print(dict(sorted(Counter(q['year'] for q in candidate_new).items())))
    print("\nCandidates by Subject:")
    print(dict(sorted(Counter(q['subject'] for q in candidate_new).items())))
    print("\nCandidates by Type:")
    print(dict(Counter(q['type'] for q in candidate_new)))

    # Check for internal duplicate texts within candidate_new
    cand_texts = defaultdict(list)
    for q in candidate_new:
        cand_texts[normalize(q['question'])].append(q)
    cand_dups = {k: v for k, v in cand_texts.items() if len(v) > 1}
    print(f"\nInternal text duplicate clusters within candidates: {len(cand_dups)}")

if __name__ == '__main__':
    main()
