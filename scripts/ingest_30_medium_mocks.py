# -*- coding: utf-8 -*-
"""
Ingestion & Merge Engine for 30 Medium-Level Full-Length GATE CS Mock Examinations (1,950 Questions).
Parses medium_mocks.docx, formats question text, code snippets, KaTeX formulas,
maps schemas to Firebase/platform standard, tags with difficulty: 'medium', category: 'mock',
and merges into data/sample_questions.json and data/gate_30_medium_mocks.json.
"""

import os
import sys
import json
import re
import docx

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def map_subject_topic(subj_raw):
    m = re.match(r'^(.*?)\s*\((.*)\)$', subj_raw)
    if not m:
        return 'Computer Science', subj_raw
    broad = m.group(1).strip()
    topic = m.group(2).strip()
    
    if 'General Aptitude' in broad:
        return 'Aptitude', topic
    elif 'Digital Logic' in broad:
        return 'Digital Logic', topic
    elif 'Computer Organization' in broad:
        return 'Computer Organization', topic
    elif 'Algorithms' in broad:
        return 'Algorithms', topic
    elif 'Theory of Computation' in broad:
        return 'Theory of Computation', topic
    elif 'Compiler Design' in broad:
        return 'Compiler Design', topic
    elif 'Operating Systems' in broad:
        return 'Operating Systems', topic
    elif 'Databases' in broad:
        return 'DBMS', topic
    elif 'Computer Networks' in broad:
        return 'Computer Networks', topic
    elif 'Programming and Data Structures' in broad:
        if 'Programming in C' in topic:
            return 'C Programming', topic
        else:
            return 'Data Structures', topic
    elif 'Engineering & Discrete Mathematics' in broad:
        if any(k in topic for k in ['Linear Algebra', 'Calculus', 'Probability']):
            return 'Engineering Mathematics', topic
        else:
            return 'Discrete Mathematics', topic
    return broad, topic

def format_code_block(p2):
    p2_str = p2.strip()
    if '#include <stdio.h>' in p2_str:
        return f"```c\n{p2_str}\n```"
    elif 'Emp(' in p2_str or 'SELECT ' in p2_str:
        return f"```sql\n{p2_str}\n```"
    elif '1:  i = 1' in p2_str or re.match(r'^\d+:\s*', p2_str):
        return f"```text\n{p2_str}\n```"
    elif 'E →' in p2_str or 'E ->' in p2_str or 'T →' in p2_str:
        return f"```text\n{p2_str}\n```"
    else:
        return p2_str

def parse_medium_mocks(docx_path):
    doc = docx.Document(docx_path)
    all_questions = []

    for m_idx in range(1, 31):
        mock_id = f"mock-med-{m_idx:02d}"
        paper_name = f"GATE CS Medium Mock Exam #{m_idx:02d}"

        start = 5 + (m_idx - 1) * 173
        end = start + 173 if m_idx < 30 else len(doc.paragraphs)
        paras = [doc.paragraphs[k].text.strip() for k in range(start, end)]

        # 1. Answer Keys from Quick Answer Key Reference line
        ak_line = [p for p in paras if p.startswith('Quick Answer Key Reference:')][0]
        keys_raw = re.findall(r'Q(\d+):\s*([^|]+)', ak_line)
        keys_dict = {int(q): a.strip() for q, a in keys_raw}
        assert len(keys_dict) == 65, f"Mock {m_idx}: Expected 65 keys, got {len(keys_dict)}"

        # 2. Solutions
        solutions = {}
        for qnum in range(1, 66):
            sol_p = [p for p in paras if re.match(rf'^Solution to Question\s+{qnum}\b', p)][0]
            lines = sol_p.splitlines()
            clean_lines = [l for l in lines if not l.startswith('Solution to Question') and not l.startswith('Correct Answer:')]
            solutions[qnum] = '\n'.join(clean_lines).strip()
        assert len(solutions) == 65, f"Mock {m_idx}: Expected 65 solutions, got {len(solutions)}"

        # 3. Questions
        q_indices = [i for i, p in enumerate(paras) if re.match(r'^Question\s+\d+\s*\|', p)]
        assert len(q_indices) == 65, f"Mock {m_idx}: Expected 65 questions, got {len(q_indices)}"

        for q_i, p_idx in enumerate(q_indices):
            qnum = q_i + 1
            next_idx = q_indices[q_i + 1] if q_i + 1 < len(q_indices) else paras.index(ak_line)
            q_paras = [paras[x] for x in range(p_idx, next_idx) if paras[x]]
            cleaned = [p for p in q_paras if not (p.startswith('Part ') or re.match(r'^Q\.\d+', p) or p.startswith('Mock Test'))]

            p_header = cleaned[0]
            m_meta = re.match(r'^Question\s+(\d+)\s*\|\s*Marks:\s*(\d+)\s*\|\s*Type:\s*([A-Za-z]+)\s*\|\s*Subject:\s*([^\n\r]+)\n?([\s\S]*)', p_header)
            assert m_meta, f"Mock {m_idx} Q{qnum}: Failed to match header: {p_header[:80]}"
            
            marks = int(m_meta.group(2))
            qtype_raw = m_meta.group(3).lower()
            subj_raw = m_meta.group(4).strip()
            prompt_text = m_meta.group(5).strip()

            subject, topic = map_subject_topic(subj_raw)

            # Check for second paragraph
            code_or_opts = cleaned[1] if len(cleaned) > 1 else ''

            statement = prompt_text
            options = []
            correct = []
            nat_range = None
            key_val = keys_dict[qnum]
            explanation = solutions[qnum]

            if qtype_raw == 'mcq':
                split_parts = re.split(r'(?:^|\n)\(([A-D])\)\s*', code_or_opts)
                opt_map = {}
                for k in range(1, len(split_parts), 2):
                    opt_map[split_parts[k]] = split_parts[k+1].strip()
                options = [opt_map.get('A', ''), opt_map.get('B', ''), opt_map.get('C', ''), opt_map.get('D', '')]
                assert len(options) == 4 and all(opt != '' for opt in options), f"Mock {m_idx} Q{qnum} missing option: {options}"
                opt_letter = re.sub(r'[^A-D]', '', key_val.upper())[0]
                correct = [ord(opt_letter) - ord('A')]

            elif qtype_raw == 'msq':
                split_parts = re.split(r'(?:^|\n)\(([A-D])\)\s*', code_or_opts)
                opt_map = {}
                for k in range(1, len(split_parts), 2):
                    opt_map[split_parts[k]] = split_parts[k+1].strip()
                options = [opt_map.get('A', ''), opt_map.get('B', ''), opt_map.get('C', ''), opt_map.get('D', '')]
                assert len(options) == 4 and all(opt != '' for opt in options), f"Mock {m_idx} Q{qnum} missing option: {options}"
                letters = sorted(list(set(re.findall(r'[A-D]', key_val.upper()))))
                correct = [ord(l) - ord('A') for l in letters]

            elif qtype_raw == 'nat':
                options = []
                if code_or_opts and not code_or_opts.startswith('(A)'):
                    statement = f"{statement}\n\n{format_code_block(code_or_opts)}"
                
                v_float = float(key_val)
                if abs(v_float - round(v_float)) < 1e-6 and '.' not in key_val:
                    v_int = int(round(v_float))
                    correct = [v_int]
                    nat_range = {"min": v_int, "max": v_int}
                else:
                    v_num = float(key_val)
                    correct = [v_num]
                    nat_range = {"min": round(v_num - 0.05, 2), "max": round(v_num + 0.05, 2)}

            qid = f"mock_med{m_idx:02d}_q{qnum:02d}"
            q_obj = {
                "id": qid,
                "type": qtype_raw,
                "category": "mock",
                "mockId": mock_id,
                "paper": paper_name,
                "subject": subject,
                "topic": topic,
                "difficulty": "medium",
                "year": 2026,
                "marks": marks,
                "question": statement,
                "options": options,
                "correct": correct,
                "explanation": explanation
            }
            if nat_range:
                q_obj["natRange"] = nat_range

            all_questions.append(q_obj)

    return all_questions

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docx_path = os.path.join(root_dir, 'medium_mocks.docx')
    if not os.path.exists(docx_path):
        docx_path = r'C:\Users\sahu1\.gemini\antigravity\brain\83b48b5b-908a-45fa-aa26-b3763e0cc987\.user_uploaded\media_1793030530099_adf5566e.docx'

    print(f"Reading from: {docx_path}")
    questions = parse_medium_mocks(docx_path)
    print(f"Extracted {len(questions)} total questions from 30 medium mock tests.")
    assert len(questions) == 1950, f"Expected 1950 questions, got {len(questions)}"

    # 1. Save standalone payload gate_30_medium_mocks.json
    med_json_path = os.path.join(root_dir, 'data', 'gate_30_medium_mocks.json')
    with open(med_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"-> Saved standalone dataset: {med_json_path} ({os.path.getsize(med_json_path):,} bytes)")

    # 2. Merge into data/sample_questions.json
    sq_path = os.path.join(root_dir, 'data', 'sample_questions.json')
    with open(sq_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)

    # Filter out any prior mock-med- questions to make idempotent
    existing_clean = [q for q in existing_data if not (q.get('mockId') or '').startswith('mock-med-')]
    merged = existing_clean + questions
    print(f"Previous questions count: {len(existing_data)}, after adding 30 medium mocks: {len(merged)}")

    # Backup before writing
    bak_path = sq_path + '.bak'
    if os.path.exists(sq_path):
        with open(bak_path, 'w', encoding='utf-8') as f_bak:
            json.dump(existing_data, f_bak)

    with open(sq_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"-> Successfully updated master database: {sq_path} ({os.path.getsize(sq_path):,} bytes)")

if __name__ == '__main__':
    main()
