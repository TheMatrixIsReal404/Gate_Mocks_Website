# -*- coding: utf-8 -*-
import sys, os, json
from update_ratings import MOCK_RATINGS

md_content = """# GATE Computer Science & Information Technology (CS)
# 20 Full-Length Mock Examinations Compendium: Difficulty Calibration & Rating Guide

This guide provides a comprehensive **difficulty rating, calibration analysis, and performance benchmark** for all 20 Full-Length Mock Examinations integrated into the website platform.

---

## 1. Quick Summary: Which Mocks are Medium vs Hard?

The 20 Full-Length Mocks are structured into two distinct difficulty tiers based on mathematical parameter magnitude, algorithmic state space, multi-step dependency depth, and time-pressure intensity:

* **🟡 MEDIUM (Standard / Moderate GATE Pattern) — Mocks #01 to #10 (Rating: 4.5 to 6.1 / 10)**  
  Matches the typical official IISc/IIT GATE CS paper profile (e.g., GATE 2021, GATE 2023, GATE 2025 Set 1). Features standard numerical bounds, classical 3-to-4 variable K-maps, clean planar graph instances ($V \\le 26$), standard 2-level paging, and foundational 3-to-4 step derivations.  
  * **Expected Qualifying Cutoff:** **28 – 32 Marks**  
  * **Top-100 AIR Target Score:** **72 – 78+ Marks**

* **🔴 HARD (Advanced / High Difficulty Rank Booster) — Mocks #11 to #20 (Rating: 6.8 to 9.2 / 10)**  
  High-intensity rank-booster papers designed for top percentiles. Features larger modular primes (up to $\\pmod{89}$), 6th-symbol sliding-window DFAs ($2^6 = 64$ states), 141-to-266 leaf strict $k$-ary trees, 5-iteration fork trees ($31$ processes), 8-fragment IPv4 splitting, massive matrix chains ($144,000$ operations), and deep multi-RTT TCP congestion windows ($420$ ms).  
  * **Expected Qualifying Cutoff:** **20 – 26 Marks**  
  * **Top-100 AIR Target Score:** **60 – 68 Marks**

---

## 2. Complete 20 Mock Exams Difficulty Rating & Benchmark Table

| Mock Test | Website ID | Difficulty Tier | Difficulty Rating | Est. Cutoff | Top-100 AIR | Key Distinguishing Complexity |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
"""

for i in range(1, 21):
    c = MOCK_RATINGS[i]
    badge = '🟡 Medium' if c['level'] == 'medium' else '🔴 Hard'
    md_content += f"| **Mock #{i:02d}** | `mock-flm-{i:02d}` | {badge} | **{c['rating']}/10** | {c['cutoff']} M | {c['air100']} M | {c['desc']} |\n"

md_content += """
---

## 3. Detailed Parameter Complexity Progression Across the 20 Mocks

To understand why Mocks #11 to #20 are classified as **Hard**, observe the mathematical scaling across the series:

| Examination Area | Standard GATE Mocks (#01 – #10) | Hard / Rank Booster Mocks (#11 – #20) |
| :--- | :--- | :--- |
| **Modular Arithmetic ($Q_2$)** | Small primes: $\\pmod 7$, $\\pmod{13}$, $\\pmod{17}$, up to $\\pmod{43}$ | Large primes: $\\pmod{47}$, $\\pmod{53}$, $\\pmod{59}$, up to $\\pmod{89}$ |
| **Strict $k$-ary Trees ($Q_{21}$)** | Internal nodes: $15 \\le I \\le 33$ (Leaf count $31$ to $100$) | Internal nodes: $35 \\le I \\le 53$ (Leaf count $141$ to $266$) |
| **Fork Process Trees ($Q_{29}$)** | $3$ to $5$ loop iterations (max $7$ to $31$ children) | Continuous nested processes requiring deep tree tracing |
| **Planar Graph Faces ($Q_{39}$)** | 3-regular cubic graphs with $8 \\le |V| \\le 26$ vertices | Cubic planar graphs scaling up to $46$ vertices ($|E| = 69, |F| = 25$) |
| **Sliding Window NFA/DFA ($Q_{54}$)** | 3rd to 4th symbol from right ($8$ to $16$ DFA states) | 5th to 6th symbol from right ($32$ to $64$ DFA states) |
| **Cayley-Hamilton Matrix ($Q_{36}$)** | Scalar trace multipliers $c = 3$ to $12$ (Trace $18$ to $180$) | Scalar trace multipliers $c = 13$ to $22$ (Trace $208$ to $550$) |
| **TCP Congestion Window ($Q_{63}$)** | RTT delays $20 - 30$ ms; milestones up to $140 - 280$ ms | High RTT delays $35$ ms; avoidance scaling up to $420$ ms |
| **Matrix Chain / Huffman ($Q_{50}$)** | Standard 4-matrix chains (costs $2,250$ to $60,750$) | High-dimension chains scaling up to $144,000$ scalar multiplications |

---

## 4. Complete Website Mock Test Difficulty Landscape

| Category | Mock Name | Difficulty Badge | Rating | Recommended Stage |
| :--- | :--- | :---: | :---: | :--- |
| **Foundational** | GATE CSE Full Mock 1 (Level 1) | 🟢 EASY | 3.0/10 | Diagnostic / Initial Revision |
| **Foundational** | GATE CSE Mock (Cat 1 — Set 1 & 2) | 🟢 EASY | 3.5/10 | Topic speed building |
| **Standard GATE** | GATE CSE Full Mock 2 (Level 2) | 🟡 MEDIUM | 5.0/10 | Mid-preparation benchmarking |
| **Standard GATE** | GATE CSE 2025 All-India Mock 1 | 🟡 MEDIUM | 5.5/10 | Standard exam simulation |
| **Standard GATE** | Official GATE CSE 2025 Exam (Set 1) | 🟡 MEDIUM | 5.5/10 | Real past paper practice |
| **Standard GATE** | **GATE CS Full Mocks #01 – #10** | 🟡 MEDIUM | **4.5 – 6.1/10** | **Core GATE full-length timed tests** |
| **Advanced** | GATE CSE Full Mock 3 (Level 3) | 🔴 HARD | 8.0/10 | Advanced rank booster |
| **Advanced** | GATE CSE 2025 All-India Mock 2 | 🔴 HARD | 7.0/10 | Advanced multi-concept problem solving |
| **Advanced** | Official GATE CSE 2025 Exam (Set 2) | 🔴 HARD | 7.0/10 | Tough past paper simulation |
| **Advanced** | GATE CSE Mock (Cat 2 — Set 5) | 🔴 HARD | 5.5/10 | Edge-case numericals |
| **Advanced** | **GATE CS Full Mocks #11 – #20** | 🔴 HARD | **6.8 – 9.2/10** | **Final rank booster & time-pressure mastery** |

---

*All ratings and difficulty classifications are synchronized with the website filters under the **Mock Tests** tab.*
"""

with open("mocks.md", "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Successfully generated comprehensive mocks.md ({len(md_content)} chars)")
