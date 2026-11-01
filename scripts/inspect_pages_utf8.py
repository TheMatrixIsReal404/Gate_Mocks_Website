import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open("CS_All_Old_Papers.pdf")
print("=== Page 420 ===")
print(doc[419].get_text()[:1000])

print("=== Page 478 ===")
print(doc[477].get_text()[:1000])
