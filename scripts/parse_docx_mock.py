# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re
import sys
import io

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SUBJECT_MAPPING = {
    'general aptitude': 'Aptitude',
    'aptitude': 'Aptitude',
    'discrete mathematics': 'Discrete Mathematics',
    'discrete maths': 'Discrete Mathematics',
    'engineering mathematics': 'Engineering Mathematics',
    'linear algebra': 'Engineering Mathematics',
    'calculus': 'Engineering Mathematics',
    'probability': 'Engineering Mathematics',
    'digital logic': 'Digital Logic',
    'computer organization': 'Computer Organization',
    'programming': 'C Programming',
    'c programming': 'C Programming',
    'data structures': 'Data Structures',
    'algorithms': 'Algorithms',
    'theory of computation': 'Theory of Computation',
    'compiler design': 'Compiler Design',
    'operating systems': 'Operating Systems',
    'dbms': 'DBMS',
    'databases': 'DBMS',
    'database': 'DBMS',
    'computer networks': 'Computer Networks',
    'networks': 'Computer Networks'
}

def map_subject(raw_sub_topic):
    raw_lower = raw_sub_topic.lower()
    for key, val in SUBJECT_MAPPING.items():
        if key in raw_lower:
            return val
    return 'Discrete Mathematics' if 'discrete' in raw_lower else 'Engineering Mathematics'

def parse_mock_docx(path):
    with zipfile.ZipFile(path) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    body = tree.find('.//w:body', namespaces)

    elements = []
    for child in body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            texts = [t.text for t in child.iterfind('.//w:t', namespaces) if t.text]
            if texts:
                elements.append(('p', ''.join(texts)))
        elif tag == 'tbl':
            rows = []
            for tr in child.iterfind('.//w:tr', namespaces):
                row = []
                for tc in tr.iterfind('.//w:tc', namespaces):
                    tc_texts = []
                    for p in tc.iterfind('.//w:p', namespaces):
                        p_txt = ''.join([t.text for t in p.iterfind('.//w:t', namespaces) if t.text])
                        if p_txt:
                            tc_texts.append(p_txt)
                    row.append('\n'.join(tc_texts))
                rows.append(row)
            elements.append(('tbl', rows))

    # 1. Locate Answer Key Table
    ans_tbl_idx = None
    for i, (el_type, content) in enumerate(elements):
        if el_type == 'tbl' and len(content) >= 60 and any('answer' in str(c).lower() for c in content[0]):
            ans_tbl_idx = i
            break
            
    assert ans_tbl_idx is not None, f"Answer table not found in {path}"
    ans_tbl = elements[ans_tbl_idx][1]
    
    # Map Q number to answer info
    answers = {}
    for row in ans_tbl[1:]: # skip header
        q_num = int(row[0].strip())
        q_type = row[1].strip().lower() # mcq, msq, nat
        marks = int(re.sub(r'[^\d]', '', row[2].strip()) or 1)
        raw_ans = row[3].strip()
        sub_topic = row[4].strip()
        diff = row[5].strip().lower()
        if diff in ('easy', 'moderate', 'medium', 'hard'):
            diff = 'medium' if diff == 'moderate' else diff
        else:
            diff = 'medium'
            
        answers[q_num] = {
            'type': q_type,
            'marks': marks,
            'raw_ans': raw_ans,
            'sub_topic': sub_topic,
            'difficulty': diff,
            'source': row[6].strip() if len(row) > 6 else 'Original'
        }

    # 2. Locate Solutions
    sol_start = None
    for i in range(ans_tbl_idx + 1, len(elements)):
        if elements[i][0] == 'p' and 'solutions' in elements[i][1].lower() and len(elements[i][1]) < 20:
            sol_start = i
            break
            
    solutions = {}
    if sol_start:
        curr_q = None
        curr_sol_lines = []
        for i in range(sol_start + 1, len(elements)):
            el_type, content = elements[i]
            if el_type == 'p':
                m = re.match(r'^Q\.?\s*(\d+)\s+Answer:\s*(.*)', content, re.IGNORECASE)
                if m:
                    if curr_q:
                        solutions[curr_q] = '\n'.join(curr_sol_lines).strip()
                    curr_q = int(m.group(1))
                    curr_sol_lines = []
                    # check if there is explanation after the Answer header line
                    # usually the line itself has "Q.1 Answer: B (MCQ, 1m, Easy)"
                else:
                    if curr_q is not None:
                        curr_sol_lines.append(content)
            elif el_type == 'tbl' and curr_q is not None:
                # Table in solution
                tbl_txt = '\n'.join([' | '.join(row) for row in content])
                curr_sol_lines.append(tbl_txt)
        if curr_q:
            solutions[curr_q] = '\n'.join(curr_sol_lines).strip()

    # 3. Locate Questions (from start until ans_tbl_idx)
    questions = []
    curr_q = None
    curr_header = None
    curr_body_lines = []
    curr_options = {}

    def flush_q():
        nonlocal curr_q, curr_header, curr_body_lines, curr_options
        if curr_q is not None:
            ans_info = answers.get(curr_q, {})
            q_type = ans_info.get('type', 'mcq')
            marks = ans_info.get('marks', 1)
            raw_ans = ans_info.get('raw_ans', '')
            sub_topic = ans_info.get('sub_topic', '')
            diff = ans_info.get('difficulty', 'medium')
            
            # Format question text
            q_text = '\n'.join(curr_body_lines).strip()
            
            # Options for MCQ/MSQ
            opts = []
            if q_type in ('mcq', 'msq'):
                for opt_key in ['A', 'B', 'C', 'D']:
                    opts.append(curr_options.get(opt_key, '').strip())
                # filter out empty trailing if any, but standard is 4
            
            # Parse correct answer
            correct = []
            nat_range = None
            if q_type == 'mcq':
                # e.g. "B" or "(B)"
                opt_letter = re.sub(r'[^A-D]', '', raw_ans.upper())
                if opt_letter:
                    correct = [ord(opt_letter[0]) - ord('A')]
            elif q_type == 'msq':
                # e.g. "A, B, D"
                letters = re.findall(r'[A-D]', raw_ans.upper())
                correct = sorted([ord(l) - ord('A') for l in set(letters)])
            elif q_type == 'nat':
                # e.g. "12.5" or "10 to 12" or "8"
                m_range = re.findall(r'[-+]?\d*\.?\d+', raw_ans)
                if len(m_range) == 1:
                    v = float(m_range[0]) if '.' in m_range[0] else int(m_range[0])
                    nat_range = {"min": v, "max": v}
                    correct = [v]
                elif len(m_range) >= 2:
                    v1 = float(m_range[0]) if '.' in m_range[0] else int(m_range[0])
                    v2 = float(m_range[1]) if '.' in m_range[1] else int(m_range[1])
                    v_min, v_max = min(v1, v2), max(v1, v2)
                    nat_range = {"min": v_min, "max": v_max}
                    correct = [v_min]

            # Explanation
            expl = solutions.get(curr_q, '')
            if not expl:
                expl = f"Answer: {raw_ans}. Key verified."

            # Determine subject and topic
            subj = map_subject(sub_topic)
            topic = sub_topic.split('–')[-1].strip() if '–' in sub_topic else sub_topic.split('-')[-1].strip()

            q_obj = {
                'q_num': curr_q,
                'type': q_type,
                'marks': marks,
                'difficulty': diff,
                'subject': subj,
                'topic': topic,
                'question': q_text,
                'options': opts,
                'correct': correct,
                'explanation': expl
            }
            if q_type == 'nat' and nat_range:
                q_obj['natRange'] = nat_range
            questions.append(q_obj)

        curr_q = None
        curr_header = None
        curr_body_lines = []
        curr_options = {}

    for i in range(ans_tbl_idx):
        el_type, content = elements[i]
        if el_type == 'p':
            m = re.match(r'^Q\.?\s*(\d+)\s+\[([^\]]+)\]', content)
            if m:
                flush_q()
                curr_q = int(m.group(1))
                curr_header = m.group(2)
                continue

            if curr_q is not None:
                # Check for options (A), (B), (C), (D)
                m_opt = re.match(r'^\(([A-D])\)\s*(.*)', content)
                if m_opt:
                    curr_options[m_opt.group(1)] = m_opt.group(2).strip()
                elif any(content.startswith(f'({k})') for k in ['A','B','C','D']):
                    # Check if multiple options on one line e.g. (A) ... (B) ...
                    # Or handled line by line
                    pass
                else:
                    # Ignore pure filler like "(Numerical answer type – enter the value.)"
                    if '(numerical answer type' in content.lower():
                        continue
                    curr_body_lines.append(content)
        elif el_type == 'tbl' and curr_q is not None:
            # Table inside question
            tbl_txt = '\n'.join([' | '.join(row) for row in content])
            curr_body_lines.append(tbl_txt)

    flush_q()
    return questions

if __name__ == '__main__':
    path = r'c:\Users\sahu1\Downloads\GATE(Easy_to_Medium_Mocks)\GATE_CSE_Mock_Category1_Set1.docx'
    qs = parse_mock_docx(path)
    print(f"Parsed {len(qs)} questions from {path}")
    print("\n--- Question 1 ---")
    print("Type:", qs[0]['type'], "Marks:", qs[0]['marks'], "Subj:", qs[0]['subject'], "Diff:", qs[0]['difficulty'])
    print("Q:", qs[0]['question'])
    print("Opts:", qs[0]['options'])
    print("Correct:", qs[0]['correct'])
    print("Explanation:", qs[0]['explanation'])

    print("\n--- Question 3 (NAT) ---")
    print("Type:", qs[2]['type'], "Marks:", qs[2]['marks'], "Subj:", qs[2]['subject'], "Diff:", qs[2]['difficulty'])
    print("Q:", qs[2]['question'])
    print("Correct:", qs[2]['correct'])
    print("natRange:", qs[2].get('natRange'))
    print("Explanation:", qs[2]['explanation'])

    print("\n--- Question 11 (MSQ) ---")
    print("Type:", qs[10]['type'], "Marks:", qs[10]['marks'], "Subj:", qs[10]['subject'], "Diff:", qs[10]['difficulty'])
    print("Q:", qs[10]['question'])
    print("Opts:", qs[10]['options'])
    print("Correct:", qs[10]['correct'])
    print("Explanation:", qs[10]['explanation'])
