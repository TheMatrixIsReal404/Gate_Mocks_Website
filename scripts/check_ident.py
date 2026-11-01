# -*- coding: utf-8 -*-
import re

with open('app.js', encoding='utf-8') as f:
    code = f.read()

start = code.find('Object.assign(window, {')
end = code.rfind('});')
block = code[start:end]

lines = [l.strip().rstrip(',') for l in block.split('\n') if l.strip() and not l.strip().startswith('//') and 'Object.assign' not in l]

for l in lines:
    if ':' in l:
        continue
    ident = l.strip()
    if not ident:
        continue
    # Check if ident is declared with function, const, let, var, or import
    has_decl = bool(re.search(r'\b(function|const|let|var|import\s+.*?\b)\s+' + re.escape(ident) + r'\b', code))
    if not has_decl:
        print(f'UNDECLARED IDENTIFIER: "{ident}"')
