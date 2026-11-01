# -*- coding: utf-8 -*-
"""
Script to fix Practice Papers difficulty sorting and filtering in app.js
"""

import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update PRACTICE_PAPERS array
# Replace the PRACTICE_PAPERS definition with fully annotated papers
papers_block = """const PRACTICE_PAPERS = [
  { id:'paper-gate-2025-s1', name:'Official GATE CSE 2025 (Set 1) Paper', type:'full', difficulty:'medium', rating:5.5, cutoff:'28-30', air100:'72-76', questions:65, marks:100, desc:'Complete official 65-question GATE 2025 Set 1 paper with full solutions, paginated at 20 questions per page.' },
  { id:'paper-gate-2025-s2', name:'Official GATE CSE 2025 (Set 2) Paper', type:'full', difficulty:'hard', rating:7.0, cutoff:'24-26', air100:'64-68', questions:65, marks:100, desc:'Complete official 65-question GATE 2025 Set 2 paper with full solutions, paginated at 20 questions per page.' },
  { id:'paper-cat1-set1', mockId:'mock-cat1-set1', name:'GATE CSE Practice Paper (Cat 1 — Set 1)', type:'full', difficulty:'easy', rating:3.5, cutoff:'34-36', air100:'78-82', questions:65, marks:100, desc:'Category 1 Set 1: High-weightage topic-focused mock paper with step-by-step solutions (Rating: 3.5/10).' },
  { id:'paper-cat1-set2', mockId:'mock-cat1-set2', name:'GATE CSE Practice Paper (Cat 1 — Set 2)', type:'full', difficulty:'easy', rating:3.5, cutoff:'34-36', air100:'78-82', questions:65, marks:100, desc:'Category 1 Set 2: Foundational topic-focused paper covering formulas and definitions (Rating: 3.5/10).' },
  { id:'paper-cat1-set3', mockId:'mock-cat1-set3', name:'GATE CSE Practice Paper (Cat 1 — Set 3)', type:'full', difficulty:'medium', rating:4.5, cutoff:'30-32', air100:'74-78', questions:65, marks:100, desc:'Category 1 Set 3: MSQ-intensive practice set with 25+ conceptual multi-select questions (Rating: 4.5/10).' },
  { id:'paper-cat1-set4', mockId:'mock-cat1-set4', name:'GATE CSE Practice Paper (Cat 1 — Set 4)', type:'full', difficulty:'medium', rating:4.0, cutoff:'32-34', air100:'76-80', questions:65, marks:100, desc:'Category 1 Set 4: Topic-focused paper covering Algorithms, OS, DBMS, Networks, and COA (Rating: 4/10).' },
  { id:'paper-cat1-set5', mockId:'mock-cat1-set5', name:'GATE CSE Practice Paper (Cat 1 — Set 5)', type:'full', difficulty:'medium', rating:4.0, cutoff:'32-34', air100:'76-80', questions:65, marks:100, desc:'Category 1 Set 5: Comprehensive mock paper testing C recursion, K-maps, cache, and trees (Rating: 4/10).' },
  { id:'paper-cat2-set1', mockId:'mock-cat2-set1', name:'GATE CSE Practice Paper (Cat 2 — Set 1)', type:'full', difficulty:'medium', rating:4.0, cutoff:'32-34', air100:'76-80', questions:65, marks:100, desc:'Category 2 Set 1: Core CS & standard GATE pattern simulation paper (Rating: 4/10).' },
  { id:'paper-cat2-set2', mockId:'mock-cat2-set2', name:'GATE CSE Practice Paper (Cat 2 — Set 2)', type:'full', difficulty:'medium', rating:4.0, cutoff:'32-34', air100:'76-80', questions:65, marks:100, desc:'Category 2 Set 2: Full-length core CS simulation paper with multi-choice and numerical questions (Rating: 4/10).' },
  { id:'paper-cat2-set3', mockId:'mock-cat2-set3', name:'GATE CSE Practice Paper (Cat 2 — Set 3)', type:'full', difficulty:'medium', rating:5.0, cutoff:'30-32', air100:'73-77', questions:65, marks:100, desc:'Category 2 Set 3: Balanced tripartite mock paper with 22 Easy, 22 Medium, and 21 Hard questions (Rating: 5/10).' },
  { id:'paper-cat2-set4', mockId:'mock-cat2-set4', name:'GATE CSE Practice Paper (Cat 2 — Set 4)', type:'full', difficulty:'medium', rating:4.5, cutoff:'31-33', air100:'74-78', questions:65, marks:100, desc:'Category 2 Set 4: Full-syllabus simulation paper testing comprehensive problem-solving (Rating: 4.5/10).' },
  { id:'paper-cat2-set5', mockId:'mock-cat2-set5', name:'GATE CSE Practice Paper (Cat 2 — Set 5)', type:'full', difficulty:'hard', rating:5.5, cutoff:'28-30', air100:'70-74', questions:65, marks:100, desc:'Category 2 Set 5: Advanced mock paper with 25 rank-boosting numerical and conceptual questions (Rating: 5.5/10).' },

  // ─── 20 FULL-LENGTH GATE CS PRACTICE PAPERS ───────────────────────────────
  { id:'paper-flm-01', mockId:'mock-flm-01', name:'GATE CS Full Mock Exam #01 (Standard GATE — Rating: 4.5/10)', difficulty:'medium', rating:4.5, cutoff:'31-33', air100:'74-78', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #01 [Standard GATE | Rating: 4.5/10 | Est. Cutoff: 31-33M]: Foundational-to-standard baseline paper with clean arithmetic bounds, classic cache and pipelining parameters, and standard scoring problems.' },
  { id:'paper-flm-02', mockId:'mock-flm-02', name:'GATE CS Full Mock Exam #02 (Standard GATE — Rating: 5.0/10)', difficulty:'medium', rating:5.0, cutoff:'30-32', air100:'73-77', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #02 [Standard GATE | Rating: 5.0/10 | Est. Cutoff: 30-32M]: Standard GATE difficulty featuring Peirce’s law, modulo 13 exponentiation, 4-element derangements, and 10-vertex planar graph faces.' },
  { id:'paper-flm-03', mockId:'mock-flm-03', name:'GATE CS Full Mock Exam #03 (Standard GATE — Rating: 5.5/10)', difficulty:'medium', rating:5.5, cutoff:'29-31', air100:'72-76', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #03 [Standard GATE | Rating: 5.5/10 | Est. Cutoff: 29-31M]: Standard GATE paper testing 5-iteration fork() trees (31 children), modulo 17 arithmetic, and 4-way set-associative cache tags.' },
  { id:'paper-flm-04', mockId:'mock-flm-04', name:'GATE CS Full Mock Exam #04 (Standard GATE — Rating: 5.4/10)', difficulty:'medium', rating:5.4, cutoff:'29-31', air100:'72-76', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #04 [Standard GATE | Rating: 5.4/10 | Est. Cutoff: 29-31M]: Standard GATE simulation covering self-dual Boolean functions (256), modulo 19 arithmetic, and sliding-window DFA state construction.' },
  { id:'paper-flm-05', mockId:'mock-flm-05', name:'GATE CS Full Mock Exam #05 (Standard GATE — Rating: 5.2/10)', difficulty:'medium', rating:5.2, cutoff:'30-32', air100:'73-77', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #05 [Standard GATE | Rating: 5.2/10 | Est. Cutoff: 30-32M]: Standard GATE paper testing modulo 23 modular arithmetic, 3-ary tree leaf invariants (47 leaves), and 4-to-1 MUX Shannon expansions.' },
  { id:'paper-flm-06', mockId:'mock-flm-06', name:'GATE CS Full Mock Exam #06 (Standard GATE — Rating: 5.8/10)', difficulty:'medium', rating:5.8, cutoff:'28-30', air100:'71-75', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #06 [Standard GATE | Rating: 5.8/10 | Est. Cutoff: 28-30M]: Standard-Plus GATE paper testing modulo 29 exponentiation, 18-vertex planar graphs, cyclic K-maps, and cascaded counter frequency division.' },
  { id:'paper-flm-07', mockId:'mock-flm-07', name:'GATE CS Full Mock Exam #07 (Standard GATE — Rating: 5.6/10)', difficulty:'medium', rating:5.6, cutoff:'28-30', air100:'71-75', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #07 [Standard GATE | Rating: 5.6/10 | Est. Cutoff: 28-30M]: Standard-Plus paper with modulo 31 arithmetic, 20-vertex planar graph faces, 8-element surjections (5,796), and TCP congestion milestones.' },
  { id:'paper-flm-08', mockId:'mock-flm-08', name:'GATE CS Full Mock Exam #08 (Standard GATE — Rating: 6.0/10)', difficulty:'medium', rating:6.0, cutoff:'27-29', air100:'70-74', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #08 [Standard GATE | Rating: 6.0/10 | Est. Cutoff: 27-29M]: Upper-Standard GATE paper featuring modulo 37 exponentiation, 22-vertex planar graphs, 7-element derangements (1,855), and 280ms TCP windows.' },
  { id:'paper-flm-09', mockId:'mock-flm-09', name:'GATE CS Full Mock Exam #09 (Standard GATE — Rating: 6.1/10)', difficulty:'medium', rating:6.1, cutoff:'27-29', air100:'70-74', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #09 [Standard GATE | Rating: 6.1/10 | Est. Cutoff: 27-29M]: Upper-Standard paper with modulo 41 arithmetic, 24-vertex planar graphs, 5-variable directed FD cycles, and 32.0% sliding window utilization.' },
  { id:'paper-flm-10', mockId:'mock-flm-10', name:'GATE CS Full Mock Exam #10 (Standard GATE — Rating: 5.9/10)', difficulty:'medium', rating:5.9, cutoff:'28-30', air100:'71-75', tier:'Standard GATE', type:'full', questions:65, marks:100, desc:'Full Mock Paper #10 [Standard GATE | Rating: 5.9/10 | Est. Cutoff: 28-30M]: Balanced Standard GATE paper testing modulo 43 arithmetic, 26-vertex planar graphs, cyclic candidate keys, and 180 Cayley trace calculations.' },
  { id:'paper-flm-11', mockId:'mock-flm-11', name:'GATE CS Full Mock Exam #11 (Rank Booster — Rating: 6.8/10)', difficulty:'hard', rating:6.8, cutoff:'25-27', air100:'66-70', tier:'Rank Booster', type:'full', questions:65, marks:100, desc:'Full Mock Paper #11 [Rank Booster | Rating: 6.8/10 | Est. Cutoff: 25-27M]: Advanced Rank Booster featuring modulo 47 arithmetic, 28-vertex planar graphs, 141-leaf 5-ary trees, and 330ms TCP slow-start calculations.' },
  { id:'paper-flm-12', mockId:'mock-flm-12', name:'GATE CS Full Mock Exam #12 (Rank Booster — Rating: 7.5/10)', difficulty:'hard', rating:7.5, cutoff:'24-26', air100:'65-69', tier:'Rank Booster', type:'full', questions:65, marks:100, desc:'Full Mock Paper #12 [Rank Booster | Rating: 7.5/10 | Est. Cutoff: 24-26M]: Advanced Rank Booster testing modulo 53 exponentiation, 30-vertex planar graphs, 186-leaf 6-ary trees, and 420ms TCP congestion windows.' },
  { id:'paper-flm-13', mockId:'mock-flm-13', name:'GATE CS Full Mock Exam #13 (Rank Booster — Rating: 7.0/10)', difficulty:'hard', rating:7.0, cutoff:'25-27', air100:'66-70', tier:'Rank Booster', type:'full', questions:65, marks:100, desc:'Full Mock Paper #13 [Rank Booster | Rating: 7.0/10 | Est. Cutoff: 25-27M]: Advanced Rank Booster with modulo 59 arithmetic, 32-vertex planar graphs, 8-element BST postorder reconstructions, and 270 Cayley trace.' },
  { id:'paper-flm-14', mockId:'mock-flm-14', name:'GATE CS Full Mock Exam #14 (Rank Booster — Rating: 7.4/10)', difficulty:'hard', rating:7.4, cutoff:'24-26', air100:'65-69', tier:'Rank Booster', type:'full', questions:65, marks:100, desc:'Full Mock Paper #14 [Rank Booster | Rating: 7.4/10 | Est. Cutoff: 24-26M]: Advanced Rank Booster testing modulo 61 exponentiation, 34-vertex planar graphs, 8-fragment IPv4 splitting, 304 trace, and 25% DMA overhead.' },
  { id:'paper-flm-15', mockId:'mock-flm-15', name:'GATE CS Full Mock Exam #15 (High Difficulty — Rating: 8.0/10)', difficulty:'hard', rating:8.0, cutoff:'23-25', air100:'63-67', tier:'High Difficulty', type:'full', questions:65, marks:100, desc:'Full Mock Paper #15 [High Difficulty | Rating: 8.0/10 | Est. Cutoff: 23-25M]: High Difficulty Rank Booster with modulo 67 arithmetic, 36-vertex planar graphs, 173-leaf 5-ary trees, and 144,000-cost matrix chains.' },
  { id:'paper-flm-16', mockId:'mock-flm-16', name:'GATE CS Full Mock Exam #16 (High Difficulty — Rating: 7.8/10)', difficulty:'hard', rating:7.8, cutoff:'23-25', air100:'63-67', tier:'High Difficulty', type:'full', questions:65, marks:100, desc:'Full Mock Paper #16 [High Difficulty | Rating: 7.8/10 | Est. Cutoff: 23-25M]: High Difficulty paper testing modulo 71 exponentiation, 38-vertex planar graphs, 226-leaf 6-ary trees, 6th-symbol DFA (64 states), and 378 trace.' },
  { id:'paper-flm-17', mockId:'mock-flm-17', name:'GATE CS Full Mock Exam #17 (High Difficulty — Rating: 7.9/10)', difficulty:'hard', rating:7.9, cutoff:'23-25', air100:'63-67', tier:'High Difficulty', type:'full', questions:65, marks:100, desc:'Full Mock Paper #17 [High Difficulty | Rating: 7.9/10 | Est. Cutoff: 23-25M]: High Difficulty paper with modulo 73 exponentiation, 40-vertex planar graphs, 164ns paging EMAT, 418 trace, and 15% DMA cycle stealing.' },
  { id:'paper-flm-18', mockId:'mock-flm-18', name:'GATE CS Full Mock Exam #18 (Advanced Hard — Rating: 8.4/10)', difficulty:'hard', rating:8.4, cutoff:'22-24', air100:'62-66', tier:'Advanced Hard', type:'full', questions:65, marks:100, desc:'Full Mock Paper #18 [Advanced Hard | Rating: 8.4/10 | Est. Cutoff: 22-24M]: Advanced Hard paper featuring modulo 79 exponentiation, 42-vertex planar graphs, 148-leaf 4-ary trees, 6-bit Kernighan loop, and 460 trace.' },
  { id:'paper-flm-19', mockId:'mock-flm-19', name:'GATE CS Full Mock Exam #19 (Advanced Hard — Rating: 8.6/10)', difficulty:'hard', rating:8.6, cutoff:'21-23', air100:'60-65', tier:'Advanced Hard', type:'full', questions:65, marks:100, desc:'Full Mock Paper #19 [Advanced Hard | Rating: 8.6/10 | Est. Cutoff: 21-23M]: Advanced Hard paper with modulo 83 exponentiation, 44-vertex planar graphs, 205-leaf 5-ary trees, 504 IPv4 offset, and 504 Cayley trace.' },
  { id:'paper-flm-20', mockId:'mock-flm-20', name:'GATE CS Full Mock Exam #20 (Capstone Challenge — Rating: 9.2/10)', difficulty:'hard', rating:9.2, cutoff:'20-22', air100:'58-63', tier:'Capstone Challenge', type:'full', questions:65, marks:100, desc:'Full Mock Paper #20 [Capstone Challenge | Rating: 9.2/10 | Est. Cutoff: 20-22M]: Capstone Challenge mock exam featuring modulo 89 exponentiation, 46-vertex planar graphs, 266-leaf 6-ary trees, 6th-symbol DFA (64 states), and 550 trace.' },

  { id:'paper-gate-2021', name:'Official GATE CSE 2021 Paper', type:'full', difficulty:'medium', rating:5.5, cutoff:'28-30', air100:'72-76', year:2021, questions:88, marks:100, desc:'Authentic official GATE 2021 examination paper with verified answer keys, NAT ranges, and KaTeX solutions.' },
  { id:'paper-gate-2020', name:'Official GATE CSE 2020 Paper', type:'full', difficulty:'medium', rating:5.5, cutoff:'28-30', air100:'72-76', year:2020, questions:70, marks:100, desc:'Authentic official GATE 2020 paper with complete multiple-choice and numerical answer type questions.' },
  { id:'paper-gate-2019', name:'Official GATE CSE 2019 Paper', type:'full', difficulty:'medium', rating:5.0, cutoff:'29-31', air100:'73-77', year:2019, questions:66, marks:100, desc:'Authentic official GATE 2019 paper covering all 13 core subjects with detailed explanations.' },
  { id:'paper-gate-2018', name:'Official GATE CSE 2018 Paper', type:'full', difficulty:'medium', rating:5.0, cutoff:'29-31', air100:'73-77', year:2018, questions:72, marks:100, desc:'Official GATE CSE 2018 examination paper with verified keys and comprehensive solutions.' },
  { id:'paper-gate-2015', name:'Official GATE CSE 2015 Multi-Set Paper', type:'full', difficulty:'hard', rating:6.5, cutoff:'25-27', air100:'67-71', year:2015, questions:172, marks:100, desc:'Massive compilation of authentic questions across all 3 examination sessions of GATE 2015.' },
  { id:'paper-gate-2014', name:'Official GATE CSE 2014 Multi-Set Paper', type:'full', difficulty:'medium', rating:5.0, cutoff:'29-31', air100:'73-77', year:2014, questions:205, marks:100, desc:'Comprehensive authentic question archive across all 3 sets of the GATE 2014 examination.' },
  { id:'paper-gate-2011', name:'Official GATE CSE 2011 Full Paper', type:'full', difficulty:'easy', rating:4.0, cutoff:'32-34', air100:'76-80', year:2011, questions:65, marks:100, desc:'Authentic 65-question official GATE 2011 paper with verified answers and stepwise explanations.' },
  { id:'paper-gate-overflow-decade', name:'GATE Decade PYQ Paper (2014–2024)', type:'full', difficulty:'medium', rating:5.5, cutoff:'28-30', air100:'72-76', questions:65, marks:100, desc:'Curated 65-question compilation across the last decade of GATE CSE exams from Gate Overflow.' },
  { id:'paper-full-1', name:'GATE CSE Comprehensive Paper 1', type:'full', difficulty:'easy', rating:3.5, cutoff:'34-36', air100:'78-82', questions:65, marks:100, desc:'Complete 65-question mock paper following the official GATE pattern.' },
  { id:'paper-full-2', name:'GATE CSE Comprehensive Paper 2', type:'full', difficulty:'medium', rating:4.5, cutoff:'31-33', air100:'74-78', questions:65, marks:100, desc:'Balanced multi-subject paper covering all GATE CSE core concepts.' },
  { id:'paper-dsa', name:'Data Structures & Algorithms Paper', type:'subwise', difficulty:'medium', rating:5.0, subjects:['Data Structures','Algorithms','C Programming'], questions:50, marks:80, desc:'Deep dive into C Programming, Data Structures, Trees, Graphs, and DP.' },
  { id:'paper-systems', name:'Systems & Architecture Paper', type:'subwise', difficulty:'hard', rating:6.0, subjects:['Operating Systems','Computer Networks','Computer Organization'], questions:50, marks:80, desc:'Processes, memory, TCP/IP, routing, pipelining, and cache.' },
  { id:'paper-theory', name:'Theory of Computation & Compilers', type:'subwise', difficulty:'medium', rating:5.0, subjects:['Theory of Computation','Compiler Design'], questions:35, marks:60, desc:'Automata, regular expressions, grammars, parsers, and runtime.' },
  { id:'paper-maths', name:'Maths & General Aptitude Paper', type:'subwise', difficulty:'medium', rating:4.5, subjects:['Discrete Mathematics','Engineering Mathematics','Aptitude'], questions:45, marks:70, desc:'Graph theory, combinatorics, linear algebra, probability, and aptitude.' },
];"""

start_p = code.find('const PRACTICE_PAPERS = [')
end_p = code.find('];', start_p) + 2
code = code[:start_p] + papers_block + code[end_p:]
print("PRACTICE_PAPERS updated with explicit difficulty and ratings.")

# 2. Add state variables for paper/mock sorting and filtering
state_pattern = r'  mockTab:\s*\'full\',\s*mockLevelFilter:\s*\'all\','
state_replacement = """  mockTab:          'full',
  mockLevelFilter:  'all',
  mockSort:         'default',
  paperLevelFilter: 'all',
  paperSort:        'default',"""
code = re.sub(state_pattern, state_replacement, code)
print("state updated with sorting variables.")

# 3. Update the Mocks and Practice Papers rendering and sorting functions
old_section_start = '// ─── MOCK TESTS ──────────────────────────────────────────────────────────────'
old_section_end = 'function viewMockPaper(mockId, page=1){'

p_start = code.find(old_section_start)
p_end = code.find(old_section_end)

new_code_section = r'''// ─── MOCK TESTS ──────────────────────────────────────────────────────────────
function getPaperDifficulty(p) {
  if (p && p.difficulty) return p.difficulty;
  if (p && p.mockId) {
    const m = MOCK_TESTS.find(x => x.id === p.mockId);
    if (m && m.difficulty) return m.difficulty;
  }
  if (!p || !p.id) return 'medium';
  if (p.id.includes('easy') || p.id.includes('cat1-set1') || p.id.includes('cat1-set2') || p.id === 'paper-full-1' || p.id === 'paper-gate-2011') return 'easy';
  if (p.id.includes('hard') || p.id.includes('cat2-set5') || p.id === 'paper-gate-2015' || p.id === 'paper-gate-2025-s2' || p.id === 'paper-systems') return 'hard';
  if (p.id.startsWith('paper-flm-')) {
    const num = parseInt(p.id.replace('paper-flm-', ''), 10);
    return num >= 11 ? 'hard' : 'medium';
  }
  return 'medium';
}

function getPaperRating(p) {
  if (p && typeof p.rating === 'number') return p.rating;
  if (p && p.mockId) {
    const m = MOCK_TESTS.find(x => x.id === p.mockId);
    if (m && typeof m.rating === 'number') return m.rating;
  }
  const diff = getPaperDifficulty(p);
  return diff === 'easy' ? 3.5 : (diff === 'hard' ? 7.5 : 5.0);
}

function toggleCalibrationTable() {
  state.showCalibrationTable = !state.showCalibrationTable;
  const c = document.getElementById('mock-tab-content');
  if (c && state.mockTab === 'full') {
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');
    const filtered = getFilteredAndSortedMocks(fullMocks);
    c.innerHTML = `
      ${buildMockCalibrationGuide()}
      ${buildMockLevelFilterBar(fullMocks)}
      ${buildMockGrid(filtered)}
    `;
    renderMath(c);
  }
}

function buildMockCalibrationGuide() {
  const isExpanded = state.showCalibrationTable || false;
  return `
    <div class="calibration-guide-box">
      <div class="calibration-guide-header">
        <div>
          <div style="font-size:16px;font-weight:700;color:var(--text-primary);display:flex;align-items:center;gap:8px">
            <span>🎯</span> 20 Full-Length Mocks: Difficulty Calibration & Rating Guide
          </div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:2px">
            Official IISc/IIT GATE CS syllabus benchmark — Mocks #01–#10 (Medium) vs. Mocks #11–#20 (Hard)
          </div>
        </div>
        <button class="btn btn-secondary btn-sm" onclick="toggleCalibrationTable()" style="display:inline-flex;align-items:center;gap:6px" type="button">
          <span>${isExpanded ? '🔼 Hide Rating Table' : '📋 View 20-Mock Rating Matrix'}</span>
        </button>
      </div>

      <!-- Summary Tier Cards -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;margin-bottom:${isExpanded ? '16px' : '4px'}">
        <!-- Medium Tier Card -->
        <div class="calibration-tier-card medium">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span class="q-badge medium" style="font-size:12px;padding:4px 12px">🟡 MEDIUM MOCKS (#01 – #10)</span>
            <span style="font-size:12px;font-weight:700;color:var(--yellow)">Rating: 4.5 – 6.1 / 10</span>
          </div>
          <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.5;margin-bottom:8px">
            <strong>Standard GATE Pattern:</strong> Replicates typical IISc/IIT papers (e.g. GATE 2021, 2023, 2025 Set 1). Features clean arithmetic bounds, classical K-maps, standard planar graphs (\(V \le 26\)), and 2-level paging EMAT.
          </div>
          <div style="display:flex;gap:14px;font-size:12px;color:var(--text-primary);background:var(--bg-primary);padding:6px 10px;border-radius:6px;border:1px solid var(--border)">
            <span>🎯 <strong>Est. Cutoff:</strong> 28 – 32 Marks</span>
            <span>🏆 <strong>AIR &lt; 100:</strong> 72 – 78+ Marks</span>
          </div>
        </div>

        <!-- Hard Tier Card -->
        <div class="calibration-tier-card hard">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span class="q-badge hard" style="font-size:12px;padding:4px 12px">🔴 HARD MOCKS (#11 – #20)</span>
            <span style="font-size:12px;font-weight:700;color:var(--red)">Rating: 6.8 – 9.2 / 10</span>
          </div>
          <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.5;margin-bottom:8px">
            <strong>Rank Booster Challenges:</strong> High-intensity rank-booster exams. Modulo arithmetic up to \(\pmod{89}\), 64-state sliding-window DFAs, 141–266 leaf strict \(k\)-ary trees, 31-child fork trees, 8-fragment IPv4, and 144k matrix chains.
          </div>
          <div style="display:flex;gap:14px;font-size:12px;color:var(--text-primary);background:var(--bg-primary);padding:6px 10px;border-radius:6px;border:1px solid var(--border)">
            <span>🎯 <strong>Est. Cutoff:</strong> 20 – 26 Marks</span>
            <span>🏆 <strong>AIR &lt; 100:</strong> 60 – 68 Marks</span>
          </div>
        </div>
      </div>

      <!-- Expandable Table -->
      ${isExpanded ? `
        <div class="calibration-table-wrap">
          <table class="calibration-table">
            <thead>
              <tr>
                <th style="padding:10px 12px;white-space:nowrap">Mock Exam</th>
                <th style="padding:10px 12px;text-align:center">Difficulty Tier</th>
                <th style="padding:10px 12px;text-align:center">Rating</th>
                <th style="padding:10px 12px;text-align:center">Est. Cutoff</th>
                <th style="padding:10px 12px;text-align:center">AIR &lt; 100</th>
                <th style="padding:10px 12px">Key Technical Complexity Profile</th>
                <th style="padding:10px 12px;text-align:center">Action</th>
              </tr>
            </thead>
            <tbody>
              ${Array.from({length: 20}, (_, idx) => {
                const num = idx + 1;
                const id = 'mock-flm-' + String(num).padStart(2, '0');
                const m = MOCK_TESTS.find(t => t.id === id);
                if (!m) return '';
                const isMed = m.difficulty === 'medium';
                const tierBadge = isMed
                  ? '<span class="q-badge medium" style="padding:2px 8px;font-size:11px">🟡 Medium</span>'
                  : '<span class="q-badge hard" style="padding:2px 8px;font-size:11px">🔴 Hard</span>';
                const rowBg = idx % 2 === 0 ? 'var(--bg-card)' : 'rgba(255,255,255,0.02)';
                return `
                  <tr style="background:${rowBg};border-bottom:1px solid var(--border)">
                    <td style="padding:9px 12px;font-weight:700;white-space:nowrap;color:var(--text-primary)">Mock #${String(num).padStart(2, '0')}</td>
                    <td style="padding:9px 12px;text-align:center">${tierBadge}</td>
                    <td style="padding:9px 12px;text-align:center;font-weight:700;color:var(--yellow)">⭐ ${m.rating ? m.rating.toFixed(1) : ''}/10</td>
                    <td style="padding:9px 12px;text-align:center;color:var(--text-secondary)">${m.cutoff || '28-32'} M</td>
                    <td style="padding:9px 12px;text-align:center;color:var(--text-secondary)">${m.air100 || '72-78'} M</td>
                    <td style="padding:9px 12px;color:var(--text-muted);font-size:11.5px;max-width:320px">${m.desc.split(': ').slice(1).join(': ') || m.desc}</td>
                    <td style="padding:9px 12px;text-align:center;white-space:nowrap">
                      <button class="btn btn-secondary btn-sm" onclick="startMockTest('${m.id}')" style="padding:3px 8px;font-size:11px" type="button">Start Test</button>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      ` : ''}
    </div>
  `;
}

function getFilteredAndSortedMocks(fullMocks) {
  const currentLvl = state.mockLevelFilter || 'all';
  const currentSort = state.mockSort || 'default';

  let list = currentLvl === 'all'
    ? fullMocks.slice()
    : fullMocks.filter(m => m.difficulty === currentLvl);

  const diffRank = { 'easy': 1, 'medium': 2, 'hard': 3 };

  if (currentSort === 'easy-first') {
    list.sort((a, b) => {
      const da = diffRank[a.difficulty] || 2;
      const db = diffRank[b.difficulty] || 2;
      if (da !== db) return da - db;
      return (a.rating || 5) - (b.rating || 5);
    });
  } else if (currentSort === 'hard-first') {
    list.sort((a, b) => {
      const da = diffRank[a.difficulty] || 2;
      const db = diffRank[b.difficulty] || 2;
      if (da !== db) return db - da;
      return (b.rating || 5) - (a.rating || 5);
    });
  } else if (currentSort === 'rating-desc') {
    list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
  } else if (currentSort === 'rating-asc') {
    list.sort((a, b) => (a.rating || 0) - (b.rating || 0));
  } else if (currentSort === 'name-asc') {
    list.sort((a, b) => a.name.localeCompare(b.name));
  }

  return list;
}

function setMockSort(sortVal) {
  state.mockSort = sortVal;
  const c = document.getElementById('mock-tab-content');
  if (c && state.mockTab === 'full') {
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');
    const filtered = getFilteredAndSortedMocks(fullMocks);
    c.innerHTML = `
      ${buildMockCalibrationGuide()}
      ${buildMockLevelFilterBar(fullMocks)}
      ${buildMockGrid(filtered)}
    `;
    renderMath(c);
  }
}

function buildMockLevelFilterBar(fullMocks) {
  const currentLvl = state.mockLevelFilter || 'all';
  const currentSort = state.mockSort || 'default';
  const easyCount = fullMocks.filter(m => m.difficulty === 'easy').length;
  const medCount  = fullMocks.filter(m => m.difficulty === 'medium').length;
  const hardCount = fullMocks.filter(m => m.difficulty === 'hard').length;

  return `
    <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
        <button class="chip ${currentLvl === 'all' ? 'active' : ''}" onclick="setMockLevelFilter('all')" type="button">All Levels (${fullMocks.length})</button>
        <button class="chip ${currentLvl === 'easy' ? 'active' : ''}" onclick="setMockLevelFilter('easy')" style="${currentLvl === 'easy' ? 'border-color:var(--green);color:var(--green);background:var(--green-soft)' : ''}" type="button">🟢 Easy / Foundational (${easyCount})</button>
        <button class="chip ${currentLvl === 'medium' ? 'active' : ''}" onclick="setMockLevelFilter('medium')" style="${currentLvl === 'medium' ? 'border-color:var(--yellow);color:var(--yellow);background:var(--yellow-soft)' : ''}" type="button">🟡 Moderate / Standard (${medCount})</button>
        <button class="chip ${currentLvl === 'hard' ? 'active' : ''}" onclick="setMockLevelFilter('hard')" style="${currentLvl === 'hard' ? 'border-color:var(--red);color:var(--red);background:var(--red-soft)' : ''}" type="button">🔴 Hard / Rank Booster (${hardCount})</button>
      </div>

      <div style="display:flex;align-items:center;gap:8px">
        <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>
        <select class="form-select form-select-sm" style="width:auto;min-width:185px;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setMockSort(this.value)">
          <option value="default" ${currentSort === 'default' ? 'selected' : ''}>Default Order</option>
          <option value="easy-first" ${currentSort === 'easy-first' ? 'selected' : ''}>Difficulty: Easy → Hard</option>
          <option value="hard-first" ${currentSort === 'hard-first' ? 'selected' : ''}>Difficulty: Hard → Easy</option>
          <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>
          <option value="rating-asc" ${currentSort === 'rating-asc' ? 'selected' : ''}>Rating: Low → High</option>
          <option value="name-asc" ${currentSort === 'name-asc' ? 'selected' : ''}>Name: A → Z</option>
        </select>
      </div>
    </div>
  `;
}

function setMockLevelFilter(lvl) {
  state.mockLevelFilter = lvl;
  const c = document.getElementById('mock-tab-content');
  if (c && state.mockTab === 'full') {
    const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');
    const filtered = getFilteredAndSortedMocks(fullMocks);
    c.innerHTML = `
      ${buildMockCalibrationGuide()}
      ${buildMockLevelFilterBar(fullMocks)}
      ${buildMockGrid(filtered)}
    `;
    renderMath(c);
  }
}

function renderMocks(c, params={}){
  if (state.activeMockPaper) {
    renderMockPaperView(c);
    return;
  }
  const activeTab = params.tab || state.mockTab || 'full';
  state.mockTab = activeTab;

  const fullMocks = MOCK_TESTS.filter(m => m.type === 'full');
  const filteredFullMocks = getFilteredAndSortedMocks(fullMocks);

  c.innerHTML=`
    <div class="tabs" id="mock-tabs">
      <button class="tab-btn ${activeTab==='full'?'active':''}" onclick="switchMockTab('full',this)" type="button">🏆 Full Mocks</button>
      <button class="tab-btn ${activeTab==='subwise'?'active':''}" onclick="switchMockTab('subwise',this)" type="button">📂 Subject Mocks</button>
      <button class="tab-btn ${activeTab==='papers'?'active':''}" onclick="switchMockTab('papers',this)" type="button">📝 Practice Papers</button>
      <button class="tab-btn ${activeTab==='history'?'active':''}" onclick="switchMockTab('history',this)" type="button">📊 My History</button>
    </div>
    <div id="mock-tab-content">
      ${activeTab==='full' ? `${buildMockCalibrationGuide()}${buildMockLevelFilterBar(fullMocks)}${buildMockGrid(filteredFullMocks)}` :
        activeTab==='subwise' ? buildMockGrid(MOCK_TESTS.filter(m=>m.type==='subwise')) :
        activeTab==='papers' ? buildPracticePapersSection() :
        buildTestHistory()}
    </div>`;
  renderMath(c);
}

function switchMockTab(tab, btn){
  state.mockTab = tab;
  document.querySelectorAll('#mock-tabs .tab-btn').forEach(b=>b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const c=document.getElementById('mock-tab-content');
  if (!c) return;
  if (tab==='full') {
    const fullMocks = MOCK_TESTS.filter(m=>m.type==='full');
    const filtered = getFilteredAndSortedMocks(fullMocks);
    c.innerHTML = `${buildMockCalibrationGuide()}${buildMockLevelFilterBar(fullMocks)}${buildMockGrid(filtered)}`;
  }
  if (tab==='subwise') c.innerHTML=buildMockGrid(MOCK_TESTS.filter(m=>m.type==='subwise'));
  if (tab==='papers')  c.innerHTML=buildPracticePapersSection();
  if (tab==='history') c.innerHTML=buildTestHistory();
  renderMath(c);
}

function buildMockGrid(mocks){
  if (!mocks.length) return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No tests available for selected filter</div><div class="empty-state-sub">Try selecting "All Levels" or another filter.</div></div>';
  return `<div class="mock-grid">${mocks.map(m=>{
    const past=state.testSessions.filter(s=>s.mockId===m.id);
    const best=past.length?Math.max(...past.map(s=>s.percentage)):null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const totalPages = Math.ceil(questionsCount / 20) || 1;
    const diffLabel = m.difficulty ? m.difficulty.toUpperCase() : 'MEDIUM';
    const ratingBadge = m.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${m.rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (m.cutoff && m.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${m.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${m.air100} M</span>
      </div>` : '';
    return `<div class="mock-card">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <div class="mock-type-badge ${m.type}">${m.type==='full'?'🏆 Full Mock':'📂 Subject Mock'}</div>
        <div style="display:flex;align-items:center;gap:6px">
          <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
          ${ratingBadge}
        </div>
      </div>
      <div class="mock-title">${m.name}</div>
      <div class="text-sm text-muted">${m.subject||'All 13 Subjects Covered'}</div>
      ${m.desc ? `<div class="text-sm text-secondary" style="margin:6px 0 8px;line-height:1.4">${m.desc}</div>` : ''}
      ${targetsRow}
      ${best!==null?`<div class="text-sm mt-2" style="color:var(--green)">Best Score: ${best}%</div>`:''}
      <div class="mock-meta">
        <div class="mock-meta-item">📝 ${questionsCount} Qs (${totalPages} page${totalPages>1?'s':''})</div>
        <div class="mock-meta-item">⏱ ${m.duration} min</div>
        <div class="mock-meta-item">🏅 ${m.marks} marks</div>
      </div>
      <div class="mock-card-actions">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" title="Browse questions in sets of 20 per page" type="button">📖 Practice Paper (20/page)</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" title="Start timed exam" type="button">▶ Timed Exam</button>
      </div>
      ${past.length?`<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length>1?'s':''}</div>`:''}
    </div>`;
  }).join('')}</div>`;
}

// ─── PRACTICE PAPERS FILTER & SORT ENGINE ─────────────────────────────────────
function getFilteredAndSortedPracticePapers() {
  const currentFilter = state.paperLevelFilter || 'all';
  const currentSort   = state.paperSort || 'default';

  // 1. Filter
  let list = PRACTICE_PAPERS.slice();
  if (currentFilter === 'easy') {
    list = list.filter(p => getPaperDifficulty(p) === 'easy');
  } else if (currentFilter === 'medium') {
    list = list.filter(p => getPaperDifficulty(p) === 'medium');
  } else if (currentFilter === 'hard') {
    list = list.filter(p => getPaperDifficulty(p) === 'hard');
  } else if (currentFilter === 'flm') {
    list = list.filter(p => p.id.startsWith('paper-flm-'));
  } else if (currentFilter === 'pyq') {
    list = list.filter(p => !p.id.startsWith('paper-flm-'));
  }

  // 2. Sort
  const diffRank = { 'easy': 1, 'medium': 2, 'hard': 3 };

  if (currentSort === 'easy-first') {
    list.sort((a, b) => {
      const da = diffRank[getPaperDifficulty(a)] || 2;
      const db = diffRank[getPaperDifficulty(b)] || 2;
      if (da !== db) return da - db;
      return (getPaperRating(a) || 5) - (getPaperRating(b) || 5);
    });
  } else if (currentSort === 'hard-first') {
    list.sort((a, b) => {
      const da = diffRank[getPaperDifficulty(a)] || 2;
      const db = diffRank[getPaperDifficulty(b)] || 2;
      if (da !== db) return db - da;
      return (getPaperRating(b) || 5) - (getPaperRating(a) || 5);
    });
  } else if (currentSort === 'rating-desc') {
    list.sort((a, b) => (getPaperRating(b) || 0) - (getPaperRating(a) || 0));
  } else if (currentSort === 'rating-asc') {
    list.sort((a, b) => (getPaperRating(a) || 0) - (getPaperRating(b) || 0));
  } else if (currentSort === 'questions-desc') {
    list.sort((a, b) => (b.questions || 65) - (a.questions || 65));
  } else if (currentSort === 'name-asc') {
    list.sort((a, b) => a.name.localeCompare(b.name));
  }

  return list;
}

function setPaperLevelFilter(filter) {
  state.paperLevelFilter = filter;
  if (state.currentPage === 'papers') {
    const c = document.getElementById('page-content');
    if (c) renderPracticePapers(c);
  } else if (state.currentPage === 'mocks' && state.mockTab === 'papers') {
    const c = document.getElementById('mock-tab-content');
    if (c) {
      c.innerHTML = buildPracticePapersSection();
      renderMath(c);
    }
  }
}

function setPaperSort(sortVal) {
  state.paperSort = sortVal;
  if (state.currentPage === 'papers') {
    const c = document.getElementById('page-content');
    if (c) renderPracticePapers(c);
  } else if (state.currentPage === 'mocks' && state.mockTab === 'papers') {
    const c = document.getElementById('mock-tab-content');
    if (c) {
      c.innerHTML = buildPracticePapersSection();
      renderMath(c);
    }
  }
}

function buildPracticePapersFilterBar() {
  const currentFilter = state.paperLevelFilter || 'all';
  const currentSort   = state.paperSort || 'default';
  const easyCount = PRACTICE_PAPERS.filter(p => getPaperDifficulty(p) === 'easy').length;
  const medCount  = PRACTICE_PAPERS.filter(p => getPaperDifficulty(p) === 'medium').length;
  const hardCount = PRACTICE_PAPERS.filter(p => getPaperDifficulty(p) === 'hard').length;
  const flmCount  = PRACTICE_PAPERS.filter(p => p.id.startsWith('paper-flm-')).length;
  const pyqCount  = PRACTICE_PAPERS.filter(p => !p.id.startsWith('paper-flm-')).length;

  return `
    <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
        <button class="chip ${currentFilter === 'all' ? 'active' : ''}" onclick="setPaperLevelFilter('all')" type="button">
          All Levels (${PRACTICE_PAPERS.length})
        </button>
        <button class="chip ${currentFilter === 'easy' ? 'active' : ''}" onclick="setPaperLevelFilter('easy')" style="${currentFilter === 'easy' ? 'border-color:var(--green);color:var(--green);background:var(--green-soft)' : ''}" type="button">
          🟢 Easy (${easyCount})
        </button>
        <button class="chip ${currentFilter === 'medium' ? 'active' : ''}" onclick="setPaperLevelFilter('medium')" style="${currentFilter === 'medium' ? 'border-color:var(--yellow);color:var(--yellow);background:var(--yellow-soft)' : ''}" type="button">
          🟡 Medium (${medCount})
        </button>
        <button class="chip ${currentFilter === 'hard' ? 'active' : ''}" onclick="setPaperLevelFilter('hard')" style="${currentFilter === 'hard' ? 'border-color:var(--red);color:var(--red);background:var(--red-soft)' : ''}" type="button">
          🔴 Hard (${hardCount})
        </button>
        <button class="chip ${currentFilter === 'flm' ? 'active' : ''}" onclick="setPaperLevelFilter('flm')" type="button">
          🏆 20 Full Mocks (${flmCount})
        </button>
        <button class="chip ${currentFilter === 'pyq' ? 'active' : ''}" onclick="setPaperLevelFilter('pyq')" type="button">
          📅 PYQs & Subjects (${pyqCount})
        </button>
      </div>

      <div style="display:flex;align-items:center;gap:8px">
        <label style="font-size:12px;color:var(--text-secondary);font-weight:600;white-space:nowrap">Sort by:</label>
        <select class="form-select form-select-sm" style="width:auto;min-width:185px;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setPaperSort(this.value)">
          <option value="default" ${currentSort === 'default' ? 'selected' : ''}>Default Order</option>
          <option value="easy-first" ${currentSort === 'easy-first' ? 'selected' : ''}>Difficulty: Easy → Hard</option>
          <option value="hard-first" ${currentSort === 'hard-first' ? 'selected' : ''}>Difficulty: Hard → Easy</option>
          <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>
          <option value="rating-asc" ${currentSort === 'rating-asc' ? 'selected' : ''}>Rating: Low → High</option>
          <option value="questions-desc" ${currentSort === 'questions-desc' ? 'selected' : ''}>Questions: Most → Least</option>
          <option value="name-asc" ${currentSort === 'name-asc' ? 'selected' : ''}>Name: A → Z</option>
        </select>
      </div>
    </div>
  `;
}

function buildPracticePapersGrid(papersList = null){
  const papers = papersList || getFilteredAndSortedPracticePapers();
  if (!papers.length) {
    return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No practice papers available for selected filter</div><div class="empty-state-sub">Try selecting "All Levels" or another filter.</div></div>';
  }
  return `<div class="mock-grid">${papers.map(p=>{
    const qs = getMockQuestions(p.id);
    const totalCount = qs.length || p.questions;
    const totalPages = Math.ceil(totalCount / 20) || 1;
    const diff = getPaperDifficulty(p);
    const diffLabel = diff.toUpperCase();
    const rating = getPaperRating(p);
    const ratingBadge = rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (p.cutoff && p.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${p.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${p.air100} M</span>
      </div>` : '';
    return `
      <div class="paper-card">
        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <div class="paper-meta-badge">📝 Practice Paper • 20/Page</div>
            <div style="display:flex;align-items:center;gap:6px">
              <span class="q-badge ${diff}">${diffLabel}</span>
              ${ratingBadge}
            </div>
          </div>
          <div class="mock-title">${p.name}</div>
          <div class="text-sm text-muted" style="margin-bottom:8px">${p.desc}</div>
          ${targetsRow}
          <div class="mock-meta">
            <div class="mock-meta-item">📚 ${totalCount} Questions</div>
            <div class="mock-meta-item">📄 ${totalPages} Pages (20/page)</div>
            <div class="mock-meta-item">🏅 ${p.marks} marks</div>
          </div>
        </div>
        <div class="mock-card-actions">
          <button class="btn btn-primary btn-sm" onclick="viewMockPaper('${p.id}')" type="button">📖 Open Paper (20/page)</button>
          <button class="btn btn-secondary btn-sm" onclick="startPracticePaperDirect('${p.id}')" type="button">▶ Practice Mode</button>
        </div>
      </div>
    `;
  }).join('')}</div>`;
}

function buildPracticePapersSection() {
  return `
    ${buildPracticePapersFilterBar()}
    ${buildPracticePapersGrid()}
  `;
}

function renderPracticePapers(c){
  if (state.activeMockPaper) {
    renderMockPaperView(c);
    return;
  }
  c.innerHTML = `
    <div class="section-header">
      <div class="section-title">Practice Papers <span>${PRACTICE_PAPERS.length} curated papers</span></div>
    </div>
    <p class="text-muted text-sm" style="margin-bottom:14px">Browse curated practice papers paginated at 20 questions per page with step-by-step solutions and explanations.</p>
    ${buildPracticePapersSection()}
  `;
  renderMath(c);
}
'''

code = code[:p_start] + new_code_section + '\n' + code[p_end:]
print("Mocks and Practice papers engine section replaced.")

# 4. Update window exports
window_assign_marker = 'Object.assign(window, {'
w_idx = code.find(window_assign_marker)
assert w_idx != -1

# Add missing handlers to window export
exports_to_add = """  setPaperLevelFilter,
  setPaperSort,
  setMockSort,
  toggleCalibrationTable,
"""
mock_paper_export_marker = '  viewMockPaper,'
if 'setPaperLevelFilter' not in code[w_idx:]:
    code = code.replace(mock_paper_export_marker, exports_to_add + mock_paper_export_marker, 1)
    print("Added setPaperLevelFilter, setPaperSort, setMockSort, toggleCalibrationTable to window exports.")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("app.js updated successfully!")
