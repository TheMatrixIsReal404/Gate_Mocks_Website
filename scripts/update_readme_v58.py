# scripts/update_readme_v58.py
readme_content = """# 🎯 GATE CSE Practice Platform — Prepare Smart

A high-performance, responsive web application for **GATE Computer Science & Information Technology (CS & IT)** aspirants. Modeled after the official **TCS iON GATE exam portal**, featuring authentic question patterns, subject-wise practice, complete full-length mock examinations, previous year papers (PYQs), topic-wise PYQs hub (87 chapters), 5 elite intelligence diagnostic modules, an interactive official IIT Madras syllabus guide, a virtual scientific calculator, mistake revision queue, calibrated difficulty levels (Easy, Medium, Hard), executive performance analytics, universal global question search (8,168 Qs), 10-spoke mastery radar chart, expected value risk analyzer, formula blitz speed recall, and full offline/PWA capabilities.

---

## 🛠️ Technology Stack

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATION                              │
│  HTML5 • CSS3 (Custom Properties & Dark Theme) • Vanilla JavaScript (ES6+)   │
│  KaTeX Math Typesetting • TCS iON Scientific Calculator • 20/Page Pagination │
│  Universal Global Search (8,168 Qs) • 10-Spoke SVG Radar • 60s Formula Blitz │
└───────────────────────┬───────────────────────────────┬──────────────────────┘
                        │                               │
            ┌───────────▼────────────┐      ┌───────────▼────────────┐
            │   ONLINE DATA LAYER    │      │   OFFLINE DATA LAYER   │
            │  Google Cloud Firestore│      │   Browser LocalStorage │
            │  Firebase Auth v11.10  │      │   Service Worker Cache │
            │  Security Rules (v2)   │      │   sample_questions.json│
            └────────────────────────┘      └────────────────────────┘
                        │
            ┌───────────▼────────────────────────────────────────────┐
            │              DATA ENGINEERING & TOOLING                │
            │   Python 3.14 • python-docx • Math & Deduplication     │
            │   Netlify / Firebase Hosting with SPA Rewrites         │
            └────────────────────────────────────────────────────────┘
```

### 1. Frontend & Presentation Layer
* **Vanilla Modern JavaScript (ES6+ Modules)**:
  * Zero heavyweight framework overhead (no React, Angular, or Vue bundle weight) ensuring instantaneous sub-100ms first contentful paint (FCP) and low memory consumption on mobile devices.
  * Modular architecture with native ES module imports (`import { ... } from './firebase.js'`).
  * Reactive Single Page Application (SPA) state manager (`state` object controlling active page, timer, session telemetry, filters, bookmarks, and attempts).
* **HTML5 & CSS3 Design System**:
  * Semantic HTML5 layouts with high-contrast accessibility standards.
  * Dark-themed design system powered by CSS Custom Properties (`--bg-primary: #0f0f13`, `--bg-card: #1e1e2a`, `--accent: #6c63ff`, etc.).
  * Fully responsive CSS Grid and Flexbox layouts with smooth touch drawers (`#sidebar`, `.mobile-open`) for mobile screens ($\le 900\\text{px}$).
* **KaTeX Mathematical Typesetting Engine ($v0.16.21$)**:
  * High-speed LaTeX rendering via CDN for mathematical formulas, logic proofs, asymptotic limits, combinatorics, matrix equations, and graph theory relations.
  * Touch-scrollable equation blocks (`.katex-display { overflow-x: auto; }`) preventing horizontal viewport distortion on smartphones.
* **TCS iON Virtual Scientific Calculator Engine**:
  * Custom client-side mathematical evaluation engine replicating the official TCS iON GATE Virtual Calculator.
  * Supports Degrees (`DEG`) and Radians (`RAD`) angle modes, trigonometric, inverse trig, hyperbolic, logarithms ($\\\\ln, \\\\log_{10}, \\\\log_2$), exponentials ($e^x, 10^x, x^y$), factorial ($n!$), square/cube roots, modulo arithmetic, and memory registers (`MC`, `MR`, `MS`, `M+`, `M-`).
  * Accessible via topbar button or instant keyboard shortcut <kbd>C</kbd>.
* **Dual-Bar 20-Questions-Per-Page Pagination Engine**:
  * Top and bottom pagination bars across all question-heavy views (Practice, PYQs, Full-Length Mocks, and Review Mode).
  * Page size selector (`10`, `20`, `50`, `All`), First/Prev/Next/Last controls, and smooth scroll restoration.

### 2. Database & Data Storage Layer
* **Master Question Bank (`data/sample_questions.json`)**:
  * Master JSON datastore comprising **8,168 verified questions** with complete options, correct answers, difficulty ratings, and step-by-step mathematical explanations.
  * Pre-cached for immediate instant retrieval offline.
* **Client-Side Blob Synthesis**:
  * Dynamically synthesizes downloadable JSON files directly from client memory (`new Blob(...)`), allowing offline sample downloads even under `file:///` protocol.

### 3. Authentication & Security Layer
* **Firebase Authentication ($v11.10.0$)**:
  * Multi-method authentication supporting Email / Password and Google OAuth (`signInWithPopup`, `signInWithRedirect`).
  * Instant **Guest Mode** ("Continue as Guest") enabling immediate offline access without credentials or network connectivity.
* **Cloud Firestore Security Rules (v2)**:
  * Granular rule declarations (`firestore.rules`) enforcing user-level isolation:
    * Questions collection (`/questions/{qid}`): Public read/write for authenticated users.
    * User attempts (`/users/{uid}/attempts/{id}`): Restricted strictly to `request.auth.uid == userId`.
    * Test sessions (`/users/{uid}/testSessions/{id}`): Restricted strictly to `request.auth.uid == userId`.
    * User profile (`/users/{uid}`): Restricted strictly to `request.auth.uid == userId`.

### 4. Progressive Web App (PWA) & Offline Layer
* **Service Worker (`sw.js`)**:
  * Pre-caches core application assets (`index.html`, `style.css`, `app.js`, `firebase.js`, `manifest.json`, `sample_questions.json`) under cache version `gate-cse-v5`.
  * Implements Cache-First fetch strategies with network fallback for static assets.
  * Ignores Google API / Firestore endpoints to let the Firebase SDK manage its native offline persistence.
* **W3C Web App Manifest (`manifest.json`)**:
  * Enables standalone native-like home screen installation on Android, iOS, Windows, and macOS.
  * Features dark theme background `#0a0a14` and brand accent `#6c63ff`.

### 5. Data Engineering & Compilation Pipeline
* **Python 3.14 Pipeline (`scripts/`)**:
  * `verify_all_thirty_seven_features.py`: Complete automated Chrome DevTools Protocol (CDP) test suite verifying all 37 modules and features end-to-end.
  * `ingest_30_medium_mocks.py`: Automated parser converting `medium_mocks.docx` (30 full tests, 1,950 questions) into normalized JSON structures.
  * `ingest_30_easy_mocks.py`: Parser converting `easy_mocks.docx` (30 full tests, 1,950 questions).
  * `apply_medium_mocks_to_app.py`: Synchronizes mock test definitions, UI buttons, and window hooks across `app.js`.
  * `merge_all_master_questions.py`: Unifies all mock datasets, PYQs, and supplementary collections into `sample_questions.json`.
  * `verify_app_syntax.py`: End-to-end regression test suite verifying question count, mark sums, answer keys, and symbol exports.
  * `math_verifier.py`: Automated symbolic and numerical verifier ensuring LaTeX validity, NAT decimal ranges, and answer key consistency.
  * `check_duplicates.py` & `comprehensive_duplicate_check.py`: Multi-stage duplicate detection using MD5 exact hashing and Jaccard token similarity ($> 0.80$).

### 6. Hosting & Deployment
* **Netlify / Static CDN**:
  * Single-command deployment configured with `netlify.toml` providing SPA redirect rules (`/* -> /index.html 200`).
  * Compatible with Firebase Hosting, GitHub Pages, or any static server (`python -m http.server 8080`, `npx serve .`).

---

## 🏛️ Database & Data Architecture

### Firestore Collections & Data Schemas

```mermaid
erDiagram
    USERS ||--o{ ATTEMPTS : records
    USERS ||--o{ TEST_SESSIONS : completes
    QUESTIONS ||--o{ ATTEMPTS : evaluated_in

    USERS {
        string uid PK "Firebase Auth UID"
        string email "User email address"
        string displayName "Aspirant Name"
        timestamp createdAt "Registration timestamp"
    }

    QUESTIONS {
        string id PK "Unique Question ID (e.g., mock_med01_q01)"
        string mockId "Associated Mock ID (e.g., mock-med-01)"
        string paper "Paper title (e.g., GATE CS Medium Mock Exam #01)"
        string subject "GATE Subject (e.g., Operating Systems)"
        string topic "Specific Topic (e.g., CPU Scheduling)"
        string type "Question type: mcq | msq | nat"
        number marks "Marks awarded: 1 or 2"
        string difficulty "Difficulty: easy | medium | hard"
        string question "Question statement with KaTeX formulas & code blocks"
        array options "Array of 4 options (MCQ/MSQ)"
        array correct "0-indexed correct option array or numeric value"
        string explanation "Step-by-step mathematical solution"
        object natRange "NAT numerical acceptance range {min, max}"
        number year "Examination year"
    }

    ATTEMPTS {
        string id PK "Auto-generated Attempt ID"
        string questionId FK "Reference to question"
        string selectedAnswer "User selected answer or NAT input"
        boolean correct "Evaluation result: true | false"
        number timeSpent "Time spent in seconds"
        timestamp timestamp "Attempt timestamp"
    }

    TEST_SESSIONS {
        string id PK "Auto-generated Session ID"
        string mockId "Reference to Mock Test"
        string mockName "Name of the mock test"
        number score "Final score achieved"
        number totalMarks "Maximum marks (100)"
        number percentage "Percentage score"
        number correctCount "Total correct answers"
        number incorrectCount "Total incorrect answers"
        number unattemptedCount "Total skipped questions"
        number timeSpentSeconds "Total duration in seconds"
        object subjectBreakdown "Per-subject accuracy telemetry"
        timestamp date "Completion timestamp"
    }
```

### Storage Mechanism & Key Mapping

| Scope | Storage Mechanism | Path / Key | Retention / Sync | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Questions Bank** | Cloud Firestore / Static JSON Fallback | `/questions/{qid}` | Global / Cloud Synced | **8,168 verified GATE questions** shared across all users. |
| **Practice Attempts** | Cloud Firestore & LocalStorage | `/users/{uid}/attempts/{id}` | User Private / Synced | Tracks every question attempted, options chosen, correctness, and time spent. |
| **Test Sessions** | Cloud Firestore & LocalStorage | `/users/{uid}/testSessions/{id}` | User Private / Synced | Complete history of timed tests, mock exams, scores, accuracy, and subject breakdown. |
| **Question Bookmarks** | Browser LocalStorage | `gate_bookmarks_{uid}` | Device Local | Set of starred question IDs (`⭐`) for rapid revision. |
| **Confidence Tags** | Browser LocalStorage | `gate_cse_confidence_tags` | Device Local | Candidate confidence ratings (`high`, `educated`, `blind`) per question. |
| **Daily Streak** | Browser LocalStorage | `gate_daily_streak_v1` | Device Local | Daily active attempt counter, target goal, and streak history. |
| **Offline Cache** | Browser LocalStorage & IndexedDB | `gate_cse_v8_{uid}` / `GATE_CSE_QUESTION_BANK` | Device Local | Complete offline backup of question bank, attempts, and sessions. |
| **Master Static JSON** | HTTP Static File | `data/sample_questions.json` | PWA Service Worker Cached | 8,168-question master library loaded during bootstrapping or offline fallback. |

---

## 🏛️ Official GATE CSE Syllabus Specification (IIT Madras Standards)

The entire platform's 8,168 questions, topic tags, and practice modules are strictly calibrated against the official **GATE Computer Science & Information Technology (CS)** curriculum established by the organizing institute (**IIT Madras**):

| Section | Title | Topics & Sub-Domains (Official Specification Alignment) | Questions in Bank |
| :--- | :--- | :--- | :--- |
| **Section 1** | **Engineering Mathematics** | **Discrete Mathematics**: Propositional and first order logic. Sets, relations, functions, partial orders and lattices. Monoids, Groups. Graphs: connectivity, matching, coloring. Combinatorics: counting, recurrence relations, generating functions.<br>**Linear Algebra**: Matrices, determinants, system of linear equations, eigenvalues and eigenvectors, LU decomposition.<br>**Calculus**: Limits, continuity and differentiability. Maxima and minima. Mean value theorem. Integration.<br>**Probability and Statistics**: Random variables. Uniform, normal, exponential, poisson and binomial distributions. Mean, median, mode and standard deviation. Conditional probability and Bayes theorem. | **1,170 Q** (511 EM + 659 DM) |
| **Section 2** | **Digital Logic** | Boolean algebra. Combinational and sequential circuits. Minimization (algebraic technique, K-maps, tabular method). Number representations and computer arithmetic (fixed and floating point). | **421 Q** |
| **Section 3** | **Computer Organization and Architecture** | Machine instructions and addressing modes. ALU, data-path and control unit (hardwired and microprogrammed). Instruction pipelining, pipeline hazards. Memory hierarchy: cache, main memory and secondary storage; I/O interface (interrupt and DMA mode). | **616 Q** |
| **Section 4** | **Programming and Data Structures** | Programming in C. Recursion. Arrays, stacks, queues, linked lists, trees, binary search trees, binary heaps, graphs. | **969 Q** (390 C + 579 DS) |
| **Section 5** | **Algorithms** | Searching, sorting, hashing. Asymptotic worst case time and space complexity. Algorithm design techniques: greedy, dynamic programming and divide-and-conquer. Graph traversals, minimum spanning trees, shortest paths. | **796 Q** |
| **Section 6** | **Theory of Computation** | Regular expressions and finite automata. Context-free grammars and push-down automata. Regular and context-free languages, pumping lemma. Turing machines and undecidability. | **618 Q** |
| **Section 7** | **Compiler Design** | Lexical analysis, parsing, syntax-directed translation. Runtime environments. Intermediate code generation. Local optimisation, Data flow analyses: constant propagation, liveness analysis, common subexpression elimination. | **357 Q** |
| **Section 8** | **Operating System** | System calls, processes, threads, inter-process communication, concurrency and synchronization, deadlocks. CPU and I/O scheduling. Memory management and virtual memory. File systems. | **694 Q** |
| **Section 9** | **Databases** | ER-model. Relational model: relational algebra, tuple calculus, SQL. Integrity constraints, normal forms. File organization, indexing (e.g., B and B+ trees). Transactions and concurrency control. | **638 Q** |
| **Section 10** | **Computer Networks** | Concept of layering: OSI and TCP/IP protocol stacks; Basics of packet, circuit and virtual circuit switching; Data link layer: framing, error detection, Medium Access Control, Ethernet bridging; Routing protocols: shortest path, flooding, distance vector and link state routing; Fragmentation and IP addressing (IPv4, CIDR, NAT); Transport layer: flow control and congestion control, UDP, TCP, sockets; Application layer protocols: DNS, SMTP, HTTP, FTP, Email. | **709 Q** |
| **GA** | **General Aptitude** | **Verbal Aptitude**: Basic English grammar, vocabulary, reading comprehension, narrative sequencing.<br>**Quantitative Aptitude**: Data interpretation, numerical computation and estimation (ratios, percentages, powers, exponents, series, permutations, combinations).<br>**Analytical Aptitude**: Logic, deduction, analogy, numerical relations and reasoning.<br>**Spatial Aptitude**: Transformation of shapes (translation, rotation, scaling, mirroring, paper folding), patterns in 2 and 3 dimensions. | **1,180 Q** |

> [!NOTE]
> **Deprecated Topics Excluded**: Legacy topics discontinued in recent syllabus revisions (e.g., 8085 Microprocessor Assembly Programming, Web Technologies HTML/XML, and Information Systems) are omitted to prevent negative transfer.

---

## 🚀 Key Features & Innovations

### 1. 🔍 Universal Global Question Search (8,168 Questions)
* Instant global keyword search accessible via topbar button or keyboard shortcut <kbd>/</kbd>.
* Searches across the entire master question bank (8,168 questions) with real-time tokenized matching on question statements, options, topics, algorithm names, and explanations.
* Type-filtering chips: `All`, `MCQ`, `MSQ`, and `NAT`.
* 1-Click direct actions: **"▶ Practice Now"** or **"🗂️ Playlist"** directly from search results.

### 2. 🕸️ 10-Spoke Subject Mastery Radar Chart
* Responsive SVG Spider / Radar Chart rendered on the **Performance** page.
* Evaluates candidate accuracy across the 10 core GATE CS areas: *Engineering Math & DM, Digital Logic, COA, C & Data Structures, Algorithms, TOC, Compiler Design, Operating Systems, DBMS, and Networks*.
* 5 concentric calibration rings ($20\%$, $40\%$, $60\%$, $80\%$, $100\%$) and interactive data points with hover tooltips and strength tier badges (🟢 Strong $\ge 75\%$, 🟡 Average, 🔴 Focus Area).

### 3. ⏳ Exam Countdown & Daily Study Streak Engine
* Live persistent countdown widget in the topbar tracking days remaining until GATE (e.g. `⏳ GATE 2027: 100d`).
* Daily goal streak engine tracking daily questions completed (target: $20\text{ Q/day}$) with persistent flame badge (`🔥 3d (15/20 Q)`).

### 4. ⚖️ Option Elimination & Expected Value ($\mathbb{E}$) Risk Analyzer
* Real-time statistical decision support for MCQs, MSQs, and NATs:
  * 4 choices blind guess: $\mathbb{E} = 0.00\text{ M}$
  * 1 option eliminated (3 choices): $\mathbb{E} = +0.11\text{ M}$ ($1\text{M}$) / $+0.22\text{ M}$ ($2\text{M}$)
  * 2 options eliminated ($50:50$): $\mathbb{E} = +0.33\text{ M}$ ($1\text{M}$) / $+0.67\text{ M}$ ($2\text{M}$)
  * MSQs & NATs: $\mathbb{E} \ge 0\text{ M}$ (Zero negative penalty)
* **Confidence-Based Marking**: Rate questions as 🟢 Sure, 🟡 50:50 Guess, or 🔴 Blind Guess to calibrate self-awareness and detect overconfidence blindspots.

### 5. ⚡ 60-Second Formula Blitz Mode (Speed Recall)
* High-intensity rapid formula recall challenge inside the Formula Flashcards deck.
* 60-second countdown clock with streak scoring, solution peeking, and memory recall tracking.

### 6. 🎯 NAT Precision & Rounding Trap Inspector
* Dedicated numerical tolerance preview for NAT questions displaying exact acceptance bounds (e.g., $[3.14, 3.16]$).
* Contextual warning alerting students against intermediate float truncation traps.

### 7. 📄 1-Click Printable 2-Column PDF Practice Worksheet Generator
* Clean 2-column examination paper generator with print-optimized CSS (`@media print`).
* Includes question checkboxes, code fences, and a separate detachable Answer Key & Solutions page.

### 8. 🧠 5 Elite GATE Intelligence Modules
* **Loss Diagnosis & Root-Cause Error Tagging**: Attributing misses to Silly Errors, Misread, Concept Gap, Formula Slip, or Time Rushed with Potential Score Boost & Mark Bleed analytics.
* **GATE PYQ Weightage Heatmap & Topic Trend Engine (1990–2025)**: Top 25 Highest-Yield Chapters Leaderboard with 1-click targeted drills.
* **Speed vs. Accuracy 4-Quadrant Matrix**: Sweet Spot, Under-Confident, Rash Errors, and "The Black Hole" detector with remediation drill.
* **Smart Playlists & Revision Buckets**: Custom and pre-seeded revision buckets (Starred NATs, High-Yield Chapters, Last 7 Days Mistakes).
* **Multi-Method Explanations & KaTeX Student Shortcut Notes**: Method 1 (Standard Derivation) vs. Method 2 (GATE Shortcut / Elimination) with private persistent notes.

### 9. 📑 Topic-Wise GATE CSE PYQs Hub (87 Chapters across 13 Subjects)
* Dedicated navigation item (`#nav-pyqs`) mapping all **2,224 authentic GATE PYQs (1990–2025)** into **87 curated syllabus chapters**.
* Real-time search, subject filter buttons, and combined difficulty / type selectors.

### 10. 📝 Authentic 5-State TCS iON Exam Simulator & Real-time Telemetry
* Full-featured GATE exam interface with countdown timer (180 minutes), interactive question palette adhering to the official 5-state protocol (Not Visited, Not Answered, Answered, Marked for Review, Answered & Marked for Review).
* Auto-save exam crash recovery every 5 seconds to `localStorage`.
* Synthesized Web Audio pacing chimes at 60m, 30m, and 5m milestones.
* Fullscreen exam lockdown with proctored tab-switch alerts (<kbd>F</kbd>).

---

## 📂 Project Structure

```
0.Gate_Mocks_Website/
│
├── index.html                   # Main application entry point, layouts, topbar, modals
├── style.css                    # Unified design system, responsive styles, themes, calibration badges
├── app.js                       # Core SPA logic, state management, test engines, calculator, ratings
├── firebase.js                  # Firebase Auth & Firestore client configuration (CDN ESM)
├── firestore.rules              # Cloud Firestore security rules with user-level isolation
├── manifest.json                # PWA manifest for standalone home-screen installation
├── sw.js                        # Service Worker for offline asset caching (gate-cse-v5)
├── netlify.toml                 # Netlify SPA redirect and rewrite rules
├── medium_mocks.docx            # Word source for 30 Medium-Level Full-Length Mock Exams
├── easy_mocks.docx              # Word source for 30 Easy-Level Full-Length Mock Exams
├── mocks.docx                   # Word compendium of 20 Full-Length Mocks with calibration table
├── mocks.md                     # Markdown calibration and difficulty rating reference guide
│
├── data/
│   ├── sample_questions.json    # Master database: 8,168 verified questions with step-by-step solutions
│   ├── gate_30_medium_mocks.json# Standalone 30 Medium Mocks dataset (1,950 questions)
│   ├── gate_30_easy_mocks.json  # Standalone 30 Easy Mocks dataset (1,950 questions)
│   ├── gate_20_full_mocks.json  # 20 Full-Length Mocks Compendium (1,300 questions)
│   ├── gate_easy_medium_mocks.json # Category 1 & 2 Mocks (650 questions)
│   ├── gate_2025_pyqs.json      # GATE 2025 Set 1 & Set 2 complete papers (130 questions)
│   ├── gate_overflow_pyqs_added.json # Curated historical questions from Gate Overflow Books
│   ├── gate_drive_pyqs_added.json    # Authentic PYQs ingested from Drive paper archive
│   └── gate_pyqs_added.json     # Clean multi-year historical PYQs (1990-2021)
│
├── scripts/
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
│   └── generate_questions.py    # Question bank builder and schema validation utility
│
└── README.md                    # Project documentation, tech stack, database architecture & changelog
```

---

## 📝 Changelog

### Version 5.8 (Current Release — Universal Global Question Search, 10-Spoke Mastery Radar, Expected Value Risk Analyzer, Formula Blitz, Exam Countdown & Study Streak)
* **🔍 Universal Global Question Search (8,168 Questions)**:
  * Fast tokenized search across all 8,168 questions by topic, algorithm, theorem, or code snippet with topbar shortcut <kbd>/</kbd>.
* **🕸️ 10-Spoke Subject Mastery Radar Chart**:
  * Pure SVG spider chart on the **Performance** page evaluating 360° syllabus depth across the 10 core GATE CS areas.
* **⏳ Exam Countdown & Daily Study Streak Engine**:
  * Live topbar countdown to the first Saturday of February and daily attempt tracker (goal: $20\text{ Q/day}$) with persistent streak badges.
* **⚖️ Option Elimination & Expected Value ($\mathbb{E}$) Risk Analyzer**:
  * Statistical return on risk analyzer for MCQs, MSQs, and NATs with confidence tagging (🟢 Sure, 🟡 50:50, 🔴 Blind).
* **⚡ 60-Second Formula Blitz Mode**:
  * Timed rapid-fire formula recall challenge with streak scoring and solution peeking.
* **🎯 NAT Precision & Rounding Trap Inspector**:
  * Numerical tolerance boundaries $[min, max]$ display with intermediate truncation advisories.
* **📄 2-Column Printable Practice Worksheet Generator**:
  * 1-Click formatted PDF worksheet generator with detachable answer key and solution tables.
* **🧪 37/37 Full-Site Verification Suite Passing 100%**:
  * Verified end-to-end via automated Chrome DevTools Protocol test suite (`scripts/verify_all_twenty_nine_features.py`).

### Version 5.7 (Official IIT Madras Syllabus Standards, 5 Elite Intelligence Modules & Topic-Wise PYQs Hub)
* **🏛️ Official IIT Madras Verbatim Syllabus Alignment & Interactive Guide**:
  * Embedded complete 10-section syllabus guide directly into the "Subjects" page with 1-click "▶ Practice" and "📑 PYQ Chapters" shortcuts.
* **📑 Topic-Wise GATE CSE PYQs Hub (87 Chapters & 2,224 PYQs)**:
  * Multi-decade PYQs (1990–2025) organized into 87 high-yield chapters with custom filters and drills.
* **🧠 5 Elite GATE Intelligence Modules**:
  * Loss Diagnosis & Error Tagging, Multi-Decade Weightage Heatmap, Speed vs. Accuracy 4-Quadrant Matrix, Smart Playlists & Revision Buckets, Dual-Method Explanations & Shortcut Notes.

### Version 5.6 (Formula Flashcards & Spaced Repetition, Exam Crash Protection, 5-State TCS iON Palette)
* **📇 Formula Flashcards & Practice Hint System (Spaced Repetition)**: 3D Flip-Card deck for high-frequency formulas with Leitner SRS ratings.
* **🛡️ Exam Crash Protection & Auto-Save Recovery**: Saves candidate state every 5 seconds to `localStorage`.
* **🎨 Authentic 5-State TCS iON Question Palette & Live Counter Legend**.

### Version 5.5 (Mistake Vault, GATE Score & AIR Predictor, Pacing Analytics & PWA v5)
* **📖 Diagnostic Mistake Vault**: Unresolved, Mastered, Starred classification with 1-click re-test.
* **🎯 Official GATE Score & AIR Predictor**: Normalization simulation with IIT/PSU cutoff brackets.

---

## 🛠️ How to Run Locally

### Option 1: Python Built-in HTTP Server (Recommended)
Run the following command in PowerShell / Terminal:
```powershell
python -m http.server 8080
```
Then open `http://localhost:8080` in your browser.

### Option 2: VS Code Live Server
1. Open the project folder in VS Code.
2. Right-click [`index.html`](index.html) and select **"Open with Live Server"**.

### Option 3: Node.js `serve`
```bash
npx serve .
```

---

## 🔑 Authentication & Access
* **Guest Access (No Login Required)**: Click **"📴 Continue as Guest (Offline Mode)"** on the sign-in modal to immediately access all practice questions, full-length mocks, papers, and the virtual calculator without internet or login.
* **Email Sign In / Sign Up**: Enter your email address and password to sync your bookmarks, test history, and custom questions across devices via Firebase Cloud Firestore.
"""

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("README.md updated for Version 5.8 successfully!")
