# -*- coding: utf-8 -*-
import re

readme_path = 'README.md'
with open(readme_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace general occurrences of 19,874 with 20,093
# and 19874 with 20093
text = text.replace('19,874 Questions', '20,093 Questions')
text = text.replace('(19,874 Qs)', '(20,093 Qs)')
text = text.replace('19,874 questions', '20,093 questions')
text = text.replace('19,874 verified questions', '20,093 verified questions')
text = text.replace('all 19,874 questions', 'all 20,093 questions')
text = text.replace('19,874 total verified questions', '20,093 total verified questions')
text = text.replace('**19,874 total questions**', '**20,093 total questions**')
text = text.replace('**19,874 questions**', '**20,093 questions**')

v70_changelog = """### Version 7.0 (Current Release — 20,093 Verified Questions, OCR Question Integration, LaTeX Math & Prism.js C Blocks, High-Res Diagram Assets, Complete Deduplication & Canonical Mapping)
* **🏛️ 20,093 Master Question Bank Milestone (OCR High-Fidelity Hybrid Integration)**:
  * Ingested and integrated **1,143 high-fidelity OCR questions** with authentic mathematical KaTeX formatting, syntax-highlighted Prism.js C programs, and high-resolution cropped diagrams:
    * **Zeal C Programming (112 Questions)**: 100% complete with 111 multi-line formatted C code blocks (` ```c `), memory pointer representations, and 100% official answer keys.
    * **Zeal Digital Logic Basic (251 Questions)**: Comprehensive Boolean algebra expressions with KaTeX overbars ($\\bar{A}$, $\\bar{B}$), $\\oplus$ XOR operators, minterm summations, and **56 crisp vector-cropped K-map and logic circuit diagrams** (`assets/diagrams/zeal/`).
    * **Zeal Engineering Mathematics (745 Questions)**: Complete Linear Algebra & Matrices, Calculus & Limits, Permutations & Combinations, and Probability & Distributions with 100% KaTeX matrices and integrals.
    * **Made Easy 2024 Single Subject Tests (35 Questions)**: High-resolution question cards and schematic diagrams (`assets/diagrams/made_easy_2024/`) with official step-by-step explanations from solution reports.
  * Replaced 924 legacy low-fidelity unformatted OCR questions from `sample_questions.json` with the superior high-fidelity versions while registering all 771 legacy question IDs in `data/id_aliases.json` for 100% backward compatibility.
* **🎯 Comprehensive Deduplication & Canonical Mapping Architecture**:
  * Cross-Paper Duplication: Evaluated all 1,143 new questions against the entire master datastore. Detected and mapped 6 exact cross-paper duplicates (e.g., questions mirroring official GATE PYQs or GO Test Series) to their primary `canonicalId`.
  * Internal Duplication: Identified and linked 11 internal duplicate pairs within the practice sheets.
  * Aliases Synchronization: Registered 2,735 total ID aliases in `data/id_aliases.json` so deduplication in Practice Mode (`q.canonicalId || q.id`) ensures students never encounter duplicate questions.
  * 100% Datastore Integrity: Zero duplicate IDs, all subjects mapped to official 13 CANONICAL_SUBJECTS, and all 91 embedded diagram image assets verified present on disk.

"""

text = text.replace('### Version 6.9 (Current Release', v70_changelog + '### Version 6.9')

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated README.md to Version 7.0 and 20,093 questions successfully.")
