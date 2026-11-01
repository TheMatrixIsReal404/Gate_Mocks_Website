import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open(r'g:\0.Gate_Lectures\0.3.Gate_Overflow_Books\GATE2027_volume1.pdf')
page = doc[21]
d = page.get_text('dict')
for b in d['blocks']:
    for line in b.get('lines', []):
        for span in line.get('spans', []):
            txt = span['text'].strip()
            if txt:
                print(f"[{span['bbox'][0]:.1f}, {span['bbox'][1]:.1f}] '{txt}' (font={span['font']}, size={span['size']:.1f})")
            if '1.2.3' in txt:
                break
