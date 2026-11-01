import pymupdf
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open("CS_All_Old_Papers.pdf")

print("Locating all GATE papers and Answer Keys in CS_All_Old_Papers.pdf:")
for i, page in enumerate(doc):
    txt = page.get_text()[:400]
    # Check for GATE YYYY or Answer Key
    m_gate = re.search(r'GATE\s*(20\d\d)', txt, re.IGNORECASE)
    m_key = re.search(r'Answer\s*Key', txt, re.IGNORECASE)
    if m_gate or m_key:
        first_line = txt.strip().split('\n')[0] if txt.strip() else ""
        second_line = txt.strip().split('\n')[1] if len(txt.strip().split('\n')) > 1 else ""
        print(f"Page {i+1:3d}: {'[KEY]' if m_key else '     '} {'[GATE ' + m_gate.group(1) + ']' if m_gate else '           '} | {first_line[:40]} // {second_line[:40]}")
