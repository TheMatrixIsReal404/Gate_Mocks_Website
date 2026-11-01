# -*- coding: utf-8 -*-
"""
parse_and_dedup_go25.py
Extracts all questions from gateoverflow25_testseries_sol.pdf, parses options, types, marks, answers,
and checks for exact & fuzzy duplicates against the existing questions bank.
"""
import pymupdf
import re
import json
import hashlib
from collections import Counter

SUBJECT_MAP = {
    'ALGORITHMS': 'Algorithms',
    'CALCULUS': 'Engineering Mathematics',
    'COMPILER DESIGN': 'Compiler Design',
    'COMPUTER NETWORKS': 'Computer Networks',
    'COMPUTER ORGANIZATION AND': 'Computer Organization',
    'DATA STRUCTURES': 'Data Structures',
    'DATABASES': 'DBMS',
    'DIGITAL LOGIC': 'Digital Logic',
    'DISCRETE MATHEMATICS': 'Discrete Mathematics',
    'LINEAR ALGEBRA': 'Engineering Mathematics',
    'MIX SUBJECTS': 'Engineering Mathematics',
    'MIXED SUBJECTS': 'Engineering Mathematics',
    'MOCK GATE': 'Mock',
    'OPERATING SYSTEMS': 'Operating Systems',
    'PROBABILITY': 'Engineering Mathematics',
    'PROGRAMMING IN C': 'C Programming',
    'QUANTITATIVE APTITUDE 1': 'Aptitude',
    'SPACIAL AND ANALYTICAL APTITUDE': 'Aptitude',
    'THEORY OF COMPUTATION': 'Theory of Computation',
    'VERBAL APTITUDE 1': 'Aptitude',
}

def normalize_text_for_hash(text):
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r'[\s\W_]+', ' ', t)
    return t.strip()

def tokenize(text):
    norm = normalize_text_for_hash(text)
    return set([w for w in norm.split() if len(w) > 2])

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def clean_question_body(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'---PAGE_\d+---', '', text)
    text = re.sub(r'GATE OVERFLOW CS TEST SERIES 2025[^\n]*\n', '', text)
    text = re.sub(r'DURATION\s+MAX MARKS\s+QUESTIONS\s*\n\s*\d+\s*Mins\s*\d+\s*\d+\s*\n', '', text)
    text = re.sub(r'\n\s*TECHNICAL\s*\n', '\n', text)
    text = re.sub(r'\n\s*APTITUDE\s*\n', '\n', text)
    return text.strip()

def main():
    print("Loading existing questions to build deduplication registry...")
    master_qs = json.load(open('data/sample_questions.json', encoding='utf-8'))
    pw_qs = json.load(open('data/pw_extracted_new_questions.json', encoding='utf-8'))
    
    existing_all = master_qs + pw_qs
    print(f"Total existing questions in memory: {len(existing_all)}")
    
    exact_hashes = {}
    token_cache = []
    
    for q in existing_all:
        q_id = q.get('id', '')
        q_text = q.get('question', '')
        h = hashlib.sha256(normalize_text_for_hash(q_text).encode('utf-8')).hexdigest()
        exact_hashes[h] = q_id
        tokens = tokenize(q_text)
        if len(tokens) >= 5:
            token_cache.append((q_id, tokens))
            
    print(f"Registry ready: {len(exact_hashes)} hashes, {len(token_cache)} token sets for fuzzy matching.")

    # Now parse Gate Overflow 2025 PDF
    pdf_path = r'G:\0.Gate_Lectures\0.2.Questions_Books_Practice_Materials\Practice Material (CSE)\Test Series\test series pdf\Gate CS 2027\gateoverflow25_testseries_sol.pdf'
    doc = pymupdf.open(pdf_path)
    print(f"Opened PDF with {len(doc)} pages.")
    
    current_subject = "General"
    current_test_title = "GO 2025 Test"
    
    all_pages = []
    for p in range(len(doc)):
        raw_text = doc[p].get_text('text', sort=True)
        m = re.search(r'GATE OVERFLOW CS TEST SERIES 2025\s*\|\s*([^|\n]+)(?:\s*\|\s*([^\n]+))?', raw_text)
        if m:
            sub_key = m.group(1).strip()
            for k, val in SUBJECT_MAP.items():
                if k in sub_key:
                    current_subject = val
                    break
            current_test_title = (sub_key + (" - " + m.group(2).strip() if m.group(2) else "")).strip()
            
        all_pages.append({
            'page': p + 1,
            'subject': current_subject,
            'test': current_test_title,
            'text': raw_text
        })
        
    # Group by test
    tests = {}
    for pg in all_pages:
        t_name = pg['test']
        if t_name not in tests:
            tests[t_name] = {'subject': pg['subject'], 'text': ""}
        tests[t_name]['text'] += f"\n---PAGE_{pg['page']}---\n" + pg['text']
        
    print(f"Grouped into {len(tests)} tests.")
    
    parsed_questions = []
    duplicates = []
    
    # Question delimiter pattern
    pattern = r'(?:\n|^)\s*Q\.(\d+)\s+(?:.*?\s+)?(MCQ|MSQ|NAT)\s*\|\s*(\+[0-9\.]+)(?:\s*[\-\–\—][0-9\.]+)?[^\n]*\n'
    
    q_counter = 0
    for t_name, t_data in tests.items():
        subject = t_data['subject']
        full_text = t_data['text']
        tokens = list(re.finditer(pattern, full_text, re.IGNORECASE))
        
        for i in range(len(tokens)):
            match = tokens[i]
            q_num = int(match.group(1))
            q_type = match.group(2).lower()
            marks_str = match.group(3)
            marks = 2 if '2' in marks_str else 1
            
            start_pos = match.end()
            end_pos = tokens[i+1].start() if i + 1 < len(tokens) else len(full_text)
            raw_block = full_text[start_pos:end_pos].strip()
            
            # Find Correct Answer
            ans_match = re.search(r'Correct Answer\s*:\s*([^\n\r]+)', raw_block, re.IGNORECASE)
            ans_raw = ""
            if ans_match:
                ans_raw = ans_match.group(1).replace('Discuss', '').strip()
                # body is before Correct Answer
                body = raw_block[:ans_match.start()].strip()
                explanation = raw_block[ans_match.end():].replace('Discuss', '').strip()
            else:
                body = raw_block
                explanation = ""
                
            body = clean_question_body(body)
            explanation = clean_question_body(explanation)
            
            # Options pattern
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
                    
            # Parse correct
            correct = []
            has_key = False
            first_ans_line = ans_raw.split('\n')[0].strip()
            
            if q_type == 'mcq':
                let_m = re.search(r'\b([A-D])\b', first_ans_line.upper())
                if let_m:
                    correct = [ord(let_m.group(1)) - ord('A')]
                    has_key = True
            elif q_type == 'msq':
                letters = re.findall(r'[A-D]', first_ans_line.upper())
                if letters:
                    correct = sorted(list(set([ord(l) - ord('A') for l in letters])))
                    has_key = True
            else: # nat
                range_m = re.search(r'([0-9\.\-]+)\s*:\s*([0-9\.\-]+)', first_ans_line)
                if range_m:
                    try:
                        v1 = float(range_m.group(1))
                        v2 = float(range_m.group(2))
                        correct = [v1, v2] if v1 != v2 else [v1]
                        has_key = True
                    except:
                        pass
                else:
                    single_m = re.search(r'([0-9\.\-]+)', first_ans_line)
                    if single_m:
                        try:
                            correct = [float(single_m.group(1))]
                            has_key = True
                        except:
                            pass
                            
            # Skip noise or empty questions
            if len(q_text) < 20:
                continue
                
            # DEDUPLICATION CHECK
            q_hash = hashlib.sha256(normalize_text_for_hash(q_text).encode('utf-8')).hexdigest()
            if q_hash in exact_hashes:
                duplicates.append({
                    'reason': 'Exact hash match',
                    'original_id': exact_hashes[q_hash],
                    'test': t_name,
                    'num': q_num,
                    'text_snippet': q_text[:80]
                })
                continue
                
            q_tokens = tokenize(q_text)
            is_fuzzy_dup = False
            if len(q_tokens) >= 5:
                for orig_id, orig_tokens in token_cache:
                    sim = jaccard_similarity(q_tokens, orig_tokens)
                    if sim >= 0.85:
                        duplicates.append({
                            'reason': f'Fuzzy match ({sim:.2%})',
                            'original_id': orig_id,
                            'test': t_name,
                            'num': q_num,
                            'text_snippet': q_text[:80]
                        })
                        is_fuzzy_dup = True
                        break
            if is_fuzzy_dup:
                continue
                
            # It's unique! Add to exact_hashes and token_cache to prevent duplicates within the PDF itself
            q_counter += 1
            cid = f"go25_ts_{q_counter:04d}"
            exact_hashes[q_hash] = cid
            if len(q_tokens) >= 5:
                token_cache.append((cid, q_tokens))
                
            difficulty = "EASY" if marks == 1 else "MEDIUM"
            if "HARD" in t_name.upper():
                difficulty = "HARD"
                
            # If subject is Mock, let's categorize appropriately
            final_subject = subject
            if subject == 'Mock':
                # Can default to Algorithms or Engineering Mathematics or distribute
                final_subject = 'Engineering Mathematics'
                
            item = {
                'id': cid,
                'canonicalId': cid,
                'type': q_type,
                'category': 'test_series',
                'subject': final_subject,
                'topic': t_name,
                'difficulty': difficulty,
                'year': 2025,
                'marks': marks,
                'question': q_text,
                'options': options,
                'correct': correct,
                'explanation': explanation,
                'hasUsableKey': has_key,
                'source': f"Gate Overflow 2025 Test Series - {t_name}"
            }
            parsed_questions.append(item)
            
    print(f"\n==========================================")
    print(f"Extraction & Deduplication Summary:")
    print(f"Total Evaluated Questions: {len(parsed_questions) + len(duplicates)}")
    print(f"Duplicates Detected & Filtered: {len(duplicates)}")
    print(f"Unique New Questions Extracted: {len(parsed_questions)}")
    print(f"==========================================")
    
    # Breakdown
    types_cnt = Counter(q['type'] for q in parsed_questions)
    subj_cnt = Counter(q['subject'] for q in parsed_questions)
    keys_cnt = Counter(q['hasUsableKey'] for q in parsed_questions)
    
    print("Types Breakdown:", types_cnt)
    print("Subjects Breakdown:", subj_cnt)
    print("Answer Key Present:", keys_cnt)
    
    # Save extracted questions
    out_path = 'data/go25_extracted_new_questions.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_questions, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(parsed_questions)} questions to {out_path}")
    
    # Save duplicates log
    dup_path = 'data/go25_duplicates_log.json'
    with open(dup_path, 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, ensure_ascii=False, indent=2)
    print(f"Saved duplicates log to {dup_path}")

if __name__ == '__main__':
    main()
