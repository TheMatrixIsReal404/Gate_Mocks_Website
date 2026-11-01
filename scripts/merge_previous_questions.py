# -*- coding: utf-8 -*-
"""
Ingestion & Merge Engine for previous_questions.json.
Filters duplicates, validates data integrity, and merges authentic PYQs into data/sample_questions.json.
"""

import os
import sys
import json
import re
from collections import defaultdict, Counter

VALID_SUBJECTS = {
    "Algorithms",
    "Aptitude",
    "General Aptitude",
    "C Programming",
    "Compiler Design",
    "Computer Networks",
    "Computer Organization",
    "DBMS",
    "Data Structures",
    "Digital Logic",
    "Discrete Mathematics",
    "Engineering Mathematics",
    "Operating Systems",
    "Theory of Computation"
}

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

def clean_question_text(text):
    if not text:
        return ""
    # Strip leading OCR junk like "answer: - 1/3). Ql " or "Q.1 "
    text = re.sub(r'^(answer:\s*[^\.\n]+\.\s*)?Q\.?\s*\d+[\.\:\s]*', '', text, flags=re.IGNORECASE)
    # Strip trailing question that got concatenated across page breaks
    m = re.search(r'[\r\n]+\s*Q\.?\s*(\d+)[\.\,\s]', text)
    if m:
        text = text[:m.start()].strip()
    # Normalize common Unicode characters & OCR artifacts
    text = text.replace('\ufffd', "'")
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def clean_option(opt):
    if not opt:
        return ""
    opt = str(opt).strip()
    # Remove leading OCR junk e.g. "} 21" -> "21"
    opt = re.sub(r'^[}\~@]\s*', '', opt)
    # Remove leading "(A) ", "(B) ", "A. ", "B. " if explicitly followed by whitespace
    opt = re.sub(r'^[\(\[]?[A-Da-d][\)\]\.\:]\s+', '', opt)
    opt = opt.replace('\ufffd', "'")
    opt = opt.replace('\u2018', "'").replace('\u2019', "'")
    opt = opt.replace('\u201c', '"').replace('\u201d', '"')
    opt = opt.replace('\u2013', '-').replace('\u2014', '-')
    return opt.strip()

def validate_question(q):
    qid = q.get("id")
    assert qid, "Question missing id"
    assert q.get("type") in ["mcq", "msq", "nat"], f"{qid}: Invalid type {q.get('type')}"
    assert q.get("subject") in VALID_SUBJECTS or q.get("subject") == "Aptitude", f"{qid}: Invalid subject {q.get('subject')}"
    assert q.get("difficulty") in ["easy", "medium", "hard"], f"{qid}: Invalid difficulty {q.get('difficulty')}"
    assert q.get("marks") in [1, 2], f"{qid}: Invalid marks {q.get('marks')}"
    assert q.get("question") and len(q["question"].strip()) >= 15, f"{qid}: Question text too short ({len(q['question'].strip())})"
    assert q.get("explanation") and len(q["explanation"].strip()) >= 5, f"{qid}: Empty explanation"

    if q["type"] in ["mcq", "msq"]:
        opts = q.get("options", [])
        assert len(opts) >= 2, f"{qid}: Too few options ({len(opts)})"
        for idx, opt in enumerate(opts):
            assert len(str(opt).strip()) > 0, f"{qid}: Empty option at index {idx}"
        corrs = q.get("correct", [])
        assert len(corrs) >= 1, f"{qid}: Missing correct answer"
        for c in corrs:
            assert isinstance(c, int), f"{qid}: Correct answer index not int ({c})"
            assert 0 <= c < len(opts), f"{qid}: Correct index {c} out of bounds (len {len(opts)})"
    elif q["type"] == "nat":
        assert "natRange" in q, f"{qid}: NAT question missing natRange"
        nr = q["natRange"]
        assert "min" in nr and "max" in nr, f"{qid}: natRange missing min/max"
        assert isinstance(nr["min"], (int, float)) and isinstance(nr["max"], (int, float)), f"{qid}: non-numeric min/max"

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pq_path = os.path.join(base_dir, 'previous_questions.json')
    sq_path = os.path.join(base_dir, 'data', 'sample_questions.json')
    added_path = os.path.join(base_dir, 'data', 'gate_pyqs_added.json')

    with open(pq_path, 'r', encoding='utf-8') as f:
        pq = json.load(f)

    # Base original 546 questions
    with open(sq_path, 'r', encoding='utf-8') as f:
        current_sq = json.load(f)

    # If already merged in previous run, retrieve original 546
    if os.path.exists(added_path):
        with open(added_path, 'r', encoding='utf-8') as f:
            prev_added = json.load(f)
        prev_added_ids = {q['id'] for q in prev_added}
        orig_sq = [q for q in current_sq if q['id'] not in prev_added_ids]
    else:
        orig_sq = current_sq

    print(f"=== GATE CSE QUESTION INGESTION & DEDUPLICATION ENGINE ===")
    print(f"Loaded {len(pq)} questions from previous_questions.json")
    print(f"Base authentic questions in database: {len(orig_sq)}")

    sq_ids = {q['id'] for q in orig_sq}
    sq_texts = {normalize(q['question']) for q in orig_sq}
    sq_words = [(q, get_words(q['question'])) for q in orig_sq]

    candidate_new = []
    cand_words_list = []
    seen_cand_texts = set()
    skipped_existing = []
    skipped_incomplete = []
    skipped_fuzzy = []

    for q in pq:
        qid = q.get('id')
        text = clean_question_text(q.get('question', ''))
        norm = normalize(text)
        q_type = q.get('type')
        opts = [clean_option(o) for o in q.get('options', [])]
        corr = q.get('correct')
        nat_range = q.get('natRange')

        # 1. Deduplication check: existing in sample_questions.json or already in this batch
        if qid in sq_ids:
            skipped_existing.append((qid, "Existing ID in database"))
            continue
        if norm in sq_texts:
            skipped_existing.append((qid, "Exact text match in database"))
            continue
        if norm in seen_cand_texts:
            skipped_existing.append((qid, "Duplicate text within candidate batch"))
            continue

        # 2. Text quality check
        if len(text) < 15:
            skipped_incomplete.append((qid, "Text < 15 characters"))
            continue

        # 3. Fuzzy similarity check against existing database (> 80% word overlap)
        q_words = get_words(text)
        if len(q_words) >= 6:
            is_fuzzy_dup = False
            for sq_q, sq_w in sq_words:
                if len(sq_w) >= 6 and jaccard(q_words, sq_w) >= 0.80:
                    skipped_fuzzy.append((qid, sq_q['id'], jaccard(q_words, sq_w)))
                    is_fuzzy_dup = True
                    break
            if is_fuzzy_dup:
                continue

            # Fuzzy check within candidates batch
            for cand_id, cand_w in cand_words_list:
                if len(cand_w) >= 6 and jaccard(q_words, cand_w) >= 0.85:
                    is_fuzzy_dup = True
                    skipped_fuzzy.append((qid, cand_id, jaccard(q_words, cand_w)))
                    break
            if is_fuzzy_dup:
                continue

        # 4. Type-specific checks
        if q_type == 'mcq':
            if len(opts) < 2:
                skipped_incomplete.append((qid, f"Options count {len(opts)} < 2"))
                continue
            if any(len(o) == 0 for o in opts):
                skipped_incomplete.append((qid, "Contains empty option string"))
                continue
            if not corr or len(corr) != 1:
                skipped_incomplete.append((qid, f"Correct count {len(corr) if corr else 0} != 1"))
                continue
            c = corr[0]
            if not isinstance(c, int) or c < 0 or c >= len(opts):
                skipped_incomplete.append((qid, f"Correct index {c} out of range [0..{len(opts)-1}]"))
                continue
        elif q_type == 'msq':
            if len(opts) < 2:
                skipped_incomplete.append((qid, f"Options count {len(opts)} < 2"))
                continue
            if any(len(o) == 0 for o in opts):
                skipped_incomplete.append((qid, "Contains empty option string"))
                continue
            if not corr or len(corr) < 1:
                skipped_incomplete.append((qid, "Empty correct answers for MSQ"))
                continue
            if any(not isinstance(c, int) or c < 0 or c >= len(opts) for c in corr):
                skipped_incomplete.append((qid, f"Correct indices out of range [0..{len(opts)-1}]"))
                continue
        elif q_type == 'nat':
            if not nat_range or 'min' not in nat_range or 'max' not in nat_range:
                if corr and len(corr) > 0 and isinstance(corr[0], (int, float)):
                    val = corr[0]
                    nat_range = {"min": val, "max": val}
                else:
                    skipped_incomplete.append((qid, "Missing NAT range/numeric value"))
                    continue
            else:
                try:
                    nat_range = {"min": float(nat_range['min']), "max": float(nat_range['max'])}
                except Exception:
                    skipped_incomplete.append((qid, "Non-numeric NAT min/max values"))
                    continue
        else:
            skipped_incomplete.append((qid, f"Unsupported question type: {q_type}"))
            continue

        seen_cand_texts.add(norm)
        cand_words_list.append((qid, q_words))

        # Subject normalization
        subj = q.get('subject', 'Aptitude')
        if subj == 'General Aptitude':
            subj = 'Aptitude'
        if subj not in VALID_SUBJECTS:
            subj = 'Aptitude'

        # Explanation generation
        expl = (q.get('explanation') or '').strip()
        if len(expl) < 5:
            if q_type == 'mcq':
                c_idx = corr[0]
                expl = f"Official GATE {q.get('year')} Key: Option ({chr(65+c_idx)}) is the correct answer. {opts[c_idx]}"
            elif q_type == 'nat':
                v_min, v_max = nat_range['min'], nat_range['max']
                range_str = f"{v_min}" if v_min == v_max else f"between {v_min} and {v_max}"
                expl = f"Official GATE {q.get('year')} Key: Numerical answer is {range_str}."
            elif q_type == 'msq':
                c_opts = [f"({chr(65+c)}) {opts[c]}" for c in corr]
                expl = f"Official GATE {q.get('year')} Key: Correct options are {', '.join(c_opts)}."

        # Paper designation
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
            "subject": subj,
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

        # Validate against schema
        validate_question(clean_item)
        candidate_new.append(clean_item)

    print(f"\n--- AUDIT SUMMARY ---")
    print(f"Skipped exact duplicates (already in database or batch): {len(skipped_existing)}")
    print(f"Skipped fuzzy duplicates (> 80% similarity with existing questions): {len(skipped_fuzzy)}")
    for f_qid, o_qid, sim in skipped_fuzzy[:5]:
        print(f"   - {f_qid} skipped (matches {o_qid} at {sim:.1%})")
    print(f"Skipped incomplete/missing keys: {len(skipped_incomplete)}")
    print(f"Clean, verified, distinct candidates ready to merge: {len(candidate_new)}")

    # Merge into database
    merged_questions = orig_sq + candidate_new
    print(f"\nFinal question count in master database: {len(merged_questions)}")

    # Write merged questions to sample_questions.json
    with open(sq_path, 'w', encoding='utf-8') as f:
        json.dump(merged_questions, f, indent=2, ensure_ascii=False)
    print(f"-> Successfully saved {len(merged_questions)} questions to {sq_path}")

    # Write newly added questions backup
    with open(added_path, 'w', encoding='utf-8') as f:
        json.dump(candidate_new, f, indent=2, ensure_ascii=False)
    print(f"-> Successfully saved {len(candidate_new)} added questions to {added_path}")

    # Breakdown of newly added questions
    print("\nAdded Questions Breakdown:")
    print("By Year:", dict(sorted(Counter(q['year'] for q in candidate_new).items())))
    print("By Subject:", dict(sorted(Counter(q['subject'] for q in candidate_new).items())))
    print("By Type:", dict(Counter(q['type'] for q in candidate_new)))
    print("By Difficulty:", dict(Counter(q['difficulty'] for q in candidate_new)))

if __name__ == '__main__':
    main()
