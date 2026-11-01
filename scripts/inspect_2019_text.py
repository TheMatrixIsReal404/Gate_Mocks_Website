import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open("CS_All_Old_Papers.pdf")

# Page 375 is index 374
page = doc[374]
print("=== Page 375 (GATE 2019 CS) ===")
print(page.get_text()[:1500])

# Page 376
print("\n=== Page 376 ===")
print(doc[375].get_text()[:1500])
