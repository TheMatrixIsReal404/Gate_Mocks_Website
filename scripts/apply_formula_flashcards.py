# -*- coding: utf-8 -*-
import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. State: add flashcardStats
if 'flashcardStats:' not in code:
    code = code.replace(
        "questionNotes:    {},",
        "questionNotes:    {},\n  flashcardStats:   {},"
    )

# 2. In bootApp / cache loading
if 'state.flashcardStats = JSON.parse' not in code:
    code = code.replace(
        "try { state.questionNotes = JSON.parse(localStorage.getItem('gate_question_notes') || '{}'); } catch(e){ state.questionNotes = {}; }",
        "try { state.questionNotes = JSON.parse(localStorage.getItem('gate_question_notes') || '{}'); } catch(e){ state.questionNotes = {}; }\n    try { state.flashcardStats = JSON.parse(localStorage.getItem('gate_formula_flashcards_srs') || '{}'); } catch(e){ state.flashcardStats = {}; }"
    )

# 3. In exportUserData
if 'flashcardStats: state.flashcardStats' not in code:
    code = code.replace(
        "questionNotes: state.questionNotes || {}",
        "questionNotes: state.questionNotes || {},\n      flashcardStats: state.flashcardStats || {}"
    )

# 4. In handleRestoreProgressFile
if 'state.flashcardStats = Object.assign' not in code:
    code = code.replace(
        "state.questionNotes = Object.assign({}, state.questionNotes || {}, data.questionNotes || {});",
        "state.questionNotes = Object.assign({}, state.questionNotes || {}, data.questionNotes || {});\n      state.flashcardStats = Object.assign({}, state.flashcardStats || {}, data.flashcardStats || {});\n      try { localStorage.setItem('gate_formula_flashcards_srs', JSON.stringify(state.flashcardStats)); } catch(e){}"
    )

# 5. In renderPracticeQuestion topbar: add Flashcards button
old_topbar_btn = """<button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()" type="button" title="GATE Virtual Calculator (C)">🧮 <span class="hide-xs">Calc</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleShortcutsModal()" type="button" title="Shortcuts (?)">⌨️</button>"""
new_topbar_btn = """<button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()" type="button" title="GATE Virtual Calculator (C)">🧮 <span class="hide-xs">Calc</span></button>
        <button class="btn btn-secondary btn-sm" onclick="openFormulaFlashcardsModal('${getMatchingFlashcardId(q)}')" type="button" title="Formula Flashcards (H)">📇 <span class="hide-xs">Flashcards</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleShortcutsModal()" type="button" title="Shortcuts (?)">⌨️</button>"""
if old_topbar_btn in code:
    code = code.replace(old_topbar_btn, new_topbar_btn, 1)

# 6. In buildPracticeQHTML: add Hint button and hint box
old_qhtml_header = """      <div class="question-number">Question ${state.currentQuestion + 1} of ${total}</div>
      <div class="question-text">${formatQuestionContent(q.question)}</div>"""
new_qhtml_header = """      <div style="display:flex;align-items:center;justify-content:space-between;margin:6px 0 10px 0;">
        <div class="question-number" style="margin:0">Question ${state.currentQuestion + 1} of ${total}</div>
        <button class="btn btn-secondary btn-sm" onclick="togglePracticeHint()" type="button" title="View Concept Hint & Formula Flashcards (H)" style="border-color:var(--accent);color:var(--accent);font-weight:600;display:inline-flex;align-items:center;gap:5px;font-size:12px;padding:3px 10px">
          💡 <span>Hint / Formula</span>
        </button>
      </div>
      <div class="practice-hint-box" id="practice-hint-box" style="display:none">
        ${buildQuestionHintHTML(q)}
      </div>
      <div class="question-text">${formatQuestionContent(q.question)}</div>"""
if old_qhtml_header in code:
    code = code.replace(old_qhtml_header, new_qhtml_header, 1)

old_qactions = """    <div class="question-actions" id="q-actions">
      <button class="btn btn-primary" onclick="submitPracticeAnswer()">Submit Answer</button>
      <button class="btn btn-secondary" onclick="skipQuestion()">Skip →</button>"""
new_qactions = """    <div class="question-actions" id="q-actions">
      <button class="btn btn-primary" onclick="submitPracticeAnswer()">Submit Answer</button>
      <button class="btn btn-secondary" onclick="togglePracticeHint()" type="button">💡 Hint / Formula</button>
      <button class="btn btn-secondary" onclick="skipQuestion()">Skip →</button>"""
if old_qactions in code:
    code = code.replace(old_qactions, new_qactions, 1)

# 7. Add Flashcard Data, SRS Engine, and UI Methods
flashcard_engine_code = r'''
// ─── 8. FORMULA FLASHCARDS (SPACED REPETITION) ENGINE ─────────────────────────
const FORMULA_FLASHCARDS = [
  {
    id: 'card-masters-theorem',
    subject: 'Algorithms',
    topic: 'Asymptotic Analysis & Recurrences',
    title: "Master's Theorem Recurrence Bounds",
    question: "Given recurrence $T(n) = a T(n/b) + \\Theta(n^k \\log^p n)$ with $a \\ge 1, b > 1, k \\ge 0$. What are the exact 3 cases and boundary conditions?",
    hintText: "Compare $\\log_b a$ with $k$ (the polynomial exponent of $f(n)$). If $k = \\log_b a$, check the logarithmic power $p$.",
    formulaHTML: `
      <div style="margin-bottom:8px"><strong>Standard Form:</strong> $T(n) = a T(n/b) + \\Theta(n^k \\log^p n)$</div>
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>Case 1 ($k < \\log_b a$):</strong> $T(n) = \\Theta(n^{\\log_b a})$ (Leaf/Tree-heavy)</div>
        <div><strong>Case 2 ($k = \\log_b a$):</strong>
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li>$p > -1 \\implies T(n) = \\Theta(n^{\\log_b a} \\log^{p+1} n)$</li>
            <li>$p = -1 \\implies T(n) = \\Theta(n^{\\log_b a} \\log \\log n)$</li>
            <li>$p < -1 \\implies T(n) = \\Theta(n^{\\log_b a})$</li>
          </ul>
        </div>
        <div><strong>Case 3 ($k > \\log_b a$):</strong> (Root-heavy, with regularity $a f(n/b) \\le c f(n)$ for $c < 1$):
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li>$p \\ge 0 \\implies T(n) = \\Theta(n^k \\log^p n)$</li>
            <li>$p < 0 \\implies T(n) = \\Theta(n^k)$</li>
          </ul>
        </div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Does NOT apply if $f(n)$ is non-polynomial or the ratio is non-polynomial (e.g. $T(n) = 2T(n/2) + n/\\log n$, use recursion tree $\\Theta(n \\log \\log n)$).</div>
    `,
    keywords: ['master', 'recurrence', 'divide and conquer', 'algorithm', 'asymptotic', 'complexity', 'o(n', 'theta(']
  },
  {
    id: 'card-graph-invariants',
    subject: 'Discrete Mathematics',
    topic: 'Graph Theory & Planarity',
    title: 'Graph Invariants & Planar Graph Formulas',
    question: "What are the core invariants for Planar Graphs, Handshaking Lemma, and Spanning Tree counts in $K_n$ and $K_{m,n}$?",
    hintText: "Use Euler's formula $V - E + R = 2$. For planar graphs with region degree $\\ge 3$, remember $3R \\le 2E \\implies E \\le 3V - 6$.",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. Handshaking Lemma:</strong> $\\sum_{v \\in V} \\deg(v) = 2|E|$. Total odd degree vertices is always <em>even</em>.</div>
        <div><strong>2. Euler's Planar Formula:</strong> For connected planar graph: $V - E + R = 2$. (For $k$ components: $V - E + R = 1 + k$).</div>
        <div><strong>3. Edge Bounds in Planar Graphs:</strong>
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li>Standard (region degree $\\ge 3$): $E \\le 3V - 6$ (and min degree $\\delta(G) \\le 5$)</li>
            <li>Triangle-Free / Bipartite (region degree $\\ge 4$): $E \\le 2V - 4$</li>
          </ul>
        </div>
        <div><strong>4. Spanning Trees (Cayley's Formula):</strong>
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li>Complete Graph $K_n$: $n^{n-2}$ spanning trees.</li>
            <li>Complete Bipartite $K_{m,n}$: $m^{n-1} \\cdot n^{m-1}$ spanning trees.</li>
          </ul>
        </div>
        <div><strong>5. Eulerian Conditions:</strong> Circuit $\\iff$ connected and <em>all</em> vertices have even degree. Path $\\iff$ connected and exactly 0 or 2 vertices have odd degree.</div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Kuratowski's Theorem: A graph is planar $\\iff$ it does NOT contain a subgraph homeomorphic to $K_5$ or $K_{3,3}$.</div>
    `,
    keywords: ['graph', 'planar', 'euler', 'spanning tree', 'degree', 'vertex', 'edge', 'bipartite', 'handshaking', 'chromatic']
  },
  {
    id: 'card-cpu-scheduling',
    subject: 'Operating Systems',
    topic: 'CPU Scheduling & Metrics',
    title: 'CPU Scheduling Metrics & Waiting Time Bounds',
    question: "What are the exact formulas for Turnaround Time, Waiting Time, Response Time, and Round Robin max waiting time bounds?",
    hintText: "Turnaround Time is total lifecycle: Completion - Arrival. Waiting Time is idle time: Turnaround - Burst.",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. Turnaround Time ($TAT$):</strong> $TAT = \\text{Completion Time (CT)} - \\text{Arrival Time (AT)}$</div>
        <div><strong>2. Waiting Time ($WT$):</strong> $WT = TAT - \\text{Burst Time (BT)}$</div>
        <div><strong>3. Response Time ($RT$):</strong> $RT = \\text{Time of First CPU Allotment} - AT$</div>
        <div><strong>4. Round Robin Bound:</strong> For $n$ active processes with time quantum $q$:
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li>Maximum wait time between turns for a process: $(n - 1) \\cdot q$</li>
            <li>If context switch overhead is $s$, effective quantum is $q + s$, CPU efficiency = $\\frac{q}{q + s}$</li>
          </ul>
        </div>
        <div><strong>5. Convoy Effect:</strong> Under FCFS, short processes get delayed behind a long CPU-burst process $\\implies$ high average waiting time.</div>
        <div><strong>6. Optimality:</strong> SJF (non-preemptive) & SRTF (preemptive) guarantee the theoretical <em>minimum average waiting time</em>.</div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> In Round Robin, if a process arrives at time $t$ while an executing process's quantum expires at time $t$, by convention the newly arrived process is added to the ready queue <em>before</em> the preempted process!</div>
    `,
    keywords: ['cpu', 'scheduling', 'turnaround', 'waiting time', 'burst', 'round robin', 'fcfs', 'sjf', 'srtf', 'gantt']
  },
  {
    id: 'card-subnetting-rules',
    subject: 'Computer Networks',
    topic: 'IPv4 Addressing & CIDR Subnetting',
    title: 'IPv4 CIDR Subnetting & Mask Calculations',
    question: "For an IPv4 CIDR prefix $/n$, what are the exact rules for total addresses, usable hosts, network ID, and broadcast address?",
    hintText: "With $n$ network bits, there are $32 - n$ host bits. Total IPs = $2^{32-n}$, subtract 2 for network & broadcast IDs.",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. Total Addresses:</strong> $2^{32 - n}$ addresses</div>
        <div><strong>2. Usable Host Addresses:</strong> $2^{32 - n} - 2$
          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">• Excluded: All-0s host ID (Network Address), All-1s host ID (Directed Broadcast)</div>
          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">• Exceptions: $/31$ (2 usable, RFC 3021 point-to-point) and $/32$ (single loopback host)</div>
        </div>
        <div><strong>3. Network Address:</strong> $\\text{IP Address} \\text{ BITWISE-AND } \\text{Subnet Mask}$</div>
        <div><strong>4. Directed Broadcast Address:</strong> $\\text{Network Address} \\text{ BITWISE-OR } (\\sim\\text{Subnet Mask})$</div>
        <div><strong>5. Subnetting from $/n$:</strong> Borrowing $k$ host bits creates $2^k$ subnets, each with $/ (n + k)$ mask and $2^{32 - n - k} - 2$ usable hosts.</div>
        <div><strong>6. Quick CIDR Host Table:</strong>
          <span style="font-family:monospace;font-size:12px">/24 $\\to$ 254 | /25 $\\to$ 126 | /26 $\\to$ 62 | /27 $\\to$ 30 | /28 $\\to$ 14 | /29 $\\to$ 6 | /30 $\\to$ 2</span>
        </div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Limited Broadcast address is $255.255.255.255$ (never routed across routers). Directed broadcast is specific to the subnet (host bits all 1).</div>
    `,
    keywords: ['subnet', 'cidr', 'ipv4', 'mask', 'broadcast', 'host', 'network address', 'ip address', 'classful', 'routing']
  },
  {
    id: 'card-emat-vm',
    subject: 'Operating Systems',
    topic: 'Virtual Memory & Paging',
    title: 'Effective Memory Access Time (EMAT)',
    question: "What is the formula for EMAT with a TLB and $k$-level page tables, and how is it modified when accounting for page fault rate $p$?",
    hintText: "On a TLB hit, time is $t_{TLB} + t_{mem}$. On a TLB miss with $k$ levels, you access memory $k$ times for page tables + 1 time for actual data.",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. Basic TLB Paging EMAT ($h$ = hit ratio):</strong>
          $$\\text{EMAT} = h \\cdot (t_{\\text{TLB}} + t_{\\text{mem}}) + (1 - h) \\cdot (t_{\\text{TLB}} + (k + 1) \\cdot t_{\\text{mem}})$$
          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">($k = 1$ for single-level paging $\\implies t_{\\text{TLB}} + 2 \\cdot t_{\\text{mem}}$ on miss)</div>
        </div>
        <div><strong>2. EMAT with Page Faults ($p$ = page fault probability):</strong>
          $$\\text{EMAT} = (1 - p) \\cdot \\text{EMAT}_{\\text{no-fault}} + p \\cdot \\text{Page Fault Service Time (PFST)}$$
        </div>
        <div><strong>3. Page Table Size:</strong>
          $$\\text{Page Table Size} = \\text{Number of Entries} \\times \\text{Page Table Entry (PTE) Size}$$
          $$\\text{Number of Entries} = \\frac{\\text{Virtual Address Space (VAS)}}{\\text{Page Size}}$$
        </div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Check whether TLB search is performed concurrently with cache or sequentially before memory lookup. In inverted page tables, entry count equals the number of physical frames, not virtual pages!</div>
    `,
    keywords: ['emat', 'tlb', 'paging', 'virtual memory', 'page fault', 'pte', 'frame', 'page table']
  },
  {
    id: 'card-amat-cache',
    subject: 'Computer Organization & Architecture',
    topic: 'Memory Hierarchy & Cache Mapping',
    title: 'Average Memory Access Time (AMAT) & Cache Address Splits',
    question: "What is AMAT and how are Tag, Set-Index, and Word-Offset bit widths calculated for Direct and $k$-way associative caches?",
    hintText: "AMAT = Hit Time + Miss Rate $\\times$ Miss Penalty. For address bits, start from Block Offset = $\\log_2(\\text{Block Size})$.",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. AMAT Formula:</strong>
          $$\\text{AMAT} = t_{\\text{hit}} + \\text{Miss Rate} \\times \\text{Miss Penalty}$$
          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">With 2 levels (L1, L2): $\\text{AMAT} = t_{L1} + m_{L1} \\times (t_{L2} + m_{L2} \\times t_{\\text{main}})$</div>
        </div>
        <div><strong>2. Address Bit Fields (Total $n$ bits for byte-addressable):</strong>
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li>$\\text{Block/Byte Offset (BO)} = \\log_2(\\text{Block Size in bytes})$</li>
            <li>$\\text{Set Index Bits (SI)} = \\log_2(\\text{Number of Sets})$</li>
            <li>$\\text{Tag Bits} = n - \\text{Set Index} - \\text{Block Offset}$</li>
          </ul>
        </div>
        <div><strong>3. Set Calculations by Mapping:</strong>
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li>Direct Mapped: $\\text{Sets} = \\text{Total Lines} \\implies \\text{SI} = \\log_2(\\text{Lines})$</li>
            <li>$k$-way Associative: $\\text{Sets} = \\frac{\\text{Total Lines}}{k} \\implies \\text{SI} = \\log_2(\\text{Sets})$</li>
            <li>Fully Associative: $\\text{Sets} = 1 \\implies \\text{SI} = 0$, all remaining bits are Tag!</li>
          </ul>
        </div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Total cache memory size includes Tag directory overhead: $\\text{Tag Directory} = \\text{Lines} \\times (\\text{Tag bits} + \\text{Valid bit} + \\text{Dirty bit})$.</div>
    `,
    keywords: ['cache', 'amat', 'tag', 'set index', 'block offset', 'associative', 'hit rate', 'miss rate', 'memory hierarchy']
  },
  {
    id: 'card-pipeline-speedup',
    subject: 'Computer Organization & Architecture',
    topic: 'Instruction Pipelining',
    title: 'Pipeline Speedup, Stalls & CPI Formulas',
    question: "What is the speedup of a $k$-stage pipeline for $n$ instructions with stall cycles, and what is its asymptotic limit?",
    hintText: "Unpipelined time is $n \\cdot k \\cdot \\tau$. Pipelined time is $(k + n - 1 + \\text{Stalls}) \\cdot \\tau$. Take ratio as $n \\to \\infty$.",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. Execution Times (clock cycle $\\tau$):</strong>
          $$\\text{Non-pipelined: } T_n = n \\cdot k \\cdot \\tau$$
          $$\\text{Pipelined: } T_p = (k + n - 1 + \\text{Stalls}) \\cdot \\tau$$
        </div>
        <div><strong>2. Speedup ($S$):</strong>
          $$S = \\frac{T_n}{T_p} = \\frac{n \\cdot k}{k + n - 1 + \\text{Stalls}} \\xrightarrow{n \\to \\infty} \\frac{k}{1 + \\text{Stalls per instruction}}$$
        </div>
        <div><strong>3. Pipeline CPI & Throughput:</strong>
          $$\\text{CPI} = 1 + \\frac{\\text{Total Stall Cycles}}{n}$$
          $$\\text{Throughput} = \\frac{n}{(k + n - 1 + \\text{Stalls}) \\cdot \\tau} \\xrightarrow{n \\to \\infty} \\frac{1}{\\text{CPI} \\cdot \\tau}$$
        </div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Stage cycle time $\\tau$ is determined by the slowest stage plus buffer delay: $\\tau = \\max(\\text{stage delays}) + \\text{register delay}$.</div>
    `,
    keywords: ['pipeline', 'speedup', 'cpi', 'stall', 'hazard', 'clock cycle', 'throughput', 'instruction']
  },
  {
    id: 'card-dbms-normal-forms',
    subject: 'Databases (DBMS)',
    topic: 'Normalization & Functional Dependencies',
    title: 'DBMS Normal Forms Hierarchy & Lossless Join',
    question: "What are the exact tests for 1NF, 2NF, 3NF, BCNF, and the mathematical test for Lossless Decomposition?",
    hintText: "For 3NF: $X \\to Y \\implies X$ is Superkey OR $Y$ is Prime. For BCNF: $X$ MUST be a Superkey. For lossless join: $R_1 \\cap R_2$ must be superkey of $R_1$ or $R_2$.",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. Normal Form Requirements for non-trivial $X \\to Y$:</strong>
          <ul style="margin:4px 0 4px 18px;padding:0">
            <li><strong>1NF:</strong> All attribute values are atomic (no composite/multivalued attributes).</li>
            <li><strong>2NF:</strong> 1NF + No partial dependency (no proper subset of any candidate key determines a non-prime attribute).</li>
            <li><strong>3NF:</strong> 2NF + For every $X \\to Y$, either $X$ is a superkey OR $Y$ is a prime attribute.</li>
            <li><strong>BCNF:</strong> For every $X \\to Y$, $X$ <em>must</em> be a superkey.</li>
          </ul>
        </div>
        <div><strong>2. Lossless-Join Decomposition Test:</strong>
          $$R_1 \\bowtie R_2 = R \\iff (R_1 \\cap R_2 \\to R_1) \\in F^+ \\quad\\lor\\quad (R_1 \\cap R_2 \\to R_2) \\in F^+$$
          <div style="font-size:12px;color:var(--text-muted);margin-left:14px">(The common attribute must be a candidate key of at least one relation)</div>
        </div>
        <div><strong>3. Preservation Guarantee:</strong> 3NF always guarantees both <em>Lossless Join</em> and <em>Dependency Preservation</em>. BCNF guarantees Lossless Join, but dependency preservation is <strong>not</strong> always possible.</div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Every binary relation with functional dependencies is always in BCNF and lossless! Prime attributes can be part of ANY candidate key.</div>
    `,
    keywords: ['normal form', '2nf', '3nf', 'bcnf', 'functional dependency', 'lossless', 'dependency preservation', 'superkey', 'candidate key']
  },
  {
    id: 'card-toc-closure',
    subject: 'Theory of Computation',
    topic: 'Chomsky Hierarchy & Closure Properties',
    title: 'Chomsky Hierarchy & Language Closure Properties',
    question: "Which language families in the Chomsky hierarchy are closed under Union, Intersection, Complement, and Concatenation?",
    hintText: "Regular is closed under EVERYTHING. CFL is NOT closed under Intersection or Complement (intersection of 2 CFLs can be non-CFL).",
    formulaHTML: `
      <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:6px;font-size:13px;line-height:1.7;margin-bottom:8px">
        <div><strong>1. Chomsky Hierarchy Containment:</strong>
          $$\\text{Regular (Type 3)} \\subset \\text{DCFL} \\subset \\text{CFL (Type 2)} \\subset \\text{CSL (Type 1)} \\subset \\text{Recursive} \\subset \\text{RE (Type 0)}$$
        </div>
        <div><strong>2. Major Closure Properties Matrix:</strong>
          <table style="width:100%;font-size:12px;border-collapse:collapse;margin-top:6px;text-align:center">
            <tr style="border-bottom:1px solid var(--border);color:var(--accent)">
              <th style="text-align:left">Language Class</th><th>Union</th><th>Intersection</th><th>Complement</th><th>Kleene *</th>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
              <td style="text-align:left;font-weight:600">Regular</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
              <td style="text-align:left;font-weight:600">DCFL</td><td>❌</td><td>❌</td><td>✅</td><td>❌</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
              <td style="text-align:left;font-weight:600">CFL</td><td>✅</td><td>❌</td><td>❌</td><td>✅</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
              <td style="text-align:left;font-weight:600">Recursive</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td>
            </tr>
            <tr>
              <td style="text-align:left;font-weight:600">RE</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td>
            </tr>
          </table>
        </div>
      </div>
      <div style="font-size:12px;color:#f87171">⚠️ <strong>GATE Trap:</strong> Intersection of a CFL with a Regular language is <em>always a CFL</em> ($L_{\\text{CFL}} \\cap L_{\\text{REG}} = \\text{CFL}$).</div>
    `,
    keywords: ['chomsky', 'closure', 'regular', 'cfl', 'dcfl', 'context-free', 'decidable', 'recursive', 'turing', 'pumping lemma']
  }
];

function getMatchingFlashcard(q) {
  if (!q) return FORMULA_FLASHCARDS[0];
  const qText = ((q.question || '') + ' ' + (q.topic || '') + ' ' + (q.subject || '')).toLowerCase();
  for (const card of FORMULA_FLASHCARDS) {
    if (card.keywords && card.keywords.some(k => qText.includes(k.toLowerCase()))) {
      return card;
    }
  }
  const subMatch = FORMULA_FLASHCARDS.find(c => c.subject.toLowerCase() === (q.subject || '').toLowerCase());
  if (subMatch) return subMatch;
  return FORMULA_FLASHCARDS[0];
}

function getMatchingFlashcardId(q) {
  return getMatchingFlashcard(q).id;
}

function buildQuestionHintHTML(q) {
  const card = getMatchingFlashcard(q);
  return `
    <div class="practice-hint-header">
      <div class="practice-hint-title">💡 <span>Concept Hint & Relevant Formula</span></div>
      <button class="palette-close-btn" onclick="togglePracticeHint(false)" type="button" style="font-size:12px">✕</button>
    </div>
    <div class="practice-hint-body">
      <div style="margin-bottom:6px;font-size:12.5px;color:var(--text-muted)">
        <span class="chip" style="font-size:11px">${card.subject}</span>
        <strong>${card.title}</strong>
      </div>
      <div style="margin-bottom:8px">${card.hintText}</div>
      <div style="background:var(--bg-card);border:1px solid rgba(108,99,255,0.25);border-radius:6px;padding:8px 12px;font-size:12.5px">
        ${card.formulaHTML}
      </div>
    </div>
    <div class="practice-hint-actions">
      <button class="btn btn-primary btn-sm" onclick="openFormulaFlashcardsModal('${card.id}')" type="button">📇 Open Spaced Repetition Flashcard</button>
      <button class="btn btn-secondary btn-sm" onclick="togglePracticeHint(false)" type="button">Got it 👍</button>
    </div>
  `;
}

function togglePracticeHint(forceState) {
  const box = document.getElementById('practice-hint-box');
  if (!box) return;
  const isHidden = box.style.display === 'none' || !box.style.display;
  const show = forceState !== undefined ? forceState : isHidden;
  box.style.display = show ? 'block' : 'none';
  if (show) {
    renderMath(box);
  }
}

let flashcardModalOpen = false;
let activeDeck = [...FORMULA_FLASHCARDS];
let currentCardIndex = 0;
let isCardFlipped = false;

function toggleFormulaFlashcards(isOpen, targetCardId) {
  flashcardModalOpen = isOpen !== undefined ? isOpen : !flashcardModalOpen;
  const modal = document.getElementById('flashcard-modal-backdrop');
  if (!modal) return;
  modal.classList.toggle('active', flashcardModalOpen);

  if (flashcardModalOpen) {
    filterFlashcardDeck();
    if (targetCardId) {
      const idx = activeDeck.findIndex(c => c.id === targetCardId);
      if (idx !== -1) currentCardIndex = idx;
    }
    isCardFlipped = false;
    renderActiveFlashcard();
  }
}

function openFormulaFlashcardsModal(targetCardId) {
  toggleFormulaFlashcards(true, targetCardId);
}

function renderActiveFlashcard() {
  if (!activeDeck.length) {
    activeDeck = [...FORMULA_FLASHCARDS];
    currentCardIndex = 0;
  }
  if (currentCardIndex >= activeDeck.length) currentCardIndex = 0;
  if (currentCardIndex < 0) currentCardIndex = activeDeck.length - 1;

  const card = activeDeck[currentCardIndex];
  const srs = state.flashcardStats?.[card.id] || { status: 'due', reps: 0 };
  const srsLabel = srs.status === 'mastered' ? '🟢 Mastered' : srs.status === 'learning' ? '🟡 In Progress' : '🔴 Due for Review';

  // Front Face
  const frontEl = document.getElementById('fc-face-front');
  if (frontEl) {
    frontEl.innerHTML = `
      <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
          <span class="flashcard-subject-chip">${card.subject}</span>
          <span class="flashcard-srs-status-tag ${srs.status}">${srsLabel}</span>
        </div>
        <div class="flashcard-concept-title">${card.title}</div>
        <div class="flashcard-prompt-text">${card.question}</div>
      </div>
      <div class="flashcard-flip-prompt">
        <span>🔄 Click card or press <strong>Space</strong> to reveal formula</span>
        <span style="font-size:11px;color:var(--text-muted)">Repetitions: ${srs.reps || 0}</span>
      </div>
    `;
  }

  // Back Face
  const backEl = document.getElementById('fc-face-back');
  if (backEl) {
    backEl.innerHTML = `
      <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
          <span class="flashcard-subject-chip" style="background:rgba(34,197,94,0.15);color:#22c55e">${card.subject} • Solution</span>
          <span class="flashcard-srs-status-tag ${srs.status}">${srsLabel}</span>
        </div>
        <div class="flashcard-concept-title" style="color:#22c55e">${card.title}</div>
        <div class="flashcard-formula-content">${card.formulaHTML}</div>
      </div>
      <div class="flashcard-srs-controls">
        <span style="font-size:12px;font-weight:600;color:var(--text-muted)">Rate recall:</span>
        <div class="flashcard-srs-buttons">
          <button class="srs-btn srs-btn-again" onclick="rateFlashcard('again')" title="Review soon (Key 1)">🔴 Hard (1)</button>
          <button class="srs-btn srs-btn-good" onclick="rateFlashcard('good')" title="Good recall (Key 2)">🟡 Good (2)</button>
          <button class="srs-btn srs-btn-mastered" onclick="rateFlashcard('mastered')" title="Mastered (Key 3)">🟢 Mastered (3)</button>
        </div>
      </div>
    `;
  }

  // Counter
  const badge = document.getElementById('fc-counter-badge');
  if (badge) {
    badge.textContent = `Card ${currentCardIndex + 1} of ${activeDeck.length}`;
  }

  // Ensure card flip state is synced
  const inner = document.getElementById('active-flashcard-inner');
  if (inner) inner.classList.toggle('is-flipped', isCardFlipped);

  // Render KaTeX in the modal
  const modal = document.getElementById('flashcard-modal-card');
  if (modal) renderMath(modal);
}

function flipActiveFlashcard() {
  isCardFlipped = !isCardFlipped;
  const inner = document.getElementById('active-flashcard-inner');
  if (inner) inner.classList.toggle('is-flipped', isCardFlipped);
}

function navFlashcard(delta) {
  isCardFlipped = false;
  const inner = document.getElementById('active-flashcard-inner');
  if (inner) inner.classList.remove('is-flipped');
  currentCardIndex += delta;
  renderActiveFlashcard();
}

function shuffleFlashcardDeck() {
  for (let i = activeDeck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [activeDeck[i], activeDeck[j]] = [activeDeck[j], activeDeck[i]];
  }
  currentCardIndex = 0;
  isCardFlipped = false;
  renderActiveFlashcard();
  showToast('Flashcard deck shuffled! 🔀', 'info');
}

function rateFlashcard(rating) {
  if (!activeDeck[currentCardIndex]) return;
  const card = activeDeck[currentCardIndex];
  if (!state.flashcardStats) state.flashcardStats = {};
  const current = state.flashcardStats[card.id] || { reps: 0 };

  if (rating === 'again') {
    state.flashcardStats[card.id] = { status: 'learning', reps: 0, lastReviewed: Date.now() };
    showToast('Marked for review soon! ⏳', 'warning');
  } else if (rating === 'good') {
    state.flashcardStats[card.id] = { status: 'learning', reps: (current.reps || 0) + 1, lastReviewed: Date.now() };
    showToast('Good job! Progress saved. 👍', 'info');
  } else if (rating === 'mastered') {
    state.flashcardStats[card.id] = { status: 'mastered', reps: (current.reps || 0) + 2, lastReviewed: Date.now() };
    showToast('Mastered formula! 🟢', 'success');
  }

  try {
    localStorage.setItem('gate_formula_flashcards_srs', JSON.stringify(state.flashcardStats));
  } catch(e) {}

  setTimeout(() => {
    navFlashcard(1);
  }, 250);
}

function filterFlashcardDeck() {
  const subFilter = document.getElementById('fc-subject-filter')?.value || 'all';
  const srsFilter = document.getElementById('fc-srs-filter')?.value || 'all';

  let list = [...FORMULA_FLASHCARDS];
  if (subFilter !== 'all') {
    list = list.filter(c => c.subject === subFilter);
  }
  if (srsFilter !== 'all') {
    list = list.filter(c => {
      const s = state.flashcardStats?.[c.id]?.status || 'due';
      return s === srsFilter;
    });
  }

  activeDeck = list.length ? list : [...FORMULA_FLASHCARDS];
  currentCardIndex = 0;
  isCardFlipped = false;
  renderActiveFlashcard();
}
'''

if 'FORMULA_FLASHCARDS' not in code:
    # Insert right before setupKeyboardShortcuts
    idx_sc = code.find('function setupKeyboardShortcuts()')
    assert idx_sc != -1, "setupKeyboardShortcuts not found"
    code = code[:idx_sc] + flashcard_engine_code + "\n\n" + code[idx_sc:]

# 8. Update keyboard shortcuts in setupKeyboardShortcuts
old_esc_block = """    if (e.key === 'Escape') {
      if (calcState.isOpen) { toggleGateCalc(false); return; }"""
new_esc_block = """    if (e.key === 'Escape') {
      if (flashcardModalOpen) { toggleFormulaFlashcards(false); return; }
      if (calcState.isOpen) { toggleGateCalc(false); return; }"""
if old_esc_block in code:
    code = code.replace(old_esc_block, new_esc_block, 1)

# Add flashcard modal keys (Space, ArrowLeft, ArrowRight, 1, 2, 3) and H key
old_p_key = """    if (e.key === 'p' || e.key === 'P') {
      const palette = document.getElementById('test-sidebar');
      if (palette) {
        e.preventDefault();
        toggleTestPalette();
        return;
      }
    }"""
new_p_key = """    if (flashcardModalOpen) {
      if (e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        flipActiveFlashcard();
        return;
      }
      if (e.key === 'ArrowRight') {
        e.preventDefault();
        navFlashcard(1);
        return;
      }
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        navFlashcard(-1);
        return;
      }
      if (e.key === '1') {
        e.preventDefault();
        rateFlashcard('again');
        return;
      }
      if (e.key === '2') {
        e.preventDefault();
        rateFlashcard('good');
        return;
      }
      if (e.key === '3') {
        e.preventDefault();
        rateFlashcard('mastered');
        return;
      }
    }

    if (e.key === 'h' || e.key === 'H') {
      e.preventDefault();
      if (document.getElementById('practice-hint-box')) {
        togglePracticeHint();
      } else {
        openFormulaFlashcardsModal();
      }
      return;
    }

    if (e.key === 'p' || e.key === 'P') {
      const palette = document.getElementById('test-sidebar');
      if (palette) {
        e.preventDefault();
        toggleTestPalette();
        return;
      }
    }"""
if old_p_key in code:
    code = code.replace(old_p_key, new_p_key, 1)

# 9. Expose on Object.assign(window, {...})
exports_to_add = """  // Formula Flashcards (Spaced Repetition)
  FORMULA_FLASHCARDS,
  getMatchingFlashcard,
  getMatchingFlashcardId,
  buildQuestionHintHTML,
  togglePracticeHint,
  toggleFormulaFlashcards,
  openFormulaFlashcardsModal,
  renderActiveFlashcard,
  flipActiveFlashcard,
  navFlashcard,
  shuffleFlashcardDeck,
  rateFlashcard,
  filterFlashcardDeck,
"""
if 'FORMULA_FLASHCARDS' not in code[code.rfind('Object.assign(window'):]:
    code = code.replace(
        "  // Advanced Improvements & Simulators",
        exports_to_add + "\n  // Advanced Improvements & Simulators"
    )

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully injected Formula Flashcards & Practice Hint system into app.js!")
