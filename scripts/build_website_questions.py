# -*- coding: utf-8 -*-
"""
build_website_questions.py
High-fidelity extraction of test questions with LaTeX mathematics,
formatted C programs (Prism.js code blocks), and clean cropped diagrams/assets.
Formatted strictly according to the website architecture of 0.Gate_Mocks_Website.
"""
import os
import re
import sys
import json
import hashlib
from collections import Counter
import pymupdf
from PIL import Image, ImageOps

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

WEBSITE_DIR = r"g:\0.Gate_Lectures\0.Gate_Mocks_Website"
DATA_DIR = os.path.join(WEBSITE_DIR, "data")
ASSETS_DIR = os.path.join(WEBSITE_DIR, "assets", "diagrams")
ZEAL_ASSETS_DIR = os.path.join(ASSETS_DIR, "zeal")
ME2024_ASSETS_DIR = os.path.join(ASSETS_DIR, "made_easy_2024")
ME2023_ASSETS_DIR = os.path.join(ASSETS_DIR, "made_easy_2023")

OCR_TEXT_DIR = r"g:\0.Gate_Lectures\OCR_to_Text"

os.makedirs(ZEAL_ASSETS_DIR, exist_ok=True)
os.makedirs(ME2024_ASSETS_DIR, exist_ok=True)
os.makedirs(ME2023_ASSETS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. LaTeX & Mathematical Notation Formatter
# -------------------------------------------------------------
MATH_UNICODE_MAP = {
    '': r' \oplus ',
    '⊕': r' \oplus ',
    '': r' \times ',
    '×': r' \times ',
    '∑': r'\sum ',
    '∏': r'\prod ',
    '∫': r'\int ',
    '√': r'\sqrt ',
    '≤': r' \le ',
    '≥': r' \ge ',
    '≠': r' \ne ',
    '∈': r' \in ',
    '∉': r' \notin ',
    '∪': r' \cup ',
    '∩': r' \cap ',
    '⊂': r' \subset ',
    '⊆': r' \subseteq ',
    '→': r' \to ',
    '↔': r' \leftrightarrow ',
    '¬': r' \neg ',
    '∧': r' \land ',
    '∨': r' \lor ',
    '∞': r' \infty ',
    'α': r'\alpha',
    'β': r'\beta',
    'γ': r'\gamma',
    'δ': r'\delta',
    'θ': r'\theta',
    'λ': r'\lambda',
    'μ': r'\mu',
    'π': r'\pi',
    'σ': r'\sigma',
    'ω': r'\omega',
    '𝛽': r'\beta',
    '𝛾': r'\gamma',
    '𝛼': r'\alpha',
    '𝛱': r'\prod ',
    '𝝀': r'\lambda',
    '\uf071': r'\theta',
    '\uf0ac': r' \leftarrow ',
    '\uf061': r'\alpha',
    '\uf062': r'\beta',
    '\uf067': r'\gamma',
    '\uf064': r'\delta',
    '\uf070': r'\pi',
    '\uf073': r'\sigma',
    '\uf077': r'\omega',
    '\uf053': r'\sum ',
}

def to_katex_latex(text):
    """Converts mathematical expressions, Greek symbols, and overbars to KaTeX LaTeX."""
    if not text:
        return ""
    
    chars = []
    i = 0
    n = len(text)
    
    while i < n:
        c = text[i]
        cp = ord(c)
        
        # Mathematical italic small: U+1D44E to U+1D467 (𝑎 to 𝑧)
        if 0x1D44E <= cp <= 0x1D467:
            base_char = chr(ord('a') + (cp - 0x1D44E))
        # Mathematical italic capital: U+1D434 to U+1D44D (𝐴 to 𝑍)
        elif 0x1D434 <= cp <= 0x1D44D:
            base_char = chr(ord('A') + (cp - 0x1D434))
        elif c in MATH_UNICODE_MAP:
            base_char = MATH_UNICODE_MAP[c]
        else:
            base_char = c
            
        # Check combining overbar U+0305, U+0304
        if i + 1 < n and text[i+1] in ['\u0305', '\u0304']:
            chars.append(f'\\bar{{{base_char}}}')
            i += 2
            continue
            
        chars.append(base_char)
        i += 1
        
    res = ''.join(chars)
    res = re.sub(r'([A-Za-z0-9])’', r"\1'", res)
    # Normalize backtick primes: x` -> x'
    res = re.sub(r'([A-Za-z])`', r"\1'", res)
    
    # Clean any malformed commands
    res = re.sub(r'\\summ\b', lambda m: r'\sum m', res)
    res = re.sub(r'\\prodM\b', lambda m: r'\prod M', res)
    res = re.sub(r'\\prodm\b', lambda m: r'\prod m', res)
    res = re.sub(r'\\sqrtsin2x\+\s*sin2(?:\\theta|)', lambda m: r'\sqrt{\sin^2 x + \sin^2 \theta}', res)
    res = re.sub(r'\\sqrt([0-9a-zA-Z]+)', lambda m: f'\\sqrt{{{m.group(1)}}}', res)
    
    # Wrap function definitions like F(A, B, C) = ... strictly within a single line
    def clean_func_expr(m):
        eq = m.group(0).replace('$', '').strip()
        return f"${eq}$"

    res = re.sub(
        r'([FfWwXxYyZzA-D]\s*\([A-Za-z0-9,\s]+\)\s*=\s*[\w\+\-\*\/\^\_[ \t]\(\)\\\'\.\,\{\}\[\]\=]+?)(?=[ \t]*(?:is|be|where|then|and|which|with|for|can|satisfies|in|let|\.|\?|$|\n))',
        clean_func_expr,
        res
    )
    
    # Wrap standalone \sum m(...) or \prod M(...) or \prod M if NOT already inside $...$
    parts = res.split('$')
    for p_idx in range(0, len(parts), 2):
        parts[p_idx] = re.sub(
            r'(\\sum\s*m\s*\([0-9,\s]+\)|\\prod\s*M\s*\([0-9,\s]+\)|\\prod\s*M\b|\\sum\s*m\b)',
            r'$\1$',
            parts[p_idx]
        )
    res = '$'.join(parts)
    
    # Clean nested/double dollars: $expr1 = $\expr2$$ -> $expr1 = \expr2$
    res = re.sub(r'\$([^$]+?)\s*\$\s*(\\[a-zA-Z]+[^$]+?)\s*\$\$', r'$\1 \2$', res)
    
    return res

# -------------------------------------------------------------
# 2. C Program Code Block Formatter
# -------------------------------------------------------------
C_KEYWORDS = {
    '#include', 'int', 'void', 'char', 'float', 'double', 'struct', 'typedef',
    'return', 'printf', 'scanf', 'for', 'while', 'if', 'else', 'switch',
    'case', 'break', 'continue', 'default', 'static', 'const', 'sizeof'
}

def is_c_code_line(line):
    s = line.strip()
    if not s:
        return False
    if s.startswith(('#include', '#define', '//', '/*', '*/')):
        return True
    if any(s.startswith(kw + ' ') or s.startswith(kw + '(') or s.startswith(kw + '{') for kw in C_KEYWORDS):
        return True
    if re.search(r'\b(main|printf|scanf|malloc|free|sizeof)\s*\(', s):
        return True
    if re.search(r'\b(int|char|void|float|double)\s+\*?[a-zA-Z_]\w*', s):
        return True
    if s in ['{', '}', '};']:
        return True
    return False

def clean_and_format_c_code(raw_code_lines):
    """Formats raw C code lines into cleanly indented code block."""
    cleaned = []
    indent_level = 0
    for line in raw_code_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_clean = re.sub(r'\s*\{\s*$', ' {', line_clean)
        if line_clean.startswith(('}', '};')):
            indent_level = max(0, indent_level - 1)
            
        indent = "    " * indent_level
        cleaned.append(f"{indent}{line_clean}")
        
        if '{' in line_clean and '}' not in line_clean and not line_clean.startswith('//'):
            indent_level += 1
            
    code_str = "\n".join(cleaned)
    return f"\n```c\n{code_str}\n```\n"

def extract_c_code_from_block(text):
    """Scans text for C programming sections and wraps them into ```c ... ``` blocks."""
    lines = text.split('\n')
    output_lines = []
    c_buffer = []
    in_code = False
    
    for line in lines:
        s = line.strip()
        if is_c_code_line(line):
            in_code = True
            c_buffer.append(line)
        elif in_code and not s:
            c_buffer.append('')
        else:
            if in_code:
                while c_buffer and not c_buffer[-1].strip():
                    c_buffer.pop()
                if len([l for l in c_buffer if l.strip()]) >= 2:
                    formatted_code = clean_and_format_c_code(c_buffer)
                    output_lines.append(formatted_code)
                else:
                    output_lines.extend(c_buffer)
                c_buffer = []
                in_code = False
            output_lines.append(line)
            
    if in_code and c_buffer:
        while c_buffer and not c_buffer[-1].strip():
            c_buffer.pop()
        if len([l for l in c_buffer if l.strip()]) >= 2:
            output_lines.append(clean_and_format_c_code(c_buffer))
        else:
            output_lines.extend(c_buffer)
            
    return "\n".join(output_lines)

# -------------------------------------------------------------
# 3. Diagram Cropping & White-Padding Removal
# -------------------------------------------------------------
def crop_tight_diagram(pix, out_path):
    """Tight-crops whitespace from a pixmap and saves as crisp PNG."""
    if os.path.exists(out_path):
        return
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    gray = img.convert('L')
    inv = ImageOps.invert(gray)
    threshold = 15
    inv = inv.point(lambda p: 255 if p > threshold else 0)
    bbox = inv.getbbox()
    if bbox:
        w, h = img.size
        x0 = max(0, bbox[0] - 10)
        y0 = max(0, bbox[1] - 10)
        x1 = min(w, bbox[2] + 10)
        y1 = min(h, bbox[3] + 10)
        cropped = img.crop((x0, y0, x1, y1))
        cropped.save(out_path, optimize=True)
    else:
        img.save(out_path, optimize=True)

# -------------------------------------------------------------
# 4. Zeal Practice Sheets: C Programming (112 Questions)
# -------------------------------------------------------------
def parse_zeal_c_programming():
    pdf_path = r"g:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\Zeal_Practice Sheet 2023\3. C programming\C Programming Language Questions.pdf"
    ans_path = r"g:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\Zeal_Practice Sheet 2023\3. C programming\Basic C programming Answer Keys.pdf"
    
    if not os.path.exists(pdf_path):
        print("C programming PDF not found:", pdf_path)
        return []
        
    doc = pymupdf.open(pdf_path)
    ans_doc = pymupdf.open(ans_path)
    ans_txt = "\n".join([ans_doc[p].get_text() for p in range(len(ans_doc))])
    
    answer_keys = {}
    for line in ans_txt.splitlines():
        line = line.strip()
        m = re.match(r'^(\d+)[\.\)]\s*(.*)$', line)
        if m:
            try:
                qnum = int(m.group(1))
                answer_keys[qnum] = m.group(2).strip()
            except:
                pass
                
    print(f"Loaded {len(answer_keys)} answer keys for Zeal C Programming.")
    
    all_text = ""
    for p in range(len(doc)):
        txt = doc[p].get_text('text', sort=True)
        all_text += f"\n---PAGE_{p+1}---\n" + txt
        
    matches = list(re.finditer(r'(?:^|\n)\s*Q(\d+)[\.\)]\s*', all_text))
    questions = []
    
    for i in range(len(matches)):
        qnum = int(matches[i].group(1))
        start_pos = matches[i].end()
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(all_text)
        raw_block = all_text[start_pos:end_pos].strip()
        raw_block = re.sub(r'---PAGE_\d+---', '', raw_block)
        raw_block = re.sub(r'C Programming\s+Page \d+', '', raw_block, flags=re.I).strip()
        
        opt_matches = list(re.finditer(r'(?:^|\n|\s{3,})\(([a-dA-D])\)\s*', raw_block))
        options = []
        if len(opt_matches) >= 2:
            body = raw_block[:opt_matches[0].start()].strip()
            for j in range(len(opt_matches)):
                ostart = opt_matches[j].end()
                oend = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(raw_block)
                opt_str = raw_block[ostart:oend].strip()
                opt_str = re.sub(r'C Programming\s+Page \d+', '', opt_str, flags=re.I).strip()
                options.append(opt_str)
            q_type = 'mcq'
        else:
            body = raw_block
            options = []
            q_type = 'nat'
            
        body_with_code = extract_c_code_from_block(body)
        
        ans_val = answer_keys.get(qnum, '')
        correct = []
        has_usable_key = False
        
        if ans_val:
            ans_upper = ans_val.upper()
            if len(ans_upper) == 1 and 'A' <= ans_upper <= 'D':
                idx = ord(ans_upper) - ord('A')
                if idx < len(options) or q_type == 'nat':
                    correct = [idx]
                    has_usable_key = True
            elif '.' in ans_val or any(l in ans_val.lower() for l in ['a', 'b', 'c', 'd']):
                letters = re.findall(r'[A-D]', ans_upper)
                if len(letters) > 1:
                    q_type = 'msq'
                    correct = sorted(list(set([ord(l) - ord('A') for l in letters if ord(l) - ord('A') < len(options)])))
                    has_usable_key = len(correct) > 0
                elif len(letters) == 1 and len(options) > ord(letters[0]) - ord('A'):
                    correct = [ord(letters[0]) - ord('A')]
                    has_usable_key = True
            else:
                try:
                    num_val = float(ans_val.split()[0])
                    correct = [num_val]
                    q_type = 'nat'
                    has_usable_key = True
                except:
                    pass
                    
        seq_idx = i + 1
        qid = f"zeal_cp_{seq_idx:03d}"
        q_obj = {
            'id': qid,
            'canonicalId': qid,
            'type': q_type,
            'category': 'test_series',
            'subject': 'C Programming',
            'topic': 'C Language Fundamentals & Pointers',
            'difficulty': 'medium',
            'year': 2023,
            'paper': 'Zeal Practice Sheet 2023 - C Programming',
            'marks': 1 if len(body) < 250 else 2,
            'question': body_with_code,
            'options': options,
            'correct': correct,
            'explanation': f"Official Answer: {ans_val}" if ans_val else "",
            'hasUsableKey': has_usable_key,
            'source': 'Zeal Practice Sheet 2023 - C Programming Language Questions.pdf'
        }
        questions.append(q_obj)
        
    print(f"Extracted {len(questions)} Zeal C programming questions.")
    return questions

# -------------------------------------------------------------
# 5. Zeal DLD Basic Parser (251 Questions, 5 Sections)
# -------------------------------------------------------------
def parse_zeal_dld_basic():
    pdf_path = r"g:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\Zeal_Practice Sheet 2023\6. DLD\Basic\DLD - Basic  Sheet.pdf"
    ans_path = r"g:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\Zeal_Practice Sheet 2023\6. DLD\Basic\Basic Digital Booklet Answer Keys.pdf"
    
    if not os.path.exists(pdf_path):
        print("DLD PDF not found:", pdf_path)
        return []
        
    doc = pymupdf.open(pdf_path)
    ans_doc = pymupdf.open(ans_path)
    ans_p1 = ans_doc[0].get_text()
    ans_p2 = ans_doc[1].get_text()
    
    # Parse section keys
    def extract_sec_keys(text):
        res = {}
        for line in text.splitlines():
            line = line.strip()
            m = re.match(r'^(\d+)[\.\)]\s*(.*)$', line)
            if m:
                try:
                    q = int(m.group(1))
                    res[q] = m.group(2).strip()
                except:
                    pass
        return res
        
    # K-Map section
    kmap_start = ans_p1.find("K – MAP")
    comb_start = ans_p1.find("Combinational Circuits")
    seq_start = ans_p1.find("Sequential Circuit")
    test1_start = ans_p2.find("Digital Test -1")
    test2_start = ans_p2.find("Digital Test-2")
    
    kmap_keys = extract_sec_keys(ans_p1[kmap_start:comb_start])
    comb_keys = extract_sec_keys(ans_p1[comb_start:seq_start])
    seq_keys = extract_sec_keys(ans_p1[seq_start:] + "\n" + ans_p2[:test1_start])
    test1_keys = extract_sec_keys(ans_p2[test1_start:test2_start])
    test2_keys = extract_sec_keys(ans_p2[test2_start:])
    
    print(f"DLD Keys loaded: KMap={len(kmap_keys)}, Comb={len(comb_keys)}, Seq={len(seq_keys)}, T1={len(test1_keys)}, T2={len(test2_keys)}")
    
    questions = []
    global_seq = 0
    
    for pno in range(len(doc)):
        page = doc[pno]
        blocks = page.get_text('blocks')
        page_txt = page.get_text('text', sort=True)
        q_matches = list(re.finditer(r'(?:^|\n)\s*Q(\d+)[\.\)]\s*', page_txt))
        if not q_matches:
            continue
            
        # Determine topic and keys from page number (0-indexed)
        # P3..P23 -> K-Map (pno 2..22)
        # P24..P41 -> Comb (pno 23..40)
        # P42..P53 -> Seq (pno 41..52)
        # P54..P58 -> Test 1 (pno 53..57)
        # P59..P64 -> Test 2 (pno 58..63)
        if pno <= 22:
            sec_name = "K-Map & Boolean Minimization"
            sec_keys = kmap_keys
        elif pno <= 40:
            sec_name = "Combinational Circuits"
            sec_keys = comb_keys
        elif pno <= 52:
            sec_name = "Sequential Circuits & Flip-Flops"
            sec_keys = seq_keys
        elif pno <= 57:
            sec_name = "Digital Logic Test-1"
            sec_keys = test1_keys
        else:
            sec_name = "Digital Logic Test-2"
            sec_keys = test2_keys
            
        for i in range(len(q_matches)):
            global_seq += 1
            qnum = int(q_matches[i].group(1))
            start_pos = q_matches[i].end()
            end_pos = q_matches[i+1].start() if i + 1 < len(q_matches) else len(page_txt)
            raw_block = page_txt[start_pos:end_pos].strip()
            raw_block = re.sub(r'BASIC DIGITAL LOGIC\s+Page \d+', '', raw_block, flags=re.I).strip()
            
            has_diagram = any(w in raw_block.lower() for w in ['k-map', 'figure', 'shown below', 'circuit', 'gate', 'logic', 'following'])
            diagram_html = ""
            
            # Check existing cropped diagram
            diag_filename = f"dld_basic_p{pno+1}_q{qnum}.png"
            diag_full_path = os.path.join(ZEAL_ASSETS_DIR, diag_filename)
            
            if os.path.exists(diag_full_path):
                web_rel_path = f"assets/diagrams/zeal/{diag_filename}"
                diagram_html = f'\n\n<figure class="q-diagram-container">\n  <img src="{web_rel_path}" alt="Question {qnum} Diagram" />\n</figure>\n\n'
            elif has_diagram:
                q_blocks = [b for b in blocks if f"Q{qnum}" in b[4] or f"Q.{qnum}" in b[4]]
                if q_blocks:
                    qb = q_blocks[0]
                    subseq = [b for b in blocks if b[1] > qb[3] and b[4].strip() and "BASIC DIGITAL LOGIC" not in b[4]]
                    if subseq:
                        next_b = subseq[0]
                        gap = next_b[1] - qb[3]
                        if gap > 35:
                            clip_rect = pymupdf.Rect(35, qb[3] - 2, 565, next_b[1] + 2)
                            pix = page.get_pixmap(clip=clip_rect, dpi=200)
                            crop_tight_diagram(pix, diag_full_path)
                            web_rel_path = f"assets/diagrams/zeal/{diag_filename}"
                            diagram_html = f'\n\n<figure class="q-diagram-container">\n  <img src="{web_rel_path}" alt="Question {qnum} Diagram" />\n</figure>\n\n'
                            
            opt_matches = list(re.finditer(r'(?:^|\n|\s{3,})\(([a-dA-D])\)\s*', raw_block))
            options = []
            if len(opt_matches) >= 2:
                body = raw_block[:opt_matches[0].start()].strip()
                for j in range(len(opt_matches)):
                    ostart = opt_matches[j].end()
                    oend = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(raw_block)
                    opt_str = raw_block[ostart:oend].strip()
                    opt_str = to_katex_latex(opt_str)
                    options.append(opt_str)
                q_type = 'mcq'
            else:
                body = raw_block
                options = []
                q_type = 'nat'
                
            body_latex = to_katex_latex(body)
            if diagram_html:
                body_latex += diagram_html
                
            ans_val = sec_keys.get(qnum, '')
            correct = []
            has_usable_key = False
            if ans_val:
                ans_upper = ans_val.upper()
                if len(ans_upper) == 1 and 'A' <= ans_upper <= 'D':
                    idx = ord(ans_upper) - ord('A')
                    if idx < len(options) or q_type == 'nat':
                        correct = [idx]
                        has_usable_key = True
                elif '.' in ans_val or any(l in ans_val.lower() for l in ['a', 'b', 'c', 'd']):
                    letters = re.findall(r'[A-D]', ans_upper)
                    if len(letters) > 1:
                        q_type = 'msq'
                        correct = sorted(list(set([ord(l) - ord('A') for l in letters if ord(l) - ord('A') < len(options)])))
                        has_usable_key = len(correct) > 0
                    elif len(letters) == 1 and len(options) > ord(letters[0]) - ord('A'):
                        correct = [ord(letters[0]) - ord('A')]
                        has_usable_key = True
                else:
                    try:
                        num_val = float(ans_val.split()[0])
                        correct = [num_val]
                        q_type = 'nat'
                        has_usable_key = True
                    except:
                        pass
                        
            qid = f"zeal_dld_{global_seq:03d}"
            q_obj = {
                'id': qid,
                'canonicalId': qid,
                'type': q_type,
                'category': 'test_series',
                'subject': 'Digital Logic',
                'topic': sec_name,
                'difficulty': 'medium',
                'year': 2023,
                'paper': 'Zeal Practice Sheet 2023 - DLD Basic',
                'marks': 1 if len(body) < 250 else 2,
                'question': body_latex,
                'options': options,
                'correct': correct,
                'explanation': f"Official Key ({sec_name} Q{qnum}): {ans_val}" if ans_val else "",
                'hasUsableKey': has_usable_key,
                'source': f'Zeal Practice Sheet 2023 - DLD Basic ({sec_name} Q{qnum})'
            }
            questions.append(q_obj)
            
    print(f"Extracted {len(questions)} Zeal DLD questions with unique sequential IDs.")
    return questions

# -------------------------------------------------------------
# 6. Zeal Engineering Mathematics Parser (745 Questions, 4 Sections)
# -------------------------------------------------------------
def parse_zeal_math_sheet():
    pdf_path = r"g:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\Zeal_Practice Sheet 2023\2. EM\Maths  Sheet_2022.pdf"
    ans_path = r"g:\0.Gate_Lectures\Gate_Test_Series&Subject_Questions\Zeal_Practice Sheet 2023\2. EM\Maths sheet Answers key_2022.pdf"
    
    if not os.path.exists(pdf_path):
        print("Math PDF not found:", pdf_path)
        return []
        
    doc = pymupdf.open(pdf_path)
    ans_doc = pymupdf.open(ans_path)
    all_ans_text = '\n'.join([ans_doc[p].get_text() for p in range(len(ans_doc))])
    
    # Extract keys per section
    def parse_em_subkeys(subtext):
        k_map = {}
        for line in subtext.splitlines():
            line = line.strip()
            matches = re.findall(r'(?:Q\s*)?(\d+)[\.\)]\s*([A-Za-z0-9\-\.\,\s]+?)(?=(?:Q\s*)?\d+[\.\)]|$)', line)
            for q_str, ans_str in matches:
                try:
                    q = int(q_str)
                    clean_ans = ans_str.strip()
                    if clean_ans and q not in k_map:
                        k_map[q] = clean_ans
                except:
                    pass
        return k_map
        
    c_idx = all_ans_text.find("Calculus")
    pnc_idx = all_ans_text.find("PNC")
    prob_idx = all_ans_text.find("Probability Answer Key 2022")
    
    mat_keys = parse_em_subkeys(all_ans_text[:c_idx])
    calc_keys = parse_em_subkeys(all_ans_text[c_idx:pnc_idx])
    pnc_keys = parse_em_subkeys(all_ans_text[pnc_idx:prob_idx])
    prob_keys = parse_em_subkeys(all_ans_text[prob_idx:])
    
    print(f"EM Keys loaded: Matrices={len(mat_keys)}, Calculus={len(calc_keys)}, PNC={len(pnc_keys)}, Prob={len(prob_keys)}")
    
    questions = []
    global_seq = 0
    
    # Process section by section
    # P3..P40 (pno 2..39): Matrices
    # P41..P66 (pno 40..65): Calculus
    # P67..P88 (pno 66..87): PNC
    # P89..P120 (pno 88..119): Probability
    sections_def = [
        ("Matrices & Linear Algebra", mat_keys, 2, 39),
        ("Calculus & Limits", calc_keys, 40, 65),
        ("Permutations & Combinations", pnc_keys, 66, 87),
        ("Probability & Distributions", prob_keys, 88, 119)
    ]
    
    for sec_title, sec_keys, p_start, p_end in sections_def:
        sec_text = ""
        for pno in range(p_start, p_end + 1):
            txt = doc[pno].get_text('text', sort=True)
            sec_text += f"\n---PAGE_{pno+1}---\n" + txt
            
        q_matches = list(re.finditer(r'(?:^|\n)\s*Q(\d+)[\.\)]\s*', sec_text))
        for i in range(len(q_matches)):
            global_seq += 1
            qnum = int(q_matches[i].group(1))
            start_pos = q_matches[i].end()
            end_pos = q_matches[i+1].start() if i + 1 < len(q_matches) else len(sec_text)
            raw_block = sec_text[start_pos:end_pos].strip()
            raw_block = re.sub(r'---PAGE_\d+---', '', raw_block)
            raw_block = re.sub(r'MATHEMATICS\s+PAGE \d+', '', raw_block, flags=re.I).strip()
            
            opt_matches = list(re.finditer(r'(?:^|\n|\s{3,})\(([a-dA-D])\)\s*', raw_block))
            options = []
            if len(opt_matches) >= 2:
                body = raw_block[:opt_matches[0].start()].strip()
                for j in range(len(opt_matches)):
                    ostart = opt_matches[j].end()
                    oend = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(raw_block)
                    opt_str = raw_block[ostart:oend].strip()
                    opt_str = to_katex_latex(opt_str)
                    options.append(opt_str)
                q_type = 'mcq'
            else:
                body = raw_block
                options = []
                q_type = 'nat'
                
            body_latex = to_katex_latex(body)
            
            ans_val = sec_keys.get(qnum, '')
            correct = []
            has_usable_key = False
            if ans_val:
                ans_upper = ans_val.upper()
                if len(ans_upper) == 1 and 'A' <= ans_upper <= 'D':
                    idx = ord(ans_upper) - ord('A')
                    if idx < len(options) or q_type == 'nat':
                        correct = [idx]
                        has_usable_key = True
                elif '.' in ans_val or any(l in ans_val.lower() for l in ['a', 'b', 'c', 'd']):
                    letters = re.findall(r'[A-D]', ans_upper)
                    if len(letters) > 1:
                        q_type = 'msq'
                        correct = sorted(list(set([ord(l) - ord('A') for l in letters if ord(l) - ord('A') < len(options)])))
                        has_usable_key = len(correct) > 0
                    elif len(letters) == 1 and len(options) > ord(letters[0]) - ord('A'):
                        correct = [ord(letters[0]) - ord('A')]
                        has_usable_key = True
                else:
                    try:
                        num_val = float(ans_val.split()[0])
                        correct = [num_val]
                        q_type = 'nat'
                        has_usable_key = True
                    except:
                        pass
                        
            qid = f"zeal_em_{global_seq:03d}"
            q_obj = {
                'id': qid,
                'canonicalId': qid,
                'type': q_type,
                'category': 'test_series',
                'subject': 'Engineering Mathematics',
                'topic': sec_title,
                'difficulty': 'medium',
                'year': 2023,
                'paper': 'Zeal Practice Sheet 2023 - Engineering Mathematics',
                'marks': 1 if len(body) < 250 else 2,
                'question': body_latex,
                'options': options,
                'correct': correct,
                'explanation': f"Official Key ({sec_title} Q{qnum}): {ans_val}" if ans_val else "",
                'hasUsableKey': has_usable_key,
                'source': f'Zeal Practice Sheet 2023 - Engineering Mathematics ({sec_title} Q{qnum})'
            }
            questions.append(q_obj)
            
    print(f"Extracted {len(questions)} Zeal Engineering Mathematics questions with unique sequential IDs.")
    return questions

# -------------------------------------------------------------
# 7. Made Easy 2024 Programming & Data Structures Parser (35 Questions)
# -------------------------------------------------------------
def parse_made_easy_programming():
    # If the JSON already has the 35 cropped questions, we reuse and refine canonical subject classification
    existing_file = os.path.join(DATA_DIR, "newly_extracted_core_cs_questions.json")
    if os.path.exists(existing_file):
        with open(existing_file, 'r', encoding='utf-8') as f:
            all_prev = json.load(f)
        me_prev = [q for q in all_prev if 'Made Easy 2024' in q.get('paper', '')]
        if len(me_prev) == 35:
            print("Reusing high-fidelity cropped Made Easy 2024 questions...")
            refined = []
            ds_keywords = ['tree', 'bst', 'binary search tree', 'traversal', 'linked list', 'stack', 'queue', 'heap', 'hashing', 'graph']
            for q in me_prev:
                # determine canonical subject
                t = q['question'].lower()
                is_ds = any(k in t for k in ds_keywords)
                subj = 'Data Structures' if is_ds else 'C Programming'
                topic = 'Trees & Data Structures' if is_ds else 'C Pointers & Functions'
                q['subject'] = subj
                q['topic'] = topic
                refined.append(q)
            return refined

    return []

# -------------------------------------------------------------
# 8. Master Pipeline Runner
# -------------------------------------------------------------
def run_pipeline():
    print("=================================================================")
    print("STARTING REFINED WEBSITE QUESTION EXTRACTION & ASSETS PIPELINE")
    print(f"Destination Website Directory: {WEBSITE_DIR}")
    print(f"Assets Directory: {ASSETS_DIR}")
    print("=================================================================")
    
    all_website_questions = []
    
    # 1. Zeal C Programming
    print("\n--- [1/4] Processing Zeal C Programming ---")
    zeal_c_qs = parse_zeal_c_programming()
    all_website_questions.extend(zeal_c_qs)
    
    # 2. Zeal DLD Basic
    print("\n--- [2/4] Processing Zeal DLD Basic ---")
    zeal_dld_qs = parse_zeal_dld_basic()
    all_website_questions.extend(zeal_dld_qs)
    
    # 3. Zeal Engineering Mathematics
    print("\n--- [3/4] Processing Zeal Engineering Mathematics ---")
    zeal_math_qs = parse_zeal_math_sheet()
    all_website_questions.extend(zeal_math_qs)
    
    # 4. Made Easy 2024 Programming & Data Structures
    print("\n--- [4/4] Processing Made Easy 2024 Programming & Data Structures ---")
    me24_prog_qs = parse_made_easy_programming()
    all_website_questions.extend(me24_prog_qs)
    
    # Save master extracted questions JSON to website data/
    out_json_path = os.path.join(DATA_DIR, "newly_extracted_core_cs_questions.json")
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_website_questions, f, ensure_ascii=False, indent=2)
        
    print(f"\n=================================================================")
    print(f"PIPELINE COMPLETE: Successfully saved {len(all_website_questions)} questions to {out_json_path}")
    print(f"Unique IDs: {len(set(q['id'] for q in all_website_questions))} / {len(all_website_questions)}")
    print("=================================================================")

if __name__ == "__main__":
    run_pipeline()
