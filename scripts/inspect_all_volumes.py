import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

for vol in [1, 2, 3]:
    path = f"g:\\0.Gate_Lectures\\0.3.Gate_Overflow_Books\\GATE2027_volume{vol}.pdf"
    doc = pymupdf.open(path)
    print(f"\n================ Volume {vol} ({len(doc)} pages) ================")
    toc = doc.get_toc()
    print(f"TOC items: {len(toc)}")
    for lvl, title, page in toc[:15]:
        print(f"  L{lvl} | P{page} | {title}")
