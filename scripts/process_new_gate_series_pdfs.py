# -*- coding: utf-8 -*-
"""
process_new_gate_series_pdfs.py
Extracts, structures, and deduplicates questions from:
- go25_weeklyquiz_sol.pdf
- go25_testseries_sol.pdf
against the existing 10,060-question bank in data/sample_questions.json.
"""
import pymupdf
import re
import json
import hashlib
from collections import Counter

SUBJECT_KEYWORDS = [
    (['c-programming', 'c programming', 'pointer', 'storage class', 'recursion'], 'C Programming'),
    (['algorithms', 'asymptotic', 'sorting', 'greedy', 'dynamic programming', 'divide and conquer'], 'Algorithms'),
    (['data structures', 'dsa', 'stack', 'queue', 'tree', 'heap', 'hashing', 'graph'], 'Data Structures'),
    (['relational', 'functional', 'normalization', 'sql', 'dbms', 'transaction', 'acid'], 'DBMS'),
    (['operating system', 'process', 'thread', 'deadlock', 'memory management', 'paging', 'virtual memory'], 'Operating Systems'),
    (['computer network', 'subnetting', 'ip address', 'routing', 'tcp', 'udp', 'sliding window'], 'Computer Networks'),
    (['co and architecture', 'computer organization', 'pipeline', 'cache', 'instruction', 'addressing mode'], 'Computer Organization'),
    (['digital logic', 'boolean algebra', 'multiplexer', 'combinational', 'k-map', 'flip-flop', 'counter'], 'Digital Logic'),
    (['theory of computation', 'finite automata', 'context free', 'fa, cfl', 'turing', 'cfg', 'pda', 'regular language'], 'Theory of Computation'),
    (['compiler', 'parser', 'syntax', 'lexical', 'lr(0)', 'lr(1)', 'slr', 'lalr', 'three address code'], 'Compiler Design'),
    (['propositional', 'lattice', 'poset', 'set theory', 'functions', 'relations', 'first order logic', 'discrete'], 'Discrete Mathematics'),
    (['calculus', 'probability', 'linear algebra', 'eigenvalue', 'matrix', 'derivative', 'integral'], 'Engineering Mathematics'),
    (['aptitude', 'verbal', 'quantitative', 'reasoning', 'analytical', 'numerical'], 'Aptitude')
]

def map_subject_from_title_and_text(title, text):
    combined = (title + " " + text).lower()
    for kw_list, sub in SUBJECT_KEYWORDS:
        if any(kw in combined for kw in kw_list):
            return sub
    return 'Engineering Mathematics'

def normalize_text(text):
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r'[\s\W_]+', ' ', t)
    return t.strip()

def tokenize(text):
    norm = normalize_text(text)
    return set([w for w in norm.split() if len(w) > 2])

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    u = len(set1.union(set2))
    return len(set1.intersection(set2)) / u if u > 0 else 0.0

def clean_body(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'GO CLASSES CS (?:TEST SERIES )?2025[^\n]*\n', '', text)
    text = re.sub(r'DURATION\s+MAX MARKS\s+(?:TOTAL )?QUESTIONS\s*\n\s*\d+\s*Mins\s*\d+\s*\d+\s*\n', '', text)
    text = re.sub(r'\n\s*TECHNICAL(?:\s+SECTION)?\s*\n', '\n', text)
    text = re.sub(r'\n\s*APTITUDE(?:\s+SECTION)?\s*\n', '\n', text)
    text = re.sub(r'\n\s*GENERAL APTITUDE SECTION\s*\n', '\n', text)
    return text.strip()

def parse_pdf_file(pdf_path, source_label, exact_hashes, token_cache):
    doc = pymupdf.open(pdf_path)
    print(f"\nProcessing {source_label}: {len(doc)} pages...")
    
    current_title = source_label
    all_pages = []
    
    for p in range(len(doc)):
        txt = doc[p].get_text('text', sort=True)
        m = re.search(r'GO CLASSES CS (?:TEST SERIES )?2025\s*\|\s*([^|\n]+)(?:\s*\|\s*([^\n]+))?', txt, re.I)
        if m:
            t1 = m.group(1).strip()
            t2 = m.group(2).strip() if m.group(2) else ""
            current_title = (t1 + (" - " + t2 if t2 else "")).strip()
            
        all_pages.append({
            'page': p + 1,
            'title': current_title,
            'text': txt
        })
        
    # Group continuous pages by title
    test_blocks = []
    curr_test = {'title': all_pages[0]['title'], 'text': ""}
    for pg in all_pages:
        if pg['title'] != curr_test['title']:
            test_blocks.append(curr_test)
            curr_test = {'title': pg['title'], 'text': ""}
        curr_test['text'] += f"\n---PAGE_{pg['page']}---\n" + pg['text']
    test_blocks.append(curr_test)
    
    print(f"Grouped into {len(test_blocks)} test sections.")
    
    pattern = r'(?:\n|^)\s*Q\.(\d+)\s+(?:.*?\s+)?(MCQ|MSQ|NAT)\s*\|\s*(\+[0-9\.]+)(?:\s*[\-\–\—][0-9\.]+)?[^\n]*\n'
    
    extracted = []
    duplicates = []
    q_counter = 0
    
    for tb in test_blocks:
        title = tb['title']
        full_text = tb['text']
        tokens = list(re.finditer(pattern, full_text, re.I))
        
        for i in range(len(tokens)):
            match = tokens[i]
            q_num = int(match.group(1))
            q_type = match.group(2).lower()
            marks_str = match.group(3)
            marks = 2 if '2' in marks_str else 1
            
            start_pos = match.end()
            end_pos = tokens[i+1].start() if i + 1 < len(tokens) else len(full_text)
            raw_block = full_text[start_pos:end_pos].strip()
            
            # Answer extraction
            ans_match = re.search(r'Correct Answer\s*:\s*([^\n\r]+)', raw_block, re.I)
            ans_raw = ""
            if ans_match:
                ans_raw = ans_match.group(1).replace('Discuss', '').strip()
                body = raw_block[:ans_match.start()].strip()
                explanation = raw_block[ans_match.end():].replace('Discuss', '').strip()
            else:
                body = raw_block
                explanation = ""
                
            body = clean_body(body)
            body = re.sub(r'---PAGE_\d+---', '', body).strip()
            explanation = clean_body(explanation)
            explanation = re.sub(r'---PAGE_\d+---', '', explanation).strip()
            
            # Options A. B. C. D.
            opt_matches = list(re.finditer(r'(?:^|\n)\s*([A-D])\.\s+', body))
            options = []
            if len(opt_matches) >= 2:
                q_text = body[:opt_matches[0].start()].strip()
                for j in range(len(opt_matches)):
                    ostart = opt_matches[j].end()
                    oend = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(body)
                    options.append(body[ostart:oend].strip())
            else:
                q_text = body.strip()
                options = []
                if q_type != 'nat' and not options:
                    q_type = 'nat'
                    
            if len(q_text) < 20:
                continue
                
            # Parse correct answer
            correct = []
            has_key = False
            first_ans = ans_raw.split('\n')[0].strip()
            
            if q_type == 'mcq':
                let_m = re.search(r'\b([A-D])\b', first_ans.upper())
                if let_m:
                    correct = [ord(let_m.group(1)) - ord('A')]
                    has_key = True
            elif q_type == 'msq':
                letters = re.findall(r'[A-D]', first_ans.upper())
                if letters:
                    correct = sorted(list(set([ord(l) - ord('A') for l in letters])))
                    has_key = True
            else: # nat
                range_m = re.search(r'([0-9\.\-]+)\s*:\s*([0-9\.\-]+)', first_ans)
                if range_m:
                    try:
                        v1 = float(range_m.group(1))
                        v2 = float(range_m.group(2))
                        correct = [v1, v2] if v1 != v2 else [v1]
                        has_key = True
                    except:
                        pass
                else:
                    single_m = re.search(r'([0-9\.\-]+)', first_ans)
                    if single_m:
                        try:
                            correct = [float(single_m.group(1))]
                            has_key = True
                        except:
                            pass
                            
            # Convert mcq with multiple keys to msq
            if q_type == 'mcq' and len(correct) > 1:
                q_type = 'msq'
                
            # Bounds check
            if q_type in ['mcq', 'msq']:
                if len(options) < 2:
                    continue
                if any(isinstance(k, int) and (k < 0 or k >= len(options)) for k in correct):
                    continue
                    
            # DEDUPLICATION CHECK
            q_hash = hashlib.sha256(normalize_text(q_text).encode('utf-8')).hexdigest()
            if q_hash in exact_hashes:
                duplicates.append({
                    'reason': 'Exact hash match',
                    'original_id': exact_hashes[q_hash],
                    'source': source_label,
                    'title': title,
                    'snippet': q_text[:80]
                })
                continue
                
            q_tokens = tokenize(q_text)
            is_fuzzy = False
            if len(q_tokens) >= 5:
                for orig_id, orig_tokens in token_cache:
                    sim = jaccard_similarity(q_tokens, orig_tokens)
                    if sim >= 0.85:
                        duplicates.append({
                            'reason': f'Fuzzy match ({sim:.2%})',
                            'original_id': orig_id,
                            'source': source_label,
                            'title': title,
                            'snippet': q_text[:80]
                        })
                        is_fuzzy = True
                        break
            if is_fuzzy:
                continue
                
            # New unique question!
            q_counter += 1
            cid = f"{source_label.lower()[:4]}_{q_counter:04d}"
            exact_hashes[q_hash] = cid
            if len(q_tokens) >= 5:
                token_cache.append((cid, q_tokens))
                
            subject = map_subject_from_title_and_text(title, q_text)
            difficulty = "easy" if marks == 1 else "medium"
            if "ADVANCE" in title.upper() or "HARD" in title.upper():
                difficulty = "hard"
                
            item = {
                'id': cid,
                'canonicalId': cid,
                'type': q_type,
                'category': 'test_series',
                'subject': subject,
                'topic': title,
                'difficulty': difficulty,
                'year': 2025,
                'marks': marks,
                'question': q_text,
                'options': options,
                'correct': correct,
                'explanation': explanation,
                'hasUsableKey': has_key,
                'source': f"{source_label} - {title}"
            }
            extracted.append(item)
            
    print(f"[{source_label}] Evaluated: {len(extracted) + len(duplicates)} | Duplicates: {len(duplicates)} | Unique: {len(extracted)}")
    return extracted, duplicates

def main():
    print("Loading 10,060 master questions for deduplication...")
    master = json.load(open('data/sample_questions.json', encoding='utf-8'))
    print(f"Master datastore loaded: {len(master)} questions.")
    
    exact_hashes = {}
    token_cache = []
    for q in master:
        qid = q['id']
        qtext = q.get('question', '')
        h = hashlib.sha256(normalize_text(qtext).encode('utf-8')).hexdigest()
        exact_hashes[h] = qid
        toks = tokenize(qtext)
        if len(toks) >= 5:
            token_cache.append((qid, toks))
            
    print(f"Deduplication index ready: {len(exact_hashes)} hashes, {len(token_cache)} token sets.")
    
    # 1. Weekly Quiz
    wq_path = r'G:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\go25_weeklyquiz_sol.pdf'
    wq_extracted, wq_duplicates = parse_pdf_file(wq_path, "GO_WQ25", exact_hashes, token_cache)
    
    # 2. GO 2025 Test Series
    ts_path = r'G:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\go25_testseries_sol.pdf'
    ts_extracted, ts_duplicates = parse_pdf_file(ts_path, "GO_TS25", exact_hashes, token_cache)
    
    all_extracted = wq_extracted + ts_extracted
    all_duplicates = wq_duplicates + ts_duplicates
    
    print("\n=======================================================")
    print(f"TOTAL EVALUATED: {len(all_extracted) + len(all_duplicates)}")
    print(f"TOTAL DUPLICATES DETECTED & FILTERED: {len(all_duplicates)}")
    print(f"TOTAL NEW UNIQUE QUESTIONS: {len(all_extracted)}")
    print("=======================================================")
    print("Types Breakdown:", Counter(q['type'] for q in all_extracted))
    print("Subjects Breakdown:", Counter(q['subject'] for q in all_extracted))
    print("Usable Keys:", Counter(q['hasUsableKey'] for q in all_extracted))
    
    out_extracted = 'data/newly_extracted_testseries_questions.json'
    with open(out_extracted, 'w', encoding='utf-8') as f:
        json.dump(all_extracted, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_extracted)} new unique questions to {out_extracted}")
    
    out_duplicates = 'data/newly_detected_duplicates.json'
    with open(out_duplicates, 'w', encoding='utf-8') as f:
        json.dump(all_duplicates, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_duplicates)} duplicates log to {out_duplicates}")

if __name__ == '__main__':
    main()
