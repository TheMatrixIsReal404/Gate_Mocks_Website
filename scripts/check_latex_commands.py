# -*- coding: utf-8 -*-
import json
import re

with open('data/sample_questions.json', encoding='utf-8') as f:
    master = json.load(f)

new_qs = [q for q in master if q['id'].startswith(('zeal_cp_', 'zeal_dld_', 'zeal_em_', 'me24_pds_'))]

all_latex_commands = set()
for q in new_qs:
    fields = [q.get('question', '')] + (q.get('options') or []) + [q.get('explanation') or '']
    for text in fields:
        if not isinstance(text, str):
            continue
        math_blocks = re.findall(r'\$([^\$]+)\$', text)
        for mb in math_blocks:
            cmds = re.findall(r'\\[a-zA-Z]+', mb)
            all_latex_commands.update(cmds)

print('All LaTeX commands found in new questions:')
print(sorted(list(all_latex_commands)))
