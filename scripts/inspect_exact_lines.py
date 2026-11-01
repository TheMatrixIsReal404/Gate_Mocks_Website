import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open(r"g:\0.Gate_Lectures\0.3.Gate_Overflow_Books\GATE2027_volume1.pdf")

# Let's inspect page 20, 21, 22 in detail
for p in [20, 21, 22]:
    print(f"\n================ PAGE {p+1} ================")
    lines = doc[p].get_text().split("\n")
    for i, line in enumerate(lines[:60]):
        print(f"{i:2d}: {line}")
