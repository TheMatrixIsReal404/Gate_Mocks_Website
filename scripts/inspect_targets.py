import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
mock_block = m.group(1)

entries = re.findall(r'(\{\s*id:\s*[\'"]([^\'"]+)[\'"][\s\S]*?\n  \})', mock_block)

print('=== MADE EASY MOCKS ===')
for raw, mid in entries:
    if mid.startswith('mock-me24-') or mid.startswith('mock-me23-'):
        print(f"[{mid}]")
        for line in raw.splitlines():
            if any(k in line for k in ['name:', 'type:', 'difficulty:', 'rating:', 'tier:', 'desc:']):
                print(' ', line.strip())

print('\n=== GATE OVERFLOW / GO AIM MOCKS ===')
for raw, mid in entries:
    if mid.startswith('mock-go-') or mid.startswith('mock-go25-'):
        print(f"[{mid}]")
        for line in raw.splitlines():
            if any(k in line for k in ['name:', 'type:', 'difficulty:', 'rating:', 'tier:', 'desc:']):
                print(' ', line.strip())
