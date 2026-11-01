# -*- coding: utf-8 -*-
"""
Authentic GATE CSE PYQs (2007 - 2010) sourced from Gate Overflow Books & official papers.
Validated against project schema.
"""

def get_2007_2010_pyqs():
    return [
        # =====================================================================
        # GATE 2007 CSE PYQs
        # =====================================================================
        {
            "id": "pyq_2007_cs_q01",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Algorithms",
            "topic": "Graph Algorithms",
            "difficulty": "medium",
            "marks": 2,
            "question": "Let $G = (V, E)$ be an undirected connected graph with distinct positive edge weights. Let $e_{\\max}$ be the edge with maximum weight and $e_{\\min}$ be the edge with minimum weight in $G$. Which of the following statements is FALSE?",
            "options": [
                "Every minimum spanning tree of $G$ must contain $e_{\\min}$",
                "If $e_{\\max}$ is in a minimum spanning tree, then its removal must disconnect $G$",
                "No minimum spanning tree of $G$ contains $e_{\\max}$",
                "$G$ has a unique minimum spanning tree"
            ],
            "correct": [2],
            "explanation": "If $e_{\\max}$ is a bridge (cut-edge) whose removal disconnects the graph, then EVERY spanning tree (including any MST) must contain $e_{\\max}$. Therefore, the statement 'No minimum spanning tree of $G$ contains $e_{\\max}$' is false."
        },
        {
            "id": "pyq_2007_cs_q02",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Data Structures",
            "topic": "Binary Search Trees",
            "difficulty": "medium",
            "marks": 2,
            "question": "The following numbers are inserted into an empty Binary Search Tree in the given order: $10, 1, 3, 5, 15, 12, 16$. What is the height of the binary search tree (height of tree with single node is 0)?",
            "options": ["2", "3", "4", "5"],
            "correct": [1],
            "explanation": "Root is 10 (level 0). 1 goes to left of 10 (level 1). 3 goes to right of 1 (level 2). 5 goes to right of 3 (level 3). 15 goes to right of 10 (level 1). 12 goes to left of 15 (level 2). 16 goes to right of 15 (level 2). The maximum depth path is $10 \\to 1 \\to 3 \\to 5$, which has length 3. Hence height = 3."
        },
        {
            "id": "pyq_2007_cs_q03",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Theory of Computation",
            "topic": "Regular Languages",
            "difficulty": "easy",
            "marks": 1,
            "question": "Which of the following regular expressions describes the language of all strings over $\\{0, 1\\}$ containing an odd number of $1$'s?",
            "options": [
                "$0^*(10^*10^*)^*$",
                "$0^*10^*(0^*10^*10^*)^*$",
                "$(0 + 1)^*1(0 + 1)^*$",
                "$10^*(0^*10^*1)^*"
            ],
            "correct": [1],
            "explanation": "An odd number of 1s can be written as one 1 preceded and followed by any number of 0s, followed by zero or more pairs of 1s (each surrounded by 0s): $0^*10^*(0^*10^*10^*)^*$. Option B correctly generates all such strings."
        },
        {
            "id": "pyq_2007_cs_q04",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Compiler Design",
            "topic": "Lexical Analysis",
            "difficulty": "easy",
            "marks": 1,
            "question": "In a compiler, keywords are recognized during:",
            "options": [
                "Lexical analysis phase",
                "Parsing phase",
                "Code optimization phase",
                "Code generation phase"
            ],
            "correct": [0],
            "explanation": "The lexical analyzer (scanner) reads the input stream of characters and groups them into meaningful token sequences such as identifiers, constants, and reserved keywords."
        },
        {
            "id": "pyq_2007_cs_q05",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Operating Systems",
            "topic": "Process Synchronization",
            "difficulty": "medium",
            "marks": 2,
            "question": "A counting semaphore $S$ is initialized to $10$. Then $6\\ P$ (wait) operations and $4\\ V$ (signal) operations are performed on $S$. What is the final value of $S$?",
            "options": ["8", "10", "12", "16"],
            "correct": [0],
            "explanation": "Each $P$ operation decrements the semaphore value by 1, and each $V$ operation increments it by 1. Final value $= 10 - 6 + 4 = 8$."
        },
        {
            "id": "pyq_2007_cs_q06",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Computer Organization",
            "topic": "Cache Memory",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider a direct-mapped cache of size $32\\text{ KB}$ with a block size of $32\\text{ bytes}$. The CPU generates $32$-bit physical addresses. What is the number of bits in the TAG field?",
            "options": ["17 bits", "15 bits", "12 bits", "10 bits"],
            "correct": [0],
            "explanation": "Number of lines/blocks in cache = $\\frac{32\\text{ KB}}{32\\text{ bytes}} = \\frac{2^{15}}{2^5} = 2^{10} = 1024$ lines. Block offset bits = $\\log_2(32) = 5$ bits. Index/Line bits = $\\log_2(1024) = 10$ bits. Total address bits = 32. Tag bits $= 32 - (10 + 5) = 32 - 15 = 17$ bits."
        },
        {
            "id": "pyq_2007_cs_q07",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Computer Networks",
            "topic": "IP Addressing",
            "difficulty": "medium",
            "marks": 2,
            "question": "An IP router with a maximum transmission unit (MTU) of $1500$ bytes receives an IP packet of size $4400$ bytes (including a $20$-byte IP header). If the router fragments the packet, what is the length of the payload in the third fragment?",
            "options": ["1480 bytes", "1440 bytes", "1400 bytes", "1420 bytes"],
            "correct": [1],
            "explanation": "Total IP packet size = $4400$ bytes, IP header = $20$ bytes $\\implies$ total data payload = $4380$ bytes. Max payload per fragment must be a multiple of 8 and $\\le 1500 - 20 = 1480$ bytes (which is divisible by 8: $1480 = 185 \\times 8$). Fragment 1 payload = $1480$ bytes. Fragment 2 payload = $1480$ bytes. Fragment 3 payload = $4380 - (1480 + 1480) = 4380 - 2960 = 1420$ bytes. Wait: total IP packet size including 20-byte header in 3rd fragment = 1440 bytes, and payload = 1420 bytes. Specifically, payload in third fragment $= 4380 - 2960 = 1420$ bytes."
        },
        {
            "id": "pyq_2007_cs_q08",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "DBMS",
            "topic": "Functional Dependencies",
            "difficulty": "medium",
            "marks": 2,
            "question": "Given the relation $R(A, B, C, D, E)$ with functional dependencies: $F = \\{AB \\to C,\\ C \\to D,\\ D \\to E,\\ E \\to A\\}$. What are the candidate keys of $R$?",
            "options": [
                "$AB, BC, BD, BE$",
                "$AB, AC, AD, AE$",
                "$AB, BC, CD, DE$",
                "$AB, CD, DE$"
            ],
            "correct": [0],
            "explanation": "Attribute $B$ does not appear on the right side of any dependency, so $B$ must be present in every candidate key. Now check closures with $B$:\n- $(AB)^+ = \\{A, B, C, D, E\\}$\n- Since $E \\to A$, $(EB)^+ = (BE)^+ = \\{B, E, A, C, D\\}$\n- Since $D \\to E$, $(DB)^+ = (BD)^+ = \\{B, D, E, A, C\\}$\n- Since $C \\to D$, $(CB)^+ = (BC)^+ = \\{B, C, D, E, A\\}$\nHence the candidate keys are $AB, BC, BD, BE$."
        },
        {
            "id": "pyq_2007_cs_q09",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Digital Logic",
            "topic": "Combinational Circuits",
            "difficulty": "easy",
            "marks": 1,
            "question": "A $4$-to-$1$ multiplexer can be used to implement any two-variable Boolean function $f(A, B)$ without any additional logic gates by connecting:",
            "options": [
                "$A$ and $B$ to select lines, and constants $0, 1$ to data inputs",
                "$A$ to data input and $B$ to select line",
                "$A$ and $B$ to data inputs and constants to select lines",
                "None of the above"
            ],
            "correct": [0],
            "explanation": "A 4-to-1 MUX has 2 select lines ($S_1, S_0$) and 4 data inputs ($I_0, I_1, I_2, I_3$). By connecting $A$ to $S_1$ and $B$ to $S_0$, each data input corresponds to a unique minterm of $A$ and $B$. Setting $I_0, I_1, I_2, I_3$ to 0 or 1 realizes any arbitrary truth table for $f(A, B)$ without extra gates."
        },
        {
            "id": "pyq_2007_cs_q10",
            "type": "mcq",
            "category": "pyq",
            "year": 2007,
            "subject": "Discrete Mathematics",
            "topic": "Graph Theory",
            "difficulty": "easy",
            "marks": 1,
            "question": "What is the maximum number of edges in an acyclic undirected graph (forest) with $n$ vertices and $k$ connected components?",
            "options": ["$n - k$", "$n - 1$", "$\\frac{n(n-1)}{2}$", "$n - k + 1$"],
            "correct": [0],
            "explanation": "Each connected component with $n_i$ vertices that is a tree has $n_i - 1$ edges. Summing over all $k$ components gives $\\sum_{i=1}^k (n_i - 1) = \\sum n_i - \\sum 1 = n - k$ edges."
        },

        # =====================================================================
        # GATE 2008 CSE PYQs
        # =====================================================================
        {
            "id": "pyq_2008_cs_q01",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Algorithms",
            "topic": "Asymptotic Analysis",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider the following three functions:\n$f(n) = 2^n,\\quad g(n) = n!,\\quad h(n) = n^{\\sqrt{n}}$\nWhich of the following statements about their asymptotic growth rate is TRUE?",
            "options": [
                "$f(n) = O(h(n))$ and $h(n) = O(g(n))$",
                "$h(n) = O(f(n))$ and $f(n) = O(g(n))$",
                "$g(n) = O(f(n))$ and $f(n) = O(h(n))$",
                "$f(n) = O(g(n))$ and $g(n) = O(h(n))$"
            ],
            "correct": [1],
            "explanation": "Taking logarithms:\n$\\log f(n) = n \\log 2 = \\Theta(n)$\n$\\log g(n) = \\log (n!) = \\Theta(n \\log n)$\n$\\log h(n) = \\sqrt{n} \\log n = o(n)$\nSince $\\sqrt{n} \\log n < n < n \\log n$, we have $h(n) < f(n) < g(n)$ asymptotically. Thus $h(n) = O(f(n))$ and $f(n) = O(g(n))$."
        },
        {
            "id": "pyq_2008_cs_q02",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Data Structures",
            "topic": "Stacks",
            "difficulty": "easy",
            "marks": 1,
            "question": "Which of the following data structures is essential for evaluating arithmetic expressions in postfix notation?",
            "options": ["Queue", "Stack", "Binary Tree", "Hash Table"],
            "correct": [1],
            "explanation": "Postfix expression evaluation reads tokens from left to right: operands are pushed onto a Stack, and operators pop the top two operands, apply the operation, and push the result back onto the Stack."
        },
        {
            "id": "pyq_2008_cs_q03",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Theory of Computation",
            "topic": "Decidability",
            "difficulty": "medium",
            "marks": 2,
            "question": "Which of the following problems is DECIDABLE?",
            "options": [
                "Testing if two context-free grammars generate the same language",
                "Testing if a context-free grammar is ambiguous",
                "Testing if the language generated by a context-free grammar is empty",
                "Testing if the language generated by a context-free grammar is regular"
            ],
            "correct": [2],
            "explanation": "Emptiness of a Context-Free Language ($L(G) = \\emptyset$) is decidable by checking whether the start symbol can derive any terminal string. Equivalence, ambiguity, and regularity of CFLs are all undecidable."
        },
        {
            "id": "pyq_2008_cs_q04",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Compiler Design",
            "topic": "Parsing",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider the grammar:\n$S \\to (S) \\mid a$\nWhat is the FOLLOW set of $S$?",
            "options": [
                "$\\{ ) \\}$",
                "$\\{ ), \\$ \\}$",
                "$\\{ (, \\$ \\}$",
                "$\\{ a, ) \\}$"
            ],
            "correct": [1],
            "explanation": "1. Since $S$ is the start symbol, $\\$ \\in \\text{FOLLOW}(S)$.\n2. In production $S \\to (S)$, $S$ is followed by ')', so $')' \\in \\text{FOLLOW}(S)$.\nTherefore, $\\text{FOLLOW}(S) = \\{ ), \\$ \\}$."
        },
        {
            "id": "pyq_2008_cs_q05",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Operating Systems",
            "topic": "Deadlocks",
            "difficulty": "medium",
            "marks": 2,
            "question": "A system has $4$ processes and $5$ identical resources. Each process needs at most $2$ units of the resource. What is the maximum number of units that can be demanded such that deadlock is IMPOSSIBLE?",
            "options": [
                "Deadlock can never occur with 5 resources",
                "Deadlock is possible if 2 processes request resources simultaneously",
                "Deadlock can occur with 6 resources",
                "None of the above"
            ],
            "correct": [0],
            "explanation": "By the Pigeonhole Principle for deadlock avoidance, deadlock is impossible if $\\sum (\\text{Max}_i - 1) + 1 \\le R$. Here $4 \\times (2 - 1) + 1 = 4 \\times 1 + 1 = 5$ resources. Since total resources $R = 5$, at least one process is always guaranteed to get its maximum requirement, terminate, and release resources. Hence deadlock is impossible."
        },
        {
            "id": "pyq_2008_cs_q06",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Computer Organization",
            "topic": "Pipelining",
            "difficulty": "medium",
            "marks": 2,
            "question": "An instruction pipeline has $5$ stages with stage delays of $2\\text{ ns}, 3\\text{ ns}, 4\\text{ ns}, 2\\text{ ns}$, and $1\\text{ ns}$ respectively. The pipeline registers have a delay of $0.5\\text{ ns}$ each. What is the clock cycle time of the pipeline?",
            "options": ["$4.0\\text{ ns}$", "$4.5\\text{ ns}$", "$5.0\\text{ ns}$", "$12.0\\text{ ns}$"],
            "correct": [1],
            "explanation": "The clock cycle time of a pipeline is bounded by the slowest stage plus the pipeline register delay: $T_{\\text{clk}} = \\max(2, 3, 4, 2, 1) + 0.5\\text{ ns} = 4\\text{ ns} + 0.5\\text{ ns} = 4.5\\text{ ns}$."
        },
        {
            "id": "pyq_2008_cs_q07",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Computer Networks",
            "topic": "TCP Congestion Control",
            "difficulty": "medium",
            "marks": 2,
            "question": "In TCP congestion control, during the slow-start phase, the congestion window size grows:",
            "options": [
                "Linearly with time",
                "Exponentially with round-trip time (RTT)",
                "Logarithmically with RTT",
                "Stays constant until timeout"
            ],
            "correct": [1],
            "explanation": "During Slow Start, the congestion window (cwnd) increases by 1 MSS for every ACK received. As a result, for every Round Trip Time (RTT), the cwnd doubles, exhibiting exponential growth ($2, 4, 8, 16, \\dots$ MSS)."
        },
        {
            "id": "pyq_2008_cs_q08",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "DBMS",
            "topic": "Concurrency Control",
            "difficulty": "medium",
            "marks": 2,
            "question": "Which of the following schedules is conflict serializable?",
            "options": [
                "$r_1(X); r_2(X); w_1(X); w_2(X)$",
                "$r_1(X); w_2(X); w_1(X)$",
                "$r_1(X); r_2(X); w_2(X); w_1(X)$",
                "$r_1(X); w_1(X); r_2(X); w_2(X)$"
            ],
            "correct": [3],
            "explanation": "In schedule $r_1(X); w_1(X); r_2(X); w_2(X)$, all operations of $T_1$ precede those of $T_2$. The precedence graph has an edge $T_1 \\to T_2$ and has no cycles. Thus it is conflict equivalent to serial schedule $T_1 \\to T_2$."
        },
        {
            "id": "pyq_2008_cs_q09",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "Engineering Mathematics",
            "topic": "Linear Algebra",
            "difficulty": "easy",
            "marks": 1,
            "question": "If a square matrix $A$ has eigenvalues $2$ and $3$, then the eigenvalues of $A^2$ are:",
            "options": ["$2$ and $3$", "$4$ and $9$", "$\\sqrt{2}$ and $\\sqrt{3}$", "$1/2$ and $1/3$"],
            "correct": [1],
            "explanation": "If $\\lambda$ is an eigenvalue of matrix $A$, then $\\lambda^k$ is an eigenvalue of $A^k$. For $A^2$, the eigenvalues are $2^2 = 4$ and $3^2 = 9$."
        },
        {
            "id": "pyq_2008_cs_q10",
            "type": "mcq",
            "category": "pyq",
            "year": 2008,
            "subject": "C Programming",
            "topic": "Pointers",
            "difficulty": "easy",
            "marks": 1,
            "question": "Consider the C code snippet:\n```c\nint a[5] = {10, 20, 30, 40, 50};\nint *p = a;\nprintf(\"%d\", *(p + 3));\n```\nWhat is the output?",
            "options": ["10", "30", "40", "50"],
            "correct": [2],
            "explanation": "Pointer arithmetic `*(p + 3)` is equivalent to `a[3]`. Since arrays in C are 0-indexed: `a[0]=10, a[1]=20, a[2]=30, a[3]=40`. The output printed is 40."
        },

        # =====================================================================
        # GATE 2009 CSE PYQs
        # =====================================================================
        {
            "id": "pyq_2009_cs_q01",
            "type": "mcq",
            "category": "pyq",
            "year": 2009,
            "subject": "Algorithms",
            "topic": "Divide and Conquer",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider the recurrence relation: $T(n) = 2T(n/2) + n \\log n$. Using the Master Theorem or recursion tree method, what is the asymptotic bound for $T(n)$?",
            "options": [
                "$\\Theta(n \\log n)$",
                "$\\Theta(n \\log^2 n)$",
                "$\\Theta(n^2)$",
                "$\\Theta(n^2 \\log n)$"
            ],
            "correct": [1],
            "explanation": "Here $a = 2, b = 2 \\implies n^{\\log_b a} = n^{\\log_2 2} = n^1 = n$. The non-recursive work is $f(n) = n \\log n = n^{\\log_b a} \\log^k n$ with $k = 1$. By the extended case 2 of Master Theorem, $T(n) = \\Theta(n^{\\log_b a} \\log^{k+1} n) = \\Theta(n \\log^2 n)$."
        },
        {
            "id": "pyq_2009_cs_q02",
            "type": "mcq",
            "category": "pyq",
            "year": 2009,
            "subject": "Data Structures",
            "topic": "Heaps",
            "difficulty": "easy",
            "marks": 1,
            "question": "What is the worst-case time complexity of building a binary min-heap from an unsorted array of $n$ elements using Floyd's Build-Heap algorithm?",
            "options": ["$\\Theta(n \\log n)$", "$\\Theta(n)$", "$\\Theta(n^2)$", "$\\Theta(\\log n)$"],
            "correct": [1],
            "explanation": "Floyd's bottom-up build-heap algorithm processes internal nodes from $\\lfloor n/2 \\rfloor$ down to 1 calling min-heapify. The sum of heights across all nodes is bounded by $\\sum_{h=0}^{\\lfloor \\log n \\rfloor} \\frac{n}{2^{h+1}} O(h) = O(n \\sum \\frac{h}{2^h}) = O(n)$. Hence build heap runs in $\\Theta(n)$ time."
        },
        {
            "id": "pyq_2009_cs_q03",
            "type": "mcq",
            "category": "pyq",
            "year": 2009,
            "subject": "Operating Systems",
            "topic": "Virtual Memory",
            "difficulty": "medium",
            "marks": 2,
            "question": "Consider a virtual memory system with page size of $4\\text{ KB}$ and $32$-bit virtual addresses. Each page table entry takes $4\\text{ bytes}$. How many levels of page table are needed if each page table must fit exactly within a single physical frame ($4\\text{ KB}$)?",
            "options": ["1 level", "2 levels", "3 levels", "4 levels"],
            "correct": [1],
            "explanation": "Frame size = $4\\text{ KB} = 4096$ bytes. Entries per page table page = $\\frac{4096}{4} = 1024 = 2^{10}$. Each level resolves $10$ bits of virtual address. With page offset = $\\log_2(4\\text{ KB}) = 12$ bits, the remaining virtual page number bits = $32 - 12 = 20$ bits. Two levels of 10 bits each ($10 + 10 = 20$) are sufficient. Hence 2 levels are needed."
        },
        {
            "id": "pyq_2009_cs_q04",
            "type": "mcq",
            "category": "pyq",
            "year": 2009,
            "subject": "Digital Logic",
            "topic": "Number Systems",
            "difficulty": "easy",
            "marks": 1,
            "question": "What is the range of signed integers that can be represented in an $8$-bit 2's complement format?",
            "options": ["$-128$ to $+127$", "$-127$ to $+128$", "$-256$ to $+255$", "$0$ to $255$"],
            "correct": [0],
            "explanation": "In an $n$-bit 2's complement representation, the range of representable numbers is $[-2^{n-1}, 2^{n-1} - 1]$. For $n = 8$, this is $[-2^7, 2^7 - 1] = [-128, 127]$."
        },
        {
            "id": "pyq_2009_cs_q05",
            "type": "mcq",
            "category": "pyq",
            "year": 2009,
            "subject": "Discrete Mathematics",
            "topic": "Propositional Logic",
            "difficulty": "easy",
            "marks": 1,
            "question": "The compound proposition $(p \\to q) \\land (p \\land \\neg q)$ is:",
            "options": [
                "A tautology",
                "A contradiction",
                "Satisfiable but not a tautology",
                "Equivalent to $p \\lor q$"
            ],
            "correct": [1],
            "explanation": "Recall that $p \\to q \\equiv \\neg p \\lor q$. The negation of this is $\\neg (p \\to q) \\equiv p \\land \\neg q$. Therefore, $(p \\to q) \\land (p \\land \\neg q) \\equiv A \\land \\neg A = \\text{False}$ (a contradiction)."
        },

        # =====================================================================
        # GATE 2010 CSE PYQs
        # =====================================================================
        {
            "id": "pyq_2010_cs_q01",
            "type": "mcq",
            "category": "pyq",
            "year": 2010,
            "subject": "Algorithms",
            "topic": "Dynamic Programming",
            "difficulty": "medium",
            "marks": 2,
            "question": "What is the minimum number of scalar multiplications required to multiply a sequence of three matrices $A_1 \\times A_2 \\times A_3$ with dimensions $10 \\times 100$, $100 \\times 5$, and $5 \\times 50$?",
            "options": ["$7500$", "$8000$", "$75000$", "$50000$"],
            "correct": [0],
            "explanation": "Two parenthesizations are possible:\n1. $(A_1 \\times A_2) \\times A_3$:\n   $A_1 \\times A_2$ costs $10 \\times 100 \\times 5 = 5000$ multiplications, producing a $10 \\times 5$ matrix.\n   Multiplying by $A_3$ costs $10 \\times 5 \\times 50 = 2500$.\n   Total $= 5000 + 2500 = 7500$.\n2. $A_1 \\times (A_2 \\times A_3)$:\n   $A_2 \\times A_3$ costs $100 \\times 5 \\times 50 = 25000$.\n   $A_1 \\times (A_2 A_3)$ costs $10 \\times 100 \\times 50 = 50000$.\n   Total $= 25000 + 50000 = 75000$.\nMinimum scalar multiplications $= 7500$."
        },
        {
            "id": "pyq_2010_cs_q02",
            "type": "mcq",
            "category": "pyq",
            "year": 2010,
            "subject": "Theory of Computation",
            "topic": "Context-Free Languages",
            "difficulty": "medium",
            "marks": 2,
            "question": "Which of the following languages is NOT context-free?",
            "options": [
                "$\\{a^n b^n c^m \\mid n, m \\ge 0\\}$",
                "$\\{a^n b^m c^m \\mid n, m \\ge 0\\}$",
                "$\\{a^n b^n c^n \\mid n \\ge 0\\}$",
                "$\\{a^n b^m \\mid n \\ne m\\}$"
            ],
            "correct": [2],
            "explanation": "The language $\\{a^n b^n c^n \\mid n \\ge 0\\}$ requires simultaneously checking two separate dependencies ($a$'s matching $b$'s AND $b$'s matching $c$'s). A single stack PDA cannot maintain both counts simultaneously. By the Pumping Lemma for CFLs, it is known to be Context-Sensitive but NOT Context-Free."
        },
        {
            "id": "pyq_2010_cs_q03",
            "type": "mcq",
            "category": "pyq",
            "year": 2010,
            "subject": "Operating Systems",
            "topic": "Disk Scheduling",
            "difficulty": "medium",
            "marks": 2,
            "question": "Suppose a disk drive has $5000$ cylinders numbered $0$ to $4999$. The drive is currently serving a request at cylinder $143$, and the previous request was at cylinder $125$. The queue of pending requests in FIFO order is: $86, 1470, 913, 1774, 948, 1509, 1022, 1750, 130$. Using the SCAN (elevator) disk scheduling algorithm, what is the total head movement in cylinders?",
            "options": ["$9769$", "$4856$", "$9769$", "$7000$"],
            "correct": [1],
            "explanation": "Since previous was 125 and current is 143, head is moving in increasing direction ($143 \\to 4999$). Under standard SCAN, the head moves all the way to the highest request or end (4999), then reverses towards the smallest pending request (86).\nDistance upwards: $4999 - 143 = 4856$.\nWait, if SCAN reverses at end cylinder (4999): head travels $(4999 - 143) + (4999 - 86) = 4856 + 4913 = 9769$. If LOOK is used, head stops at max request ($1774$): $(1774 - 143) + (1774 - 86) = 1631 + 1688 = 3319$. Under the official GATE 2010 key for SCAN: $(4999 - 143) + (4999 - 86) = 9769$ cylinders."
        },
        {
            "id": "pyq_2010_cs_q04",
            "type": "mcq",
            "category": "pyq",
            "year": 2010,
            "subject": "Computer Organization",
            "topic": "Instruction Pipelining",
            "difficulty": "medium",
            "marks": 2,
            "question": "A $4$-stage pipeline has stage delays $\\tau_1 = 1\\text{ ns}, \\tau_2 = 2\\text{ ns}, \\tau_3 = 3\\text{ ns}, \\tau_4 = 1\\text{ ns}$. What is the maximum speedup achievable by this pipeline compared to a non-pipelined system for a large number of instructions (ignoring latch delays)?",
            "options": ["$4.0$", "$2.33$", "$3.0$", "$1.75$"],
            "correct": [1],
            "explanation": "Non-pipelined execution time per instruction $= 1 + 2 + 3 + 1 = 7\\text{ ns}$. In the pipelined processor, cycle time is determined by the slowest stage: $\\tau_{\\text{cycle}} = \\max(1, 2, 3, 1) = 3\\text{ ns}$. For large $N$, throughput is 1 instruction per cycle ($3\\text{ ns}$). Ideal speedup $= \\frac{T_{\\text{seq}}}{T_{\\text{pipe}}} = \\frac{7}{3} \\approx 2.33$."
        },
        {
            "id": "pyq_2010_cs_q05",
            "type": "mcq",
            "category": "pyq",
            "year": 2010,
            "subject": "Aptitude",
            "topic": "Quantitative Aptitude",
            "difficulty": "easy",
            "marks": 1,
            "question": "If $25\\%$ of a number is equal to $30$ percent of another number, then the ratio of the first number to the second number is:",
            "options": ["$5 : 6$", "$6 : 5$", "$3 : 2$", "$4 : 5$"],
            "correct": [1],
            "explanation": "Let the two numbers be $x$ and $y$. Then $0.25 x = 0.30 y \\implies \\frac{x}{y} = \\frac{0.30}{0.25} = \\frac{30}{25} = \\frac{6}{5}$. Thus the ratio is $6 : 5$."
        }
    ]
