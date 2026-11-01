# -*- coding: utf-8 -*-
"""
parse_all_zeal_sheets.py
Fast, instantaneous extraction and deduplication for all 12 Zeal Practice subjects.
"""
import pymupdf
import re
import json
import hashlib
import glob
import os
import sys
from collections import Counter

sys.stdout.reconfigure(line_buffering=True)

SUBJECT_DIR_MAP = {
    '1. Apti': 'Aptitude',
    '2. EM': 'Engineering Mathematics',
    '3. C programming': 'C Programming',
    '4. DM': 'Discrete Mathematics',
    '5. DSA': 'Data Structures',
    '6. DLD': 'Digital Logic',
    '7. COA': 'Computer Organization',
    '8. OS': 'Operating Systems',
    '9. TOC': 'Theory of Computation',
    '10. CD': 'Compiler Design',
    '11. DBMS': 'DBMS',
    '12. CN': 'Computer Networks'
}

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

def parse_answer_key_pdf(ans_pdf_path):
    doc = pymupdf.open(ans_pdf_path)
    txt = '\n'.join([doc[p].get_text() for p in range(len(doc))])
    matches = re.findall(r'(?:Q\s*)?(\d+)[\.\)]\s*([a-dA-D](?:\s*[\,\&]\s*[a-dA-D])*|[\-\d\.]+)', txt)
    answers = {}
    for qstr, vstr in matches:
        try:
            qnum = int(qstr)
            val = re.sub(r'\s+', '', vstr).upper()
            if qnum not in answers and len(val) <= 10:
                answers[qnum] = val
        except:
            pass
    return answers

def main():
    base_dir = r'G:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\Zeal_Practice Sheet 2023'
    
    print("Loading reference questions for deduplication...")
    master = json.load(open('data/sample_questions.json', encoding='utf-8'))
    if os.path.exists('data/go26_extracted_questions.json'):
        master += json.load(open('data/go26_extracted_questions.json', encoding='utf-8'))
        
    print(f"Total reference questions: {len(master)}")
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
            
    print(f"Deduplication registry ready with {len(exact_hashes)} hashes.")
    
    all_extracted = []
    all_duplicates = []
    global_counter = 0
    
    for dir_name, subject in SUBJECT_DIR_MAP.items():
        sub_path = os.path.join(base_dir, dir_name)
        if not os.path.exists(sub_path):
            continue
            
        pdfs = glob.glob(sub_path + '/**/*.pdf', recursive=True)
        q_pdfs = [p for p in pdfs if 'answer' not in p.lower() and 'solution' not in p.lower() and 'sloution' not in p.lower()]
        ans_pdfs = [p for p in pdfs if 'answer' in p.lower()]
        
        subj_answers = {}
        for ap in ans_pdfs:
            ans_map = parse_answer_key_pdf(ap)
            subj_answers.update(ans_map)
            
        print(f"Subject: {subject} ({len(q_pdfs)} Q sheets, {len(subj_answers)} answers loaded)")
        
        for qp in q_pdfs:
            q_fname = os.path.basename(qp)
            try:
                doc = pymupdf.open(qp)
            except Exception as e:
                continue
                
            q_text = ""
            for p in range(len(doc)):
                txt = doc[p].get_text('text', sort=True)
                q_text += f"\n---PAGE_{p+1}---\n" + txt
                
            matches = list(re.finditer(r'(?:^|\n)\s*(?:Q\.?\s*)?(\d+)[\.\)]\s+', q_text, re.I))
            if not matches:
                continue
                
            sheet_extracted = 0
            sheet_dups = 0
            
            for i in range(len(matches)):
                qnum = int(matches[i].group(1))
                start_pos = matches[i].end()
                end_pos = matches[i+1].start() if i + 1 < len(matches) else len(q_text)
                block = q_text[start_pos:end_pos].strip()
                block = re.sub(r'---PAGE_\d+---', '', block).strip()
                block = re.sub(r'\bPage\s+\d+\b', '', block, flags=re.I).strip()
                
                # Options
                opt_matches = list(re.finditer(r'(?:^|\n|\s{3,})\(([a-dA-D])\)\s*', block))
                options = []
                if len(opt_matches) >= 2:
                    body = block[:opt_matches[0].start()].strip()
                    for j in range(len(opt_matches)):
                        ostart = opt_matches[j].end()
                        oend = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(block)
                        options.append(block[ostart:oend].strip())
                    q_type = 'mcq'
                else:
                    body = block
                    options = []
                    q_type = 'nat'
                    
                if len(body) < 25 or len(body) > 3000:
                    continue
                    
                ans_str = subj_answers.get(qnum, '')
                correct = []
                has_key = False
                
                if ans_str:
                    letters = re.findall(r'[A-D]', ans_str)
                    if len(letters) > 1:
                        q_type = 'msq'
                        correct = sorted(list(set([ord(l) - ord('A') for l in letters])))
                        has_key = True
                    elif len(letters) == 1:
                        c_idx = ord(letters[0]) - ord('A')
                        if c_idx < len(options) or q_type == 'nat':
                            correct = [c_idx]
                            has_key = True
                    else:
                        try:
                            v = float(ans_str)
                            correct = [v]
                            q_type = 'nat'
                            has_key = True
                        except:
                            pass
                            
                if q_type in ['mcq', 'msq']:
                    if len(options) < 2:
                        continue
                    if any(isinstance(k, int) and (k < 0 or k >= len(options)) for k in correct):
                        continue
                        
                q_hash = hashlib.sha256(normalize_text(body).encode('utf-8')).hexdigest()
                if q_hash in exact_hashes:
                    sheet_dups += 1
                    all_duplicates.append({
                        'reason': 'Exact hash match',
                        'original_id': exact_hashes[q_hash],
                        'source': f'Zeal_{subject}',
                        'sheet': q_fname,
                        'snippet': body[:80]
                    })
                    continue
                    
                q_tokens = tokenize(body)
                is_fuzzy = False
                if len(q_tokens) >= 5:
                    for orig_id, orig_tokens in token_cache:
                        sim = jaccard_similarity(q_tokens, orig_tokens)
                        if sim >= 0.85:
                            sheet_dups += 1
                            all_duplicates.append({
                                'reason': f'Fuzzy match ({sim:.2%})',
                                'original_id': orig_id,
                                'source': f'Zeal_{subject}',
                                'sheet': q_fname,
                                'snippet': body[:80]
                            })
                            is_fuzzy = True
                            break
                if is_fuzzy:
                    continue
                    
                global_counter += 1
                cid = f"zeal_{subject.lower()[:3]}_{global_counter:04d}"
                exact_hashes[q_hash] = cid
                if len(q_tokens) >= 5:
                    token_cache.append((cid, q_tokens))
                    
                item = {
                    'id': cid,
                    'canonicalId': cid,
                    'type': q_type,
                    'category': 'test_series',
                    'subject': subject,
                    'topic': q_fname.replace('.pdf', ''),
                    'difficulty': 'medium',
                    'year': 2023,
                    'marks': 1 if len(body) < 250 else 2,
                    'question': body,
                    'options': options,
                    'correct': correct,
                    'explanation': '',
                    'hasUsableKey': has_key,
                    'source': f"Zeal Practice Sheet 2023 - {q_fname}"
                }
                all_extracted.append(item)
                sheet_extracted += 1
                
            print(f"   [{q_fname}] Unique: {sheet_extracted} | Duplicates: {sheet_dups}")
            
    print(f"\n=======================================================")
    print(f"ZEAL PRACTICE SHEETS SUMMARY:")
    print(f"Total Unique Questions Extracted: {len(all_extracted)}")
    print(f"Total Duplicates Filtered: {len(all_duplicates)}")
    print(f"=======================================================")
    print("Types Breakdown:", Counter(q['type'] for q in all_extracted))
    print("Subjects Breakdown:", Counter(q['subject'] for q in all_extracted))
    print("Usable Keys:", Counter(q['hasUsableKey'] for q in all_extracted))
    
    out_path = 'data/zeal_extracted_questions.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_extracted, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_extracted)} questions to {out_path}.")
    
    dup_path = 'data/zeal_duplicates.json'
    with open(dup_path, 'w', encoding='utf-8') as f:
        json.dump(all_duplicates, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_duplicates)} duplicates to {dup_path}.")

if __name__ == '__main__':
    main()
