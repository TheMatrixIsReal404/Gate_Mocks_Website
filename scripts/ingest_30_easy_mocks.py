# -*- coding: utf-8 -*-
"""
Ingestion & Merge Engine for 30 Easy-Level Full-Length GATE CS Mock Exams (1,950 Questions).
Parses easy_mocks.docx, formats question text, code snippets, KaTeX formulas,
maps schemas to Firebase/platform standard, tags with difficulty: 'easy', category: 'mock',
and merges into data/sample_questions.json and data/gate_30_easy_mocks.json.
"""

import os
import sys
import json
import re
import docx

TOPICS_BY_QNUM = {
    1: ("Aptitude", "Verbal Aptitude (Sentence Completion)"),
    2: ("Aptitude", "Deductive Logic & Syllogisms"),
    3: ("Aptitude", "Quantitative Aptitude (Arithmetic Progression)"),
    4: ("Aptitude", "Quantitative Aptitude (Percentages & Profit/Loss)"),
    5: ("Aptitude", "Spatial Aptitude (Painted Cubes & Geometry)"),
    6: ("Aptitude", "Quantitative Aptitude (Speed, Time & Distance)"),
    7: ("Aptitude", "Set Theory & Venn Diagrams"),
    8: ("Aptitude", "Permutations & Combinations"),
    9: ("Aptitude", "Data Interpretation & Timeout Rates"),
    10: ("Aptitude", "Algebra (Quadratic Equations & Roots)"),
    11: ("Engineering Mathematics", "Linear Algebra (Eigenvalues & Trace)"),
    12: ("Engineering Mathematics", "Calculus (Limits & Continuity)"),
    13: ("Discrete Mathematics", "Graph Theory (Planar Graphs & Euler's Formula)"),
    14: ("Discrete Mathematics", "Set Theory & Binary Relations"),
    15: ("Digital Logic", "Boolean Algebra & K-Maps"),
    16: ("Digital Logic", "Number Systems & 2's Complement Representation"),
    17: ("Computer Organization", "Cache Memory (Tag Bits & Direct Mapping)"),
    18: ("Computer Organization", "Instruction Set Architecture (Addressing Modes)"),
    19: ("Computer Organization", "Memory Hierarchy (Effective Access Time)"),
    20: ("C Programming", "Static Variable Scope & Functions"),
    21: ("Data Structures", "Stacks & Postfix Evaluation"),
    22: ("Data Structures", "Trees (Strict k-ary Tree Invariants)"),
    23: ("Algorithms", "Asymptotic Analysis & Growth Rates"),
    24: ("Algorithms", "Comparison-based Sorting Algorithms"),
    25: ("Algorithms", "Hashing & Open Addressing (Linear Probing)"),
    26: ("Theory of Computation", "Finite Automata & Product DFA Construction"),
    27: ("Compiler Design", "Lexical Analysis & Maximal Munch Rule"),
    28: ("Compiler Design", "Parsing Theory (LL & LR Grammars)"),
    29: ("Operating Systems", "Process Management (fork Hierarchy)"),
    30: ("Operating Systems", "Virtual Memory (Paging & Page Table Size)"),
    31: ("Operating Systems", "Concurrency & Deadlock Prevention"),
    32: ("DBMS", "ER Model to Relational Schema Mapping"),
    33: ("DBMS", "Functional Dependencies & Normal Forms"),
    34: ("Computer Networks", "IPv4 Addressing & CIDR Subnetting"),
    35: ("Computer Networks", "Network Protocols & Address Resolution"),
    36: ("Engineering Mathematics", "Linear Algebra (System of Linear Equations)"),
    37: ("Engineering Mathematics", "Probability (Binomial Distribution)"),
    38: ("Discrete Mathematics", "Recurrence Relations (Homogeneous Linear)"),
    39: ("Discrete Mathematics", "Group Theory & First-Order Logic"),
    40: ("Discrete Mathematics", "Graph Theory (Bipartite Graphs)"),
    41: ("Digital Logic", "Sequential Circuits (Asynchronous Ripple Counters)"),
    42: ("Computer Organization", "Pipelining & Hazard Penalties"),
    43: ("Computer Organization", "Secondary Storage (Disk Access Time)"),
    44: ("C Programming", "Recursion & Call Stacks"),
    45: ("Data Structures", "Binary Search Trees (Preorder to Postorder)"),
    46: ("Data Structures", "Binary Heaps (Max-Heap Array Representation)"),
    47: ("Data Structures", "Linked Lists & Height-Balanced AVL Trees"),
    48: ("Algorithms", "Divide and Conquer (Master Theorem)"),
    49: ("Algorithms", "Greedy Algorithms (Huffman Codes)"),
    50: ("Algorithms", "Graph Algorithms (Minimum Spanning Tree)"),
    51: ("Theory of Computation", "Regular Languages & Minimal DFA"),
    52: ("Theory of Computation", "Context-Free Grammars (Chomsky Normal Form)"),
    53: ("Theory of Computation", "Formal Languages & Closure Properties"),
    54: ("Theory of Computation", "Decidability & Undecidability"),
    55: ("Compiler Design", "Syntax-Directed Translation (SDT Attributes)"),
    56: ("Operating Systems", "CPU Scheduling (Preemptive SRTF)"),
    57: ("Operating Systems", "Virtual Memory (TLB & 2-Level Page Tables)"),
    58: ("Operating Systems", "Process Synchronization (Counting Semaphores)"),
    59: ("DBMS", "B+ Trees (Order & Block Capacity)"),
    60: ("DBMS", "Relational Database Design (Candidate Keys)"),
    61: ("DBMS", "SQL Queries (Aggregate Functions & NULL Handling)"),
    62: ("Computer Networks", "Sliding Window Protocol (Link Utilization)"),
    63: ("Computer Networks", "TCP Congestion Control (Slow Start & Congestion Avoidance)"),
    64: ("Computer Networks", "Medium Access Control (CSMA/CD Minimum Frame Size)"),
    65: ("Computer Networks", "Routing Protocols & Transport Layer Connection Management")
}

def format_question_code(text):
    text = text.strip()
    if '#include' in text and '```' not in text:
        m = re.search(r'(#include\s*<stdio\.h>[\s\S]*?return 0;\s*})', text)
        if m:
            text = text.replace(m.group(1), f'```c\n{m.group(1).strip()}\n```')
    elif 'int fun(int n)' in text and '```' not in text:
        m = re.search(r'(int fun\(int n\)[\s\S]*?})', text)
        if m:
            text = text.replace(m.group(1), f'```c\n{m.group(1).strip()}\n```')
    elif 'for (int i = 0;' in text and '```' not in text:
        m = re.search(r'(for\s*\(int i = 0;[\s\S]*?})', text)
        if m:
            text = text.replace(m.group(1), f'```c\n{m.group(1).strip()}\n```')
    return text

def parse_easy_mocks(docx_path):
    doc = docx.Document(docx_path)
    all_questions = []

    for m_idx in range(1, 31):
        mock_id = f"mock-easy-{m_idx:02d}"
        paper_name = f"GATE CSE Full Mock Exam (Easy) #{m_idx:02d}"
        
        # 1. Answer Keys from Table m_idx
        tbl = doc.tables[m_idx]
        keys = {}
        for row in tbl.rows[1:]:
            for cell in row.cells:
                txt = cell.text.strip()
                m = re.match(r'Q\.?(\d+)\s*:\s*([^()]+)\s*\(([^)]+)\)', txt)
                if m:
                    qnum = int(m.group(1))
                    ans_str = m.group(2).strip()
                    keys[qnum] = ans_str
        assert len(keys) == 65, f"Mock {m_idx}: Expected 65 keys, got {len(keys)}"

        # 2. Extract paragraphs for this mock
        start_para = 5 + (m_idx - 1) * 171
        end_para = start_para + 171
        exam_paras = [p.text.strip() for p in doc.paragraphs[start_para:end_para]]

        # 3. Extract solutions
        solutions = {}
        for p in exam_paras:
            m = re.match(r'Solution Q\.(\d+)\s*\(([^)]+)\)\s*—\s*Correct Answer:\s*(.+)', p, re.DOTALL)
            if m:
                qnum = int(m.group(1))
                full_sol = p
                # Remove header line to get clean step-by-step solution
                lines = full_sol.splitlines()
                if len(lines) > 1:
                    clean_sol = '\n'.join(lines[1:]).strip()
                else:
                    clean_sol = full_sol
                solutions[qnum] = clean_sol
        assert len(solutions) == 65, f"Mock {m_idx}: Expected 65 solutions, got {len(solutions)}"

        # 4. Extract questions and options
        for i, p in enumerate(exam_paras):
            if p.startswith('Solution Q.') or 'Answer Key & Detailed' in p:
                break
            m_q = re.match(r'^Q\.(\d+)\s*\[([^\]]+)\]\s*([\s\S]*)', p)
            if m_q:
                qnum = int(m_q.group(1))
                meta_parts = [s.strip() for s in m_q.group(2).split('|')]
                marks = 1 if '1' in meta_parts[0] else 2
                qtype_str = meta_parts[1].lower() if len(meta_parts) > 1 else 'mcq'
                if 'msq' in qtype_str:
                    q_type = 'msq'
                elif 'nat' in qtype_str:
                    q_type = 'nat'
                else:
                    q_type = 'mcq'

                statement_raw = m_q.group(3).strip()
                statement = format_question_code(statement_raw)

                subject, topic = TOPICS_BY_QNUM.get(qnum, ("Computer Science", "General"))

                key_val = keys[qnum]
                explanation = solutions.get(qnum, "")

                options = []
                correct = []
                nat_range = None

                if q_type == 'mcq':
                    next_p = exam_paras[i+1] if i + 1 < len(exam_paras) else ''
                    split_parts = re.split(r'(?:^|\n)\(([A-D])\)\s*', next_p)
                    opt_map = {}
                    for k in range(1, len(split_parts), 2):
                        opt_map[split_parts[k]] = split_parts[k+1].strip()
                    options = [opt_map.get('A', ''), opt_map.get('B', ''), opt_map.get('C', ''), opt_map.get('D', '')]
                    opt_letter = re.sub(r'[^A-D]', '', key_val.upper())[0]
                    correct = [ord(opt_letter) - ord('A')]

                elif q_type == 'msq':
                    next_p = exam_paras[i+1] if i + 1 < len(exam_paras) else ''
                    split_parts = re.split(r'(?:^|\n)\(([A-D])\)\s*', next_p)
                    opt_map = {}
                    for k in range(1, len(split_parts), 2):
                        opt_map[split_parts[k]] = split_parts[k+1].strip()
                    options = [opt_map.get('A', ''), opt_map.get('B', ''), opt_map.get('C', ''), opt_map.get('D', '')]
                    letters = sorted(list(set(re.findall(r'[A-D]', key_val.upper()))))
                    correct = [ord(l) - ord('A') for l in letters]

                elif q_type == 'nat':
                    options = []
                    v_float = float(key_val)
                    if abs(v_float - round(v_float)) < 1e-6 and '.' not in key_val:
                        v_int = int(round(v_float))
                        correct = [v_int]
                        nat_range = {"min": v_int, "max": v_int}
                    else:
                        v_num = float(key_val)
                        correct = [v_num]
                        # Rounding tolerance of +/- 0.05
                        nat_range = {"min": round(v_num - 0.05, 2), "max": round(v_num + 0.05, 2)}

                qid = f"mock_easy{m_idx:02d}_q{qnum:02d}"

                q_obj = {
                    "id": qid,
                    "type": q_type,
                    "category": "mock",
                    "mockId": mock_id,
                    "paper": paper_name,
                    "subject": subject,
                    "topic": topic,
                    "difficulty": "easy",
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
    docx_path = os.path.join(root_dir, 'easy_mocks.docx')
    if not os.path.exists(docx_path):
        docx_path = r'C:\Users\sahu1\Downloads\easy_mocks.docx'

    print(f"Reading from: {docx_path}")
    questions = parse_easy_mocks(docx_path)
    print(f"Extracted {len(questions)} total questions from 30 mocks.")
    assert len(questions) == 1950, f"Expected 1950 questions, got {len(questions)}"

    # 1. Save standalone payload gate_30_easy_mocks.json
    easy_json_path = os.path.join(root_dir, 'data', 'gate_30_easy_mocks.json')
    with open(easy_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"-> Saved standalone dataset: {easy_json_path} ({os.path.getsize(easy_json_path)} bytes)")

    # 2. Merge into data/sample_questions.json
    sq_path = os.path.join(root_dir, 'data', 'sample_questions.json')
    with open(sq_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)

    # Filter out any prior mock-easy- questions to make idempotent
    existing_clean = [q for q in existing_data if not (q.get('mockId') or '').startswith('mock-easy-')]
    merged = existing_clean + questions
    print(f"Previous questions count: {len(existing_data)}, after adding 30 easy mocks: {len(merged)}")

    with open(sq_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"-> Successfully updated master database: {sq_path} ({os.path.getsize(sq_path)} bytes)")

if __name__ == '__main__':
    main()
