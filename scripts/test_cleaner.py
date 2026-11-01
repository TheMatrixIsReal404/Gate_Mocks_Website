# -*- coding: utf-8 -*-
import json
import re

with open('previous_questions.json', 'r', encoding='utf-8') as f:
    pq = json.load(f)

def clean_option(opt):
    if not opt:
        return ''
    opt = str(opt).strip()
    opt = re.sub(r'^[}\~@]\s*', '', opt)
    opt = re.sub(r'^[\(\[]?[A-Da-d][\)\]\.\:]\s+', '', opt)
    opt = opt.replace('\ufffd', "'")
    return opt.strip()

empty_opts = []
for q in pq:
    for idx, opt in enumerate(q.get('options', [])):
        cleaned = clean_option(opt)
        if not cleaned:
            empty_opts.append((q['id'], idx, opt))

print(f"Empty options with refined cleaner: {len(empty_opts)}")
if empty_opts:
    print("Sample empty opts:", empty_opts[:5])
