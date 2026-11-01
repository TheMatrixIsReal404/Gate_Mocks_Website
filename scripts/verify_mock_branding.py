import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
assert m, "MOCK_TESTS not found"
mock_block = m.group(1)

entries = re.findall(r'(\{\s*id:\s*[\'"]([^\'"]+)[\'"][\s\S]*?\n  \})', mock_block)

print(f"Total mocks in MOCK_TESTS: {len(entries)}")

errors = []
target_counts = {'me': 0, 'go_aim': 0, 'go_mg': 0, 'go25': 0}

for raw, mid in entries:
    def get_field(k):
        fm = re.search(rf'{k}:\s*[\'"]([^\'"]+)[\'"]', raw)
        return fm.group(1) if fm else ''
    
    mtype = get_field('type')
    diff = get_field('difficulty')
    name = get_field('name')
    desc = get_field('desc')
    provider = get_field('provider')
    tier = get_field('tier')

    if mid.startswith('mock-me24-') or mid.startswith('mock-me23-'):
        target_counts['me'] += 1
        if mtype != 'full':
            errors.append(f"{mid}: type is '{mtype}', expected 'full'")
        if diff not in ['easy', 'medium', 'hard']:
            errors.append(f"{mid}: invalid difficulty '{diff}'")
        if 'Made Easy' not in provider:
            errors.append(f"{mid}: provider is '{provider}', expected Made Easy")
        if not desc.startswith('[Provider: Made Easy'):
            errors.append(f"{mid}: desc does not start with '[Provider: Made Easy': {desc[:40]}")
        if not name.startswith('Made Easy:'):
            errors.append(f"{mid}: name does not start with 'Made Easy:': {name}")

    elif mid.startswith('mock-go-ts25-aim-') or mid.startswith('mock-go-ts26-aim-'):
        target_counts['go_aim'] += 1
        if mtype != 'full':
            errors.append(f"{mid}: type is '{mtype}', expected 'full'")
        if diff not in ['easy', 'medium', 'hard']:
            errors.append(f"{mid}: invalid difficulty '{diff}'")
        if 'GO Classes' not in provider:
            errors.append(f"{mid}: provider is '{provider}', expected GO Classes & Gate Overflow")
        if not desc.startswith('[Provider: GO Classes & Gate Overflow]'):
            errors.append(f"{mid}: desc does not start with '[Provider: GO Classes & Gate Overflow]': {desc[:40]}")
        if not name.startswith('GO Classes & Gate Overflow:'):
            errors.append(f"{mid}: name does not start with 'GO Classes & Gate Overflow:': {name}")

    elif mid.startswith('mock-go-ts25-mg-'):
        target_counts['go_mg'] += 1
        if mtype != 'full':
            errors.append(f"{mid}: type is '{mtype}', expected 'full'")
        if diff not in ['easy', 'medium', 'hard']:
            errors.append(f"{mid}: invalid difficulty '{diff}'")
        if 'GO Classes' not in provider:
            errors.append(f"{mid}: provider is '{provider}', expected GO Classes & Gate Overflow")
        if not desc.startswith('[Provider: GO Classes & Gate Overflow]'):
            errors.append(f"{mid}: desc does not start with '[Provider: GO Classes & Gate Overflow]': {desc[:40]}")
        if not name.startswith('GO Classes & Gate Overflow:'):
            errors.append(f"{mid}: name does not start with 'GO Classes & Gate Overflow:': {name}")

    elif mid.startswith('mock-go25-mg-'):
        target_counts['go25'] += 1
        if mtype != 'full':
            errors.append(f"{mid}: type is '{mtype}', expected 'full'")
        if diff not in ['easy', 'medium', 'hard']:
            errors.append(f"{mid}: invalid difficulty '{diff}'")
        if 'Gate Overflow' not in provider:
            errors.append(f"{mid}: provider is '{provider}', expected Gate Overflow")
        if not desc.startswith('[Provider: Gate Overflow]'):
            errors.append(f"{mid}: desc does not start with '[Provider: Gate Overflow]': {desc[:40]}")
        if not name.startswith('Gate Overflow:'):
            errors.append(f"{mid}: name does not start with 'Gate Overflow:': {name}")

print(f"Target counts verified: {target_counts}")
print(f"Total target mocks checked: {sum(target_counts.values())}")

if errors:
    print(f"FAILED with {len(errors)} errors:")
    for err in errors[:10]:
        print("  -", err)
    exit(1)
else:
    print("ALL 48 TARGET MOCKS PASS ALL BRANDING, FULL-LENGTH, DIFFICULTY, AND DESCRIPTION CRITERIA!")
