import pymupdf
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

q_pattern = re.compile(r'([A-Za-z0-9 &/-]+):\s*GATE\s*(?:CS(?:E)?|IT)?\s*(\d{4})(?:\s*\|\s*Set\s*(\d+))?\s*\|\s*Question:\s*([^\n\r]+)', re.IGNORECASE)

for vol in [1, 2, 3]:
    path = f"g:\\0.Gate_Lectures\\0.3.Gate_Overflow_Books\\GATE2027_volume{vol}.pdf"
    doc = pymupdf.open(path)
    found = 0
    years = {}
    for page in doc:
        txt = page.get_text()
        for m in q_pattern.finditer(txt):
            found += 1
            yr = m.group(2)
            years[yr] = years.get(yr, 0) + 1
    print(f"Volume {vol}: Found {found} questions")
    print(f"  Years sample: {sorted(years.keys())[-10:]} -> {[years[y] for y in sorted(years.keys())[-10:]]}")
