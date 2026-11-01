# -*- coding: utf-8 -*-
import re

with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all inline handlers like onclick="foo(" or onclick='foo('
matches1 = re.findall(r'on(?:click|change|input|submit|keyup)="([a-zA-Z0-9_]+)\(', text)
matches2 = re.findall(r"on(?:click|change|input|submit|keyup)='([a-zA-Z0-9_]+)\(", text)
all_calls = sorted(set(matches1 + matches2))

print(f"Total unique inline event calls: {len(all_calls)}")

missing = []
present = []

for fn in all_calls:
    if f"window.{fn}" in text:
        present.append(fn)
    else:
        is_def = f"function {fn}" in text or f"const {fn}" in text or f"let {fn}" in text
        missing.append((fn, is_def))

print(f"\nPresent on window ({len(present)}):", present)
print(f"\nMissing on window ({len(missing)}):")
for fn, is_def in missing:
    print(f"  {fn:30} defined in app.js: {is_def}")
