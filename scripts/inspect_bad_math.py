# -*- coding: utf-8 -*-
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/sample_questions.json', encoding='utf-8') as f:
    master = json.load(f)

bad_qids = [
    'zeal_dld_009', 'zeal_dld_010', 'zeal_dld_020', 'zeal_dld_022',
    'zeal_dld_028', 'zeal_dld_031', 'zeal_dld_066', 'zeal_dld_067',
    'zeal_dld_069', 'zeal_dld_070', 'zeal_dld_135', 'zeal_dld_136',
    'zeal_em_363', 'zeal_em_364'
]

for q in master:
    if q['id'] in bad_qids:
        print(f"*** {q['id']} ***")
        print(q['question'])
        print('Options:', q.get('options'))
        print('---')
