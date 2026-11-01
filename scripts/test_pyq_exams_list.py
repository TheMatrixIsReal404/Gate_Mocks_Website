# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('const FULL_LENGTH_PYQ_EXAMS = [')
idx2 = text.find('];', idx1)
block = text[idx1:idx2+2]

# Evaluate the exams array safely in JS via node or python regex
import re
exams = re.findall(r'id:\s*[\'"]([^\'"]+)[\'"].*?name:\s*[\'"]([^\'"]+)[\'"].*?year:\s*([0-9\w\'"]+)', block, re.DOTALL)
print(f"Total exams found in block: {len(exams)}")
for eid, name, year in exams:
    print(f"  {eid:20} year={year:10} {name[:35]}")
