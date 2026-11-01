import pymupdf

doc = pymupdf.open("CS_All_Old_Papers.pdf")

for pno in range(43, 50):
    page = doc[pno]
    print(f"\n==================== PAGE {pno+1} ====================")
    text = page.get_text()
    print(text[:1500])
