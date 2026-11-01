import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open(r"g:\0.Gate_Lectures\0.3.Gate_Overflow_Books\GATE2027_volume2.pdf")

# Page 275 is index 274
print("=== Page 275 (Start of C questions) ===")
print(doc[274].get_text()[:1500])

# Page 319 is index 318
print("\n=== Page 319 (Answer Keys) ===")
print(doc[318].get_text()[:1000])
