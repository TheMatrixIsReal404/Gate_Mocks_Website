import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
mock_block = m.group(1)

# Extract each object
raw_objects = []
depth = 0
start = -1
for i, ch in enumerate(mock_block):
    if ch == '{':
        if depth == 0:
            start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and start != -1:
            raw_objects.append(mock_block[start:i+1])
            start = -1

print(f"Total objects in MOCK_TESTS: {len(raw_objects)}")

subwise = []
full_and_practice = []

for obj in raw_objects:
    id_m = re.search(r'id:\s*[\'"]([^\'"]+)[\'"]', obj)
    type_m = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', obj)
    name_m = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', obj)
    prov_m = re.search(r'provider:\s*[\'"]([^\'"]+)[\'"]', obj)
    diff_m = re.search(r'difficulty:\s*[\'"]([^\'"]+)[\'"]', obj)
    
    mid = id_m.group(1) if id_m else ''
    mtype = type_m.group(1) if type_m else 'full'
    mname = name_m.group(1) if name_m else ''
    mprov = prov_m.group(1) if prov_m else ''
    mdiff = diff_m.group(1) if diff_m else ''

    if mtype == 'subwise':
        subwise.append((mid, mname))
    else:
        full_and_practice.append({
            'id': mid,
            'type': mtype,
            'name': mname,
            'provider': mprov,
            'difficulty': mdiff,
            'raw': obj
        })

print(f"Subwise mocks: {len(subwise)}")
print(f"Full-length & practice mocks: {len(full_and_practice)}")

# Breakdown of full_and_practice:
groups = {}
for item in full_and_practice:
    mid = item['id']
    if mid.startswith('mock-me24-') or mid.startswith('mock-me23-'):
        grp = 'Made Easy (21)'
    elif mid.startswith('mock-go-') or mid.startswith('mock-go25-'):
        grp = 'Gate Overflow / GO Classes (27)'
    elif mid.startswith('mock-gate-2025'):
        grp = 'Official GATE 2025 (2)'
    elif mid.startswith('mock-cat'):
        grp = 'Category 1 & 2 (10)'
    elif mid.startswith('mock-full-'):
        grp = 'Full Level 1-3 & Masters (5)'
    elif mid.startswith('mock-flm-'):
        grp = 'Compendium FLM (20)'
    elif mid.startswith('mock-med-'):
        grp = '30 Medium Series (30)'
    elif mid.startswith('mock-easy-'):
        grp = '30 Easy Series (30)'
    elif item['type'] == 'practice-set':
        grp = 'Practice Sets (7)'
    else:
        grp = 'Other'
    groups.setdefault(grp, []).append(item['id'])

for g, items in groups.items():
    print(f"  {g}: {len(items)} items")
