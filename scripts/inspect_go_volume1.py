import pymupdf
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open(r'g:\0.Gate_Lectures\0.3.Gate_Overflow_Books\GATE2027_volume1.pdf')

for pno in range(20, 26):
    print(f"\n==================== PAGE {pno+1} ====================")
    txt = doc[pno].get_text()
    print(txt[:1500])
