with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
m = re.search(r'function buildTestHistory[\s\S]*?\n\}', content)
if m:
    print(m.group(0)[:800])
