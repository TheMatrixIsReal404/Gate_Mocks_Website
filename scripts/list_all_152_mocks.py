import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
mock_block = m.group(1)

# Let's extract all mock objects properly
# Find where each { begins and ends
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

print(f"Total extracted mock objects: {len(raw_objects)}")

full_mocks = []
for obj in raw_objects:
    id_m = re.search(r'id:\s*[\'"]([^\'"]+)[\'"]', obj)
    type_m = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', obj)
    name_m = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', obj)
    desc_m = re.search(r'desc:\s*[\'"]([^\'"]+)[\'"]', obj)
    prov_m = re.search(r'provider:\s*[\'"]([^\'"]+)[\'"]', obj)
    diff_m = re.search(r'difficulty:\s*[\'"]([^\'"]+)[\'"]', obj)
    
    mid = id_m.group(1) if id_m else ""
    mtype = type_m.group(1) if type_m else ""
    name = name_m.group(1) if name_m else ""
    desc = desc_m.group(1) if desc_m else ""
    prov = prov_m.group(1) if prov_m else ""
    diff = diff_m.group(1) if diff_m else ""
    
    if mtype in ['full', 'practice-set']:
        full_mocks.append({
            'id': mid,
            'type': mtype,
            'name': name,
            'desc': desc,
            'provider': prov,
            'difficulty': diff,
            'raw': obj
        })

print(f"Total full/practice mocks: {len(full_mocks)}")
for idx, fm in enumerate(full_mocks):
    print(f"{idx+1:03d}. {fm['id']} | type: {fm['type']} | diff: {fm['difficulty']} | name: {fm['name']}")
