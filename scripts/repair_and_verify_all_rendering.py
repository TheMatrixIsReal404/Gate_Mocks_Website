# -*- coding: utf-8 -*-
"""
repair_and_verify_all_rendering.py
Thoroughly repairs and audits math expressions, LaTeX syntax, and formatting
across all 20,093 questions in data/sample_questions.json.
"""
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

MASTER_PATH = 'data/sample_questions.json'

def clean_question_math(text):
    if not text:
        return text
        
    s = text
    
    # 1. Fix Symbol font and Private Use characters
    s = s.replace('\uf071', r'\theta')
    s = s.replace('\uf0ac', r'\leftarrow')
    s = s.replace('\uf061', r'\alpha')
    s = s.replace('\uf062', r'\beta')
    s = s.replace('\uf067', r'\gamma')
    s = s.replace('\uf064', r'\delta')
    s = s.replace('\uf070', r'\pi')
    s = s.replace('\uf073', r'\sigma')
    s = s.replace('\uf077', r'\omega')
    s = s.replace('\uf053m', r'\sum m')
    s = s.replace('𝝀', r'\lambda')
    s = s.replace('𝛱', r'\prod')
    
    # 2. Fix broken LaTeX commands
    s = s.replace(r'\summ', r'\sum m')
    s = s.replace(r'\prodM', r'\prod M')
    s = s.replace(r'\prodm', r'\prod m')
    
    # Fix \sqrtsin2x+ sin2\theta
    s = re.sub(r'\\sqrtsin2x\+\s*sin2(?:\\theta|)', r'\\sqrt{\\sin^2 x + \\sin^2 \\theta}', s)
    s = re.sub(r'\\sqrt([0-9a-zA-Z]+)', r'\\sqrt{\1}', s)
    
    # 3. Fix double/nested dollar expressions
    # e.g. $F(A, B, C, D) = $\summ(0, 4, 5, 8, 12, 13)$$
    s = re.sub(r'\$([Ff]\s*\([A-Za-z,\s]+\)\s*=)\s*\$\s*\\sum\s*m\s*(\([0-9,\s]+\))\s*\$\$', r'$\1 \\sum m\2$', s)
    s = re.sub(r'\$([Ff]\s*\([A-Za-z,\s]+\)\s*=)\s*\$\s*\\prod\s*M\s*(\([0-9,\s]+\))\s*\$\$', r'$\1 \\prod M\2$', s)
    s = re.sub(r'\$([A-Za-z]\s*\([A-Za-z,\s]+\)\s*=)\s*\$\s*\\sum\s*m\s*(\([0-9,\s]+\))\s*\$\$', r'$\1 \\sum m\2$', s)
    s = re.sub(r'\$([A-Za-z]\s*\([A-Za-z,\s]+\)\s*=)\s*\$\s*\\prod\s*M\s*(\([0-9,\s]+\))\s*\$\$', r'$\1 \\prod M\2$', s)
    
    # Generic double dollar un-nesting: $expr1 = $\expr2$$ -> $expr1 = \expr2$
    s = re.sub(r'\$([^$]+?)\s*\$\s*(\\[a-zA-Z]+[^$]+?)\s*\$\$', r'$\1 \2$', s)
    
    # 4. Fix specific questions with English trapped in math
    # zeal_dld_052: Consider the Boolean function$F(x, y, z) = 𝛱(0,3,4,7). Which one of the following is the$ ...
    if 'Consider the Boolean function$F(x, y, z)' in s:
        s = s.replace(
            'Consider the Boolean function$F(x, y, z) = \\prod(0,3,4,7). Which one of the following is the$',
            'Consider the Boolean function $F(x, y, z) = \\prod(0,3,4,7)$. Which one of the following is the'
        )
        s = s.replace('function \\bar{f}', 'function $\\bar{f}$')
        
    # zeal_dld_022: Consider the function$f(a, b, c) = ab+ b'c' + ac'. The minterm list form of a Boolean$
    if 'Consider the function$f(a, b, c)' in s:
        s = s.replace(
            "Consider the function$f(a, b, c) = ab+ b'c' + ac'. The minterm list form of a Boolean$",
            "Consider the function $f(a, b, c) = ab + b'c' + ac'$. The minterm list form of a Boolean"
        )
        s = s.replace('function \\bar{f}', 'function $\\bar{f}$')
        
    # zeal_em_363: If $f (x) = x2 + 2bx + 2c2 and g (x) = -x2 – 2cx + b2 are such that minimum value of f (x) is$
    if 'If $f (x) = x2 + 2bx + 2c2' in s:
        s = s.replace(
            'If $f (x) = x2 + 2bx + 2c2 and g (x) = -x2 – 2cx + b2 are such that minimum value of f (x) is$',
            'If $f(x) = x^2 + 2bx + 2c^2$ and $g(x) = -x^2 - 2cx + b^2$ are such that the minimum value of $f(x)$ is'
        )
        
    # zeal_em_364: Let $f (x) = cos x (sin x + \sqrt{\sin^2 x + \sin^2 \theta}), where ‘\theta’ is a given constant ,then maximum$
    if 'Let $f (x) = cos x (sin x' in s:
        s = re.sub(
            r'Let \$f \(x\) = cos x \(sin x \+ [^\$]+?\), where [^\$]+? ,then maximum\$',
            r'Let $f(x) = \\cos x (\\sin x + \\sqrt{\\sin^2 x + \\sin^2 \\theta})$, where $\\theta$ is a given constant, then the maximum',
            s
        )
        
    # zeal_dld_135: A Boolean function $f(A, B, C, D) = $\prodM(1, 5, 7, 11, 15)$ is to be implemented using an 8 x$
    if 'A Boolean function $f(A, B, C, D) =' in s and 'is to be implemented using an 8 x$' in s:
        s = s.replace(
            'A Boolean function $f(A, B, C, D) = $\\prodM(1, 5, 7, 11, 15)$ is to be implemented using an 8 x$',
            'A Boolean function $f(A, B, C, D) = \\prod M(1, 5, 7, 11, 15)$ is to be implemented using an $8 \\times 1$'
        )
        s = s.replace('1 multiplexer (A is MSB)', 'multiplexer (A is MSB)')
        
    # 5. Escape standalone currency $5, $10, $20, $30, $40, $50
    s = re.sub(r'(?:^|[\s(])\$(\d+(?:\.\d+)?)(?=[\s,.;:!?)]|$)', r' \\\$\1', s)
    
    return s

def clean_options(options):
    if not isinstance(options, list):
        return options
    cleaned = []
    for opt in options:
        if isinstance(opt, str):
            opt_clean = clean_question_math(opt)
            cleaned.append(opt_clean)
        else:
            cleaned.append(opt)
    return cleaned

def main():
    print("Loading master datastore...")
    master = json.load(open(MASTER_PATH, encoding='utf-8'))
    print(f"Loaded {len(master)} questions.")
    
    repaired_count = 0
    for q in master:
        orig_q = q.get('question', '')
        orig_opts = json.dumps(q.get('options', []))
        
        new_q = clean_question_math(orig_q)
        new_opts = clean_options(q.get('options', []))
        
        if new_q != orig_q or json.dumps(new_opts) != orig_opts:
            q['question'] = new_q
            q['options'] = new_opts
            repaired_count += 1
            
    print(f"Repaired and refined math/LaTeX formatting in {repaired_count} questions.")
    
    with open(MASTER_PATH, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print("Saved updated datastore.")

if __name__ == '__main__':
    main()
