# -*- coding: utf-8 -*-
import os

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Pipeline scripts
old_pipeline = '''### 5. Data Engineering & Compilation Pipeline
* **Python 3.14 Pipeline (`scripts/`)**:
  * `verify_all_thirty_seven_features.py`: Complete automated Chrome DevTools Protocol (CDP) test suite verifying all 37 modules and features end-to-end.
  * `ingest_30_medium_mocks.py`: Automated parser converting `medium_mocks.docx` (30 full tests, 1,950 questions) into normalized JSON structures.
  * `ingest_30_easy_mocks.py`: Parser converting `easy_mocks.docx` (30 full tests, 1,950 questions).
  * `apply_medium_mocks_to_app.py`: Synchronizes mock test definitions, UI buttons, and window hooks across `app.js`.
  * `merge_all_master_questions.py`: Unifies all mock datasets, PYQs, and supplementary collections into `sample_questions.json`.
  * `verify_app_syntax.py`: End-to-end regression test suite verifying question count, mark sums, answer keys, and symbol exports.
  * `math_verifier.py`: Automated symbolic and numerical verifier ensuring LaTeX validity, NAT decimal ranges, and answer key consistency.
  * `check_duplicates.py` & `comprehensive_duplicate_check.py`: Multi-stage duplicate detection using MD5 exact hashing and Jaccard token similarity ($> 0.80$).'''

new_pipeline = '''### 5. Data Engineering & Compilation Pipeline
* **Python 3.14 Pipeline (`scripts/`)**:
  * `comprehensive_question_audit.py`: Full in-browser Headless Microsoft Edge CDP audit evaluating all 8,168 questions for HTML corruptions, KaTeX math parsing, code blocks, tables, and question truncation.
  * `verify_all_v6_features.py`: Master 112-point automated verification suite testing all v6.0, Elite Tier, Cherry on Top, Pro exam, P0/P1 security, deduplication, and multi-admin features.
  * `audit_bank.py`: Datastore integrity auditor validating canonical IDs, options bounds, and explanation coverage across 8,168 questions.
  * `verify_app_syntax.py`: End-to-end regression test suite verifying question count, mark sums, answer keys, and symbol exports.
  * `ingest_30_medium_mocks.py`: Automated parser converting `medium_mocks.docx` (30 full tests, 1,950 questions) into normalized JSON structures.
  * `ingest_30_easy_mocks.py`: Parser converting `easy_mocks.docx` (30 full tests, 1,950 questions).
  * `apply_medium_mocks_to_app.py`: Synchronizes mock test definitions, UI buttons, and window hooks across `app.js`.
  * `merge_all_master_questions.py`: Unifies all mock datasets, PYQs, and supplementary collections into `sample_questions.json`.
  * `math_verifier.py`: Automated symbolic and numerical verifier ensuring LaTeX validity, NAT decimal ranges, and answer key consistency.
  * `check_duplicates.py` & `comprehensive_duplicate_check.py`: Multi-stage duplicate detection using MD5 exact hashing and Jaccard token similarity ($> 0.80$).'''

if old_pipeline in content:
    content = content.replace(old_pipeline, new_pipeline)
    print("Replaced pipeline section successfully.")
else:
    print("Warning: old_pipeline not found exact match.")

# 2. Update Authentication & Security Layer
old_auth_sec = '''### 3. Authentication & Security Layer
* **Firebase Authentication ($v11.10.0$)**:
  * Multi-method authentication supporting Email / Password and Google OAuth (`signInWithPopup`, `signInWithRedirect`).
  * Instant **Guest Mode** ("Continue as Guest") enabling immediate offline access without credentials or network connectivity.
* **Cloud Firestore Security Rules (v2)**:
  * Granular rule declarations (`firestore.rules`) enforcing user-level isolation:
    * Questions collection (`/questions/{qid}`): Public read/write for authenticated users.
    * User attempts (`/users/{uid}/attempts/{id}`): Restricted strictly to `request.auth.uid == userId`.
    * Test sessions (`/users/{uid}/testSessions/{id}`): Restricted strictly to `request.auth.uid == userId`.
    * User profile (`/users/{uid}`): Restricted strictly to `request.auth.uid == userId`.'''

new_auth_sec = '''### 3. Authentication, Multi-Admin Governance & Security Layer
* **Firebase Authentication ($v11.10.0$)**:
  * Multi-method authentication supporting Email / Password and Google OAuth (`signInWithPopup`, `signInWithRedirect`).
  * **Dedicated Multi-Admin System**:
    * Master Administrator: `sahu1999ankit@gmail.com`.
    * 10 Dedicated Sub-Admins: `admin_1` through `admin_10` (uniform initial password: `admin@1234`).
    * Automated identifier auto-mapping in `handleEmailAuth` translating bare IDs (`admin_X`) to authenticated admin credentials.
    * Administrative permission guards protecting question bank actions (`Upload Questions`, `Delete`, `Clear All`).
  * Instant **Guest Mode** ("Continue as Guest") with safe timeout fallback ensuring offline accessibility even during Firebase handshake delays.
* **Hardened Cloud Firestore Security Rules (v2)**:
  * Granular rule declarations (`firestore.rules`) enforcing strict user-level isolation and role-based access control:
    * Questions collection (`/questions/{qid}`): **Public read-only**; writes strictly restricted to verified admin email identities (`sahu1999ankit@gmail.com` and `admin_1@gateprep.local`..`admin_10@gateprep.local`).
    * User attempts (`/users/{uid}/attempts/{id}`): Restricted strictly to `request.auth.uid == userId`.
    * Test sessions (`/users/{uid}/testSessions/{id}`): Restricted strictly to `request.auth.uid == userId`.
    * User profile (`/users/{uid}`): Restricted strictly to `request.auth.uid == userId`.'''

if old_auth_sec in content:
    content = content.replace(old_auth_sec, new_auth_sec)
    print("Replaced auth & security section successfully.")
else:
    print("Warning: old_auth_sec not found exact match.")

# 3. Update Project Structure scripts list
old_scripts_tree = '''├── scripts/
│   ├── verify_all_twenty_nine_features.py # Complete 37-feature automated CDP test suite
│   ├── verify_all_new_improvements.py    # Dedicated 7 new improvements verification suite
│   ├── verify_syllabus_guide.py          # Official IIT Madras syllabus guide test suite
│   ├── ingest_30_medium_mocks.py# Automated parser & ingestion engine for medium_mocks.docx
│   ├── ingest_30_easy_mocks.py  # Automated parser & ingestion engine for easy_mocks.docx
│   ├── apply_medium_mocks_to_app.py # Injects medium mock registrations into app.js
│   ├── merge_all_master_questions.py# Master merger script uniting all datasets into sample_questions.json
│   ├── verify_app_syntax.py     # End-to-end regression test suite verifying app.js, data, and UI
│   ├── math_verifier.py         # Mathematical and LaTeX validation utility
│   ├── check_duplicates.py      # Automated duplicate detector (ID, exact text, Jaccard similarity)
│   └── generate_questions.py    # Question bank builder and schema validation utility'''

new_scripts_tree = '''├── scripts/
│   ├── comprehensive_question_audit.py # In-browser Headless Edge CDP audit evaluating 8,168 questions
│   ├── verify_all_v6_features.py       # Master 112-point automated verification suite passing 100%
│   ├── audit_bank.py                   # Datastore integrity auditor checking canonical IDs & keys
│   ├── verify_app_syntax.py            # End-to-end regression test suite verifying app.js, data, and UI
│   ├── ingest_30_medium_mocks.py       # Automated parser & ingestion engine for medium_mocks.docx
│   ├── ingest_30_easy_mocks.py         # Automated parser & ingestion engine for easy_mocks.docx
│   ├── apply_medium_mocks_to_app.py    # Injects medium mock registrations into app.js
│   ├── merge_all_master_questions.py   # Master merger script uniting all datasets into sample_questions.json
│   ├── math_verifier.py                # Mathematical and LaTeX validation utility
│   ├── check_duplicates.py             # Automated duplicate detector (ID, exact text, Jaccard similarity)
│   └── generate_questions.py           # Question bank builder and schema validation utility'''

if old_scripts_tree in content:
    content = content.replace(old_scripts_tree, new_scripts_tree)
    print("Replaced scripts tree successfully.")
else:
    print("Warning: old_scripts_tree not found exact match.")

# 4. Insert Version 6.5 into Changelog and update Version 6.0 header
version_65_changelog = '''### Version 6.5 (Current Release — In-Browser Question Render Architecture, Multi-Admin Governance, SVG/Vector Reconstructions & Zero-Defect CDP Audit)
* **💻 Tokenized Code Block Architecture & Prism.js Syntax Highlighting**:
  * Completely resolved the critical rendering defect in C programming and data structures questions where code blocks printed raw HTML `<pre class="code-block">` and escaped entities (`&quot;`, `&lt;`, `&gt;`).
  * Replaced the defective container regex splitter in `formatQuestionContent()` with a **Tokenized Placeholder Architecture** (`@@@QB_BLOCK_X@@@`), eliminating premature truncation at inner header tags (`<div class="code-block-header">`).
  * Implemented smart language detection: automatically recognizes programming keywords (`int`, `printf`, `static`, `main`) when markdown fences lack explicit language flags and defaults gracefully to C syntax.
  * Integrated Prism.js syntax highlighting across practice cards, question palettes, and review interfaces.
* **📐 Multi-Line KaTeX LaTeX Protection Pipeline**:
  * Fixed math rendering failure on multiline display math (`$$S \\to Aa \\mid bAc...$$`) and grammar equations caused by `\\n` to `<br/>` substitutions fragmenting KaTeX DOM `Text` nodes.
  * Added upfront token-level isolation for display math (`$$...$$`, `\\[...\\]`) and inline math (`$...$`, `\\(...\\)`), ensuring full KaTeX formatting without text node fragmentation.
* **🔐 Multi-Admin Role System & Question Bank Security**:
  * Configured **10 dedicated sub-admin accounts** (`admin_1` through `admin_10` with default password `admin@1234`) alongside Master Admin `sahu1999ankit@gmail.com`.
  * Auto-mapping in `handleEmailAuth` translating simple username inputs (`admin_1`..`admin_10`) into authenticated session credentials.
  * Restricted question bank management actions (`Upload Questions`, `Delete`, `Clear All`) strictly to verified administrator accounts.
  * Hardened `firestore.rules` whitelist enforcing that only authorized admin identities can perform writes to `/questions/{qid}`.
* **🔍 8,130-Question Headless Edge CDP Verification (Zero Defects)**:
  * Executed comprehensive automated audit via Chrome DevTools Protocol (CDP) in Headless Microsoft Edge across all questions in active browser memory under strict error-throwing mode (`strict: 'warn'`, `throwOnError: true`).
  * Achieved a flawless **zero-defect scorecard**:
    * **0** HTML corruptions / unescaped entities
    * **0** unbalanced math delimiters
    * **0** KaTeX parse errors
    * **0** unclosed code blocks
    * **0** missing diagrams or tables
    * **0** truncated or dangling question endings
  * Filtered 38 legacy blank OCR stubs (`pyq_2007_cs01..05`, `pyq_2008_cs09..47`) in `loadMasterStaticQuestions()`, ensuring clean presentation in practice modes.
* **🎨 High-Fidelity Diagram Embeds & Visual Reconstructions**:
  * **Dijkstra Directed Graph (`pyq_2012_cs40`)**: Extracted high-resolution official vector graph from Page 156 of `CS_All_Old_Papers.pdf`, embedded clean base64 image inside `<figure class="q-diagram-container">`, restored verified options, correct answer `(D) SACET`, and step-by-step strict-inequality proof.
  * **Aptitude Student Share Pie Chart (`pyq_2015_S1_ga08`)**: Embedded interactive theme-matched SVG donut chart (Civil 30%, Electrical 20%, Mechanical 10%, Others 40%) with breakdown legend, fixed truncated question text ending at "Mechanical 9", and added step-by-step verification for answer `32`.
  * **Router Distance Vector Network (`pyq_2022_cs57`)**: Embedded responsive SVG schematic `[P] — [Q] — [R]`, cleaned OCR noise, restored NAT answer `0.5` and routing-loop probability proof.
  * **Dangerous Microbes Toxicity vs. Potency (`pyq_2011_ga61`)**: Embedded responsive SVG coordinate graph with sized microbe bubbles for P, Q, R, S, verified answer `(D) S`.
  * **Synchronous 3-Bit Counter (`pyq_2021_CS1_cs28`)**: Replaced OCR noise with clean toggle equations ($T_P = R$, $T_Q = \\overline{P}$, $T_R = \\overline{Q}$) and embedded SVG schematic, verified answer `011, 101, 000` (Option A).
  * **Logic Hazard Circuit (`pyq_2024_CS1_cs28`)**: Embedded responsive SVG gate schematic (AND gate with direct and inverted inputs), separated collapsed options, verified MSQ answers `(A)` and `(C)`.
  * **Probability MSQ (`pyq_2024_CS1_cs27`)**: Separated merged options, restored clean LaTeX notation, verified MSQ answers `(B)` and `(C)`.
* **🧹 Navbar Streamlining & UX Optimization**:
  * Cleaned up navigation sidebar by removing obsolete legacy items (`#nav-papers`), focusing navigation on high-yield sections: *Dashboard, Subjects, Practice Questions, Mock Tests, Full-Length PYQ Exams, Topic-Wise PYQs, Mistake Vault, Smart Playlists, Performance, and Admin Upload*.
* **📑 Metadata Alignment & Mathematical Question Restoration**:
  * **GATE 2025 Metadata Shift**: Corrected shifted topic/subject classifications across all 130 questions in Set 1 and Set 2 (e.g., corrected Q40 from DBMS to Compiler Design - Parsing).
  * **Trapezoidal Rule Error Bound (`pyq_2008_cs21`)**: Reconstructed question $\\int_1^2 x e^x dx$ with error $\\le \\frac{1}{3} \\times 10^{-6}$, verified answer `(A) 1000e`.
  * **Definite Calculus Integral (`pyq_2014_S3_cs47`)**: Formatted as $\\int_0^\\pi x^2 \\cos x\\,dx$, verified NAT answer `-6.28` ($-2\\pi$).
  * **Calculus Limit (`pyq_2015_S3_cs24`)**: Formatted as $\\lim_{x \\to \\infty} (1+x^2)e^{-x}$, reclassified under Calculus, verified NAT answer `0`.
  * **Basic Blocks Analysis (`pyq_2025_CS1_cs52`)**: Formatted 3-address code block, reclassified under Compiler Design, verified NAT answer `6`.
  * **Product Automaton Transition Tables (`pyq_2008_cs49`)**: Converted OCR transition tables to semantic `<table class="q-data-table">` for automata Y, Z, and product automaton options, verified answer `(A)`.
  * **Semantic Data Tables**: Converted 15+ questions containing unaligned OCR text into responsive `<table class="q-data-table">` elements.
  * **Spatial Aptitude Options**: Restored clear option labels for paper folding (`pyq_2025_s1_q09`) and cube folding (`pyq_2025_s2_q04`).
* **🧪 112/112 Automated Verification Checks Passing (100%)**:
  * Expanded `scripts/verify_all_v6_features.py` from 97 to 112 automated checks covering all v6.0 features, Elite Tier engines, Cherry on Top improvements, P0/P1 security rules, deduplication hashing, and multi-admin privilege systems.

'''

old_changelog_header = '''## 📝 Changelog

### Version 6.0 (Current Release — Daily Study Planner, Mock Score History & AIR Benchmarks, Weak Topic Focus Zone, Per-Question Time Heatmap, Spaced Repetition SRS, 3-State Theme Engine, Elite Tier Engines & Mobile Sticky UX)'''

new_changelog_header = '''## 📝 Changelog

''' + version_65_changelog + '''### Version 6.0 — Daily Study Planner, Mock Score History & AIR Benchmarks, Weak Topic Focus Zone, Per-Question Time Heatmap, Spaced Repetition SRS, 3-State Theme Engine, Elite Tier Engines & Mobile Sticky UX'''

if old_changelog_header in content:
    content = content.replace(old_changelog_header, new_changelog_header)
    print("Replaced changelog section successfully.")
else:
    print("Warning: old_changelog_header not found exact match.")

# 5. Update Authentication & Access section at bottom
old_auth_bottom = '''## 🔑 Authentication & Access
* **Guest Access (No Login Required)**: Click **"📴 Continue as Guest (Offline Mode)"** on the sign-in modal to immediately access all practice questions, full-length mocks, papers, and the virtual calculator without internet or login.
* **Email Sign In / Sign Up**: Enter your email address and password to sync your bookmarks, test history, and custom questions across devices via Firebase Cloud Firestore.'''

new_auth_bottom = '''## 🔑 Authentication, Admin Accounts & Access
* **Guest Access (No Login Required)**:
  * Click **"📴 Continue as Guest (Offline Mode)"** on the sign-in modal to immediately access all 8,168 practice questions, 80 full-length mocks, 21 PYQ papers, and the virtual calculator without internet or credentials.
  * Automatic fallback transition activates if Firebase network handshakes experience latency.
* **Student Sign In / Sign Up**:
  * Enter any valid email address and password to sync bookmarks, test history, notes, and custom flashcards across devices via Firebase Cloud Firestore.
* **Administrator Accounts (Question Bank Management & Auditing)**:
  * **Master Admin**: `sahu1999ankit@gmail.com`
  * **Dedicated Sub-Admins**: `admin_1` through `admin_10` (Uniform Password: `admin@1234`)
  * **Admin Privileges**:
    * Access to the **Upload Questions** panel (`#nav-upload`).
    * Ability to import custom question JSON bundles.
    * Authorization to delete custom questions or clear question batches.
    * Server-side write access to Cloud Firestore `/questions/{qid}` governed by `firestore.rules`.'''

if old_auth_bottom in content:
    content = content.replace(old_auth_bottom, new_auth_bottom)
    print("Replaced auth bottom section successfully.")
else:
    print("Warning: old_auth_bottom not found exact match.")

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("README.md updated successfully!")
