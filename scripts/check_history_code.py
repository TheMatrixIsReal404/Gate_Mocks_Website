with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
m = re.search(r'function renderMockHistory[\s\S]*?\n\}', content)
if not m:
    # search where history is rendered
    m = re.search(r'if \(tab === [\'"]history[\'"]\)[\s\S]*?\n  \}', content)

if m:
    print(m.group(0)[:500])
else:
    print("History render block not found via simple search")
