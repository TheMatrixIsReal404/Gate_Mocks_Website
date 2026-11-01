import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open(r"g:\0.Gate_Lectures\0.3.Gate_Overflow_Books\GATE2027_volume2.pdf")

# Check TOC around P266
for lvl, title, page in doc.get_toc():
    if 265 <= page <= 325 and lvl <= 2:
        print(f"L{lvl} | P{page} | {title}")
