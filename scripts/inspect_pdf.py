import pymupdf

pdf_path = "CS_All_Old_Papers.pdf"
doc = pymupdf.open(pdf_path)
print(f"Total pages: {len(doc)}")
print(f"Metadata: {doc.metadata}")

# Check Table of Contents or Bookmarks
toc = doc.get_toc()
print(f"TOC entries: {len(toc)}")
if toc:
    print("First 20 TOC entries:")
    for level, title, page in toc[:25]:
        print(f"  Level {level}: {title} (page {page})")

# Sample text from first few pages
print("\n--- Page 1 sample text ---")
print(doc[0].get_text()[:600])

if len(doc) > 1:
    print("\n--- Page 2 sample text ---")
    print(doc[1].get_text()[:600])

if len(doc) > 5:
    print("\n--- Page 5 sample text ---")
    print(doc[4].get_text()[:600])
