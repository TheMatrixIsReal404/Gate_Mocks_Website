with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines[:4000]):
    if '//' in line and any(k in line.upper() for k in ['EASY', 'MEDIUM', 'MOCKS', 'GATE', 'OVERFLOW', 'MADE']):
        clean = line.strip().encode('ascii', 'ignore').decode()
        print(f"{idx+1}: {clean}")
