import pymupdf

doc = pymupdf.open("CS_All_Old_Papers.pdf")
toc = doc.get_toc()

print(f"Total TOC items: {len(toc)}")
for item in toc:
    lvl, title, page = item
    print(f"L{lvl} | P{page} | {title}")
