with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.findall(r'(\w+\.name\b[^\n]*)', content)
print(f"Total occurrences of .name: {len(matches)}")
for m in matches[:15]:
    print(" ", m.strip())
