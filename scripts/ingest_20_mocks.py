# -*- coding: utf-8 -*-
"""
Ingestion & Synchronization Script for the 20 Full-Length GATE CS Mock Exams.
Parses C:\\Users\\sahu1\\Downloads\\mocks.docx, validates all 1,300 questions,
formats code and options, sets up exact NAT ranges, and integrates with the website.
"""

import os
import sys
import json
import re
import math
import docx

sys.path.append(os.path.dirname(__file__))
from test_parser import parse_mock, mocks

VALID_SUBJECTS = {
    'Algorithms', 'Aptitude', 'General Aptitude', 'C Programming',
    'Compiler Design', 'Computer Networks', 'Computer Organization',
    'DBMS', 'Data Structures', 'Digital Logic', 'Discrete Mathematics',
    'Engineering Mathematics', 'Operating Systems', 'Theory of Computation'
}

def map_subject_and_topic(raw_subj_str):
    parts = [p.strip() for p in re.split(r'[—–-]', raw_subj_str) if p.strip()]
    top_area = parts[0] if len(parts) > 0 else ''
    sub_topic = parts[1] if len(parts) > 1 else ''
    detail = ' — '.join(parts[2:]) if len(parts) > 2 else ''
    
    subject = 'Engineering Mathematics'
    topic = sub_topic or top_area
    if detail:
        topic += f' ({detail})'
        
    lower_raw = raw_subj_str.lower()
    
    if 'general aptitude' in lower_raw or 'aptitude' in lower_raw:
        subject = 'Aptitude'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'digital logic' in lower_raw:
        subject = 'Digital Logic'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'computer organization' in lower_raw or 'coa' in lower_raw or 'architecture' in lower_raw:
        subject = 'Computer Organization'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'compiler design' in lower_raw:
        subject = 'Compiler Design'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'operating systems' in lower_raw or 'operating system' in lower_raw:
        subject = 'Operating Systems'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'databases' in lower_raw or 'dbms' in lower_raw:
        subject = 'DBMS'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'computer networks' in lower_raw or 'network' in lower_raw:
        subject = 'Computer Networks'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'algorithms' in lower_raw or 'algorithm' in lower_raw:
        subject = 'Algorithms'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'theory of computation' in lower_raw or 'toc' in lower_raw:
        subject = 'Theory of Computation'
        topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'programming and data structures' in lower_raw or 'data structures' in lower_raw:
        if any(k in lower_raw for k in ['programming in c', 'pointer', 'recursion', 'bitwise', 'c program']):
            subject = 'C Programming'
            topic = f'{sub_topic} ({detail})' if detail else sub_topic
        else:
            subject = 'Data Structures'
            topic = f'{sub_topic} ({detail})' if detail else sub_topic
    elif 'engineering & discrete mathematics' in lower_raw or 'discrete' in lower_raw:
        if any(k in lower_raw for k in ['logic', 'set theory', 'poset', 'lattice', 'combinatorics', 'graph', 'group']):
            subject = 'Discrete Mathematics'
            topic = f'{sub_topic} ({detail})' if detail else sub_topic
        else:
            subject = 'Engineering Mathematics'
            topic = f'{sub_topic} ({detail})' if detail else sub_topic
            
    return subject, topic

def format_question_text(q):
    lines = [q['statement']]
    for l in q['extra_lines']:
        lines.append(l)
        
    full = '\n\n'.join(lines)
    
    # Check for C code blocks with 4 spaces or #include / int main
    if '#include' in full or 'int main' in full or 'int mystery' in full:
        # Wrap C code nicely if not already in code block
        if '```' not in full:
            # Pattern match indentation or code start
            m_code = re.search(r'((?:(?:    |\t).*\n?)+)', full)
            if m_code and len(m_code.group(1).strip()) > 20:
                code_text = '\n'.join([line.strip() for line in m_code.group(1).splitlines() if line.strip()])
                # re-indent
                re_indented = []
                for cl in code_text.splitlines():
                    if cl.startswith('#') or cl.endswith('{') or cl == '}':
                        re_indented.append(cl)
                    else:
                        re_indented.append('    ' + cl)
                f_code = '```c\n' + '\n'.join(re_indented) + '\n```'
                full = full.replace(m_code.group(1), '\n' + f_code + '\n')
    return full.strip()

def build_dataset():
    all_mock_questions = []
    
    for m_num in sorted(mocks.keys()):
        mock_id = f"mock-flm-{m_num:02d}"
        paper_name = f"GATE CS Full Mock Exam #{m_num:02d}"
        
        qs, keys, sols = parse_mock(m_num, mocks[m_num]['raw_items'], mocks[m_num]['table'])
        assert len(qs) == 65
        
        for q in qs:
            qn = q['q_num']
            qid = f"mock_flm{m_num:02d}_q{qn:02d}"
            marks = q['marks']
            q_type = q['type']
            key_val = keys[qn]
            explanation = sols[qn]
            
            subject, topic = map_subject_and_topic(q['raw_subject'])
            
            # Difficulty assignment
            if m_num <= 5:
                difficulty = 'easy' if marks == 1 else 'medium'
            elif m_num <= 14:
                difficulty = 'medium'
            else:
                difficulty = 'medium' if marks == 1 else 'hard'
                
            q_text = format_question_text(q)
            
            correct = []
            options = []
            nat_range = None
            
            if q_type == 'mcq':
                opt_letter = re.sub(r'[^A-D]', '', key_val.upper())[0]
                correct = [ord(opt_letter) - ord('A')]
                options = [opt.strip() for opt in q['options']]
            elif q_type == 'msq':
                letters = sorted(list(set(re.findall(r'[A-D]', key_val.upper()))))
                correct = [ord(l) - ord('A') for l in letters]
                options = [opt.strip() for opt in q['options']]
            elif q_type == 'nat':
                options = []
                v_float = float(key_val)
                # Check if it represents an exact integer
                if abs(v_float - round(v_float)) < 1e-6 and '.' not in key_val:
                    v_int = int(round(v_float))
                    correct = [v_int]
                    nat_range = {"min": v_int, "max": v_int}
                elif '.' in key_val and v_float == round(v_float, 2):
                    # Check decimal digits
                    num_dec = len(key_val.split('.')[1])
                    if num_dec <= 2 and abs(v_float - round(v_float)) < 1e-6:
                        # e.g. 6.00 or 150.0
                        v_num = float(key_val)
                        correct = [v_num]
                        # Give small floating tolerance for roundoff
                        nat_range = {"min": round(v_num - 0.05, 2), "max": round(v_num + 0.05, 2)}
                    else:
                        v_num = float(key_val)
                        correct = [v_num]
                        nat_range = {"min": round(v_num - 0.05, 3), "max": round(v_num + 0.05, 3)}
                else:
                    v_num = float(key_val)
                    correct = [v_num]
                    nat_range = {"min": round(v_num - 0.05, 3), "max": round(v_num + 0.05, 3)}
                    
            item = {
                "id": qid,
                "type": q_type,
                "category": "mock",
                "mockId": mock_id,
                "paper": paper_name,
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty,
                "year": 2026,
                "marks": marks,
                "question": q_text,
                "options": options,
                "correct": correct,
                "explanation": explanation
            }
            if nat_range:
                item["natRange"] = nat_range
                
            all_mock_questions.append(item)
            
    return all_mock_questions

def main():
    print("=== BUILDING 20 FULL-LENGTH GATE CS MOCK EXAMS DATASET ===")
    mock_qs = build_dataset()
    print(f"Total questions generated: {len(mock_qs)}")
    assert len(mock_qs) == 1300, f"Expected 1300 questions, got {len(mock_qs)}"
    
    # Save standalone compendium dataset
    comp_path = r"g:\0.Gate_Lectures\0.Gate_Mocks_Website\data\gate_20_full_mocks.json"
    with open(comp_path, 'w', encoding='utf-8') as f:
        json.dump(mock_qs, f, indent=2, ensure_ascii=False)
    print(f"Saved standalone compendium to {comp_path} ({os.path.getsize(comp_path)} bytes)")
    
    # Merge into sample_questions.json
    sq_path = r"g:\0.Gate_Lectures\0.Gate_Mocks_Website\data\sample_questions.json"
    with open(sq_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
        
    print(f"Existing sample_questions.json count: {len(existing_data)}")
    
    # Remove any previous mock-flm- questions if present
    filtered_data = [q for q in existing_data if not (q.get('mockId') or '').startswith('mock-flm-')]
    removed_count = len(existing_data) - len(filtered_data)
    if removed_count > 0:
        print(f"Removed {removed_count} existing mock-flm- questions.")
        
    # Append the 1300 questions
    merged_data = filtered_data + mock_qs
    print(f"Merged total questions: {len(merged_data)}")
    
    with open(sq_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    print(f"Successfully updated {sq_path} ({os.path.getsize(sq_path)} bytes)")

if __name__ == '__main__':
    main()
