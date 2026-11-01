# -*- coding: utf-8 -*-
import sys, docx, re
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document(r'C:\Users\sahu1\Downloads\mocks.docx')
body = doc._element.body

mocks = {}
current_mock = None

for child in body:
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        p = docx.text.paragraph.Paragraph(child, doc)
        txt = p.text.strip()
        if not txt:
            continue
        m_head = re.match(r'GATE CS FULL-LENGTH MOCK EXAMINATION #(\d+)', txt, re.IGNORECASE)
        if m_head:
            current_mock = int(m_head.group(1))
            mocks[current_mock] = {'raw_items': [], 'table': None}
            continue
        if current_mock:
            mocks[current_mock]['raw_items'].append(txt)
    elif tag == 'tbl' and current_mock:
        tbl = docx.table.Table(child, doc)
        mocks[current_mock]['table'] = tbl

def parse_mock(mock_num, p_list, table):
    keys = {}
    for row in table.rows[1:]:
        for cell in row.cells:
            txt = cell.text.strip()
            m = re.match(r'Q(\d+)\s*\(([^)]+)\):\s*(.+)', txt)
            if m:
                q_num = int(m.group(1))
                keys[q_num] = m.group(3).strip()
                
    q_paras = []
    sol_paras = []
    in_sol = False
    for txt in p_list:
        if txt.startswith('Solution to Question'):
            in_sol = True
        if in_sol:
            sol_paras.append(txt)
        else:
            q_paras.append(txt)
            
    solutions = {}
    for s_txt in sol_paras:
        m = re.match(r'^Solution to Question\s+(\d+)\s+\[([^\]]+)\]:\s*(.*)', s_txt, re.DOTALL)
        if m:
            solutions[int(m.group(1))] = m.group(3).strip()
            
    questions = []
    curr_q = None
    
    for txt in q_paras:
        m_q = re.match(r'^Question\s+(\d+)\s+\[([^\]]+)\]\s*(.*)', txt, re.DOTALL)
        if m_q:
            if curr_q:
                questions.append(curr_q)
            q_num = int(m_q.group(1))
            meta_str = m_q.group(2)
            stmt = m_q.group(3).strip()
            
            parts = [p.strip() for p in meta_str.split('|')]
            marks = 1 if '1' in parts[0] else 2
            q_type = 'mcq'
            if len(parts) > 1:
                t_str = parts[1].upper()
                if 'MSQ' in t_str: q_type = 'msq'
                elif 'NAT' in t_str: q_type = 'nat'
                elif 'MCQ' in t_str: q_type = 'mcq'
                
            subj_topic = parts[2] if len(parts) > 2 else ''
            
            curr_q = {
                'q_num': q_num,
                'marks': marks,
                'type': q_type,
                'raw_subject': subj_topic,
                'statement': stmt,
                'options': [],
                'extra_lines': []
            }
        else:
            if curr_q:
                if re.search(r'\(A\)\s+', txt) and re.search(r'\(B\)\s+', txt):
                    opts = re.split(r'\(([A-D])\)\s*', txt)
                    opt_dict = {}
                    for i in range(1, len(opts), 2):
                        opt_dict[opts[i]] = opts[i+1].strip()
                    curr_q['options'] = [opt_dict.get('A', ''), opt_dict.get('B', ''), opt_dict.get('C', ''), opt_dict.get('D', '')]
                elif txt.startswith('Answer (Numerical Answer Type'):
                    pass
                elif not (txt.startswith('Mock #') or txt.startswith('Duration:') or txt.startswith('Negative Marking') or 'Section 1' in txt or 'Section 2' in txt):
                    curr_q['extra_lines'].append(txt)
                    
    if curr_q:
        questions.append(curr_q)
        
    return questions, keys, solutions

# Test on all 20 mocks!
total_qs = 0
for m_num in sorted(mocks.keys()):
    qs, keys, sols = parse_mock(m_num, mocks[m_num]['raw_items'], mocks[m_num]['table'])
    assert len(qs) == 65, f"Mock {m_num} has {len(qs)} questions instead of 65"
    assert len(keys) == 65, f"Mock {m_num} has {len(keys)} keys instead of 65"
    assert len(sols) == 65, f"Mock {m_num} has {len(sols)} solutions instead of 65"
    
    # Check each question
    for q in qs:
        # Check statement
        full_text = q['statement']
        if q['extra_lines']:
            full_text += '\n' + '\n'.join(q['extra_lines'])
        assert len(full_text.strip()) > 5, f"Empty question text Mock {m_num} Q{q['q_num']}"
        
        # Check options
        if q['type'] in ('mcq', 'msq'):
            assert len(q['options']) == 4, f"Options != 4 in Mock {m_num} Q{q['q_num']} (got {len(q['options'])})"
            for opt_idx, opt in enumerate(q['options']):
                assert len(opt.strip()) > 0, f"Empty option {opt_idx} in Mock {m_num} Q{q['q_num']}"
        elif q['type'] == 'nat':
            # key must be convertible to float
            key_val = keys[q['q_num']]
            try:
                float(key_val)
            except ValueError:
                print(f"WARNING: NAT key not float in Mock {m_num} Q{q['q_num']}: {key_val}")
                
        # Check solution
        assert len(sols[q['q_num']].strip()) > 5, f"Empty solution Mock {m_num} Q{q['q_num']}"
        total_qs += 1

print(f"SUCCESS! All 20 Mocks successfully parsed and validated: {total_qs} questions total!")
