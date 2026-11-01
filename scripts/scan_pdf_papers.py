import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open("CS_All_Old_Papers.pdf")
toc = doc.get_toc()

print("Scanning papers in CS_All_Old_Papers.pdf:")
for i, (lvl, title, page) in enumerate(toc):
    if lvl == 1:
        # Check text on this page and next 5 pages
        start = max(0, page - 1)
        next_p = len(doc)
        for j in range(i + 1, len(toc)):
            if toc[j][0] == 1 and toc[j][2] > 0:
                next_p = toc[j][2] - 1
                break
        
        sample_pages = range(start, min(start + 5, next_p))
        total_text_len = sum(len(doc[p].get_text().strip()) for p in sample_pages if p < len(doc))
        has_images = any(len(doc[p].get_images()) > 0 for p in sample_pages if p < len(doc))
        
        paper_type = "DIGITAL TEXT" if total_text_len > 1000 else ("IMAGES / SCANNED" if has_images else "EMPTY")
        print(f"P{page:3d} - {next_p:3d} | {paper_type:15s} | text={total_text_len:5d} chars | {title}")
