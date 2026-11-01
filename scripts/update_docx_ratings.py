# -*- coding: utf-8 -*-
"""
Script to embed the official Difficulty Calibration and Ratings (Medium vs Hard)
directly into mocks.docx in both the workspace and Downloads folder.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

MOCK_RATINGS = {
    1:  {'rating': 4.5, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '31-33 M', 'air100': '74-78 M', 'desc': 'Foundational-to-standard baseline paper with clean arithmetic bounds, classic cache and pipelining parameters, and standard scoring problems.'},
    2:  {'rating': 5.0, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '30-32 M', 'air100': '73-77 M', 'desc': 'Standard GATE difficulty featuring Peirce’s law, modulo 13 exponentiation, 4-element derangements, and 10-vertex planar graph faces.'},
    3:  {'rating': 5.5, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '29-31 M', 'air100': '72-76 M', 'desc': 'Standard GATE paper testing 5-iteration fork() trees (31 children), modulo 17 arithmetic, and 4-way set-associative cache tags.'},
    4:  {'rating': 5.4, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '29-31 M', 'air100': '72-76 M', 'desc': 'Standard GATE simulation covering self-dual Boolean functions (256), modulo 19 arithmetic, and sliding-window DFA state construction.'},
    5:  {'rating': 5.2, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '30-32 M', 'air100': '73-77 M', 'desc': 'Standard GATE paper testing modulo 23 modular arithmetic, 3-ary tree leaf invariants (47 leaves), and 4-to-1 MUX Shannon expansions.'},
    6:  {'rating': 5.8, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '28-30 M', 'air100': '71-75 M', 'desc': 'Standard-Plus GATE paper testing modulo 29 exponentiation, 18-vertex planar graphs, cyclic K-maps, and cascaded counter frequency division.'},
    7:  {'rating': 5.6, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '28-30 M', 'air100': '71-75 M', 'desc': 'Standard-Plus paper with modulo 31 arithmetic, 20-vertex planar graph faces, 8-element surjections (5,796), and TCP congestion milestones.'},
    8:  {'rating': 6.0, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '27-29 M', 'air100': '70-74 M', 'desc': 'Upper-Standard GATE paper featuring modulo 37 exponentiation, 22-vertex planar graphs, 7-element derangements (1,855), and 280ms TCP windows.'},
    9:  {'rating': 6.1, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '27-29 M', 'air100': '70-74 M', 'desc': 'Upper-Standard paper with modulo 41 arithmetic, 24-vertex planar graphs, 5-variable directed FD cycles, and 32.0% sliding window utilization.'},
    10: {'rating': 5.9, 'level': 'medium', 'title_tier': 'Standard GATE',       'cutoff': '28-30 M', 'air100': '71-75 M', 'desc': 'Balanced Standard GATE paper testing modulo 43 arithmetic, 26-vertex planar graphs, cyclic candidate keys, and 180 Cayley trace calculations.'},
    11: {'rating': 6.8, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '25-27 M', 'air100': '66-70 M', 'desc': 'Advanced Rank Booster featuring modulo 47 arithmetic, 28-vertex planar graphs, 141-leaf 5-ary trees, and 330ms TCP slow-start calculations.'},
    12: {'rating': 7.5, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '24-26 M', 'air100': '65-69 M', 'desc': 'Advanced Rank Booster testing modulo 53 exponentiation, 30-vertex planar graphs, 186-leaf 6-ary trees, and 420ms TCP congestion windows.'},
    13: {'rating': 7.0, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '25-27 M', 'air100': '66-70 M', 'desc': 'Advanced Rank Booster with modulo 59 arithmetic, 32-vertex planar graphs, 8-element BST postorder reconstructions, and 270 Cayley trace.'},
    14: {'rating': 7.4, 'level': 'hard',   'title_tier': 'Rank Booster',        'cutoff': '24-26 M', 'air100': '65-69 M', 'desc': 'Advanced Rank Booster testing modulo 61 exponentiation, 34-vertex planar graphs, 8-fragment IPv4 splitting, 304 trace, and 25% DMA overhead.'},
    15: {'rating': 8.0, 'level': 'hard',   'title_tier': 'High Difficulty',     'cutoff': '23-25 M', 'air100': '63-67 M', 'desc': 'High Difficulty Rank Booster with modulo 67 arithmetic, 36-vertex planar graphs, 173-leaf 5-ary trees, and 144,000-cost matrix chains.'},
    16: {'rating': 7.8, 'level': 'hard',   'title_tier': 'High Difficulty',     'cutoff': '23-25 M', 'air100': '63-67 M', 'desc': 'High Difficulty paper testing modulo 71 exponentiation, 38-vertex planar graphs, 226-leaf 6-ary trees, 6th-symbol DFA (64 states), and 378 trace.'},
    17: {'rating': 7.9, 'level': 'hard',   'title_tier': 'High Difficulty',     'cutoff': '23-25 M', 'air100': '63-67 M', 'desc': 'High Difficulty paper with modulo 73 exponentiation, 40-vertex planar graphs, 164ns paging EMAT, 418 trace, and 15% DMA cycle stealing.'},
    18: {'rating': 8.4, 'level': 'hard',   'title_tier': 'Advanced Hard',       'cutoff': '22-24 M', 'air100': '62-66 M', 'desc': 'Advanced Hard paper featuring modulo 79 exponentiation, 42-vertex planar graphs, 148-leaf 4-ary trees, 6-bit Kernighan loop, and 460 trace.'},
    19: {'rating': 8.6, 'level': 'hard',   'title_tier': 'Advanced Hard',       'cutoff': '21-23 M', 'air100': '60-65 M', 'desc': 'Advanced Hard paper with modulo 83 exponentiation, 44-vertex planar graphs, 205-leaf 5-ary trees, 504 IPv4 offset, and 504 Cayley trace.'},
    20: {'rating': 9.2, 'level': 'hard',   'title_tier': 'Capstone Challenge', 'cutoff': '20-22 M', 'air100': '58-63 M', 'desc': 'Capstone Challenge mock exam featuring modulo 89 exponentiation, 46-vertex planar graphs, 266-leaf 6-ary trees, 6th-symbol DFA (64 states), and 550 trace.'}
}

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def update_docx_file(doc_path):
    print(f"Opening {doc_path}...")
    doc = docx.Document(doc_path)
    
    # 1. Update Mock Headings in paragraphs
    import re
    updated_headings = 0
    for p in doc.paragraphs:
        txt = p.text.strip()
        m = re.match(r'GATE CS FULL-LENGTH MOCK EXAMINATION #(\d+)', txt)
        if m:
            m_num = int(m.group(1))
            cfg = MOCK_RATINGS[m_num]
            tier_badge = "MEDIUM" if cfg['level'] == 'medium' else "HARD"
            new_title = f"GATE CS FULL-LENGTH MOCK EXAMINATION #{m_num:02d} (Questions 1 to 65 \u2014 100 Marks)   [{tier_badge} | Rating: {cfg['rating']}/10 | {cfg['title_tier'].upper()}]"
            p.text = new_title
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.bold = True
                p.runs[0].font.size = Pt(14)
                if cfg['level'] == 'medium':
                    p.runs[0].font.color.rgb = RGBColor(0x9A, 0x34, 0x12) # Amber / Dark Orange
                else:
                    p.runs[0].font.color.rgb = RGBColor(0xB9, 0x1C, 0x1C) # Deep Red
            updated_headings += 1
            
    print(f"Updated {updated_headings} mock heading titles.")
    
    # Check if Executive Calibration heading already exists to prevent duplicate insertion
    already_has_table = any("Executive Mock Calibration & Difficulty Rating Index" in p.text for p in doc.paragraphs[:10])
    
    if not already_has_table:
        # Find where Mock 1 starts
        p_mock1 = None
        for p in doc.paragraphs:
            if "GATE CS FULL-LENGTH MOCK EXAMINATION #01" in p.text or "GATE CS FULL-LENGTH MOCK EXAMINATION #1" in p.text:
                p_mock1 = p
                break
                
        if p_mock1:
            # Insert section heading
            p_heading = p_mock1.insert_paragraph_before()
            r_head = p_heading.add_run("Executive Mock Calibration & Difficulty Rating Index (Medium vs. Hard Mocks)")
            r_head.font.name = "Calibri"
            r_head.font.size = Pt(16)
            r_head.bold = True
            r_head.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A) # Navy
            p_heading.paragraph_format.space_before = Pt(18)
            p_heading.paragraph_format.space_after = Pt(6)
            
            # Explanatory paragraph 1
            p_desc1 = p_mock1.insert_paragraph_before()
            r1 = p_desc1.add_run("This compendium's 20 Full-Length Mock Examinations are strictly calibrated into two official difficulty tiers according to mathematical parameter magnitude, multi-step dependency depth, sliding-window DFA state spaces, and time-pressure intensity:")
            r1.font.name = "Calibri"
            r1.font.size = Pt(10)
            r1.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
            p_desc1.paragraph_format.space_after = Pt(4)
            
            # Bullet 1: Medium
            p_b1 = p_mock1.insert_paragraph_before()
            rb1_tag = p_b1.add_run("• MEDIUM (Standard / Moderate GATE Pattern) \u2014 Mocks #01 to #10 (Difficulty Rating: 4.5 to 6.1 / 10): ")
            rb1_tag.bold = True
            rb1_tag.font.color.rgb = RGBColor(0x9A, 0x34, 0x12)
            rb1_tag.font.size = Pt(9.5)
            rb1_txt = p_b1.add_run("Replicates the standard official IISc/IIT GATE CS paper profile (e.g., GATE 2021, GATE 2023, GATE 2025 Set 1). Features standard numerical bounds, classical K-maps, clean planar graphs (V \u2264 26), 2-level paging EMAT, and standard 3-to-4 step derivations. Expected Qualifying Cutoff: 28\u201332 Marks | Target Top-100 AIR: 72\u201378+ Marks.")
            rb1_txt.font.size = Pt(9.5)
            p_b1.paragraph_format.space_after = Pt(3)
            
            # Bullet 2: Hard
            p_b2 = p_mock1.insert_paragraph_before()
            rb2_tag = p_b2.add_run("• HARD (Advanced / High Difficulty Rank Booster) \u2014 Mocks #11 to #20 (Difficulty Rating: 6.8 to 9.2 / 10): ")
            rb2_tag.bold = True
            rb2_tag.font.color.rgb = RGBColor(0xB9, 0x1C, 0x1C)
            rb2_tag.font.size = Pt(9.5)
            rb2_txt = p_b2.add_run("Challenging rank-booster papers designed for top percentiles. Features larger modular primes (up to mod 89), 64-state sliding-window DFAs, 141-to-266 leaf strict k-ary trees, 31-process fork trees, 8-fragment IPv4 splitting, massive matrix chains (144,000 operations), and deep multi-RTT TCP congestion windows (420 ms). Expected Qualifying Cutoff: 20\u201326 Marks | Target Top-100 AIR: 60\u201368 Marks.")
            rb2_txt.font.size = Pt(9.5)
            p_b2.paragraph_format.space_after = Pt(8)
            
            # Insert Calibration Table
            table = doc.add_table(rows=1, cols=6)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            col_widths = [Inches(0.85), Inches(0.95), Inches(0.70), Inches(0.80), Inches(0.80), Inches(2.40)]
            
            hdr_cells = table.rows[0].cells
            headers = ["Mock Exam", "Difficulty Tier", "Rating", "Est. Cutoff", "AIR < 100", "Complexity & Syllabus Focus"]
            for idx, name in enumerate(headers):
                hdr_cells[idx].text = name
                hdr_cells[idx].width = col_widths[idx]
                set_cell_background(hdr_cells[idx], "1E3A8A")
                set_cell_margins(hdr_cells[idx], top=120, bottom=120, left=100, right=100)
                p = hdr_cells[idx].paragraphs[0]
                if idx in (0, 1, 2, 3, 4):
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.runs[0]
                r.font.name = "Calibri"
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                r.font.size = Pt(9)
                
            for m_num in range(1, 21):
                cfg = MOCK_RATINGS[m_num]
                tier_str = "Medium" if cfg['level'] == 'medium' else "Hard"
                row_cells = table.add_row().cells
                
                row_cells[0].text = f"Mock #{m_num:02d}"
                row_cells[1].text = tier_str
                row_cells[2].text = f"{cfg['rating']}/10"
                row_cells[3].text = cfg['cutoff']
                row_cells[4].text = cfg['air100']
                row_cells[5].text = cfg['desc']
                
                bg_color = "F1F5F9" if m_num % 2 == 0 else "FFFFFF"
                for c_idx, c in enumerate(row_cells):
                    c.width = col_widths[c_idx]
                    set_cell_background(c, bg_color)
                    set_cell_margins(c, top=80, bottom=80, left=90, right=90)
                    p = c.paragraphs[0]
                    if c_idx in (0, 1, 2, 3, 4):
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    r = p.runs[0]
                    r.font.name = "Calibri"
                    r.font.size = Pt(8.5)
                    if c_idx == 1:
                        r.font.bold = True
                        if cfg['level'] == 'medium':
                            r.font.color.rgb = RGBColor(0x9A, 0x34, 0x12)
                        else:
                            r.font.color.rgb = RGBColor(0xB9, 0x1C, 0x1C)
                    elif c_idx == 2:
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
                    elif c_idx == 0:
                        r.font.bold = True
            
            # Place table right before p_mock1
            p_mock1._p.addprevious(table._tbl)
            
            # Add a divider / spacing before Mock 1
            p_space = p_mock1.insert_paragraph_before()
            p_space.paragraph_format.space_before = Pt(14)
            p_space.paragraph_format.space_after = Pt(14)
            r_sep = p_space.add_run("―" * 50)
            r_sep.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
            p_space.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
    doc.save(doc_path)
    print(f"Successfully updated and saved {doc_path} with ratings!")

if __name__ == '__main__':
    workspace_doc = r"g:\0.Gate_Lectures\0.Gate_Mocks_Website\mocks.docx"
    downloads_doc = r"C:\Users\sahu1\Downloads\mocks.docx"
    
    update_docx_file(workspace_doc)
    
    if os.path.exists(downloads_doc):
        update_docx_file(downloads_doc)
    else:
        print(f"Downloads file not found at {downloads_doc}")
