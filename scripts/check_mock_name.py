with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'mock.name' in line or 'exam.name' in line:
        clean = line.strip().encode('ascii', 'ignore').decode()
        print(f"{idx+1}: {clean}")
