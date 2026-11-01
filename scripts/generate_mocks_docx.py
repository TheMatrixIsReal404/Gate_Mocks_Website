# -*- coding: utf-8 -*-
"""
Script to create and populate mocks.docx with full-length GATE CS mock tests
containing detailed step-by-step solutions for every question.
"""

import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DOCX_PATH = r"g:\0.Gate_Lectures\0.Gate_Mocks_Website\mocks.docx"

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_or_load_document():
    if os.path.exists(DOCX_PATH):
        doc = Document(DOCX_PATH)
    else:
        doc = Document()
        # Document Title
        title = doc.add_heading(level=0)
        run = title.add_run("GATE Computer Science & IT (CS)\n20 Full-Length Mock Exams")
        run.font.name = "Calibri"
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
        
        p_sub = doc.add_paragraph("Strictly based on official IISc/IIT GATE CS syllabus and recent exam pattern (MCQ, MSQ, NAT).")
        p_sub.runs[0].font.size = Pt(11)
        p_sub.runs[0].font.italic = True
        p_sub.runs[0].font.color.rgb = RGBColor(0x4A, 0x55, 0x68)
        
        doc.add_page_break()
    return doc

def add_mock1_part1(doc):
    # Heading for Mock 1
    h1 = doc.add_heading("Mock Exam 01: Full-Length GATE CS & IT", level=1)
    h1.runs[0].font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    p_meta = doc.add_paragraph()
    r = p_meta.add_run("Total Questions: 65 | Maximum Marks: 100 | Duration: 180 Minutes\nMarking Scheme: 1-mark MCQ (-0.33), 2-mark MCQ (-0.66), MSQ (No negative/partial marks), NAT (No negative marks)")
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
    
    h2 = doc.add_heading("Section 1: General Aptitude (GA) — Questions 1 to 10", level=2)
    h2.runs[0].font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
    
    questions = [
        {
            "q_num": 1,
            "marks": 1,
            "type": "MCQ",
            "subject": "General Aptitude",
            "topic": "Verbal Aptitude (Grammar & Contextual Vocabulary)",
            "statement": "Choose the most appropriate word to complete the sentence logically and grammatically:\n\n\"The committee found the proposed regulatory framework to be too ________; rather than encouraging ethical compliance, its overly punitive and unyielding clauses would stifle innovative research.\"",
            "options": [
                "(A) draconian",
                "(B) benevolent",
                "(C) perfunctory",
                "(D) ambiguous"
            ],
            "answer": "(A) draconian",
            "solution": "Step 1: Analyze the contextual clues in the sentence. The sentence describes the framework's clauses as \"overly punitive and unyielding\" and notes that they \"stifle innovative research.\"\n\nStep 2: Evaluate word meanings:\n• (A) 'Draconian' means excessively harsh, rigorous, or severe (derived from Draco, the ancient Athenian lawgiver whose legal code imposed severe penalties). This precisely matches 'punitive and unyielding'.\n• (B) 'Benevolent' means well-meaning and charitable, the direct opposite of punitive.\n• (C) 'Perfunctory' means carried out with minimal effort or reflection as a routine chore.\n• (D) 'Ambiguous' means open to multiple interpretations or unclear, which does not convey harshness or severity.\n\nConclusion: Option (A) is correct."
        },
        {
            "q_num": 2,
            "marks": 1,
            "type": "MCQ",
            "subject": "General Aptitude",
            "topic": "Analytical Aptitude (Deductive Logic & Syllogism)",
            "statement": "Given the following three statements:\nI. All members of the advisory council are domain specialists.\nII. No domain specialist is exempt from ethical clearance.\nIII. Some individuals who received project funding are members of the advisory council.\n\nWhich one of the following conclusions logically follows?",
            "options": [
                "(A) Some individuals who received project funding are not exempt from ethical clearance.",
                "(B) All individuals who received project funding are domain specialists.",
                "(C) No individual who is exempt from ethical clearance received project funding.",
                "(D) Every domain specialist received project funding."
            ],
            "answer": "(A)",
            "solution": "Step 1: Formulate set-theoretic representations:\nLet C = set of advisory council members.\nLet S = set of domain specialists.\nLet E = set of individuals exempt from ethical clearance.\nLet F = set of individuals who received project funding.\n\nStep 2: Translate premises:\n• Premise I: C ⊆ S (All council members are specialists).\n• Premise II: S ∩ E = ∅ (No specialist is exempt, i.e., S ⊆ Eᶜ).\n• Premise III: F ∩ C ≠ ∅ (At least one funded person is on the council).\n\nStep 3: Combine premises:\nSince C ⊆ S and S ⊆ Eᶜ, we have C ⊆ Eᶜ (Every council member is not exempt).\nFrom Premise III, there exists some x such that x ∈ F and x ∈ C.\nSince x ∈ C and C ⊆ Eᶜ, it follows that x ∈ Eᶜ (x is not exempt).\nTherefore, x ∈ F ∩ Eᶜ, which proves F ∩ Eᶜ ≠ ∅.\n\nStep 4: Verify statement: \"Some individuals who received project funding are not exempt from ethical clearance\" is strictly guaranteed.\n\nConclusion: Option (A) is correct."
        },
        {
            "q_num": 3,
            "marks": 1,
            "type": "MCQ",
            "subject": "General Aptitude",
            "topic": "Quantitative Aptitude (Number Theory & Modular Arithmetic)",
            "statement": "The remainder obtained when 3^2026 + 7^2026 is divided by 100 is:\n\n(A) 28\n(B) 58\n(C) 78\n(D) 98",
            "options": [
                "(A) 28",
                "(B) 58",
                "(C) 78",
                "(D) 98"
            ],
            "answer": "(C) 78",
            "solution": "Step 1: We seek (3^2026 + 7^2026) mod 100.\nNote that gcd(3, 100) = 1 and gcd(7, 100) = 1.\nEuler's totient function φ(100) = 100 × (1 - 1/2) × (1 - 1/5) = 40.\nThe reduced Carmichael totient λ(100) = lcm(φ(4), φ(25)) = lcm(2, 20) = 20.\nHence, for any integer a coprime to 100, a^20 ≡ 1 (mod 100).\n\nStep 2: Reduce exponents modulo 20:\n2026 = 20 × 101 + 6 ≡ 6 (mod 20).\nTherefore:\n• 3^2026 ≡ 3^6 (mod 100).\n  3^6 = (3^3)^2 = 27^2 = 729 ≡ 29 (mod 100).\n\n• For 7, notice powers modulo 100:\n  7^2 = 49\n  7^4 = 2401 ≡ 1 (mod 100).\n  Since 2026 = 4 × 506 + 2 ≡ 2 (mod 4):\n  7^2026 ≡ 7^2 = 49 (mod 100).\n\nStep 3: Sum the residues:\n3^2026 + 7^2026 ≡ 29 + 49 = 78 (mod 100).\n\nConclusion: The remainder is 78. Option (C) is correct."
        },
        {
            "q_num": 4,
            "marks": 1,
            "type": "NAT",
            "subject": "General Aptitude",
            "topic": "Quantitative Aptitude (Work, Time & Rates)",
            "statement": "Two inlet pipes, P1 and P2, can independently fill an empty water reservoir in 12 hours and 15 hours, respectively. A drainage pipe P3 can completely empty the full reservoir in 20 hours. Initially, the reservoir is completely empty. Pipes P1 and P2 are opened simultaneously at 8:00 AM. After exactly 3 hours, pipe P1 is closed and drainage pipe P3 is opened simultaneously, while pipe P2 remains open. The total time elapsed from 8:00 AM until the reservoir is completely full is ________ hours. (Answer in integer).",
            "options": [],
            "answer": "36 (Acceptable range: 36 to 36)",
            "solution": "Step 1: Define total capacity as C = lcm(12, 15, 20) = 60 units.\n\nStep 2: Compute individual flow rates:\n• Rate of P1 = +60 / 12 = +5 units/hour\n• Rate of P2 = +60 / 15 = +4 units/hour\n• Rate of P3 = -60 / 20 = -3 units/hour (drainage)\n\nStep 3: First 3 hours (8:00 AM to 11:00 AM):\n• P1 and P2 are open.\n• Combined rate = 5 + 4 = 9 units/hour.\n• Volume filled in 3 hours = 9 units/hour × 3 hours = 27 units.\n• Remaining volume to fill = 60 - 27 = 33 units.\n\nStep 4: Subsequent period (after 11:00 AM):\n• P1 is closed; P2 (+4) and P3 (-3) operate together.\n• Net rate = 4 - 3 = +1 unit/hour.\n• Time needed to fill remaining 33 units = 33 units / (1 unit/hour) = 33 hours.\n\nStep 5: Total elapsed time from 8:00 AM:\n• Total time = 3 hours + 33 hours = 36 hours.\n\nConclusion: Answer is 36."
        },
        {
            "q_num": 5,
            "marks": 1,
            "type": "MCQ",
            "subject": "General Aptitude",
            "topic": "Spatial Aptitude (2D Geometric Transformations)",
            "statement": "In a 2D Cartesian plane, a point P initially located at coordinates (3, 4) undergoes the following sequence of transformations in order:\n1. Reflection across the line y = x.\n2. Counter-clockwise rotation by 90° about the origin (0, 0).\n3. Reflection across the x-axis.\n\nWhat are the final coordinates of point P?",
            "options": [
                "(A) (-3, -4)",
                "(B) (-4, 3)",
                "(C) (3, -4)",
                "(D) (4, -3)"
            ],
            "answer": "(A) (-3, -4)",
            "solution": "Step 1: Reflection across y = x:\nUnder reflection across the line y = x, (x, y) ↦ (y, x).\nApplying to (3, 4) gives P1 = (4, 3).\n\nStep 2: Counter-clockwise rotation by 90° about origin:\nThe rotation matrix for angle θ = 90° is [[0, -1], [1, 0]].\nThus (x', y') ↦ (-y', x').\nApplying to (4, 3) gives P2 = (-3, 4).\n\nStep 3: Reflection across x-axis:\nUnder reflection across the x-axis, (x, y) ↦ (x, -y).\nApplying to (-3, 4) gives P3 = (-3, -4).\n\nConclusion: Final coordinates are (-3, -4). Option (A) is correct."
        },
        {
            "q_num": 6,
            "marks": 2,
            "type": "MCQ",
            "subject": "General Aptitude",
            "topic": "Verbal Aptitude (Critical Reasoning)",
            "statement": "Read the following passage carefully and answer the question that follows:\n\n\"The rapid adoption of artificial intelligence in clinical diagnostics has demonstrated diagnostic accuracy rivaling experienced clinicians in controlled trials. However, deployment in community hospitals often yields substantially poorer outcomes. Investigators have noted that clinical decision support systems are frequently ignored by attending physicians when the model's recommendation contradicts clinical intuition, while in other cases, junior medical staff accept flawed recommendations uncritically without corroborating physical findings.\"\n\nWhich one of the following statements can be most reasonably inferred from the passage above?",
            "options": [
                "(A) Clinical decision support systems are inherently inferior to the diagnostic intuition of senior clinicians in real-world settings.",
                "(B) The primary reason for degraded diagnostic efficacy in field deployments is technical flaws within the underlying AI models.",
                "(C) Human factors, ranging from over-reliance to dismissive skepticism, significantly undermine the real-world efficacy of algorithmic diagnostics.",
                "(D) Medical training curriculum should mandate that clinical decisions unconditionally conform to algorithmic recommendations."
            ],
            "answer": "(C)",
            "solution": "Step 1: Identify the main premise and conclusion of the passage.\n• Premise 1: Controlled trials prove high algorithmic accuracy.\n• Premise 2: Real-world deployments yield poor outcomes.\n• Underlying cause: Attending physicians ignore recommendations when conflicting with intuition (dismissive skepticism), while junior staff accept flawed recommendations without physical corroboration (over-reliance/automation bias).\n\nStep 2: Evaluate choices:\n• (A) Incorrect: The author notes controlled trials rival clinicians, so inferiority is not inherent.\n• (B) Incorrect: The degradation is attributed to human behavioral interaction, not internal model flaws.\n• (C) Correct: 'Human factors, ranging from over-reliance to dismissive skepticism' precisely synthesizes both identified failure modes.\n• (D) Incorrect: Unconditional conformity would exacerbate errors when junior staff accept flawed outputs.\n\nConclusion: Option (C) is correct."
        },
        {
            "q_num": 7,
            "marks": 2,
            "type": "MSQ",
            "subject": "General Aptitude",
            "topic": "Quantitative Aptitude (Calculus & Function Analysis)",
            "statement": "Let f: R → R be a real-valued cubic function defined by:\nf(x) = x^3 - 3x^2 - 9x + 5\n\nWhich of the following statements is/are CORRECT?",
            "options": [
                "(A) f(x) attains a local maximum at x = -1.",
                "(B) f(x) attains a local minimum at x = 3.",
                "(C) The graph of f(x) has an inflection point at x = 1.",
                "(D) f(x) is strictly increasing on the open interval (-1, 3)."
            ],
            "answer": "(A), (B), (C)",
            "solution": "Step 1: Compute first derivative:\nf'(x) = 3x^2 - 6x - 9 = 3(x^2 - 2x - 3) = 3(x - 3)(x + 1).\nCritical points where f'(x) = 0 are x = -1 and x = 3.\n\nStep 2: Compute second derivative:\nf''(x) = 6x - 6 = 6(x - 1).\n\nStep 3: Evaluate critical points:\n• At x = -1: f''(-1) = 6(-1 - 1) = -12 < 0. Thus, x = -1 is a local maximum. (Option A is CORRECT).\n• At x = 3: f''(3) = 6(3 - 1) = +12 > 0. Thus, x = 3 is a local minimum. (Option B is CORRECT).\n\nStep 4: Evaluate point of inflection:\n• At x = 1: f''(1) = 0. For x < 1, f''(x) < 0 (concave downwards); for x > 1, f''(x) > 0 (concave upwards).\nSince f''(x) changes sign at x = 1, x = 1 is an inflection point. (Option C is CORRECT).\n\nStep 5: Check interval (-1, 3):\nFor any x ∈ (-1, 3), (x + 1) > 0 and (x - 3) < 0, so f'(x) < 0.\nTherefore, f(x) is strictly DECREASING on (-1, 3), not increasing. (Option D is INCORRECT).\n\nConclusion: Options (A), (B), and (C) are correct."
        },
        {
            "q_num": 8,
            "marks": 2,
            "type": "NAT",
            "subject": "General Aptitude",
            "topic": "Quantitative Aptitude (Differential Rates & Mensuration)",
            "statement": "A container has the geometry of an inverted right circular cone with base radius 6 cm and vertical height 18 cm (vertex pointing downwards). Liquid is poured into the container at a constant volumetric flow rate of 4π cm³/s. At the exact instant when the depth of the liquid in the container is 6 cm, the rate at which the liquid level is rising is ________ cm/s. (Answer in integer or decimal rounded to two decimal places).",
            "options": [],
            "answer": "1 (Acceptable range: 0.98 to 1.02)",
            "solution": "Step 1: Geometry of the cone:\nTotal height H = 18 cm, base radius R = 6 cm.\nAt liquid depth h, by similar triangles:\nr / h = R / H = 6 / 18 = 1/3  ⟹  r = h / 3.\n\nStep 2: Volume expression:\nV = (1/3) π r^2 h = (1/3) π (h/3)^2 h = (π / 27) h^3.\n\nStep 3: Time derivative of volume:\ndV/dt = d/dt [(π / 27) h^3] = (3π / 27) h^2 (dh/dt) = (π / 9) h^2 (dh/dt).\n\nStep 4: Substitute given rate and depth:\nGiven dV/dt = 4π cm³/s and depth h = 6 cm:\n4π = (π / 9) (6)^2 (dh/dt)\n4π = (π / 9) (36) (dh/dt)\n4π = 4π (dh/dt)\n\nStep 5: Solve for dh/dt:\ndh/dt = 4π / 4π = 1 cm/s.\n\nConclusion: The rate of rise of liquid level is exactly 1 cm/s."
        },
        {
            "q_num": 9,
            "marks": 2,
            "type": "MCQ",
            "subject": "General Aptitude",
            "topic": "Analytical Aptitude (Sequential Ordering & Logic Constraints)",
            "statement": "Five researchers—A, B, C, D, and E—are scheduled to deliver keynote lectures on five consecutive days from Monday to Friday, exactly one lecture per day. The schedule must satisfy all of the following conditions:\n1. A delivers their lecture on an earlier day than C.\n2. Exactly two lectures are delivered between the lectures of B and D.\n3. E does not deliver their lecture on Monday or Friday.\n4. D delivers their lecture on a day immediately before or immediately after E's lecture.\n5. C does not deliver their lecture on Friday.\n6. B delivers their lecture on an earlier day than D.\n\nOn which day does B deliver their lecture?",
            "options": [
                "(A) Monday",
                "(B) Tuesday",
                "(C) Wednesday",
                "(D) Thursday"
            ],
            "answer": "(B) Tuesday",
            "solution": "Step 1: Map days to positions: 1: Mon, 2: Tue, 3: Wed, 4: Thu, 5: Fri.\n\nStep 2: Conditions 2 & 6 imply:\nB is earlier than D, with 2 days between them: Day(D) - Day(B) = 3.\nPossible pairs for (B, D):\n• Case 1: B = Mon (1), D = Thu (4)\n• Case 2: B = Tue (2), D = Fri (5)\n\nStep 3: Test Case 1 (B = 1, D = 4):\nRemaining positions for {A, C, E}: Days 2, 3, 5.\nCondition 4: D (day 4) is adjacent to E. So E must be Day 3 or Day 5.\nCondition 3: E cannot be on Friday (Day 5), so E must be Day 3 (Wed).\nRemaining positions for {A, C}: Days 2 and 5.\nCondition 5: C cannot be on Friday (Day 5), so C must be Day 2 (Tue).\nThis forces A to be Day 5 (Fri).\nHowever, Condition 1 requires A < C. Here A (5) > C (2), contradiction! Thus Case 1 is impossible.\n\nStep 4: Test Case 2 (B = 2, D = 5):\nRemaining positions for {A, C, E}: Days 1, 3, 4.\nCondition 4: D (day 5) is adjacent to E. So E must be Day 4 (Thu).\nCondition 3 is satisfied (Thu is neither Mon nor Fri).\nRemaining positions for {A, C}: Days 1 and 3.\nCondition 1 requires A < C, so A = Day 1 (Mon) and C = Day 3 (Wed).\nCondition 5 is satisfied (C is on Wed ≠ Fri).\n\nFinal Valid Schedule:\n• Monday: A\n• Tuesday: B\n• Wednesday: C\n• Thursday: E\n• Friday: D\n\nConclusion: B delivers their lecture on Tuesday. Option (B) is correct."
        },
        {
            "q_num": 10,
            "marks": 2,
            "type": "NAT",
            "subject": "General Aptitude",
            "topic": "Quantitative Aptitude (Probability & Bayes' Theorem)",
            "statement": "In a binary digital communication channel, symbol X ∈ {0, 1} is transmitted and symbol Y ∈ {0, 1} is received. The transmitter generates bit '0' with prior probability P(X = 0) = 0.70 and bit '1' with prior probability P(X = 1) = 0.30. Due to channel noise, the bit transition probabilities are given by:\nP(Y = 1 | X = 0) = 0.10  and  P(Y = 0 | X = 1) = 0.30\n\nGiven that symbol '1' was observed at the receiver (Y = 1), the conditional probability that symbol '1' was transmitted, P(X = 1 | Y = 1), is ________. (Answer in integer or decimal rounded to two decimal places).",
            "options": [],
            "answer": "0.75 (Acceptable range: 0.74 to 0.76)",
            "solution": "Step 1: Identify given probabilities:\n• Prior probabilities: P(X = 0) = 0.70, P(X = 1) = 0.30\n• Channel noise:\n  P(Y = 1 | X = 0) = 0.10\n  P(Y = 0 | X = 1) = 0.30  ⟹  P(Y = 1 | X = 1) = 1 - 0.30 = 0.70\n\nStep 2: Total probability of receiving symbol '1':\nP(Y = 1) = P(Y = 1 | X = 0) P(X = 0) + P(Y = 1 | X = 1) P(X = 1)\nP(Y = 1) = (0.10 × 0.70) + (0.70 × 0.30)\nP(Y = 1) = 0.07 + 0.21 = 0.28\n\nStep 3: Apply Bayes' Theorem:\nP(X = 1 | Y = 1) = [P(Y = 1 | X = 1) × P(X = 1)] / P(Y = 1)\nP(X = 1 | Y = 1) = (0.70 × 0.30) / 0.28\nP(X = 1 | Y = 1) = 0.21 / 0.28 = 21 / 28 = 3 / 4 = 0.75\n\nConclusion: The conditional probability is 0.75."
        }
    ]
    
    # Add Questions Section
    for q in questions:
        p_q = doc.add_paragraph()
        r_num = p_q.add_run(f"Question {q['q_num']} ")
        r_num.bold = True
        r_num.font.size = Pt(11)
        r_num.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        
        r_tag = p_q.add_run(f"[{q['type']} | {q['marks']} Mark{'s' if q['marks'] > 1 else ''} | {q['topic']}]\n")
        r_tag.bold = True
        r_tag.font.size = Pt(9.5)
        r_tag.font.color.rgb = RGBColor(0x71, 0x80, 0x96)
        
        r_stmt = p_q.add_run(q['statement'])
        r_stmt.font.size = Pt(10.5)
        
        if q['options']:
            for opt in q['options']:
                p_opt = doc.add_paragraph(opt)
                p_opt.paragraph_format.left_indent = Inches(0.25)
                p_opt.runs[0].font.size = Pt(10)
                
    doc.add_page_break()
    
    # Add Detailed Solutions Section
    h_sol = doc.add_heading("Section 1: General Aptitude — Answer Key & Step-by-Step Solutions", level=2)
    h_sol.runs[0].font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    
    # Summary Table
    table = doc.add_table(rows=1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    headers = ["Q. No.", "Type", "Marks", "Correct Answer", "Topic"]
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1E3A8A")
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        hdr_cells[i].paragraphs[0].runs[0].font.size = Pt(9.5)
        
    for q in questions:
        row_cells = table.add_row().cells
        row_cells[0].text = str(q['q_num'])
        row_cells[1].text = q['type']
        row_cells[2].text = str(q['marks'])
        row_cells[3].text = q['answer']
        row_cells[4].text = q['topic']
        for c in row_cells:
            c.paragraphs[0].runs[0].font.size = Pt(9)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    for q in questions:
        p_s = doc.add_paragraph()
        r_qh = p_s.add_run(f"Q.{q['q_num']} Detailed Solution [{q['type']}, {q['marks']}M] — Correct Answer: {q['answer']}\n")
        r_qh.bold = True
        r_qh.font.size = Pt(10.5)
        r_qh.font.color.rgb = RGBColor(0x2C, 0x52, 0x82)
        
        r_sol = p_s.add_run(q['solution'])
        r_sol.font.size = Pt(10)
        p_s.paragraph_format.space_after = Pt(10)

if __name__ == "__main__":
    doc = create_or_load_document()
    add_mock1_part1(doc)
    doc.save(DOCX_PATH)
    print(f"Successfully generated and saved {DOCX_PATH}")
