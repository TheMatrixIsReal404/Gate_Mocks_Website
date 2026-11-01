# scripts/update_syllabus_guide.py
with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target_str = """function renderSubjects(c) {
  c.innerHTML=`
    <div class="section-header"><div class="section-title">All Subjects <span>${SUBJECTS.length} available</span></div></div>
    <div class="subjects-grid">${buildSubjectCards()}</div>`;
}"""

new_code = """function toggleSyllabusGuide() {
  const body = document.getElementById('syllabus-guide-body');
  const icon = document.getElementById('syllabus-toggle-icon');
  if (body) {
    const isHidden = body.style.display === 'none';
    body.style.display = isHidden ? 'grid' : 'none';
    if (icon) icon.textContent = isHidden ? '▲ Hide Guide' : '▼ View Full Syllabus';
  }
}

function jumpToSubjectPYQs(subName) {
  state.selectedTopicPyqSubject = subName;
  state.topicPyqTab = 'chapters';
  state.topicPyqExpandedTopic = null;
  navigate('topic-pyqs');
}

function buildOfficialSyllabusGuideHTML() {
  const sections = [
    {
      num: 'Section 1',
      title: 'Engineering Mathematics',
      subject: 'Engineering Mathematics',
      topics: [
        { label: 'Discrete Mathematics', text: 'Propositional and first order logic. Sets, relations, functions, partial orders and lattices. Monoids, Groups. Graphs: connectivity, matching, coloring. Combinatorics: counting, recurrence relations, generating functions.' },
        { label: 'Linear Algebra', text: 'Matrices, determinants, system of linear equations, eigenvalues and eigenvectors, LU decomposition.' },
        { label: 'Calculus', text: 'Limits, continuity and differentiability. Maxima and minima. Mean value theorem. Integration.' },
        { label: 'Probability & Statistics', text: 'Random variables. Uniform, normal, exponential, Poisson and binomial distributions. Mean, median, mode and standard deviation. Conditional probability and Bayes theorem.' }
      ]
    },
    {
      num: 'Section 2',
      title: 'Digital Logic',
      subject: 'Digital Logic',
      topics: [
        { label: 'Core Topics', text: 'Boolean algebra. Combinational and sequential circuits. Minimization (algebraic technique, K-maps, tabular method). Number representations and computer arithmetic (fixed and floating point).' }
      ]
    },
    {
      num: 'Section 3',
      title: 'Computer Organization & Architecture',
      subject: 'Computer Organization',
      topics: [
        { label: 'Core Topics', text: 'Machine instructions and addressing modes. ALU, data-path and control unit (hardwired and microprogrammed). Instruction pipelining, pipeline hazards. Memory hierarchy: cache, main memory and secondary storage; I/O interface (interrupt and DMA mode).' }
      ]
    },
    {
      num: 'Section 4',
      title: 'Programming & Data Structures',
      subject: 'Data Structures',
      topics: [
        { label: 'Core Topics', text: 'Programming in C. Recursion. Arrays, stacks, queues, linked lists, trees, binary search trees, binary heaps, graphs.' }
      ]
    },
    {
      num: 'Section 5',
      title: 'Algorithms',
      subject: 'Algorithms',
      topics: [
        { label: 'Core Topics', text: 'Searching, sorting, hashing. Asymptotic worst case time and space complexity. Algorithm design techniques: greedy, dynamic programming and divide-and-conquer. Graph traversals, minimum spanning trees, shortest paths.' }
      ]
    },
    {
      num: 'Section 6',
      title: 'Theory of Computation',
      subject: 'Theory of Computation',
      topics: [
        { label: 'Core Topics', text: 'Regular expressions and finite automata. Context-free grammars and push-down automata. Regular and context-free languages, pumping lemma. Turing machines and undecidability.' }
      ]
    },
    {
      num: 'Section 7',
      title: 'Compiler Design',
      subject: 'Compiler Design',
      topics: [
        { label: 'Core Topics', text: 'Lexical analysis, parsing, syntax-directed translation. Runtime environments. Intermediate code generation. Local optimisation, Data flow analyses: constant propagation, liveness analysis, common subexpression elimination.' }
      ]
    },
    {
      num: 'Section 8',
      title: 'Operating System',
      subject: 'Operating Systems',
      topics: [
        { label: 'Core Topics', text: 'System calls, processes, threads, inter-process communication, concurrency and synchronization, deadlocks. CPU and I/O scheduling. Memory management and virtual memory. File systems.' }
      ]
    },
    {
      num: 'Section 9',
      title: 'Databases',
      subject: 'DBMS',
      topics: [
        { label: 'Core Topics', text: 'ER-model. Relational model: relational algebra, tuple calculus, SQL. Integrity constraints, normal forms. File organization, indexing (e.g., B and B+ trees). Transactions and concurrency control.' }
      ]
    },
    {
      num: 'Section 10',
      title: 'Computer Networks',
      subject: 'Computer Networks',
      topics: [
        { label: 'Core Topics', text: 'Concept of layering: OSI and TCP/IP protocol stacks; Basics of packet, circuit and virtual circuit switching; Data link layer: framing, error detection, Medium Access Control, Ethernet bridging; Routing protocols: shortest path, flooding, distance vector and link state routing; Fragmentation and IP addressing (IPv4, CIDR, NAT); Transport layer: flow control and congestion control, UDP, TCP, sockets; Application layer protocols: DNS, SMTP, HTTP, FTP, Email.' }
      ]
    },
    {
      num: 'General Aptitude',
      title: 'General Aptitude (GA)',
      subject: 'Aptitude',
      topics: [
        { label: 'Verbal & Quantitative', text: 'Basic English grammar, vocabulary, reading comprehension, narrative sequencing. Data interpretation, numerical computation and estimation (ratios, percentages, powers, exponents, series, permutations, combinations).' },
        { label: 'Analytical & Spatial', text: 'Logic, deduction, analogy, numerical relations and reasoning. Transformation of shapes: translation, rotation, scaling, mirroring, paper folding, and patterns in 2D and 3D.' }
      ]
    }
  ];

  return `
    <div class="syllabus-guide-card">
      <div class="syllabus-guide-header" onclick="toggleSyllabusGuide()">
        <div class="syllabus-guide-title">
          <span>🏛️</span>
          <span>Official GATE CSE Syllabus Guide (IIT Madras Standards)</span>
          <span class="badge" style="background:rgba(99,102,241,0.2);color:#818cf8;font-size:11px;font-weight:700">10 Sections + GA Verbatim</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <span style="font-size:12px;color:var(--text-muted)">Latest Official Pattern</span>
          <button class="btn btn-secondary btn-sm" id="syllabus-toggle-icon" type="button" style="padding:4px 10px;font-size:12px">
            ▲ Hide Guide
          </button>
        </div>
      </div>
      <div class="syllabus-sections-grid" id="syllabus-guide-body">
        ${sections.map(s => `
          <div class="syllabus-sec-card">
            <div class="syllabus-sec-header">
              <span class="syllabus-sec-title">${escapeHtml(s.num)}: ${escapeHtml(s.title)}</span>
              <span class="chip" style="font-size:10px">${escapeHtml(s.subject)}</span>
            </div>
            <div class="syllabus-sec-desc">
              ${s.topics.map(t => `<p style="margin-bottom:6px"><strong>${escapeHtml(t.label)}:</strong> ${escapeHtml(t.text)}</p>`).join('')}
            </div>
            <div class="syllabus-sec-actions">
              <button class="btn btn-primary btn-sm" onclick="navigate('practice', { subject: '${escapeHtml(s.subject)}' })" style="padding:3px 10px;font-size:11px" type="button">
                ▶ Practice
              </button>
              <button class="btn btn-secondary btn-sm" onclick="jumpToSubjectPYQs('${escapeHtml(s.subject)}')" style="padding:3px 10px;font-size:11px" type="button">
                📑 PYQ Chapters
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function renderSubjects(c) {
  c.innerHTML=`
    ${buildOfficialSyllabusGuideHTML()}
    <div class="section-header"><div class="section-title">All Subjects <span>${SUBJECTS.length} available</span></div></div>
    <div class="subjects-grid">${buildSubjectCards()}</div>`;
}"""

# Normalize newlines for matching
normalized_content = content.replace('\r\n', '\n')
if target_str in normalized_content:
    normalized_content = normalized_content.replace(target_str, new_code, 1)
    print('Replaced renderSubjects successfully!')
else:
    print('target_str not found!')

# Now add window exports
export_target = '  setTopicPyqType,'
export_addition = """  setTopicPyqType,
  toggleSyllabusGuide,
  jumpToSubjectPYQs,
  buildOfficialSyllabusGuideHTML,"""

if export_target in normalized_content:
    normalized_content = normalized_content.replace(export_target, export_addition, 1)
    print('Export added successfully!')
else:
    print('export_target not found!')

with open('app.js', 'w', encoding='utf-8', newline='') as f:
    f.write(normalized_content)
print('Script finished successfully!')
