import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
mock_block = m.group(1)

entries = re.findall(r'(\{\s*id:\s*[\'"]([^\'"]+)[\'"][\s\S]*?\n  \})', mock_block)

print(f'Total mocks in MOCK_TESTS: {len(entries)}')

groups = {}
for raw, mid in entries:
    name_m = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', raw)
    type_m = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', raw)
    diff_m = re.search(r'difficulty:\s*[\'"]([^\'"]+)[\'"]', raw)
    tier_m = re.search(r'tier:\s*[\'"]([^\'"]+)[\'"]', raw)
    desc_m = re.search(r'desc:\s*[\'"]([^\'"]+)[\'"]', raw)
    
    parts = mid.split('-')
    grp = parts[1] if len(parts) > 1 else 'other'
    groups.setdefault(grp, []).append({
        'id': mid,
        'name': name_m.group(1) if name_m else '',
        'type': type_m.group(1) if type_m else '',
        'diff': diff_m.group(1) if diff_m else '',
        'tier': tier_m.group(1) if tier_m else '',
        'desc': desc_m.group(1) if desc_m else ''
    })

for k, items in sorted(groups.items()):
    print(f'Group "{k}" ({len(items)} items):')
    for it in items[:3]:
        print(f"   {it['id']} | type: {it['type']} | diff: {it['diff']} | name: {it['name'][:40]} | desc: {it['desc'][:50]}")
    if len(items) > 3:
        print(f"   ... and {len(items)-3} more")
