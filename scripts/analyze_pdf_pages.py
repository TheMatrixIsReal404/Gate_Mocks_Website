import pymupdf

doc = pymupdf.open("CS_All_Old_Papers.pdf")
pages_with_text = 0
pages_with_images = 0
sample_texts = {}

for i, page in enumerate(doc):
    text = page.get_text().strip()
    images = page.get_images()
    if text:
        pages_with_text += 1
        if len(sample_texts) < 5:
            sample_texts[i+1] = text[:300]
    if images:
        pages_with_images += 1

print(f"Total pages: {len(doc)}")
print(f"Pages with selectable text: {pages_with_text}")
print(f"Pages with images: {pages_with_images}")

for pno, txt in sample_texts.items():
    print(f"\n--- Page {pno} Sample ---")
    print(txt)
