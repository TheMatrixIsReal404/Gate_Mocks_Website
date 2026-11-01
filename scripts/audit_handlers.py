# -*- coding: utf-8 -*-
import re

with open('index.html', encoding='utf-8') as f:
    html = f.read()

with open('app.js', encoding='utf-8') as f:
    js = f.read()

# Find all inline handlers in HTML strings inside app.js and index.html
all_text = html + '\n' + js
calls = re.findall(r'on[a-z]+\s*=\s*["\']([a-zA-Z0-9_$]+)\(', all_text, re.I)

print(f"Total unique function calls in on* handlers: {len(set(calls))}")
for fn in sorted(set(calls)):
    # Check if exposed on window or declared
    in_assign = bool(re.search(r'\b' + re.escape(fn) + r'\b', js[js.find('Object.assign(window'):]))
    in_window = f'window.{fn}' in js
    print(f"  {fn}: on window? {in_assign or in_window}")
