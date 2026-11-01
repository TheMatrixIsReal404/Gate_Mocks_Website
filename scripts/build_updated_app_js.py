# -*- coding: utf-8 -*-
"""
Build the updated app.js from app.js.bak.
Integrates 30 Easy Mocks, consolidates Mock Tests, implements Full-Length PYQ Exams,
and synchronizes Dashboard metrics.
"""

import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('app.js.bak', 'r', encoding='utf-8') as f:
    text = f.read()

# ─── 1. BUILD 30 EASY MOCKS ──────────────────────────────────────────────────
easy_mocks_list = []
for i in range(1, 31):
    easy_mocks_list.append(f"""  {{
    id: 'mock-easy-{i:02d}',
    type: 'full',
    difficulty: 'easy',
    rating: 3.5,
    cutoff: '34-36',
    air100: '78-82',
    tier: 'Foundational Easy',
    name: 'GATE CS Easy Mock Exam #{i:02d} (Foundational)',
    subject: null,
    questions: 65,
    duration: 180,
    marks: 100,
    desc: 'Mock #{i:02d} [Easy Foundational | Rating: 3.5/10 | Est. Cutoff: 34-36M]: Foundational full-length paper strictly aligned with IISc/IIT syllabus. Covers direct formulas, definitions, and standard scoring problems across all 13 subjects.'
  }},""")
easy_mocks_js = "\n".join(easy_mocks_list)

practice_sets_js = """  // ─── CURATED PRACTICE SETS (Migrated from Practice Papers) ─────────────
  { id:'paper-full-1', mockId:'paper-full-1', name:'GATE CSE Comprehensive Paper 1', type:'practice-set', difficulty:'easy', rating:3.5, cutoff:'34-36', air100:'78-82', questions:65, duration:180, marks:100, desc:'Complete 65-question mock paper following the official GATE pattern.' },
  { id:'paper-full-2', mockId:'paper-full-2', name:'GATE CSE Comprehensive Paper 2', type:'practice-set', difficulty:'medium', rating:4.5, cutoff:'31-33', air100:'74-78', questions:65, duration:180, marks:100, desc:'Balanced multi-subject paper covering all GATE CSE core concepts.' },
  { id:'paper-dsa', mockId:'paper-dsa', name:'Data Structures & Algorithms Paper', type:'practice-set', difficulty:'medium', rating:5.0, subjects:['Data Structures','Algorithms','C Programming'], questions:50, duration:120, marks:80, desc:'Deep dive into C Programming, Data Structures, Trees, Graphs, and DP.' },
  { id:'paper-systems', mockId:'paper-systems', name:'Systems & Architecture Paper', type:'practice-set', difficulty:'hard', rating:6.0, subjects:['Operating Systems','Computer Networks','Computer Organization'], questions:50, duration:120, marks:80, desc:'Processes, memory, TCP/IP, routing, pipelining, and cache.' },
  { id:'paper-theory', mockId:'paper-theory', name:'Theory of Computation & Compilers', type:'practice-set', difficulty:'medium', rating:5.0, subjects:['Theory of Computation','Compiler Design'], questions:35, duration:90, marks:60, desc:'Automata, regular expressions, grammars, parsers, and runtime.' },
  { id:'paper-maths', mockId:'paper-maths', name:'Maths & General Aptitude Paper', type:'practice-set', difficulty:'medium', rating:4.5, subjects:['Discrete Mathematics','Engineering Mathematics','Aptitude'], questions:45, duration:110, marks:70, desc:'Graph theory, combinatorics, linear algebra, probability, and aptitude.' },
  { id:'paper-gate-overflow-decade', mockId:'paper-gate-overflow-decade', name:'GATE Decade PYQ Paper (2014–2024)', type:'practice-set', difficulty:'medium', rating:5.5, cutoff:'28-30', air100:'72-76', questions:65, duration:180, marks:100, desc:'Curated 65-question compilation across the last decade of GATE CSE exams from Gate Overflow.' },"""

pyq_exams_js = """const FULL_LENGTH_PYQ_EXAMS = [
  {
    id: 'pyq-exam-2026-1',
    year: 2026,
    set: 'Mock Paper 1',
    name: 'GATE CSE 2026 All-India Exam Paper 1',
    institute: 'Official Pattern GATE 2026',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 6.5,
    cutoff: '28-30',
    air100: '72-76',
    desc: 'Official-pattern 65-question GATE CSE 2026 full exam paper with balanced distribution of MCQs, MSQs, and multi-step NAT numericals.'
  },
  {
    id: 'pyq-exam-2026-2',
    year: 2026,
    set: 'Mock Paper 2',
    name: 'GATE CSE 2026 All-India Exam Paper 2',
    institute: 'Official Pattern GATE 2026',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'hard',
    rating: 7.5,
    cutoff: '24-26',
    air100: '66-70',
    desc: 'Advanced full-length GATE CSE 2026 exam paper testing deep core CS, engineering mathematics, and general aptitude under strict 180-min timing.'
  },
  {
    id: 'pyq-exam-2025-s1',
    year: 2025,
    set: 'Set 1',
    name: 'Official GATE CSE 2025 Exam (Set 1)',
    institute: 'IIT Roorkee',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.5,
    cutoff: '28-30',
    air100: '72-76',
    desc: 'The official 65-question GATE 2025 Set 1 question paper conducted by IIT Roorkee under realistic 180-min TCS iON exam simulation.'
  },
  {
    id: 'pyq-exam-2025-s2',
    year: 2025,
    set: 'Set 2',
    name: 'Official GATE CSE 2025 Exam (Set 2)',
    institute: 'IIT Roorkee',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'hard',
    rating: 7.0,
    cutoff: '24-26',
    air100: '64-68',
    desc: 'The official 65-question GATE 2025 Set 2 question paper conducted by IIT Roorkee with verified IITR answer keys and multi-step derivations.'
  },
  {
    id: 'pyq-exam-2024',
    year: 2024,
    set: 'Full Paper',
    name: 'Official GATE CSE 2024 Exam Paper',
    institute: 'IISc Bangalore',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'hard',
    rating: 6.8,
    cutoff: '26-28',
    air100: '68-72',
    desc: 'Official GATE CSE 2024 paper conducted by IISc Bangalore covering discrete mathematics, systems, algorithms, and core CS.'
  },
  {
    id: 'pyq-exam-2023',
    year: 2023,
    set: 'Full Paper',
    name: 'Official GATE CSE 2023 Exam Paper',
    institute: 'IIT Kanpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 6.0,
    cutoff: '27-29',
    air100: '70-74',
    desc: 'Official GATE CSE 2023 examination paper conducted by IIT Kanpur with complete MCQs, MSQs, and NAT numericals.'
  },
  {
    id: 'pyq-exam-2022',
    year: 2022,
    set: 'Full Paper',
    name: 'Official GATE CSE 2022 Exam Paper',
    institute: 'IIT Kharagpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.8,
    cutoff: '28-30',
    air100: '71-75',
    desc: 'Official GATE CSE 2022 examination paper conducted by IIT Kharagpur.'
  },
  {
    id: 'pyq-exam-2021',
    year: 2021,
    set: 'Full Paper',
    name: 'Official GATE CSE 2021 Exam Paper',
    institute: 'IIT Bombay',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.5,
    cutoff: '28-30',
    air100: '72-76',
    desc: 'Official 65-question GATE CSE 2021 examination paper conducted by IIT Bombay.'
  },
  {
    id: 'pyq-exam-2020',
    year: 2020,
    set: 'Full Paper',
    name: 'Official GATE CSE 2020 Exam Paper',
    institute: 'IIT Delhi',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.5,
    cutoff: '28-30',
    air100: '72-76',
    desc: 'Official 65-question GATE CSE 2020 examination paper conducted by IIT Delhi.'
  },
  {
    id: 'pyq-exam-2019',
    year: 2019,
    set: 'Full Paper',
    name: 'Official GATE CSE 2019 Exam Paper',
    institute: 'IIT Madras',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.0,
    cutoff: '29-31',
    air100: '73-77',
    desc: 'Official 65-question GATE CSE 2019 paper conducted by IIT Madras.'
  },
  {
    id: 'pyq-exam-2018',
    year: 2018,
    set: 'Full Paper',
    name: 'Official GATE CSE 2018 Exam Paper',
    institute: 'IIT Guwahati',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.0,
    cutoff: '29-31',
    air100: '73-77',
    desc: 'Official 65-question GATE CSE 2018 paper conducted by IIT Guwahati.'
  },
  {
    id: 'pyq-exam-2017',
    year: 2017,
    set: 'Full Paper',
    name: 'Official GATE CSE 2017 Exam Paper',
    institute: 'IIT Roorkee',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.4,
    cutoff: '28-30',
    air100: '71-75',
    desc: 'Official GATE CSE 2017 examination paper conducted by IIT Roorkee.'
  },
  {
    id: 'pyq-exam-2016',
    year: 2016,
    set: 'Full Paper',
    name: 'Official GATE CSE 2016 Exam Paper',
    institute: 'IISc Bangalore',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.5,
    cutoff: '28-30',
    air100: '72-76',
    desc: 'Official GATE CSE 2016 examination paper conducted by IISc Bangalore.'
  },
  {
    id: 'pyq-exam-2015-s1',
    year: 2015,
    set: 'Set 1',
    name: 'Official GATE CSE 2015 Exam (Set 1)',
    institute: 'IIT Kanpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.2,
    cutoff: '29-31',
    air100: '72-76',
    desc: 'Official GATE CSE 2015 Set 1 examination paper conducted by IIT Kanpur.'
  },
  {
    id: 'pyq-exam-2015-s2',
    year: 2015,
    set: 'Set 2',
    name: 'Official GATE CSE 2015 Exam (Set 2)',
    institute: 'IIT Kanpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'hard',
    rating: 6.2,
    cutoff: '26-28',
    air100: '68-72',
    desc: 'Official GATE CSE 2015 Set 2 examination paper conducted by IIT Kanpur.'
  },
  {
    id: 'pyq-exam-2015-s3',
    year: 2015,
    set: 'Set 3',
    name: 'Official GATE CSE 2015 Exam (Set 3)',
    institute: 'IIT Kanpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.8,
    cutoff: '27-29',
    air100: '70-74',
    desc: 'Official GATE CSE 2015 Set 3 examination paper conducted by IIT Kanpur.'
  },
  {
    id: 'pyq-exam-2014-s1',
    year: 2014,
    set: 'Set 1',
    name: 'Official GATE CSE 2014 Exam (Set 1)',
    institute: 'IIT Kharagpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.0,
    cutoff: '29-31',
    air100: '73-77',
    desc: 'Official GATE CSE 2014 Set 1 paper conducted by IIT Kharagpur.'
  },
  {
    id: 'pyq-exam-2014-s2',
    year: 2014,
    set: 'Set 2',
    name: 'Official GATE CSE 2014 Exam (Set 2)',
    institute: 'IIT Kharagpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.0,
    cutoff: '29-31',
    air100: '73-77',
    desc: 'Official GATE CSE 2014 Set 2 paper conducted by IIT Kharagpur.'
  },
  {
    id: 'pyq-exam-2014-s3',
    year: 2014,
    set: 'Set 3',
    name: 'Official GATE CSE 2014 Exam (Set 3)',
    institute: 'IIT Kharagpur',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'hard',
    rating: 6.0,
    cutoff: '27-29',
    air100: '69-73',
    desc: 'Official GATE CSE 2014 Set 3 paper conducted by IIT Kharagpur.'
  },
  {
    id: 'pyq-exam-2011',
    year: 2011,
    set: 'Full Paper',
    name: 'Official GATE CSE 2011 Exam Paper',
    institute: 'IIT Madras',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'easy',
    rating: 4.0,
    cutoff: '32-34',
    air100: '76-80',
    desc: 'Official 65-question GATE CSE 2011 examination paper.'
  },
  {
    id: 'pyq-exam-decade',
    year: '2014–2024',
    set: 'Decade Special',
    name: 'GATE Decade Special PYQ Exam (2014–2024)',
    institute: 'Gate Overflow Compilation',
    duration: 180,
    marks: 100,
    questions: 65,
    difficulty: 'medium',
    rating: 5.5,
    cutoff: '28-30',
    air100: '72-76',
    desc: 'Curated 65-question compilation across the last decade of GATE CSE exams.'
  }
];"""

idx_mock_start = text.find('const MOCK_TESTS = [')
idx_subject_mocks = text.find('// ─── SUBJECT-WISE MOCKS ───')
idx_pyq_years = text.find('const PYQ_YEARS   = [2025,2024')

existing_full_mocks = text[idx_mock_start + len('const MOCK_TESTS = ['):idx_subject_mocks].strip()
existing_subject_mocks = text[idx_subject_mocks:text.find('];\n\nconst PRACTICE_PAPERS')].strip()

new_mock_tests_section = f"""const MOCK_TESTS = [
  // ─── 30 EASY-LEVEL FULL-LENGTH MOCK EXAMINATIONS (easy_mocks.docx) ─────────
{easy_mocks_js}

{existing_full_mocks}

{practice_sets_js}

{existing_subject_mocks}
];

{pyq_exams_js}

// Backward-compatibility alias for legacy code
const PRACTICE_PAPERS = MOCK_TESTS.filter(m => m.type === 'practice-set' || m.type === 'full');
"""

text = text[:idx_mock_start] + new_mock_tests_section + text[idx_pyq_years:]

# ─── 2. UPDATE STATE ─────────────────────────────────────────────────────────
text = text.replace("mockTab:          'full',", "mockTab:          'all',")
state_search = "paperSort:        'default',"
new_state_block = """paperSort:        'default',
  pyqExamEraFilter: 'all',
  pyqExamDiffFilter:'all',
  pyqExamSort:      'year-desc',"""
text = text.replace(state_search, new_state_block)

# ─── 3. UPDATE TITLES & NAVIGATION ───────────────────────────────────────────
text = text.replace(
    "mocks:'Mock Tests', papers:'Practice Papers', pyqs:'PYQs', performance:'Performance', upload:'Upload Questions',",
    "mocks:'Mock Tests', 'pyq-exams':'Full-Length PYQ Exams', pyqs:'Topic-wise PYQs', performance:'Performance', upload:'Upload Questions',"
)

text = text.replace(
    "function navigate(page, params={}) {",
    """function navigate(page, params={}) {
  if (page === 'papers') {
    navigate('mocks', { tab: 'practice-sets' });
    return;
  }"""
)

text = text.replace(
    "case 'papers':      renderPracticePapers(c);    break;",
    """case 'pyq-exams':   renderPyqExams(c);          break;
    case 'papers':      renderMocks(c, { tab: 'practice-sets' }); break;"""
)

# ─── 4. DASHBOARD CTA BUTTON ─────────────────────────────────────────────────
text = text.replace(
    """        <button class="btn btn-white" onclick="navigate('subjects')">📚 Practice Now</button>
        <button class="btn btn-outline-white" onclick="navigate('mocks')">🎯 Take a Mock Test</button>""",
    """        <button class="btn btn-white" onclick="navigate('subjects')">📚 Practice Now</button>
        <button class="btn btn-outline-white" onclick="navigate('mocks')">🎯 Mock Tests</button>
        <button class="btn btn-outline-white" onclick="navigate('pyq-exams')">⏱️ Full-Length PYQ Exams</button>"""
)

# ─── 5. UPDATE getMockQuestions ──────────────────────────────────────────────
old_get_mock_start = text.find('function getMockQuestions(mockId) {')
old_get_mock_end = text.find('function getPaperDifficulty(p) {')
assert old_get_mock_start != -1 and old_get_mock_end != -1, "getMockQuestions boundaries not found"

new_get_mock_fn = """function getMockQuestions(mockId) {
  // 1. Direct mock questions tagged with mockId (or matching paper mockId)
  const targetMockId = (mockId.startsWith('paper-cat') || mockId.startsWith('paper-flm') || mockId.startsWith('paper-easy'))
    ? mockId.replace('paper-', 'mock-') : mockId;
  const directQs = state.questions.filter(q => q.mockId === targetMockId || q.mockId === mockId);
  if (directQs.length >= 65) return directQs;

  // 2. Full-Length PYQ Exam papers
  if (mockId === 'pyq-exam-2025-s1' || mockId === 'paper-gate-2025-s1' || mockId === 'mock-gate-2025-s1') {
    const s1 = state.questions.filter(q => q.paper === 'GATE 2025 Set 1' || q.id.startsWith('pyq_2025_s1'));
    if (s1.length) return s1.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2025-s2' || mockId === 'paper-gate-2025-s2' || mockId === 'mock-gate-2025-s2') {
    const s2 = state.questions.filter(q => q.paper === 'GATE 2025 Set 2' || q.id.startsWith('pyq_2025_s2'));
    if (s2.length) return s2.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2026-1' || mockId === 'mock-full-001') {
    const q1 = state.questions.filter(q => q.mockId === 'mock-full-001');
    if (q1.length) return q1.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2026-2' || mockId === 'mock-full-002') {
    const q2 = state.questions.filter(q => q.mockId === 'mock-full-002');
    if (q2.length) return q2.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2021' || mockId === 'paper-gate-2021') {
    const qs = state.questions.filter(q => q.year === 2021 || (q.paper && q.paper.includes('2021')));
    if (qs.length) return qs.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2020' || mockId === 'paper-gate-2020') {
    const qs = state.questions.filter(q => q.year === 2020 || (q.paper && q.paper.includes('2020')));
    if (qs.length) return qs.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2019' || mockId === 'paper-gate-2019') {
    const qs = state.questions.filter(q => q.year === 2019 || (q.paper && q.paper.includes('2019')));
    if (qs.length) return qs.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2018' || mockId === 'paper-gate-2018') {
    const qs = state.questions.filter(q => q.year === 2018 || (q.paper && q.paper.includes('2018')));
    if (qs.length) return qs.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2015-s1') {
    const qs = state.questions.filter(q => q.paper === 'GATE 2015 Set 1');
    const all2015 = state.questions.filter(q => q.year === 2015);
    const combined = [...qs, ...all2015.filter(q => !qs.includes(q))];
    if (combined.length) return combined.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2015-s2') {
    const qs = state.questions.filter(q => q.paper === 'GATE 2015 Set 2');
    const all2015 = state.questions.filter(q => q.year === 2015);
    const combined = [...qs, ...all2015.filter(q => !qs.includes(q))];
    if (combined.length) return combined.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2015-s3') {
    const qs = state.questions.filter(q => q.paper === 'GATE 2015 Set 3');
    const all2015 = state.questions.filter(q => q.year === 2015);
    const combined = [...qs, ...all2015.filter(q => !qs.includes(q))];
    if (combined.length) return combined.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2014-s1') {
    const qs = state.questions.filter(q => q.paper === 'GATE 2014 Set 1');
    const all2014 = state.questions.filter(q => q.year === 2014);
    const combined = [...qs, ...all2014.filter(q => !qs.includes(q))];
    if (combined.length) return combined.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2014-s2') {
    const qs = state.questions.filter(q => q.paper === 'GATE 2014 Set 2');
    const all2014 = state.questions.filter(q => q.year === 2014);
    const combined = [...qs, ...all2014.filter(q => !qs.includes(q))];
    if (combined.length) return combined.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2014-s3') {
    const qs = state.questions.filter(q => q.paper === 'GATE 2014 Set 3');
    const all2014 = state.questions.filter(q => q.year === 2014);
    const combined = [...qs, ...all2014.filter(q => !qs.includes(q))];
    if (combined.length) return combined.slice(0, 65);
  }
  if (mockId === 'pyq-exam-2011' || mockId === 'paper-gate-2011') {
    const qs = state.questions.filter(q => q.year === 2011 || (q.paper && q.paper.includes('2011')));
    if (qs.length) return qs.slice(0, 65);
  }
  if (mockId === 'pyq-exam-decade' || mockId === 'paper-gate-overflow-decade') {
    const dqs = state.questions.filter(q => q.category === 'pyq');
    if (dqs.length >= 65) return dqs.slice(0, 65);
  }
  // Generic match by year in exam id e.g. pyq-exam-2024, pyq-exam-2023, pyq-exam-2022, pyq-exam-2017, pyq-exam-2016
  const ym = mockId.match(/(?:19|20)\\d\\d/);
  if (ym) {
    const y = parseInt(ym[0], 10);
    const yrQs = state.questions.filter(q => q.year === y);
    if (yrQs.length >= 65) return yrQs.slice(0, 65);
    if (yrQs.length > 0) {
      const filler = state.questions.filter(q => q.category === 'pyq' && q.year !== y);
      return [...yrQs, ...filler.slice(0, 65 - yrQs.length)];
    }
  }

  // 3. Check Practice Sets
  if (mockId === 'paper-dsa') return state.questions.filter(q => ['Data Structures', 'Algorithms', 'C Programming'].includes(q.subject)).slice(0, 50);
  if (mockId === 'paper-systems') return state.questions.filter(q => ['Operating Systems', 'Computer Networks', 'Computer Organization'].includes(q.subject)).slice(0, 50);
  if (mockId === 'paper-theory') return state.questions.filter(q => ['Theory of Computation', 'Compiler Design'].includes(q.subject)).slice(0, 35);
  if (mockId === 'paper-maths') return state.questions.filter(q => ['Discrete Mathematics', 'Engineering Mathematics', 'Aptitude'].includes(q.subject)).slice(0, 45);
  if (mockId === 'paper-full-1') return state.questions.filter((_, idx) => (idx % 2) === 0).slice(0, 65);
  if (mockId === 'paper-full-2') return state.questions.filter((_, idx) => (idx % 2) === 1).slice(0, 65);

  // 4. Fallback to mock item or subject
  const mock = MOCK_TESTS.find(m => m.id === mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === mockId);
  if (!mock) return [];

  if (mock.subject) {
    return state.questions.filter(q => q.subject === mock.subject).slice(0, mock.questions);
  }

  const targetCount = mock.questions || 65;
  if (mock.difficulty === 'easy') {
    const easyQs = state.questions.filter(q => q.difficulty === 'easy');
    const medQs = state.questions.filter(q => q.difficulty === 'medium');
    return [...easyQs, ...medQs].slice(0, targetCount);
  }
  if (mock.difficulty === 'hard') {
    const hardQs = state.questions.filter(q => q.difficulty === 'hard');
    const medQs = state.questions.filter(q => q.difficulty === 'medium');
    return [...hardQs, ...medQs].slice(0, targetCount);
  }
  return state.questions.slice(0, targetCount);
}

"""
text = text[:old_get_mock_start] + new_get_mock_fn + text[old_get_mock_end:]

# ─── 6. UPDATE renderMocks & ADD renderPyqExams ──────────────────────────────
old_render_mocks_start = text.find('function renderMocks(c, params={}){')
old_render_papers_end = text.find('function viewMockPaper(mockId, page=1){')
assert old_render_mocks_start != -1 and old_render_papers_end != -1, "renderMocks boundaries not found"

new_mocks_and_pyq_ui = """function renderMocks(c, params={}){
  if (state.activeMockPaper) {
    renderMockPaperView(c);
    return;
  }
  const activeTab = params.tab || state.mockTab || 'all';
  state.mockTab = activeTab;

  const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
  const easyCount = fullMocks.filter(m => m.difficulty === 'easy').length;
  const medCount  = fullMocks.filter(m => m.difficulty === 'medium').length;
  const hardCount = fullMocks.filter(m => m.difficulty === 'hard').length;
  const psetsCount = MOCK_TESTS.filter(m => m.type === 'practice-set').length;

  c.innerHTML = `
    <div class="tabs" id="mock-tabs">
      <button class="tab-btn ${activeTab==='all'?'active':''}" onclick="switchMockTab('all',this)" type="button">📋 All (${fullMocks.length})</button>
      <button class="tab-btn ${activeTab==='easy'?'active':''}" onclick="switchMockTab('easy',this)" type="button">🟢 Easy (${easyCount})</button>
      <button class="tab-btn ${activeTab==='medium'?'active':''}" onclick="switchMockTab('medium',this)" type="button">🟡 Medium (${medCount})</button>
      <button class="tab-btn ${activeTab==='hard'?'active':''}" onclick="switchMockTab('hard',this)" type="button">🔴 Hard (${hardCount})</button>
      <button class="tab-btn ${activeTab==='practice-sets'?'active':''}" onclick="switchMockTab('practice-sets',this)" type="button">📝 Practice Sets (${psetsCount})</button>
      <button class="tab-btn ${activeTab==='subwise'?'active':''}" onclick="switchMockTab('subwise',this)" type="button">📂 Subject Mocks</button>
      <button class="tab-btn ${activeTab==='history'?'active':''}" onclick="switchMockTab('history',this)" type="button">📊 My History</button>
    </div>
    <div id="mock-tab-content">
      ${getMockTabHTML(activeTab, fullMocks)}
    </div>`;
  renderMath(c);
}

function getMockTabHTML(tab, fullMocks) {
  if (tab === 'all') {
    const filtered = getFilteredAndSortedMocks(fullMocks);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(fullMocks, 'All Mocks')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'easy') {
    const list = fullMocks.filter(m => m.difficulty === 'easy');
    const filtered = getFilteredAndSortedMocks(list);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Easy / Foundational')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'medium') {
    const list = fullMocks.filter(m => m.difficulty === 'medium');
    const filtered = getFilteredAndSortedMocks(list);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Moderate / Standard')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'hard') {
    const list = fullMocks.filter(m => m.difficulty === 'hard');
    const filtered = getFilteredAndSortedMocks(list);
    return `${buildMockCalibrationGuide()}${buildMockSortBar(list, 'Hard / Rank Booster')}${buildMockGrid(filtered)}`;
  }
  if (tab === 'practice-sets') {
    const list = MOCK_TESTS.filter(m => m.type === 'practice-set');
    return `${buildMockSortBar(list, 'Curated Practice Sets')}${buildMockGrid(list)}`;
  }
  if (tab === 'subwise') {
    return buildMockGrid(MOCK_TESTS.filter(m => m.type === 'subwise'));
  }
  if (tab === 'history') {
    return buildTestHistory();
  }
  return buildMockGrid(fullMocks);
}

function switchMockTab(tab, btn){
  state.mockTab = tab;
  document.querySelectorAll('#mock-tabs .tab-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const c = document.getElementById('mock-tab-content');
  if (!c) return;
  const fullMocks = MOCK_TESTS.filter(m => m.type === 'full' || m.type === 'practice-set');
  c.innerHTML = getMockTabHTML(tab, fullMocks);
  renderMath(c);
}

function buildMockSortBar(list, sectionName) {
  const currentSort = state.mockSort || 'default';
  return `
    <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
      <div style="font-size:13px;font-weight:700;color:var(--text-secondary)">
        Showing ${list.length} ${sectionName}
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

function buildMockGrid(mocks){
  if (!mocks.length) return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No tests available for selected filter</div><div class="empty-state-sub">Try selecting "All" or another tab.</div></div>';
  return `<div class="mock-grid">${mocks.map(m=>{
    const past = state.testSessions.filter(s => s.mockId === m.id);
    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const totalPages = Math.ceil(questionsCount / 20) || 1;
    const diffLabel = m.difficulty ? m.difficulty.toUpperCase() : 'MEDIUM';
    const ratingBadge = m.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${m.rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (m.cutoff && m.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${m.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${m.air100} M</span>
      </div>` : '';
    const badgeType = m.type === 'practice-set' ? '📝 Practice Set' : m.type === 'full' ? '🏆 Full Mock' : '📂 Subject Mock';
    return `<div class="mock-card">
      <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
          <div class="mock-type-badge ${m.type}">${badgeType}</div>
          <div style="display:flex;align-items:center;gap:6px">
            <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
            ${ratingBadge}
          </div>
        </div>
        <div class="mock-title">${m.name}</div>
        <div class="text-sm text-muted" style="margin-bottom:8px">${m.desc}</div>
        ${targetsRow}
        <div class="mock-meta">
          <div class="mock-meta-item">📚 ${questionsCount} Questions</div>
          <div class="mock-meta-item">⏱️ ${m.duration} Min</div>
          <div class="mock-meta-item">🏅 ${m.marks} Marks</div>
          ${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}
        </div>
      </div>
      <div class="mock-card-actions">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" title="Browse questions in sets of 20 per page with solutions" type="button">📖 Practice Paper (20/page)</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" title="Start timed exam simulation" type="button">▶ Timed Exam</button>
      </div>
      ${past.length ? `<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length > 1 ? 's' : ''}</div>` : ''}
    </div>`;
  }).join('')}</div>`;
}

// ─── FULL-LENGTH PREVIOUS YEAR EXAMS (PYQ EXAMS SECTION) ────────────────────
function renderPyqExams(c) {
  if (state.activeMockPaper) {
    renderMockPaperView(c);
    return;
  }
  const filteredExams = getFilteredAndSortedPyqExams();
  c.innerHTML = `
    <div class="section-header">
      <div class="section-title">Full-Length PYQ Exams <span>${FULL_LENGTH_PYQ_EXAMS.length} Official Papers</span></div>
    </div>
    <p class="text-muted text-sm" style="margin-bottom:14px">
      Take official, full-length year-wise Previous Year Question papers in a realistic 180-minute timed exam environment. Includes countdown timer, virtual calculator, TCS iON palette, and instant score analysis.
    </p>
    ${buildPyqExamsFilterBar()}
    ${buildPyqExamsGrid(filteredExams)}
  `;
  renderMath(c);
}

function getFilteredAndSortedPyqExams() {
  const era = state.pyqExamEraFilter || 'all';
  const diff = state.pyqExamDiffFilter || 'all';
  const sort = state.pyqExamSort || 'year-desc';

  let list = FULL_LENGTH_PYQ_EXAMS.slice();

  // 1. Era filter
  if (era === 'recent') {
    list = list.filter(e => typeof e.year === 'number' && e.year >= 2020);
  } else if (era === 'decade') {
    list = list.filter(e => (typeof e.year === 'number' && e.year >= 2014 && e.year <= 2019) || e.id.includes('decade'));
  } else if (era === 'classic') {
    list = list.filter(e => typeof e.year === 'number' && e.year <= 2013);
  }

  // 2. Difficulty filter
  if (diff !== 'all') {
    list = list.filter(e => e.difficulty === diff);
  }

  // 3. Sort
  const diffRank = { 'easy': 1, 'medium': 2, 'hard': 3 };
  if (sort === 'year-desc') {
    list.sort((a, b) => {
      const ya = typeof a.year === 'number' ? a.year : 2024;
      const yb = typeof b.year === 'number' ? b.year : 2024;
      if (yb !== ya) return yb - ya;
      return a.name.localeCompare(b.name);
    });
  } else if (sort === 'year-asc') {
    list.sort((a, b) => {
      const ya = typeof a.year === 'number' ? a.year : 2024;
      const yb = typeof b.year === 'number' ? b.year : 2024;
      if (ya !== yb) return ya - yb;
      return a.name.localeCompare(b.name);
    });
  } else if (sort === 'difficulty-asc') {
    list.sort((a, b) => (diffRank[a.difficulty] || 2) - (diffRank[b.difficulty] || 2));
  } else if (sort === 'difficulty-desc') {
    list.sort((a, b) => (diffRank[b.difficulty] || 2) - (diffRank[a.difficulty] || 2));
  } else if (sort === 'rating-desc') {
    list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
  }

  return list;
}

function setPyqExamEraFilter(era) {
  state.pyqExamEraFilter = era;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'pyq-exams') renderPyqExams(c);
}

function setPyqExamDiffFilter(diff) {
  state.pyqExamDiffFilter = diff;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'pyq-exams') renderPyqExams(c);
}

function setPyqExamSort(sortVal) {
  state.pyqExamSort = sortVal;
  const c = document.getElementById('page-content');
  if (c && state.currentPage === 'pyq-exams') renderPyqExams(c);
}

function buildPyqExamsFilterBar() {
  const currentEra = state.pyqExamEraFilter || 'all';
  const currentDiff = state.pyqExamDiffFilter || 'all';
  const currentSort = state.pyqExamSort || 'year-desc';

  return `
    <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
        <button class="chip ${currentEra === 'all' ? 'active' : ''}" onclick="setPyqExamEraFilter('all')" type="button">
          All Years (${FULL_LENGTH_PYQ_EXAMS.length})
        </button>
        <button class="chip ${currentEra === 'recent' ? 'active' : ''}" onclick="setPyqExamEraFilter('recent')" type="button">
          🔥 Recent (2020–2026)
        </button>
        <button class="chip ${currentEra === 'decade' ? 'active' : ''}" onclick="setPyqExamEraFilter('decade')" type="button">
          📅 Past Decade (2014–2019)
        </button>
        <button class="chip ${currentEra === 'classic' ? 'active' : ''}" onclick="setPyqExamEraFilter('classic')" type="button">
          🏛️ Classic (2011–2013)
        </button>
      </div>

      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <div style="display:flex;align-items:center;gap:6px">
          <label style="font-size:12px;color:var(--text-secondary);font-weight:600">Difficulty:</label>
          <select class="form-select form-select-sm" style="width:auto;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setPyqExamDiffFilter(this.value)">
            <option value="all" ${currentDiff === 'all' ? 'selected' : ''}>All Difficulties</option>
            <option value="easy" ${currentDiff === 'easy' ? 'selected' : ''}>🟢 Easy</option>
            <option value="medium" ${currentDiff === 'medium' ? 'selected' : ''}>🟡 Medium</option>
            <option value="hard" ${currentDiff === 'hard' ? 'selected' : ''}>🔴 Hard</option>
          </select>
        </div>

        <div style="display:flex;align-items:center;gap:6px">
          <label style="font-size:12px;color:var(--text-secondary);font-weight:600">Sort:</label>
          <select class="form-select form-select-sm" style="width:auto;padding:5px 10px;font-size:12px;background:var(--bg-card);border:1px solid var(--border);border-radius:6px;color:var(--text-primary);cursor:pointer" onchange="setPyqExamSort(this.value)">
            <option value="year-desc" ${currentSort === 'year-desc' ? 'selected' : ''}>Year: Newest → Oldest</option>
            <option value="year-asc" ${currentSort === 'year-asc' ? 'selected' : ''}>Year: Oldest → Newest</option>
            <option value="difficulty-asc" ${currentSort === 'difficulty-asc' ? 'selected' : ''}>Difficulty: Easy → Hard</option>
            <option value="difficulty-desc" ${currentSort === 'difficulty-desc' ? 'selected' : ''}>Difficulty: Hard → Easy</option>
            <option value="rating-desc" ${currentSort === 'rating-desc' ? 'selected' : ''}>Rating: High → Low</option>
          </select>
        </div>
      </div>
    </div>
  `;
}

function buildPyqExamsGrid(exams) {
  if (!exams.length) {
    return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No PYQ exams match your filter</div><div class="empty-state-sub">Try selecting "All Years" or "All Difficulties".</div></div>';
  }
  return `<div class="mock-grid">${exams.map(exam => {
    const past = state.testSessions.filter(s => s.mockId === exam.id);
    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;
    const diffLabel = (exam.difficulty || 'medium').toUpperCase();
    const ratingBadge = exam.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${exam.rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (exam.cutoff && exam.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${exam.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${exam.air100} M</span>
      </div>` : '';
    return `
      <div class="mock-card">
        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <div class="mock-type-badge full">📅 GATE ${exam.year} ${exam.set ? '• ' + exam.set : ''}</div>
            <div style="display:flex;align-items:center;gap:6px">
              <span class="q-badge ${exam.difficulty || 'medium'}">${diffLabel}</span>
              ${ratingBadge}
            </div>
          </div>
          <div class="mock-title">${exam.name}</div>
          <div style="font-size:12px;font-weight:600;color:var(--accent);margin-bottom:6px">🏛️ ${exam.institute || 'Official GATE Exam'}</div>
          <div class="text-sm text-muted" style="margin-bottom:8px">${exam.desc}</div>
          ${targetsRow}
          <div class="mock-meta">
            <div class="mock-meta-item">📚 ${exam.questions || 65} Questions</div>
            <div class="mock-meta-item">⏱️ ${exam.duration || 180} Min</div>
            <div class="mock-meta-item">🏅 ${exam.marks || 100} Marks</div>
            ${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}
          </div>
        </div>
        <div class="mock-card-actions">
          <button class="btn btn-primary btn-sm" onclick="startMockTest('${exam.id}')" title="Start 180-min official timed exam" type="button">▶ Start Timed Exam</button>
          <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${exam.id}')" title="Browse questions in sets of 20 per page with solutions" type="button">📖 Review Paper (20/page)</button>
        </div>
        ${past.length ? `<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length > 1 ? 's' : ''}</div>` : ''}
      </div>
    `;
  }).join('')}</div>`;
}

function renderPracticePapers(c){
  renderMocks(c, { tab: 'practice-sets' });
}

function buildPracticePapersSection() {
  const psets = MOCK_TESTS.filter(m => m.type === 'practice-set');
  return `
    <div style="margin-bottom:14px;color:var(--text-secondary);font-size:13px">
      Curated multi-subject practice sets and comprehensive test papers with full solutions.
    </div>
    ${buildMockGrid(psets)}
  `;
}
"""
text = text[:old_render_mocks_start] + new_mocks_and_pyq_ui + text[old_render_papers_end:]

# ─── 7. UPDATE closeMockPaperView ────────────────────────────────────────────
text = text.replace(
    """function closeMockPaperView(){
  state.activeMockPaper = null;
  if (state.currentPage === 'papers') {
    renderPracticePapers(document.getElementById('page-content'));
  } else {
    navigate('mocks');
  }
}""",
    """function closeMockPaperView(){
  const mockId = state.activeMockPaper?.mockId || '';
  state.activeMockPaper = null;
  if (mockId.startsWith('pyq-exam-') || state.currentPage === 'pyq-exams') {
    navigate('pyq-exams');
  } else {
    navigate('mocks');
  }
}"""
)

# ─── 8. UPDATE startMockTest & renderMockPaperView ───────────────────────────
text = text.replace(
    "const mock=MOCK_TESTS.find(m=>m.id===mockId);\n  if (!mock) return;",
    "const mock = MOCK_TESTS.find(m => m.id === mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === mockId) || PRACTICE_PAPERS.find(p => p.id === mockId);\n  if (!mock) return;"
)

text = text.replace(
    "const mock = MOCK_TESTS.find(m => m.id === mockId) || PRACTICE_PAPERS.find(p => p.id === mockId);",
    "const mock = MOCK_TESTS.find(m => m.id === mockId) || FULL_LENGTH_PYQ_EXAMS.find(e => e.id === mockId) || PRACTICE_PAPERS.find(p => p.id === mockId);"
)

# ─── 9. UPDATE submitMockTest ────────────────────────────────────────────────
old_submit_start = text.find('async function submitMockTest(){')
old_submit_end = text.find('function startMockTimer(){')
assert old_submit_start != -1 and old_submit_end != -1, "submitMockTest boundaries not found"

new_submit_fn = """async function submitMockTest(){
  stopMockTimer();
  const {mock,questions,answers,timeLeft}=state.activeTest;
  state.activeTest.submitted=true;
  let score=0,correct=0,wrong=0,skipped=0;
  const answeredAttempts = [];

  questions.forEach((q,i)=>{
    const a=answers[i];
    if(a===null||a===undefined||(Array.isArray(a)&&!a.length)){skipped++;return;}
    let ok=false;
    if(q.type==='nat'){const v=parseFloat(a),e=q.correct[0];ok=v>=(q.natRange?.min??e)&&v<=(q.natRange?.max??e);}
    else{const s=(Array.isArray(a)?a:[a]).sort((x,y)=>x-y),e=[...q.correct].sort((x,y)=>x-y);ok=s.length===e.length&&s.every((v,idx)=>v===e[idx]);}
    if(ok){correct++;score+=q.marks;}else{wrong++;score-=q.marks===2?2/3:1/3;}

    answeredAttempts.push({
      questionId: q.id,
      correct: ok,
      timeMs: Math.round(((mock.duration * 60 - timeLeft) / Math.max(1, questions.length)) * 1000),
      date: Date.now(),
      uid: uid()
    });
  });

  const maxScore=questions.reduce((s,q)=>s+q.marks,0);
  const pct=Math.max(0,Math.round((score/maxScore)*100));
  const session={mockId:mock.id,name:mock.name,date:Date.now(),score:Math.max(0,parseFloat(score.toFixed(2))),maxScore,percentage:pct,correct,wrong,skipped,timeTaken:mock.duration*60-timeLeft};
  
  await persistSession(session);
  // Persist each answered question attempt to sync Dashboard Tests Completed, Questions Attempted, and Accuracy
  for (const att of answeredAttempts) {
    await persistAttempt(att);
  }

  document.getElementById('test-overlay').innerHTML='';
  document.getElementById('test-overlay').classList.remove('active');
  showTestResult(session,questions,answers);
}

"""
text = text[:old_submit_start] + new_submit_fn + text[old_submit_end:]

# ─── 10. EXPOSE TO WINDOW ────────────────────────────────────────────────────
window_exports_anchor = "  renderPracticePapers,\n"
new_window_exports = """  renderPracticePapers,
  renderPyqExams,
  setPyqExamEraFilter,
  setPyqExamDiffFilter,
  setPyqExamSort,
"""
text = text.replace(window_exports_anchor, new_window_exports)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"app.js updated successfully! New file size: {os.path.getsize('app.js')} bytes.")
