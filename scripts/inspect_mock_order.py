import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
mock_block = m.group(1)

entries = re.findall(r'(\{\s*id:\s*[\'"]([^\'"]+)[\'"][\s\S]*?\n  \})', mock_block)

print(f'Total mocks in MOCK_TESTS: {len(entries)}')
for idx, (raw, mid) in enumerate(entries):
    nm = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', raw)
    tp = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', raw)
    diff = re.search(r'difficulty:\s*[\'"]([^\'"]+)[\'"]', raw)
    prov = re.search(r'provider:\s*[\'"]([^\'"]+)[\'"]', raw)
    desc = re.search(r'desc:\s*[\'"]([^\'"]+)[\'"]', raw)
    name_str = nm.group(1) if nm else ""
    type_str = tp.group(1) if tp else ""
    diff_str = diff.group(1) if diff else ""
    prov_str = prov.group(1) if prov else ""
    desc_str = desc.group(1) if desc else ""
    print(f"{idx+1:03d}. {mid} | {type_str} | {diff_str} | {prov_str} | Name: {name_str} | Desc: {desc_str[:60]}")
