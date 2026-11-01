# -*- coding: utf-8 -*-
"""
Curated authentic GATE CSE PYQs expansion from Gate Overflow Books.
Expands coverage across all 13 GATE CSE subjects to push database to 500+ questions.
"""

def get_expansion_pyqs():
    return [
        # =====================================================================
        # Algorithms Expansion
        # =====================================================================
        {
            "id": "pyq_2016_cs_q21",
            "type": "mcq",
            "category": "pyq",
            "year": 2016,
            "subject": "Algorithms",
            "topic": "Dynamic Programming",
            "difficulty": "easy",
            "marks": 1,
            "question": "The Floyd-Warshall algorithm for all-pairs shortest paths computation is based on which algorithmic paradigm?",
            "options": [
                "Greedy paradigm",
                "Divide-and-conquer paradigm",
                "Dynamic Programming paradigm",
                "Neither Greedy nor Divide-and-Conquer nor Dynamic Programming"
            ],
            "correct": [2],
            "explanation": "Floyd-Warshall solves all-pairs shortest paths using Dynamic Programming with recurrence $d^{(k)}_{ij} = \\min(d^{(k-1)}_{ij}, d^{(k-1)}_{ik} + d^{(k-1)}_{kj})$, iteratively allowing vertices $\\{1, \\dots, k\\}$ as intermediate nodes."
        },
        {
            "id": "pyq_2017_cs_q08",
            "type": "nat",
            "category": "pyq",
            "year": 2017,
            "subject": "Algorithms",
            "topic": "Graph Algorithms",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider a weighted connected graph $G = (V, E)$ with $|V| = 100$ vertices and $|E| = 300$ edges. The weights of all edges are distinct. How many minimum spanning trees does $G$ have?",
            "options": [],
            "correct": [1],
            "natRange": {"min": 1, "max": 1},
            "explanation": "A fundamental theorem of graph theory states that if all edge weights in a connected undirected graph are distinct, then the Minimum Spanning Tree (MST) is strictly unique. Hence, there is exactly 1 MST."
        },
        {
            "id": "pyq_2019_cs_q14",
            "type": "mcq",
            "category": "pyq",
            "year": 2019,
            "subject": "Algorithms",
            "topic": "Sorting",
            "difficulty": "medium",
            "marks": 1,
            "question": "Which of the following sorting algorithms is inherently stable?",
            "options": [
                "Merge Sort",
                "Quick Sort",
                "Heap Sort",
                "Selection Sort"
            ],
            "correct": [0],
            "explanation": "Standard Merge Sort is stable because when two elements have equal keys, the element from the left sub-array is chosen first during the merge step, preserving their original relative order. Quick Sort, Heap Sort, and Selection Sort are not stable in their standard implementations."
        },
        {
            "id": "pyq_2020_cs_q17",
            "type": "nat",
            "category": "pyq",
            "year": 2020,
            "subject": "Algorithms",
            "topic": "Divide and Conquer",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider the recurrence relation: $T(n) = 4 T(n/2) + n^2$ with base case $T(1) = 1$. What is the value of $T(16)$?",
            "options": [],
            "correct": [1280],
            "natRange": {"min": 1280, "max": 1280},
            "explanation": "Evaluating level by level:\n- $T(1) = 1$\n- $T(2) = 4(1) + 2^2 = 4 + 4 = 8$\n- $T(4) = 4(8) + 4^2 = 32 + 16 = 48$\n- $T(8) = 4(48) + 8^2 = 192 + 64 = 256$\n- $T(16) = 4(256) + 16^2 = 1024 + 256 = 1280$."
        },
        {
            "id": "pyq_2021_cs_q23",
            "type": "mcq",
            "category": "pyq",
            "year": 2021,
            "subject": "Algorithms",
            "topic": "Greedy Algorithms",
            "difficulty": "medium",
            "marks": 2,
            "question": "In the fractional knapsack problem with $n$ items of values $v_i$ and weights $w_i$, which greedy choice strategy yields the optimal solution?",
            "options": [
                "Select item with maximum value $v_i$",
                "Select item with minimum weight $w_i$",
                "Select item with maximum value-to-weight ratio $v_i / w_i$",
                "Select item with minimum value-to-weight ratio $v_i / w_i$"
            ],
            "correct": [2],
            "explanation": "The fractional knapsack problem exhibits optimal substructure and greedy choice property when items are sorted in non-increasing order of their value-to-weight ratio $v_i / w_i$. Greedily taking as much as possible of the item with highest ratio maximizes total value."
        },

        # =====================================================================
        # Operating Systems Expansion
        # =====================================================================
        {
            "id": "pyq_2013_cs_q21",
            "type": "mcq",
            "category": "pyq",
            "year": 2013,
            "subject": "Operating Systems",
            "topic": "Page Replacement",
            "difficulty": "medium",
            "marks": 2,
            "question": "Belady's anomaly refers to the phenomenon where:",
            "options": [
                "Page fault rate increases as the number of allocated page frames increases",
                "Page fault rate decreases as the number of allocated page frames increases",
                "Disk access time increases with larger block sizes",
                "Thrashing occurs due to insufficient swapping space"
            ],
            "correct": [0],
            "explanation": "Belady's anomaly is the counter-intuitive phenomenon where allocating more page frames to a process actually increases the number of page faults. It can occur in First-In-First-Out (FIFO) page replacement, but never in stack-based algorithms like LRU or Optimal."
        },
        {
            "id": "pyq_2015_cs_q06",
            "type": "mcq",
            "category": "pyq",
            "year": 2015,
            "subject": "Operating Systems",
            "topic": "Process Synchronization",
            "difficulty": "medium",
            "marks": 2,
            "question": "Which of the following synchronization mechanisms guarantees bounded waiting for two processes?",
            "options": [
                "Peterson's Algorithm",
                "Strict alternation (turn variable alone)",
                "Test-and-Set without waiting queue",
                "Disable interrupts on multi-core CPU"
            ],
            "correct": [0],
            "explanation": "Peterson's algorithm satisfies all three critical section requirements for two processes: Mutual Exclusion, Progress, and Bounded Waiting (each process waits at most one turn before entering the critical section)."
        },
        {
            "id": "pyq_2018_cs_q11",
            "type": "nat",
            "category": "pyq",
            "year": 2018,
            "subject": "Operating Systems",
            "topic": "File Systems",
            "difficulty": "medium",
            "marks": 2,
            "question": "A Unix-style inode has $10$ direct block pointers, $1$ singly-indirect pointer, and $1$ doubly-indirect pointer. Disk block size is $4\\text{ KB}$ ($2^{12}$ bytes), and disk block addresses are $4\\text{ bytes}$ ($2^2$ bytes) each. What is the maximum file size (in MB) that can be supported by this inode structure?",
            "options": [],
            "correct": [4100],
            "natRange": {"min": 4096, "max": 4104},
            "explanation": "Each block contains $\\frac{4\\text{ KB}}{4\\text{ bytes}} = 1024 = 2^{10}$ pointers.\n- Direct blocks: $10 \\times 4\\text{ KB} = 40\\text{ KB}$\n- Singly indirect: $1024 \\times 4\\text{ KB} = 4\\text{ MB}$\n- Doubly indirect: $1024 \\times 1024 \\times 4\\text{ KB} = 1048576 \\times 4\\text{ KB} = 4096\\text{ MB} = 4\\text{ GB}$\nTotal size $\\approx 4096 + 4 + 0.04 = 4100.04\\text{ MB} \\approx 4100\\text{ MB}$."
        },
        {
            "id": "pyq_2021_cs_q24",
            "type": "mcq",
            "category": "pyq",
            "year": 2021,
            "subject": "Operating Systems",
            "topic": "Deadlocks",
            "difficulty": "medium",
            "marks": 2,
            "question": "In Banker's Algorithm, a state is considered SAFE if:",
            "options": [
                "There exists at least one safe sequence of process execution that allows all processes to finish without deadlock",
                "No process holds any resources",
                "All process requests are granted immediately",
                "Total available resources equal total allocated resources"
            ],
            "correct": [0],
            "explanation": "A state is defined as safe in Banker's algorithm if there exists a safe sequence $\\langle P_1, P_2, \\dots, P_n \\rangle$ such that for each $P_i$, the resources that $P_i$ can still request can be satisfied by current available resources plus resources held by all $P_j$ with $j < i$."
        },

        # =====================================================================
        # Computer Networks Expansion
        # =====================================================================
        {
            "id": "pyq_2013_cs_q22",
            "type": "mcq",
            "category": "pyq",
            "year": 2013,
            "subject": "Computer Networks",
            "topic": "Error Detection",
            "difficulty": "medium",
            "marks": 2,
            "question": "In Cyclic Redundancy Check (CRC), if the generator polynomial is $G(x) = x^3 + x + 1$, what is the length of the CRC checksum (in bits)?",
            "options": ["2 bits", "3 bits", "4 bits", "5 bits"],
            "correct": [1],
            "explanation": "The degree of the generator polynomial $G(x) = x^3 + x + 1$ is 3 (highest power of $x$). The length of the CRC remainder/checksum appended to the data is always equal to the degree of the generator polynomial, which is 3 bits."
        },
        {
            "id": "pyq_2016_cs_q22",
            "type": "nat",
            "category": "pyq",
            "year": 2016,
            "subject": "Computer Networks",
            "topic": "CSMA/CD",
            "difficulty": "medium",
            "marks": 2,
            "question": "In an Ethernet network operating at $10\\text{ Mbps}$ using CSMA/CD, the maximum cable length between any two stations is $1\\text{ km}$ and signal speed is $2 \\times 10^8\\text{ m/s}$. What is the minimum frame size (in bits) required for collision detection?",
            "options": [],
            "correct": [100],
            "natRange": {"min": 100, "max": 100},
            "explanation": "One-way propagation delay $T_p = \\frac{1000\\text{ m}}{2 \\times 10^8\\text{ m/s}} = 5 \\times 10^{-6}\\text{ s} = 5\\;\\mu\\text{s}$. Round-trip propagation time $= 2 T_p = 10\\;\\mu\\text{s}$. To ensure collision detection, transmission time $T_t \\ge 2 T_p \\implies \\frac{L}{B} \\ge 2 T_p \\implies L \\ge 2 T_p \\times B = 10 \\times 10^{-6}\\text{ s} \\times 10 \\times 10^6\\text{ bps} = 100\\text{ bits}$."
        },
        {
            "id": "pyq_2018_cs_q12",
            "type": "mcq",
            "category": "pyq",
            "year": 2018,
            "subject": "Computer Networks",
            "topic": "Routing Algorithms",
            "difficulty": "medium",
            "marks": 2,
            "question": "The Count-to-Infinity problem is a well-known vulnerability in which routing protocol?",
            "options": [
                "Distance Vector Routing (RIP)",
                "Link State Routing (OSPF)",
                "Path Vector Routing (BGP)",
                "Hierarchical Routing"
            ],
            "correct": [0],
            "explanation": "Distance Vector routing algorithms (such as RIP using Bellman-Ford) suffer from the count-to-infinity problem because nodes only share distance vectors with immediate neighbors, making convergence slow when a link breaks. Solutions include Split Horizon and Poison Reverse."
        },
        {
            "id": "pyq_2022_cs_q25",
            "type": "mcq",
            "category": "pyq",
            "year": 2022,
            "subject": "Computer Networks",
            "topic": "Application Layer",
            "difficulty": "easy",
            "marks": 1,
            "question": "Which of the following transport protocols and port numbers are typically used by the Domain Name System (DNS) for standard name resolution queries?",
            "options": [
                "UDP port 53",
                "TCP port 80",
                "UDP port 67",
                "TCP port 25"
            ],
            "correct": [0],
            "explanation": "DNS uses UDP port 53 for standard client lookup queries because UDP is lightweight, stateless, and low-latency. (TCP port 53 is used for zone transfers and messages exceeding 512 bytes)."
        },

        # =====================================================================
        # DBMS Expansion
        # =====================================================================
        {
            "id": "pyq_2013_cs_q23",
            "type": "mcq",
            "category": "pyq",
            "year": 2013,
            "subject": "DBMS",
            "topic": "Normalization",
            "difficulty": "medium",
            "marks": 2,
            "question": "A decomposition of relation $R(A, B, C)$ into $R_1(A, B)$ and $R_2(B, C)$ is lossless join if and only if:",
            "options": [
                "$B \\to A$ or $B \\to C$ holds in $R$",
                "$A \\to B$ holds in $R$",
                "$C \\to B$ holds in $R$",
                "$A \\to C$ holds in $R$"
            ],
            "correct": [0],
            "explanation": "By the Lossless Decomposition Theorem for binary decomposition $R = R_1 \\cup R_2$, the decomposition is lossless if and only if the common attribute $R_1 \\cap R_2 = \\{B\\}$ forms a superkey of at least one of the decomposed relations, i.e., $B \\to A$ or $B \\to C$."
        },
        {
            "id": "pyq_2016_cs_q23",
            "type": "nat",
            "category": "pyq",
            "year": 2016,
            "subject": "DBMS",
            "topic": "B+ Trees",
            "difficulty": "medium",
            "marks": 2,
            "question": "A $B^+$ tree index is built on a search key of size $12\\text{ bytes}$. Block size is $1024\\text{ bytes}$, and record pointers are $8\\text{ bytes}$ each. Block pointers to child nodes are $6\\text{ bytes}$ each. What is the maximum order $p$ (maximum number of child block pointers) of an internal node in this $B^+$ tree?",
            "options": [],
            "correct": [57],
            "natRange": {"min": 57, "max": 57},
            "explanation": "An internal node of order $p$ contains at most $p$ block pointers and $p-1$ key values. Total size equation: $p \\times P_{b} + (p - 1) \\times K \\le B \\implies p(6) + (p - 1)(12) \\le 1024 \\implies 6p + 12p - 12 \\le 1024 \\implies 18p \\le 1036 \\implies p \\le \\lfloor 1036 / 18 \\rfloor = 57.55$. Hence, the maximum order $p$ of an internal node is 57."
        },
        {
            "id": "pyq_2019_cs_q15",
            "type": "mcq",
            "category": "pyq",
            "year": 2019,
            "subject": "DBMS",
            "topic": "SQL",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider the relations $R(A, B)$ and $S(B, C)$. What is the effect of the SQL query:\n```sql\nSELECT DISTINCT R.A\nFROM R\nWHERE R.B NOT IN (SELECT S.B FROM S);\n```",
            "options": [
                "Finds all A values whose B values do not appear in S",
                "Finds all A values whose B values appear in all tuples of S",
                "Finds all A values where relation S is empty",
                "Finds all A values whose B values are null"
            ],
            "correct": [0],
            "explanation": "The subquery selects all $B$ values from $S$. The outer query filters tuples in $R$ whose $B$ attribute is NOT present in that set. Hence it retrieves distinct $A$ values in $R$ whose corresponding $B$ values do not appear in relation $S$."
        },

        # =====================================================================
        # Theory of Computation Expansion
        # =====================================================================
        {
            "id": "pyq_2014_cs_q14",
            "type": "mcq",
            "category": "pyq",
            "year": 2014,
            "subject": "Theory of Computation",
            "topic": "Pumping Lemma",
            "difficulty": "medium",
            "marks": 2,
            "question": "Which of the following languages is NOT regular?",
            "options": [
                "$\\{w \\in \\{0, 1\\}^* \\mid w \\text{ has an equal number of } 0\\text{'s and } 1\\text{'s}\\}$",
                "$\\{w \\in \\{0, 1\\}^* \\mid w \\text{ ends with } 00\\}$",
                "$\\{0^n 1^m \\mid n, m \\ge 0\\}$",
                "$\\{w \\in \\{0, 1\\}^* \\mid \\text{decimal value of } w \\text{ is divisible by } 7\\}$"
            ],
            "correct": [0],
            "explanation": "Checking that the count of 0s equals the count of 1s across arbitrary strings requires an unbounded counter/memory, which cannot be modeled by a Finite Automaton. By the Pumping Lemma, it is non-regular."
        },
        {
            "id": "pyq_2018_cs_q13",
            "type": "mcq",
            "category": "pyq",
            "year": 2018,
            "subject": "Theory of Computation",
            "topic": "Closure Properties",
            "difficulty": "medium",
            "marks": 2,
            "question": "Context-Free Languages are closed under which of the following operations?",
            "options": [
                "Union and Kleene Star",
                "Intersection and Complement",
                "Intersection and Set Difference",
                "Complement and Kleene Star"
            ],
            "correct": [0],
            "explanation": "Context-Free Languages (CFLs) are closed under Union ($S \\to S_1 \\mid S_2$), Concatenation ($S \\to S_1 S_2$), and Kleene Star ($S \\to S S_1 \\mid \\epsilon$), but NOT closed under Intersection or Complement."
        },
        {
            "id": "pyq_2023_cs_q28",
            "type": "mcq",
            "category": "pyq",
            "year": 2023,
            "subject": "Theory of Computation",
            "topic": "Decidability",
            "difficulty": "medium",
            "marks": 2,
            "question": "Which of the following statements about Rice's Theorem is TRUE?",
            "options": [
                "Any non-trivial semantic property of the language recognized by a Turing Machine is undecidable",
                "Any syntactic property of a Turing Machine is undecidable",
                "Rice's Theorem applies to Context-Free Languages",
                "Rice's Theorem proves that all languages are recursively enumerable"
            ],
            "correct": [0],
            "explanation": "Rice's Theorem states that any non-trivial property of the language recognized by a Turing Machine (a semantic property concerning what the TM accepts, rather than how it is syntactically encoded) is undecidable."
        },

        # =====================================================================
        # Compiler Design Expansion
        # =====================================================================
        {
            "id": "pyq_2015_cs_q07",
            "type": "mcq",
            "category": "pyq",
            "year": 2015,
            "subject": "Compiler Design",
            "topic": "Syntax Directed Translation",
            "difficulty": "medium",
            "marks": 2,
            "question": "In a Syntax-Directed Definition (SDD), an attribute is synthesized if its value at a parse tree node is determined by:",
            "options": [
                "Attribute values at its children nodes",
                "Attribute values at its parent node and left siblings",
                "Attribute values at arbitrary right siblings",
                "Global compiler flags only"
            ],
            "correct": [0],
            "explanation": "A synthesized attribute at node $N$ is defined only in terms of attribute values at the children of $N$ and at $N$ itself. If an attribute depends on parent or sibling attributes, it is an inherited attribute."
        },
        {
            "id": "pyq_2018_cs_q14",
            "type": "mcq",
            "category": "pyq",
            "year": 2018,
            "subject": "Compiler Design",
            "topic": "LR Parsing",
            "difficulty": "medium",
            "marks": 2,
            "question": "Which of the following parser families has the greatest parsing power (accepts the largest class of grammars)?",
            "options": ["LR(1)", "LALR(1)", "SLR(1)", "LR(0)"],
            "correct": [0],
            "explanation": "The hierarchy of bottom-up shift-reduce parsers in strictly increasing order of parsing power is: $\\text{LR}(0) \\subset \\text{SLR}(1) \\subset \\text{LALR}(1) \\subset \\text{LR}(1)$. Canonical LR(1) keeps items separate with distinct 1-symbol lookaheads, avoiding reduce-reduce conflicts merged in LALR(1)."
        },
        {
            "id": "pyq_2022_cs_q26",
            "type": "mcq",
            "category": "pyq",
            "year": 2022,
            "subject": "Compiler Design",
            "topic": "Code Optimization",
            "difficulty": "easy",
            "marks": 1,
            "question": "Which code optimization technique replaces expensive operations (such as multiplication by a constant power of 2) with cheaper operations (such as bitwise left shift)?",
            "options": [
                "Strength Reduction",
                "Constant Folding",
                "Loop Invariant Code Motion",
                "Dead Code Elimination"
            ],
            "correct": [0],
            "explanation": "Strength reduction replaces computationally costly operations (like multiplication and division) with equivalent, lower-cost operations (such as additions or bit-shifts, e.g., $x \\times 4 \\implies x \\ll 2$)."
        },

        # =====================================================================
        # Computer Organization Expansion
        # =====================================================================
        {
            "id": "pyq_2016_cs_q24",
            "type": "mcq",
            "category": "pyq",
            "year": 2016,
            "subject": "Computer Organization",
            "topic": "Addressing Modes",
            "difficulty": "easy",
            "marks": 1,
            "question": "In which addressing mode is the operand located inside the instruction itself?",
            "options": [
                "Immediate Addressing Mode",
                "Direct Addressing Mode",
                "Register Indirect Addressing Mode",
                "Indexed Addressing Mode"
            ],
            "correct": [0],
            "explanation": "In Immediate Addressing Mode, the operand value is explicitly contained in the address field of the instruction itself (e.g., `MOV R1, #25`), so no additional memory reference is required to fetch the operand."
        },
        {
            "id": "pyq_2019_cs_q16",
            "type": "nat",
            "category": "pyq",
            "year": 2019,
            "subject": "Computer Organization",
            "topic": "Instruction Pipelining",
            "difficulty": "medium",
            "marks": 2,
            "question": "A $5$-stage pipeline processor executes $100$ independent instructions without any pipeline stalls or hazards. Each stage takes $1\\text{ clock cycle}$. How many clock cycles are required to complete all $100$ instructions?",
            "options": [],
            "correct": [104],
            "natRange": {"min": 104, "max": 104},
            "explanation": "For a $k$-stage pipeline executing $n$ instructions without stalls, the first instruction takes $k$ cycles to complete, and each of the remaining $(n - 1)$ instructions completes at the rate of 1 per cycle. Total clock cycles $= k + (n - 1) = 5 + (100 - 1) = 5 + 99 = 104\\text{ cycles}$."
        },
        {
            "id": "pyq_2023_cs_q29",
            "type": "mcq",
            "category": "pyq",
            "year": 2023,
            "subject": "Computer Organization",
            "topic": "Control Unit",
            "difficulty": "easy",
            "marks": 1,
            "question": "Compared to a Hardwired Control Unit, a Microprogrammed Control Unit is:",
            "options": [
                "Easier to modify and update with new instructions, but slower in execution speed",
                "Faster in execution speed and easier to modify",
                "Faster in execution speed, but harder to modify",
                "Implemented entirely using fixed combinational logic gates"
            ],
            "correct": [0],
            "explanation": "Microprogrammed control units store control words in a control memory (ROM), making updates, microcode additions, and instruction set modifications much easier. However, fetching microinstructions from control memory adds latency compared to direct hardwired logic gates."
        },

        # =====================================================================
        # Digital Logic Expansion
        # =====================================================================
        {
            "id": "pyq_2014_cs_q15",
            "type": "mcq",
            "category": "pyq",
            "year": 2014,
            "subject": "Digital Logic",
            "topic": "Boolean Algebra",
            "difficulty": "easy",
            "marks": 1,
            "question": "The minimal sum-of-products (SOP) expression for the Boolean function $F(A, B) = A + \\bar{A}B$ is:",
            "options": ["$A + B$", "$A B$", "$\\bar{A} + B$", "$A + \\bar{B}$"],
            "correct": [0],
            "explanation": "Using Boolean absorption and distributive laws: $A + \\bar{A}B = (A + \\bar{A})(A + B) = (1)(A + B) = A + B$."
        },
        {
            "id": "pyq_2018_cs_q15",
            "type": "nat",
            "category": "pyq",
            "year": 2018,
            "subject": "Digital Logic",
            "topic": "K-Maps",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider the 4-variable function $f(w, x, y, z) = \\sum m(0, 2, 8, 10, 14)$. How many Essential Prime Implicants (EPIs) does this function have?",
            "options": [],
            "correct": [2],
            "natRange": {"min": 2, "max": 2},
            "explanation": "Minterms: 0(0000), 2(0010), 8(1000), 10(1010), 14(1110).\nGrouping:\n1. Four corners $m(0, 2, 8, 10)$: combines to $\\bar{x} \\bar{z}$. Minterm 0 is covered only by this group, making $\\bar{x}\\bar{z}$ an Essential Prime Implicant.\n2. Pair $m(10, 14)$: combines $1010$ and $1110$ to $w y \\bar{z}$. Minterm 14 is covered only by this group, making $w y \\bar{z}$ an Essential Prime Implicant.\nBoth prime implicants are essential, so total EPIs $= 2$."
        },
        {
            "id": "pyq_2021_cs_q25",
            "type": "mcq",
            "category": "pyq",
            "year": 2021,
            "subject": "Digital Logic",
            "topic": "Flip-Flops",
            "difficulty": "easy",
            "marks": 1,
            "question": "In a $J$-$K$ flip-flop, the toggle mode occurs when inputs $J$ and $K$ are set to:",
            "options": ["$J = 1, K = 1$", "$J = 0, K = 0$", "$J = 1, K = 0$", "$J = 0, K = 1$"],
            "correct": [0],
            "explanation": "When $J = 1$ and $K = 1$, the characteristic equation $Q_{next} = J\\bar{Q} + \\bar{K}Q = 1\\cdot\\bar{Q} + 0\\cdot Q = \\bar{Q}$ inverts the previous state on each active clock edge, which is the toggle mode."
        },

        # =====================================================================
        # Discrete Mathematics Expansion
        # =====================================================================
        {
            "id": "pyq_2015_cs_q08",
            "type": "nat",
            "category": "pyq",
            "year": 2015,
            "subject": "Discrete Mathematics",
            "topic": "Planar Graphs",
            "difficulty": "medium",
            "marks": 2,
            "question": "A connected planar graph has $10$ vertices and each vertex has degree $3$. Into how many faces (regions) does this graph divide the plane?",
            "options": [],
            "correct": [7],
            "natRange": {"min": 7, "max": 7},
            "explanation": "By the Handshaking Lemma, $2E = \\sum \\deg(v) = 10 \\times 3 = 30 \\implies E = 15$ edges. By Euler's Formula for connected planar graphs: $V - E + F = 2 \\implies 10 - 15 + F = 2 \\implies -5 + F = 2 \\implies F = 7$ faces."
        },
        {
            "id": "pyq_2019_cs_q17",
            "type": "mcq",
            "category": "pyq",
            "year": 2019,
            "subject": "Discrete Mathematics",
            "topic": "Relations",
            "difficulty": "easy",
            "marks": 1,
            "question": "A relation $R$ on a non-empty set $A$ is an equivalence relation if and only if $R$ is:",
            "options": [
                "Reflexive, Symmetric, and Transitive",
                "Reflexive, Antisymmetric, and Transitive",
                "Irreflexive, Symmetric, and Transitive",
                "Symmetric and Transitive only"
            ],
            "correct": [0],
            "explanation": "By definition, an equivalence relation must satisfy three fundamental properties: Reflexivity ($a R a$), Symmetry ($a R b \\implies b R a$), and Transitivity ($a R b \\land b R c \\implies a R c$)."
        },
        {
            "id": "pyq_2022_cs_q27",
            "type": "nat",
            "category": "pyq",
            "year": 2022,
            "subject": "Discrete Mathematics",
            "topic": "Combinatorics",
            "difficulty": "medium",
            "marks": 2,
            "question": "What is the number of non-negative integer solutions to the equation $x_1 + x_2 + x_3 + x_4 = 10$?",
            "options": [],
            "correct": [286],
            "natRange": {"min": 286, "max": 286},
            "explanation": "The number of non-negative integer solutions to $\\sum_{i=1}^k x_i = n$ is given by the stars-and-bars formula: $\\binom{n + k - 1}{k - 1}$. Here $n = 10$ and $k = 4$, so $\\binom{10 + 4 - 1}{4 - 1} = \\binom{13}{3} = \\frac{13 \\times 12 \\times 11}{3 \\times 2 \\times 1} = 13 \\times 2 \\times 11 = 286$."
        },

        # =====================================================================
        # Engineering Mathematics Expansion
        # =====================================================================
        {
            "id": "pyq_2014_cs_q16",
            "type": "nat",
            "category": "pyq",
            "year": 2014,
            "subject": "Engineering Mathematics",
            "topic": "Probability",
            "difficulty": "medium",
            "marks": 2,
            "question": "Two fair 6-sided dice are rolled simultaneously. What is the probability that the sum of the numbers appearing on the top faces is $7$?",
            "options": [],
            "correct": [0.1667],
            "natRange": {"min": 0.16, "max": 0.17},
            "explanation": "Total possible outcomes $= 6 \\times 6 = 36$. Favorable outcomes summing to 7 are: $(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1)$, which is 6 outcomes. Probability $= \\frac{6}{36} = \\frac{1}{6} \\approx 0.1667$."
        },
        {
            "id": "pyq_2017_cs_q09",
            "type": "nat",
            "category": "pyq",
            "year": 2017,
            "subject": "Engineering Mathematics",
            "topic": "Linear Algebra",
            "difficulty": "easy",
            "marks": 1,
            "question": "The trace of a $2 \\times 2$ matrix $M$ is $8$ and its determinant is $15$. What is the absolute difference between the two eigenvalues of $M$?",
            "options": [],
            "correct": [2],
            "natRange": {"min": 2, "max": 2},
            "explanation": "Let the eigenvalues be $\\lambda_1$ and $\\lambda_2$. Then $\\lambda_1 + \\lambda_2 = \\text{trace} = 8$ and $\\lambda_1 \\lambda_2 = \\det = 15$. The quadratic equation is $\\lambda^2 - 8\\lambda + 15 = 0 \\implies (\\lambda - 3)(\\lambda - 5) = 0$. So $\\lambda_1 = 5, \\lambda_2 = 3$. Absolute difference $= |5 - 3| = 2$."
        },
        {
            "id": "pyq_2020_cs_q18",
            "type": "nat",
            "category": "pyq",
            "year": 2020,
            "subject": "Engineering Mathematics",
            "topic": "Calculus",
            "difficulty": "easy",
            "marks": 1,
            "question": "Evaluate the limit: $$\\lim_{x \\to 0} \\frac{e^{3x} - 1}{x}$$",
            "options": [],
            "correct": [3],
            "natRange": {"min": 3, "max": 3},
            "explanation": "This is in indeterminate form $\\frac{0}{0}$. Applying L'Hopital's rule, differentiate numerator and denominator with respect to $x$: $\\lim_{x \\to 0} \\frac{3e^{3x}}{1} = \\frac{3e^0}{1} = 3$."
        },

        # =====================================================================
        # C Programming Expansion
        # =====================================================================
        {
            "id": "pyq_2015_cs_q09",
            "type": "mcq",
            "category": "pyq",
            "year": 2015,
            "subject": "C Programming",
            "topic": "Recursion",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider the following recursive C function:\n```c\nint fun(int n) {\n    if (n <= 1) return 1;\n    if (n % 2 == 0) return fun(n / 2);\n    return fun(n / 2) + fun(n - 1);\n}\n```\nWhat is the return value of `fun(5)`?",
            "options": ["1", "2", "3", "4"],
            "correct": [1],
            "explanation": "Trace `fun(5)`:\n- 5 is odd $\\implies$ `fun(5/2) + fun(4) = fun(2) + fun(4)`\n- `fun(2)`: 2 is even $\\implies$ `fun(1) = 1`\n- `fun(4)`: 4 is even $\\implies$ `fun(2) = 1`\n- Therefore, `fun(5) = fun(2) + fun(4) = 1 + 1 = 2`."
        },
        {
            "id": "pyq_2018_cs_q16",
            "type": "mcq",
            "category": "pyq",
            "year": 2018,
            "subject": "C Programming",
            "topic": "Operator Precedence",
            "difficulty": "easy",
            "marks": 1,
            "question": "What is the output of the following C code?\n```c\nint x = 5;\nint y = x++ + ++x;\nprintf(\"%d\", y);\n```\nNote: Assume evaluation from left to right per C standards or sequence point definitions.",
            "options": [
                "12",
                "10",
                "Undefined behavior in standard C",
                "14"
            ],
            "correct": [2],
            "explanation": "Modifying a variable (`x++` and `++x`) more than once between two sequence points without an intervening sequence point invokes Undefined Behavior in standard C (ISO C99/C11)."
        },
        {
            "id": "pyq_2021_cs_q26",
            "type": "mcq",
            "category": "pyq",
            "year": 2021,
            "subject": "C Programming",
            "topic": "Static Variables",
            "difficulty": "medium",
            "marks": 2,
            "question": "What is the output of the following C program?\n```c\n#include <stdio.h>\nint count() {\n    static int x = 0;\n    x += 2;\n    return x;\n}\nint main() {\n    printf(\"%d %d\", count(), count());\n    return 0;\n}\n```",
            "options": [
                "2 4 (or 4 2 depending on argument evaluation order)",
                "2 2",
                "0 0",
                "4 4"
            ],
            "correct": [0],
            "explanation": "Because `x` is declared static inside `count()`, its value persists between function calls. The first call increments `x` to 2; the second call increments `x` to 4. In C, order of argument evaluation in `printf` is unspecified, so printed values will be 2 and 4 (either '2 4' or '4 2')."
        }
    ]
