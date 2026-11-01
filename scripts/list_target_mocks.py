import re, json

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
mock_block = m.group(1)

entries = re.findall(r'(\{\s*id:\s*[\'"]([^\'"]+)[\'"][\s\S]*?\n  \})', mock_block)

print(f"Total mocks: {len(entries)}")

found = []
for raw, mid in entries:
    if any(k in mid.lower() or k in raw.lower() for k in ['made', 'easy', 'overflow', 'aim', 'gateoverflow', 'classes']):
        # extract properties
        def get_field(k):
            fm = re.search(rf'{k}:\s*[\'"]([^\'"]+)[\'"]', raw)
            return fm.group(1) if fm else ''
        def get_num_field(k):
            fm = re.search(rf'{k}:\s*([0-9.]+)', raw)
            return float(fm.group(1)) if fm else None
        
        found.append({
            'id': mid,
            'name': get_field('name'),
            'type': get_field('type'),
            'difficulty': get_field('difficulty'),
            'rating': get_num_field('rating'),
            'tier': get_field('tier'),
            'desc': get_field('desc')
        })

print(f"Found {len(found)} candidate mock objects:")
for f_item in found:
    if not (f_item['id'].startswith('mock-easy-')): # suppress generic mock-easy-01..30 for brevity
        print(f"ID: {f_item['id']} | Type: {f_item['type']} | Diff: {f_item['difficulty']} | Rating: {f_item['rating']} | Name: {f_item['name']}")
        print(f"   Desc: {f_item['desc']}")
        print(f"   Tier: {f_item['tier']}")
        print("-" * 60)
