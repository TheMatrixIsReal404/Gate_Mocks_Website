import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
mock_block = m.group(1)
entries = re.findall(r'\{\s*id:\s*[\'"]([^\'"]+)[\'"]', mock_block)
print(f'Total objects with id in MOCK_TESTS: {len(entries)}')

subwise = [mid for mid in entries if 'subwise' in mid]
print(f'Subwise: {len(subwise)}')
full = [mid for mid in entries if 'subwise' not in mid]
print(f'Full length / practice: {len(full)}')
