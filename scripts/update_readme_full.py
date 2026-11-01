# scripts/update_readme_full.py
import os

readme_content = """# 🎯 GATE CSE Practice Platform — Prepare Smart

A high-performance, responsive web application for **GATE Computer Science & Information Technology (CS & IT)** aspirants. Modeled after the official **TCS iON GATE exam portal**, featuring authentic question patterns, subject-wise practice, complete full-length mock examinations, previous year papers (PYQs), topic-wise PYQs hub (87 chapters), 5 elite intelligence diagnostic modules, an interactive official IIT Madras syllabus guide, a virtual scientific calculator, mistake revision queue, calibrated difficulty levels (Easy, Medium, Hard), executive performance analytics, and full offline/PWA capabilities.

---

## 🛠️ Technology Stack

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATION                              │
│  HTML5 • CSS3 (Custom Properties & Dark Theme) • Vanilla JavaScript (ES6+)   │
│  KaTeX Math Typesetting • TCS iON Scientific Calculator • 20/Page Pagination │
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
  * Features touch-scrollable equation blocks (`.katex-display { overflow-x: auto; }`) preventing horizontal viewport distortion on smartphones.
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
  * `ingest_30_medium_mocks.py`: Automated parser converting `medium_mocks.docx` (30 full tests, 1,950 questions) into normalized JSON structures.
  * `ingest_30_easy_mocks.py`: Parser converting `easy_mocks.docx` (30 full tests, 1,950 questions).
  * `apply_medium_mocks_to_app.py`: Synchronizes mock test definitions, UI buttons, and window hooks across `app.js`.
  * `merge_all_master_questions.py`: Unifies all mock datasets, PYQs, and supplementary collections into `sample_questions.json`.
  * `verify_all_twenty_nine_features.py`: Complete automated Chrome DevTools Protocol (CDP) test suite verifying all 29 modules and features end-to-end.
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
| **Offline Cache** | Browser LocalStorage & IndexedDB | `gate_cse_v8_{uid}` / `GATE_CSE_QUESTION_BANK` | Device Local | Complete offline backup of question bank, attempts, and sessions. |
| **Master Static JSON** | HTTP Static File | `data/sample_questions.json` | PWA Service Worker Cached | 8,168-question master library loaded during bootstrapping or offline fallback. |

---

## 🏛️ Official GATE CSE Syllabus Specification (IIT Madras Standards)

The entire platform's 8,168 questions, topic tags, and practice modules are strictly calibrated against the official **GATE Computer Science & Information Technology (CS)** curriculum established by the organizing institute (**IIT Madras**):

| Section | Title | Topics & Sub-Domains (Verbatim from Official Specification) | Questions in Bank |
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

### 1. 🏆 Comprehensive Full-Length Mock Exams & Difficulty Engine
* **90+ Full-Length Mock Exams & Official Papers** (65 Questions, 180 Min, 100 Marks each):
  * **30 Medium Mock Examinations**:
    * Full 65-question papers (`mock-med-01` to `mock-med-30`) strictly aligned with the latest IISc / IIT GATE CS syllabus and pattern.
    * Calibrated ratings (**4.8 to 5.7 / 10**), target cutoffs (**29–33 M**), and AIR < 100 benchmarks (**72–78 M**).
  * **30 Easy Mock Examinations**: Foundational full-syllabus papers (`mock-easy-01` to `mock-easy-30`).
  * **20 Compendium Mocks**: 10 Medium (`mock-flm-01` to `mock-flm-10`) and 10 Hard Rank Boosters (`mock-flm-11` to `mock-flm-20`).
  * **10 Category 1 & 2 Mocks**: Topic-Focused & Core CS exams.
  * **21 Full-Length PYQ Examination Papers**: Complete papers from 2007 through 2025.
* **Interactive Difficulty Calibration Matrix**:
  * Direct level-filtering tabs on the Mock Tests page: `All`, `Easy`, `Medium (55 papers)`, `Hard`, `Practice Sets`, `Subject Mocks`, and `My History`.
  * Performance targets displayed on each mock card: `🎯 Cutoff: 30-32 M` • `🏆 AIR < 100: 74-78 M`.

### 2. 📚 8,168 Authentic Questions & Complete Syllabus Coverage
* Massive verified question repository with **8,168 authentic questions**:
  * **1,950 Questions**: 30 Medium Mock Examinations (`medium_mocks.docx`) with step-by-step solutions.
  * **1,950 Questions**: 30 Easy Mock Examinations (`easy_mocks.docx`).
  * **1,300 Questions**: 20 Full-Length Mocks Compendium (`mocks.docx`).
  * **650 Questions**: 10 Category 1 & Category 2 Full Mocks.
  * **2,224 Questions**: Multi-decade official GATE Previous Year Questions (1990–2025).
  * **94 Questions**: Topic and subject practice banks.
* Breakdown by difficulty: **3,358 Easy**, **4,252 Medium**, **558 Hard**.
* Breakdown by question type: **3,726 NATs**, **3,379 MCQs**, **1,063 MSQs**.

### 3. 📑 Topic-Wise GATE CSE PYQs Hub (87 Chapters across 13 Subjects)
* Dedicated navigation item (`#nav-pyqs`) mapping all **2,224 authentic GATE PYQs (1990–2025)** into **87 curated syllabus chapters**.
* Real-time search, subject filter buttons, and combined difficulty / type selectors.
* Expandable topic accordion cards displaying:
  * Question counts, marks, and 1M vs 2M split.
  * Quick 1-click **"▶ Topic Drill"** targeting the specific chapter.
  * 1-Click **"🎲 Random 15-Question Mixed Drill"** for spontaneous topic evaluation.

### 4. 🧠 5 Elite GATE Intelligence Diagnostic Modules
* **Loss Diagnosis & Root-Cause Error Tagging**:
  * Tag every missed question with actionable root-cause categories: 🔴 **Silly Mistake** (calculation/sign error), 🟡 **Misread / Misinterpreted**, 🟣 **Concept Gap**, 🔵 **Formula Slip**, and ⏱️ **Time Pressure**.
  * Dynamic calculation of **Potential Score Boost** (recoverable marks) and **Mark Bleed** penalty metrics on test review and Mistake Vault.
* **Multi-Decade PYQ Weightage Heatmap & Topic Trend Engine (1990–2025)**:
  * Interactive historical mark distribution across all GATE subjects with annual mark averages.
  * **Top 25 Highest-Yield Chapters Leaderboard** ranked by total marks and question frequencies with 1-click targeted drills.
* **Speed vs. Accuracy 4-Quadrant Cognitive Matrix**:
  * Evaluates every question attempt against time spent and correctness:
    * 🟢 **Quadrant 1 (The Sweet Spot)**: High Speed & High Accuracy.
    * 🟡 **Quadrant 2 (Under-Confident)**: High Accuracy but Slow Dwell Time.
    * 🟠 **Quadrant 3 (Rash Errors)**: High Speed but Incorrect.
    * 🔴 **Quadrant 4 (The Black Hole)**: Excessive Time Spent (>3.5 min) and Incorrect.
  * 1-Click **"🌀 Drill My Black Hole Questions"** remediation engine.
* **Smart Playlists & Revision Buckets**:
  * Dedicated sidebar navigation item (`#nav-playlists`) enabling custom student revision decks.
  * Pre-seeded smart buckets: **⭐ Bookmarked Numerical Answer Types (NATs)**, **🔥 High-Yield Chapters**, and **🕒 Last 7 Days Mistakes**.
  * Instant modal for creating new playlists and adding/removing questions from Practice or Review modes.
* **Dual-Method Explanations & KaTeX Student Shortcut Notes**:
  * Side-by-side solution tabs: **Method 1 (Standard / Rigorous Textbook Derivation)** vs. **Method 2 (GATE Shortcut / Option Elimination / Boundary Cases)**.
  * Private persistent revision scratchpad on every question with KaTeX LaTeX math support.

### 5. 🏛️ Interactive Official GATE CSE Syllabus Guide
* Expandable syllabus guide embedded directly on the **Subjects** page.
* Detailed verbatim topic descriptions across Sections 1 to 10 + General Aptitude.
* Direct shortcuts: **"▶ Practice"** and **"📑 PYQ Chapters"** for immediate subject-level drilling.

### 6. 📝 Authentic 5-State TCS iON Exam Simulator & Real-time Telemetry
* Full-featured GATE exam interface with countdown timer (180 minutes), interactive question palette adhering to the official 5-state protocol:
  * ⚪ **Not Visited** (`#2b3245`)
  * 🔴 **Not Answered** (`#ef4444`)
  * 🟢 **Answered** (`#22c55e`)
  * 🟣 **Marked for Review** (`#8b5cf6`)
  * 🟣🟢 **Answered & Marked for Review** (`#8b5cf6` with green indicator)
* Real-time legend counters dynamically showing quantities for all five states.
* **Exam Crash Protection & Auto-Save**: Saves candidate responses, timers, and dwell times every 5 seconds to `localStorage` with a recovery modal to resume after accidental browser closures or reloads.
* **Exam Pacing Chimes**: Synthesized Web Audio countdown alerts at 60m, 30m, and 5m remaining marks with topbar mute toggle (`🔔`/`🔕`).
* **Fullscreen Exam Lockdown & Tab-Switch Proctored Alerts**: 1-click fullscreen toggle (<kbd>F</kbd>) with real-time blur/tab-switch logging.
* Automatic score calculation adhering strictly to GATE negative marking rules:
  * 1-mark MCQ: $-\\\\frac{1}{3}$ penalty
  * 2-mark MCQ: $-\\\\frac{2}{3}$ penalty
  * MSQ & NAT: $0$ negative marking

### 7. 📇 Formula Flashcards & Practice Hint System (Spaced Repetition)
* Dedicated **"💡 Hint / Formula"** button on every practice question card and action bar, dynamically revealing concept hints and key formulas without spoiling the full solution.
* Interactive **3D Flip-Card Flashcard Deck** for high-frequency formulas:
  * **Master's Theorem Recurrences**: Form $T(n) = aT(n/b) + \\\\Theta(n^k \\\\log^p n)$, 3 standard cases, extended logarithmic subcases, regularity condition, and non-polynomial boundary traps.
  * **Graph Theory Invariants**: Handshaking lemma, Euler's planar formula $V - E + R = 2$, planar edge bounds ($E \\\\le 3V - 6$ standard, $E \\\\le 2V - 4$ triangle-free), Cayley's spanning tree formulas ($n^{n-2}$ for $K_n$, $m^{n-1} n^{m-1}$ for $K_{m,n}$), and Eulerian path/circuit conditions.
  * **CPU Scheduling Metrics & Bounds**: $TAT = CT - AT$, $WT = TAT - BT$, $RT$, Round Robin max waiting time $(n-1)q$, convoy effect, and SJF/SRTF optimality.
  * **IPv4 CIDR Subnetting & Masking**: Total IPs ($2^{32-n}$), usable host counts ($2^{32-n}-2$), bitwise AND network address masking, directed broadcast masking, and CIDR power table.
  * **Virtual Memory EMAT**: Multi-level page tables, TLB hits/misses, and page fault penalties.
  * **Cache Memory & AMAT**: Direct, set-associative, and fully-associative Tag/Index/Offset address splits and hit/miss penalties.
  * **Pipeline Speedup & CPI**: Non-pipelined vs pipelined throughput and stall hazard degradation.
  * **Database Normal Forms**: 1NF, 2NF, 3NF, BCNF strict definitions, and Lossless-Join decomposition test.
  * **Chomsky Hierarchy Closures**: Complete operation closure matrix across Regular, DCFL, CFL, Decidable, and RE languages.
* **Spaced Repetition (SRS) Engine**: Self-rating controls (🔴 Hard / Again, 🟡 Good, 🟢 Mastered) with persistence to `localStorage` (`gate_formula_flashcards_srs`), subject filtering, deck shuffling (<kbd>🔀</kbd>), 3D flip animation, and desktop shortcuts.

### 8. 📖 Diagnostic "Mistake Vault" & Weakness Revision Engine
* Dedicated sidebar navigation item (`#nav-mistakes`) classifying errors as Unresolved, Mastered, or Starred.
* 1-Click **"🔥 Re-Test My Mistakes"** focused revision drill targeting historical errors.

### 9. 🎯 Official GATE Score & Normalized AIR Predictor
* Realistic simulation engine based on the official IISc/IIT normalization formula with marks slider, category adjustments, and direct PSU / IIT eligibility insights.

### 10. 🧮 GATE Virtual Scientific Calculator (TCS iON Pattern)
* Replicates the exact TCS iON exam calculator with keyboard shortcut <kbd>C</kbd> and touch/mouse draggable floating modal.

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
│   ├── verify_all_twenty_nine_features.py # End-to-end 29-feature CDP test suite
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

### Version 5.7 (Current Release — Official IIT Madras Syllabus Standards, 5 Elite Intelligence Modules & Topic-Wise PYQs Hub)
* **🏛️ Official IIT Madras Verbatim Syllabus Alignment & Interactive Guide**:
  * Embedded complete 10-section syllabus guide directly into the "Subjects" page with 1-click "▶ Practice" and "📑 PYQ Chapters" shortcuts.
  * Verbatim synchronization across all subject cards and diagnostic tracking with zero legacy baggage.
  * Excluded discontinued syllabus topics (8085 Microprocessor Assembly, HTML/XML Web Technologies, Information Systems).
* **📑 Topic-Wise GATE CSE PYQs Hub (87 Chapters & 2,224 PYQs)**:
  * Comprehensive topic-wise practice hub categorizing multi-decade PYQs (1990–2025) into 87 high-yield chapters.
  * Instant filter by Subject, Difficulty (Easy, Medium, Hard), Question Type (MCQ, MSQ, NAT), and search keyword.
  * Expandable topic drawers displaying question breakdown, 1-click topic drills, and random 15-question revision drills.
* **🧠 5 Elite GATE Intelligence Modules**:
  * **1. Loss Diagnosis & Root-Cause Error Tagging**:
    * Granular error attribution on every incorrect question: 🔴 **Silly Mistake** (calculation/sign error), 🟡 **Misread / Misinterpreted**, 🟣 **Concept Gap**, 🔵 **Formula Slip**, and ⏱️ **Time Pressure**.
    * Real-time calculation of **Potential Score Boost** (recoverable marks from avoidable errors) and **Mark Bleed** penalty metrics on test review and Mistake Vault.
  * **2. Multi-Decade Weightage Heatmap & Topic Trend Engine (1990–2025)**:
    * Comprehensive historical mark distribution across all GATE subjects with annual mark averages.
    * **Top 25 Highest-Yield Chapters Leaderboard** ranked by total marks and question frequencies with 1-click targeted drills.
  * **3. Speed vs. Accuracy 4-Quadrant Matrix**:
    * Classifies every question attempt into 4 cognitive quadrants:
      * 🟢 **Quadrant 1 (The Sweet Spot)**: High Speed & High Accuracy.
      * 🟡 **Quadrant 2 (Under-Confident)**: High Accuracy but Slow Dwell Time.
      * 🟠 **Quadrant 3 (Rash Errors)**: High Speed but Incorrect.
      * 🔴 **Quadrant 4 (The Black Hole)**: Excessive Time Spent (>3.5 min) and Incorrect.
    * 1-Click **"🌀 Drill My Black Hole Questions"** remediation engine.
  * **4. Smart Playlists & Revision Buckets**:
    * Create, manage, and drill custom student question buckets.
    * Pre-seeded smart buckets: **⭐ Bookmarked Numerical Answer Types (NATs)**, **🔥 High-Yield Chapters**, and **🕒 Last 7 Days Mistakes**.
    * 1-Click question addition/removal directly from Practice, Mock Review, and Mistake Vault modals.
  * **5. Dual-Method Explanations & KaTeX Student Shortcut Notes**:
    * Side-by-side solution tabs: **Method 1 (Standard / Rigorous Textbook Derivation)** vs. **Method 2 (GATE Shortcut / Option Elimination / Boundary Cases)**.
    * Private persistent revision scratchpad on every question with KaTeX LaTeX math support.
* **🧪 29/29 Full-Site Verification Suite Passing 100%**:
  * End-to-end automated CDP test suite (`scripts/verify_all_twenty_nine_features.py`) verifying all 29 modules with zero regressions.

### Version 5.6 (Formula Flashcards & Spaced Repetition, Exam Crash Protection, 5-State TCS iON Palette, GATE Mastery Matrix, Custom Drills, Data Portability, Revision Scratchpad & Pacing Chimes)
* **📇 Formula Flashcards & Practice Hint System (Spaced Repetition)**:
  * Dedicated **"💡 Hint / Formula"** button on every practice question card and action bar, dynamically revealing concept hints and key formulas without spoiling the full solution.
  * Interactive **3D Flip-Card Flashcard Deck** for high-frequency formulas (Master's Theorem, Graph Theory Invariants, CPU Scheduling, IPv4 Subnetting, Virtual Memory, Cache Memory, Pipeline Speedup, Normal Forms, Chomsky Hierarchy Closures).
  * **Spaced Repetition (SRS) Engine**: Self-rating controls (🔴 Hard / Again, 🟡 Good, 🟢 Mastered) with persistence to `localStorage` (`gate_formula_flashcards_srs`).
* **🛡️ Exam Crash Protection & Auto-Save Recovery**:
  * Real-time candidate state synchronization every 5 seconds to `localStorage` (`gate_active_test_autosave_v1`), saving answers, timer remaining, per-question dwell times, and visited/marked sets.
* **🎨 Authentic 5-State TCS iON Question Palette & Live Counter Legend**:
  * Full adherence to the official GATE CBT protocol (Not Visited, Not Answered, Answered, Marked for Review, Answered & Marked for Review).
* **📊 GATE Syllabus Mastery Matrix & Weightage Heatmap**:
  * Visual diagnostic card on the **Performance** page categorizing performance against canonical GATE CSE syllabus weightage (GA: 15M, EM/DM: 13M, Core CS: 72M).
* **⚙️ Custom Mock Exam & Practice Drill Generator**:
  * Interactive modal generator (`#custom-drill-modal`) accessible from both Mocks and Practice pages.
* **💾 1-Click Offline User Data Portability (Backup & Restore)**:
  * Export complete student progress to a clean JSON file (`gate_cse_progress_[DATE].json`) and instant restore.
* **🔔 Exam Pacing Web Audio Countdown Chimes**:
  * Web Audio API synthesized gentle chime notifications alerting candidates at 60m, 30m, and 5m remaining marks.

### Version 5.5 (Authentic CBT Simulation, Mistake Vault, GATE Score & AIR Predictor, Pacing Analytics & PWA v5)
* **📖 Diagnostic "Mistake Vault" & Weakness Revision Engine**:
  * Dedicated sidebar navigation item (`#nav-mistakes`) collecting every question ever missed in timed mock tests or practice sessions.
  * 1-Click **"🔥 Re-Test My Mistakes"**: Automatically generates a focused 15-question revision drill targeting historical errors.
* **🎯 Official GATE Score & Normalized AIR Predictor Simulator**:
  * High-precision simulation engine based on the official IISc/IIT GATE scoring normalization formula.
* **⏱️ Question-Wise Time & Pacing Analytics Engine**:
  * Precision dwell-time tracking: records exact seconds spent per question during timed exams.
* **🖥️ Fullscreen Exam Lockdown & Proctored Tab-Switch Alerts**:
  * 1-Click **"⛶ Fullscreen"** exam mode toggle in the test topbar with tab-switch logging.
* **🧮 Draggable TCS iON Scientific Calculator**:
  * Draggable floating modal on desktop and touch screens.

### Version 5.0 (8,168 Questions, 30 Medium Mocks Ingestion, 30 Easy Mocks & PYQ Suite)
* **30 Medium-Level Full-Length Mock Examinations Ingestion (`medium_mocks.docx`)**:
  * Parsed and extracted all 30 Full-Length Mock Exams (1,950 questions) aligned strictly with the official IISc/IIT GATE CS syllabus.
  * Merged into master database `data/sample_questions.json`, expanding the question bank from 6,218 to **8,168 questions**.
* **Dashboard Counter & Upload Utility Synchronization**:
  * Verified dynamic update of the **Total Questions** counter on the Dashboard to **8,168**.

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

with open('README.md', 'w', encoding='utf-8', newline='') as f:
    f.write(readme_content)

print("README.md updated successfully!")
