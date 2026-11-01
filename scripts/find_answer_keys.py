import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open(r'g:\0.Gate_Lectures\0.3.Gate_Overflow_Books\GATE2027_volume1.pdf')

# Check links on page 22 (0-indexed 21)
page = doc[21]
links = page.get_links()
print(f"Page 22 links ({len(links)}):")
for l in links[:10]:
    print(" ", l)

# Also let's check TOC for "Answer" or "Key" or "Solutions"
toc = doc.get_toc()
for lvl, title, pno in toc:
    if any(w in title.lower() for w in ['answer', 'key', 'solution', 'explanation']):
        print(f"TOC match: L{lvl} | P{pno} | {title}")
