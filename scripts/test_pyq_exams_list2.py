# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('const FULL_LENGTH_PYQ_EXAMS = [')
idx2 = text.find('];', idx1)
block = text[idx1:idx2+2]

import re
items = block.split('  {\n    id:')
print("Total split items:", len(items) - 1)
for it in items[1:]:
    lines = it.split('\n')
    it_id = lines[0].strip().strip("',\"")
    it_name = [l for l in lines if 'name:' in l]
    it_year = [l for l in lines if 'year:' in l]
    it_diff = [l for l in lines if 'difficulty:' in l]
    name_str = it_name[0].strip() if it_name else 'no name'
    year_str = it_year[0].strip() if it_year else 'no year'
    diff_str = it_diff[0].strip() if it_diff else 'no diff'
    print(f"{it_id:22} | {year_str:12} | {diff_str:25} | {name_str}")
