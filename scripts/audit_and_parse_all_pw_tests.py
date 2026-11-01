# -*- coding: utf-8 -*-
import os
import re
import json
import pymupdf
from collections import defaultdict

def normalize_text(text):
    text = re.sub(r'[\$\`\#\*\_\{\}\\\(\)\[\]\:\,\.\?\!\;\"]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def get_words(text):
    return set(normalize_text(text).split())

def jaccard(s1, s2):
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)

# Load existing master datastore
print("Loading existing question bank (data/sample_questions.json)...")
existing_data = json.load(open('data/sample_questions.json', encoding='utf-8'))
print(f"Total existing questions: {len(existing_data)}")

# Index existing questions
exact_norm_map = {}
word_sets = []

for q in existing_data:
    qtext = q.get('question', '')
    norm = normalize_text(qtext)
    if norm and norm not in exact_norm_map:
        exact_norm_map[norm] = q.get('id')
    w = get_words(qtext)
    if len(w) >= 6:
        word_sets.append((q.get('id'), w))

print(f"Indexed {len(exact_norm_map)} unique normalized question statements.")

base_pw = r'G:\0.Gate_Lectures\0.2.Questions_Books_Practice_Materials\Practice Material (CSE)\PYQS & DPP\Weekly Test Papers PW'

sub_map = {
    'Algorithms': 'Algorithms',
    'C Programming': 'Programming and Data Structures',
    'CN': 'Computer Networks',
    'COA': 'Computer Organization and Architecture',
    'Compiler Design': 'Compiler Design',
    'DBMS': 'Databases',
    'Digital Logic': 'Digital Logic',
    'Discrete Mathematics': 'Engineering Mathematics',
    'Operating System': 'Operating System',
    'Theory Of Computation': 'Theory of Computation'
}

total_parsed = 0
duplicates_found = []
new_questions = []

for sub_dir in sorted(os.listdir(base_pw)):
    sub_path = os.path.join(base_pw, sub_dir)
    if not os.path.isdir(sub_path):
        continue
    standard_subject = sub_map.get(sub_dir, sub_dir)
    pdf_files = sorted([f for f in os.listdir(sub_path) if f.endswith('.pdf')])
    
    print(f"\nProcessing Subject: {standard_subject} ({len(pdf_files)} test papers)...")
    
    for pdf_name in pdf_files:
        fp = os.path.join(sub_path, pdf_name)
        try:
            doc = pymupdf.open(fp)
            full_text = "\n".join([page.get_text() for page in doc])
        except Exception as e:
            print(f"  Error reading {pdf_name}: {e}")
            continue
            
        ak_match = re.search(r'\n\s*Answer Key\s*\n', full_text, re.IGNORECASE)
        hs_match = re.search(r'\n\s*(?:Hints and Solutions|Solutions|Hints & Solutions)\s*\n', full_text, re.IGNORECASE)
        
        q_sec = ""
        ak_sec = ""
        hs_sec = ""
        
        if ak_match:
            q_sec = full_text[:ak_match.start()]
            if hs_match and hs_match.start() > ak_match.end():
                ak_sec = full_text[ak_match.end():hs_match.start()]
                hs_sec = full_text[hs_match.end():]
            else:
                ak_sec = full_text[ak_match.end():]
        else:
            q_sec = full_text
            
        # Topic
        topic_match = re.search(r'Topic\s*:\s*([^\n\r]+)', q_sec, re.IGNORECASE)
        topic = re.sub(r'\s+', ' ', topic_match.group(1)).strip() if topic_match else standard_subject
        
        # Test label
        test_match = re.search(r'WEEKLY TEST\s*–?\s*(\d+)', q_sec, re.IGNORECASE)
        test_num = test_match.group(1) if test_match else "01"
        paper_label = f"PW CS Weekly Test {test_num} - {standard_subject}"
        
        # Answers
        answers = {}
        for m in re.finditer(r'(?:Q\.?)?(\d+)[\.\s]+[\(]?([a-dA-D0-9\s,\.\-]+)[\)]?', ak_sec):
            qnum = int(m.group(1))
            ans_raw = m.group(2).strip().lower()
            answers[qnum] = ans_raw
            
        # Solutions
        solutions = {}
        if hs_sec:
            sol_parts = re.split(r'\n\s*(?:Q\.?)?(\d+)\s*[\.\)]\s*', hs_sec)
            for i in range(1, len(sol_parts), 2):
                try:
                    qnum = int(sol_parts[i])
                    solutions[qnum] = re.sub(r'\s+', ' ', sol_parts[i+1]).strip()
                except:
                    pass
                    
        # Questions
        matches = list(re.finditer(r'\n\s*\[\s*(MCQ|MSQ|NAT)\s*\]\s*\n\s*(\d+)[\.\)]', q_sec, re.IGNORECASE))
        if not matches:
            # Fallback pattern without brackets
            matches = list(re.finditer(r'\n\s*(\d+)[\.\)]\s*', q_sec))
            
        for i, m in enumerate(matches):
            total_parsed += 1
            if len(m.groups()) == 2:
                q_type = m.group(1).lower()
                q_num = int(m.group(2))
            else:
                q_type = 'mcq'
                q_num = int(m.group(1))
                
            start_idx = m.end()
            end_idx = matches[i+1].start() if i+1 < len(matches) else len(q_sec)
            raw_block = q_sec[start_idx:end_idx].strip()
            
            raw_block = re.sub(r'\n\s*Maximum Marks\s*\d+\s*', '', raw_block, flags=re.I)
            raw_block = re.sub(r'\n\s*Q\.\d+\s+to\s+\d+\s+Carry\s+[^\n]+', '', raw_block, flags=re.I)
            raw_block = re.sub(r'\n\s*\d+\s*\n', '\n', raw_block)
            
            # Options
            opt_matches = list(re.finditer(r'(?:^|\n|\s)\(([a-dA-D])\)\s*', raw_block))
            if len(opt_matches) >= 3:
                q_text = raw_block[:opt_matches[0].start()].strip()
                opts = []
                for j in range(len(opt_matches)):
                    ostart = opt_matches[j].end()
                    oend = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(raw_block)
                    opts.append(raw_block[ostart:oend].strip())
            else:
                q_text = raw_block.strip()
                opts = []
                if q_type != 'nat' and not opts:
                    q_type = 'nat'
                    
            if len(q_text) < 15:
                continue
                
            # Deduplication check against existing question bank
            norm_q = normalize_text(q_text)
            dup_id = None
            dup_reason = None
            
            if norm_q in exact_norm_map:
                dup_id = exact_norm_map[norm_q]
                dup_reason = "Exact Match"
            else:
                w_candidate = get_words(q_text)
                if len(w_candidate) >= 8:
                    for ex_id, ex_w in word_sets:
                        if jaccard(w_candidate, ex_w) > 0.85:
                            dup_id = ex_id
                            dup_reason = f"High Similarity (>85%)"
                            break
                            
            if dup_id:
                duplicates_found.append({
                    'paper': paper_label,
                    'q_num': q_num,
                    'dup_with': dup_id,
                    'reason': dup_reason,
                    'snippet': q_text[:80]
                })
            else:
                # Add to index so future questions within this batch don't duplicate
                exact_norm_map[norm_q] = f"pw_{sub_dir.lower()}_w{test_num}_q{q_num:02d}"
                word_sets.append((f"pw_{sub_dir.lower()}_w{test_num}_q{q_num:02d}", get_words(q_text)))
                
                # Format answers and options
                ans_raw = answers.get(q_num, '')
                correct = []
                ans_val = None
                
                if q_type == 'nat':
                    ans_val = re.sub(r'[^\d\.\-]', '', ans_raw)
                    if ans_val:
                        correct = [ans_val]
                else:
                    opt_letters = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
                    for letter in re.findall(r'[a-dA-D]', ans_raw):
                        idx = opt_letters.get(letter.lower())
                        if idx is not None and idx < len(opts):
                            correct.append(idx)
                            
                expl = solutions.get(q_num, '')
                
                new_q = {
                    'id': f"pw_{re.sub(r'[^a-z0-9]', '', sub_dir.lower())}_w{test_num}_q{q_num:02d}",
                    'type': q_type,
                    'category': 'test_series',
                    'subject': standard_subject,
                    'topic': topic,
                    'difficulty': 'medium' if q_num <= 5 else 'hard',
                    'year': 2026,
                    'paper': paper_label,
                    'marks': 1 if q_num <= 5 else 2,
                    'question': q_text,
                    'options': opts,
                    'correct': correct,
                    'answer': ans_val if q_type == 'nat' else None,
                    'explanation': expl,
                    'canonicalId': f"pw_{re.sub(r'[^a-z0-9]', '', sub_dir.lower())}_w{test_num}_q{q_num:02d}",
                    'hasUsableKey': len(correct) > 0
                }
                new_questions.append(new_q)

print("\n" + "=" * 70)
print("📊 DEDUPLICATION & EXTRACTION REPORT FOR PW WEEKLY TESTS")
print("=" * 70)
print(f"Total Questions Evaluated from PDFs: {total_parsed}")
print(f"Duplicates Detected (against 8,168 existing bank): {len(duplicates_found)}")
print(f"Unique New Questions Extracted: {len(new_questions)}")
print(f"Unique Questions with Answer Key: {sum(1 for q in new_questions if q['hasUsableKey'])} / {len(new_questions)}")
print(f"Unique Questions with Step-by-Step Explanation: {sum(1 for q in new_questions if len(q['explanation']) > 10)} / {len(new_questions)}")

if duplicates_found:
    print("\nSample Duplicates Detected & Filtered:")
    for d in duplicates_found[:5]:
        print(f"  • {d['paper']} Q{d['q_num']} -> Duplicate with {d['dup_with']} ({d['reason']})")
        print(f"    Snippet: {d['snippet']}...")

with open('data/pw_extracted_new_questions.json', 'w', encoding='utf-8') as f:
    json.dump(new_questions, f, indent=2, ensure_ascii=False)
print("\nSaved extracted unique questions to data/pw_extracted_new_questions.json!")
