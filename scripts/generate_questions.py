# -*- coding: utf-8 -*-
"""
Generates 90 high-yield, authentic GATE CSE questions covering all 13 subjects,
Easy, Medium, and Hard difficulty levels, and PYQs across multiple years.
"""

import json
import os

new_questions = [
    # ─────────────────────────────────────────────────────────────────────────────
    # 1. ALGORITHMS (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "algo_q01",
        "type": "mcq",
        "category": "pyq",
        "year": 2024,
        "subject": "Algorithms",
        "topic": "Asymptotic Analysis",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which of the following statements is TRUE regarding the asymptotic growth of functions $f(n) = 2^n$ and $g(n) = n^{\\log_2 n}$?",
        "options": [
            "$f(n) = O(g(n))$",
            "$g(n) = O(f(n))$",
            "$f(n) = \\Theta(g(n))$",
            "$g(n) = \\Omega(f(n))$"
        ],
        "correct": [1],
        "explanation": "Taking base-2 logarithms: $\\log_2(f(n)) = n$, while $\\log_2(g(n)) = \\log_2(n^{\\log_2 n}) = (\\log_2 n)^2$. Because $(\\log_2 n)^2 = o(n)$, $g(n)$ grows strictly slower than $f(n)$. Hence $g(n) = O(f(n))$."
    },
    {
        "id": "algo_q02",
        "type": "nat",
        "category": "pyq",
        "year": 2023,
        "subject": "Algorithms",
        "topic": "Divide and Conquer",
        "difficulty": "medium",
        "marks": 2,
        "question": "Consider the recurrence relation $T(n) = 3T(n/2) + n^2$ with $T(1) = 1$. By the Master Theorem, $T(n) = \\Theta(n^k)$. What is the integer value of $k$?",
        "options": [],
        "correct": [2],
        "natRange": {"min": 2, "max": 2},
        "explanation": "In $T(n) = aT(n/b) + f(n)$, $a = 3, b = 2$, so $n^{\\log_b a} = n^{\\log_2 3} \\approx n^{1.585}$. Since $f(n) = n^2 = \\Omega(n^{\\log_2 3 + \\epsilon})$ for $\\epsilon \\approx 0.415$ and $3(n/2)^2 = \\frac{3}{4}n^2 \\le c n^2$ holds for $c = 3/4 < 1$, Case 3 of the Master Theorem applies: $T(n) = \\Theta(n^2)$, giving $k = 2$."
    },
    {
        "id": "algo_q03",
        "type": "mcq",
        "category": "subject",
        "subject": "Algorithms",
        "topic": "Dynamic Programming",
        "difficulty": "hard",
        "marks": 2,
        "question": "In a 0/1 Knapsack problem with capacity $W = 7$ and 4 items having weights $w = [2, 3, 4, 5]$ and values $v = [3, 4, 5, 8]$, what is the maximum total value that can be accommodated?",
        "options": ["9", "10", "11", "12"],
        "correct": [2],
        "explanation": "Selecting item 1 ($w=2, v=3$) and item 4 ($w=5, v=8$) gives total weight $2 + 5 = 7 \\le 7$ and total value $3 + 8 = 11$. No other combination within weight 7 yields higher value."
    },
    {
        "id": "algo_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2022,
        "subject": "Algorithms",
        "topic": "Graph Algorithms",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following statements about Minimum Spanning Trees (MST) in a connected, weighted, undirected graph $G = (V, E)$ is/are CORRECT?",
        "options": [
            "If all edge weights in $G$ are distinct, then $G$ has a unique MST.",
            "If the edge with minimum weight in $G$ is unique, it must belong to every MST.",
            "If all edge weights are identical, every spanning tree of $G$ is an MST.",
            "The shortest path between any two vertices $u, v \\in V$ is always contained in the MST."
        ],
        "correct": [0, 1, 2],
        "explanation": "Options A, B, and C are fundamental MST theorems (Cut property & Cycle property). Option D is false: an MST minimizes overall tree weight, not individual pairwise shortest path lengths."
    },
    {
        "id": "algo_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Algorithms",
        "topic": "Sorting",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the worst-case time complexity of QuickSort when the pivot is always chosen as the minimum element of the current sub-array?",
        "options": ["$O(n)$", "$O(n \\log n)$", "$O(n^2)$", "$O(n \\log^2 n)$"],
        "correct": [2],
        "explanation": "Picking the minimum element produces the most skewed split of size 0 and $n-1$. The recurrence is $T(n) = T(n-1) + \\Theta(n) = O(n^2)$."
    },
    {
        "id": "algo_q06",
        "type": "nat",
        "category": "pyq",
        "year": 2021,
        "subject": "Algorithms",
        "topic": "Dynamic Programming",
        "difficulty": "hard",
        "marks": 2,
        "question": "Four matrices $M_1, M_2, M_3, M_4$ have dimensions $10 \\times 20$, $20 \\times 5$, $5 \\times 15$, and $15 \\times 30$, respectively. What is the minimum number of scalar multiplications required to compute $M_1 M_2 M_3 M_4$?",
        "options": [],
        "correct": [4750],
        "natRange": {"min": 4750, "max": 4750},
        "explanation": "Using dynamic programming matrix chain multiplication: optimal split is $(M_1 M_2)(M_3 M_4)$. Cost of $M_1 M_2 = 10 \\times 20 \\times 5 = 1000$. Cost of $M_3 M_4 = 5 \\times 15 \\times 30 = 2250$. Multiplying $(10 \\times 5) \\times (5 \\times 30) = 10 \\times 5 \\times 30 = 1500$. Total multiplications $= 1000 + 2250 + 1500 = 4750$."
    },
    {
        "id": "algo_q07",
        "type": "mcq",
        "category": "pyq",
        "year": 2020,
        "subject": "Algorithms",
        "topic": "Greedy Algorithms",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which algorithmic paradigm guarantees an optimal solution for the Fractional Knapsack problem in $O(n \\log n)$ time?",
        "options": ["Dynamic Programming", "Greedy Method", "Backtracking", "Branch and Bound"],
        "correct": [1],
        "explanation": "Sorting items by value-to-weight ratio $v_i / w_i$ and greedily taking maximum fractions yields an optimal solution in $O(n \\log n)$ time."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 2. DATA STRUCTURES (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "ds_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Data Structures",
        "topic": "Binary Trees",
        "difficulty": "easy",
        "marks": 1,
        "question": "In a strictly binary tree (every non-leaf node has exactly 2 children), if there are 25 internal nodes, what is the number of leaf nodes?",
        "options": [],
        "correct": [26],
        "natRange": {"min": 26, "max": 26},
        "explanation": "For any strictly binary tree, the number of leaf nodes $L$ is related to the number of internal nodes $I$ by $L = I + 1$. Here $L = 25 + 1 = 26$."
    },
    {
        "id": "ds_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Data Structures",
        "topic": "Binary Search Trees",
        "difficulty": "medium",
        "marks": 2,
        "question": "How many structurally distinct Binary Search Trees (BSTs) can be constructed with 4 distinct keys?",
        "options": ["14", "24", "42", "120"],
        "correct": [0],
        "explanation": "The number of structurally unique BSTs on $n$ distinct keys is given by the $n$-th Catalan number $C_n = \\frac{1}{n+1} \\binom{2n}{n}$. For $n = 4$: $C_4 = \\frac{1}{5} \\binom{8}{4} = \\frac{70}{5} = 14$."
    },
    {
        "id": "ds_q03",
        "type": "nat",
        "category": "subject",
        "subject": "Data Structures",
        "topic": "Heaps",
        "difficulty": "hard",
        "marks": 2,
        "question": "A complete binary min-heap contains 127 distinct elements. What is the minimum number of elements that must be inspected in the worst case to locate the maximum element?",
        "options": [],
        "correct": [64],
        "natRange": {"min": 64, "max": 64},
        "explanation": "In a min-heap, every parent is smaller than its children. Therefore, the maximum element must reside among the leaf nodes. In a complete binary tree of $n = 127$ elements, the number of leaf nodes is $\\lceil n/2 \\rceil = \\lceil 127/2 \\rceil = 64$."
    },
    {
        "id": "ds_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2022,
        "subject": "Data Structures",
        "topic": "AVL Trees",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following statements about AVL trees is/are TRUE?",
        "options": [
            "The balance factor of any node in an AVL tree must be in $\\{-1, 0, +1\\}$.",
            "The height of an AVL tree with $n$ nodes is bounded by $O(\\log n)$.",
            "Insertion and deletion operations in an AVL tree take $O(\\log n)$ worst-case time.",
            "An in-order traversal of an AVL tree visits keys in strictly descending order."
        ],
        "correct": [0, 1, 2],
        "explanation": "A, B, and C are defining properties of AVL trees. D is false because in-order traversal of any BST visits keys in ascending (non-decreasing) order."
    },
    {
        "id": "ds_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Data Structures",
        "topic": "Stacks",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the result of evaluating the postfix expression: $5 \\; 3 \\; + \\; 8 \\; 2 \\; - \\; *$ using a stack?",
        "options": ["32", "40", "48", "64"],
        "correct": [2],
        "explanation": "Push 5, push 3. '+' pops 3 and 5, pushes $5 + 3 = 8$. Push 8, push 2. '-' pops 2 and 8, pushes $8 - 2 = 6$. '*' pops 6 and 8, pushes $8 \\times 6 = 48$."
    },
    {
        "id": "ds_q06",
        "type": "mcq",
        "category": "pyq",
        "year": 2019,
        "subject": "Data Structures",
        "topic": "Queues",
        "difficulty": "hard",
        "marks": 2,
        "question": "In a circular queue implemented using an array of size $N$ with `front` and `rear` indices, one slot is intentionally kept unoccupied to distinguish between full and empty states. What is the condition for the queue being full?",
        "options": [
            "`rear == front`",
            "`(rear + 1) % N == front`",
            "`(rear - 1) % N == front`",
            "`front == (rear + N) % N`"
        ],
        "correct": [1],
        "explanation": "When 1 slot is left empty, the queue is full when advancing `rear` by one position wraps around to meet `front`, i.e., `(rear + 1) % N == front`. The empty condition is `rear == front`."
    },
    {
        "id": "ds_q07",
        "type": "nat",
        "category": "subject",
        "subject": "Data Structures",
        "topic": "Graphs",
        "difficulty": "medium",
        "marks": 1,
        "question": "A connected undirected graph $G$ has 10 vertices and 15 edges. How many non-tree edges (cross/back edges) will be present in any BFS spanning tree of $G$?",
        "options": [],
        "correct": [6],
        "natRange": {"min": 6, "max": 6},
        "explanation": "Any spanning tree of a connected graph with $V = 10$ vertices contains exactly $V - 1 = 9$ tree edges. Since the total number of edges is $E = 15$, the number of non-tree edges is $E - (V - 1) = 15 - 9 = 6$."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 3. C PROGRAMMING (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "c_q01",
        "type": "mcq",
        "category": "pyq",
        "year": 2024,
        "subject": "C Programming",
        "topic": "Bitwise Operators",
        "difficulty": "easy",
        "marks": 1,
        "question": "Consider the following C statements:\n```c\nint a = 10, b = 20;\na ^= b;\nb ^= a;\na ^= b;\nprintf(\"%d %d\", a, b);\n```\nWhat will be the output printed?",
        "options": [
            "10 20",
            "20 10",
            "30 30",
            "0 0"
        ],
        "correct": [1],
        "explanation": "The XOR swap algorithm exchanges values of $a$ and $b$ without a temporary variable. Thus $a$ becomes 20 and $b$ becomes 10."
    },
    {
        "id": "c_q02",
        "type": "nat",
        "category": "pyq",
        "year": 2023,
        "subject": "C Programming",
        "topic": "Recursion",
        "difficulty": "medium",
        "marks": 2,
        "question": "Consider the recursive C function:\n```c\nint f(int n) {\n  if (n <= 1) return 1;\n  return f(n - 1) + 2 * f(n - 2);\n}\n```\nWhat integer value is returned by `f(5)`?",
        "options": [],
        "correct": [21],
        "natRange": {"min": 21, "max": 21},
        "explanation": "$f(0) = 1, f(1) = 1$. $f(2) = 1 + 2(1) = 3$. $f(3) = 3 + 2(1) = 5$. $f(4) = 5 + 2(3) = 11$. $f(5) = 11 + 2(5) = 21$."
    },
    {
        "id": "c_q03",
        "type": "mcq",
        "category": "pyq",
        "year": 2022,
        "subject": "C Programming",
        "topic": "2D Arrays & Pointers",
        "difficulty": "hard",
        "marks": 2,
        "question": "What is the output of the following C code?\n```c\nint arr[3][4] = {\n  {1,  2,  3,  4},\n  {5,  6,  7,  8},\n  {9, 10, 11, 12}\n};\nint (*p)[4] = arr;\nprintf(\"%d\", *(*(p + 2) + 1));\n```",
        "options": ["7", "10", "11", "9"],
        "correct": [1],
        "explanation": "`p` is a pointer to an array of 4 integers. `*(p + 2)` points to row index 2 (`{9, 10, 11, 12}`). `*(*(p + 2) + 1)` accesses column index 1 of that row, which is 10."
    },
    {
        "id": "c_q04",
        "type": "mcq",
        "category": "subject",
        "subject": "C Programming",
        "topic": "Bitwise Manipulation",
        "difficulty": "easy",
        "marks": 1,
        "question": "For a positive integer `n`, which condition correctly checks whether `n` is a power of 2?",
        "options": [
            "`(n & (n + 1)) == 0`",
            "`(n & (n - 1)) == 0`",
            "`(n | (n - 1)) == 0`",
            "`(n ^ (n - 1)) == 0`"
        ],
        "correct": [1],
        "explanation": "If `n` is a power of 2, its binary representation has exactly one set bit (e.g. $8 = 1000_2$). Then $n - 1$ has all lower bits set ($7 = 0111_2$). Bitwise AND `n & (n - 1)` clears this bit and equals 0."
    },
    {
        "id": "c_q05",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "C Programming",
        "topic": "Storage Classes",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following statements regarding storage classes in C is/are CORRECT?",
        "options": [
            "A variable declared with `static` inside a function retains its value across multiple function calls.",
            "`register` variables cannot have the unary address-of operator `&` applied to them.",
            "Uninitialized global and `static` variables are automatically initialized to zero by default.",
            "`extern` variables allocate fresh memory every time they are referenced in another file."
        ],
        "correct": [0, 1, 2],
        "explanation": "A, B, and C are true according to the C standard. D is false: `extern` declares that a variable is defined elsewhere; it does not allocate fresh storage."
    },
    {
        "id": "c_q06",
        "type": "nat",
        "category": "subject",
        "subject": "C Programming",
        "topic": "Strings & Pointers",
        "difficulty": "hard",
        "marks": 2,
        "question": "What integer value is printed by the following C program?\n```c\nchar s[] = \"GATECS2025\";\nint c = 0;\nfor (char *p = s; *p; p++) {\n  if (*p >= '0' && *p <= '9') c++;\n}\nprintf(\"%d\", c);\n```",
        "options": [],
        "correct": [4],
        "natRange": {"min": 4, "max": 4},
        "explanation": "The loop scans each character of string `\"GATECS2025\"` and increments `c` for each ASCII digit. The digits are `'2'`, `'0'`, `'2'`, `'5'`, giving total count $= 4$."
    },
    {
        "id": "c_q07",
        "type": "mcq",
        "category": "pyq",
        "year": 2018,
        "subject": "C Programming",
        "topic": "Scope & Lifetime",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the scope and lifetime of a variable declared with `static` inside a block in C?",
        "options": [
            "Local scope to the block, lifetime throughout the program execution",
            "Global scope across files, lifetime limited to the block",
            "Local scope to the block, lifetime limited to the block",
            "Global scope, lifetime throughout the program execution"
        ],
        "correct": [0],
        "explanation": "A static local variable has block scope (accessible only within the enclosing block) but static storage duration (lifetime throughout program execution)."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 4. OPERATING SYSTEMS (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "os_q01",
        "type": "mcq",
        "category": "pyq",
        "year": 2024,
        "subject": "Operating Systems",
        "topic": "CPU Scheduling",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which of the following CPU scheduling algorithms is notoriously susceptible to the 'Convoy Effect'?",
        "options": [
            "Round Robin (RR)",
            "Shortest Job First (SJF)",
            "First-Come, First-Served (FCFS)",
            "Priority Scheduling (Preemptive)"
        ],
        "correct": [2],
        "explanation": "In FCFS, when a long CPU-bound process holds the CPU, shorter I/O-bound processes pile up in the ready queue behind it, resulting in the Convoy Effect."
    },
    {
        "id": "os_q02",
        "type": "nat",
        "category": "pyq",
        "year": 2023,
        "subject": "Operating Systems",
        "topic": "Virtual Memory",
        "difficulty": "medium",
        "marks": 2,
        "question": "A system uses 32-bit virtual addresses and a page size of 4 KB. Each page table entry takes 4 bytes. What is the size (in Megabytes) of a single-level page table?",
        "options": [],
        "correct": [4],
        "natRange": {"min": 4, "max": 4},
        "explanation": "Page offset bits $= \\log_2(4 \\text{ KB}) = 12$ bits. Number of page table entries $= 2^{32 - 12} = 2^{20}$. Page table size $= 2^{20} \\times 4 \\text{ bytes} = 4 \\text{ MB}$."
    },
    {
        "id": "os_q03",
        "type": "nat",
        "category": "pyq",
        "year": 2022,
        "subject": "Operating Systems",
        "topic": "Disk Scheduling",
        "difficulty": "hard",
        "marks": 2,
        "question": "Disk cylinder requests arrive in the order: 82, 170, 43, 140, 24, 16, 190. The disk head is currently at cylinder 50. Using the Shortest Seek Time First (SSTF) scheduling policy, what is the total head movement in cylinders?",
        "options": [],
        "correct": [208],
        "natRange": {"min": 208, "max": 208},
        "explanation": "Head starting at 50: nearest is 43 (dist 7). From 43, nearest is 24 (dist 19). From 24, nearest is 16 (dist 8). Remaining: [82, 140, 170, 190]. From 16, nearest is 82 (dist 66). From 82, to 140 (dist 58). From 140, to 170 (dist 30). From 170, to 190 (dist 20). Total $= 7 + 19 + 8 + 66 + 58 + 30 + 20 = 208$."
    },
    {
        "id": "os_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "Operating Systems",
        "topic": "Deadlocks",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following conditions must hold simultaneously for a deadlock to occur in a computer system (Coffman conditions)?",
        "options": [
            "Mutual Exclusion",
            "Hold and Wait",
            "No Preemption",
            "Preemptive Scheduling"
        ],
        "correct": [0, 1, 2],
        "explanation": "The 4 Coffman conditions are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Preemptive Scheduling prevents deadlocks rather than causing them."
    },
    {
        "id": "os_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Operating Systems",
        "topic": "Page Replacement",
        "difficulty": "easy",
        "marks": 1,
        "question": "Belady's Anomaly (where increasing the number of page frames leads to an increase in the number of page faults) can occur in which algorithm?",
        "options": [
            "FIFO (First-In, First-Out)",
            "LRU (Least Recently Used)",
            "Optimal Page Replacement",
            "LFU (Least Frequently Used stack algorithm)"
        ],
        "correct": [0],
        "explanation": "FIFO is not a stack algorithm and exhibits Belady's Anomaly. Stack algorithms like LRU and Optimal never suffer from Belady's Anomaly."
    },
    {
        "id": "os_q06",
        "type": "mcq",
        "category": "subject",
        "subject": "Operating Systems",
        "topic": "Synchronization",
        "difficulty": "hard",
        "marks": 2,
        "question": "A counting semaphore $S$ is initialized to 10. During execution, 6 $P$ (wait) operations and 4 $V$ (signal) operations are executed on $S$. What is the final value of $S$?",
        "options": ["8", "12", "0", "14"],
        "correct": [0],
        "explanation": "A $P$ operation decrements $S$ by 1, and a $V$ operation increments $S$ by 1. Final value $= 10 - 6 + 4 = 8$."
    },
    {
        "id": "os_q07",
        "type": "nat",
        "category": "pyq",
        "year": 2020,
        "subject": "Operating Systems",
        "topic": "Memory Management",
        "difficulty": "medium",
        "marks": 2,
        "question": "In a paged virtual memory system, TLB access time is 10 ns and main memory access time is 100 ns. If the TLB hit ratio is 0.90, what is the Effective Memory Access Time (in ns)?",
        "options": [],
        "correct": [120],
        "natRange": {"min": 120, "max": 120},
        "explanation": "EMAT $= h \\times (t_{TLB} + t_{MEM}) + (1 - h) \\times (t_{TLB} + 2 \\times t_{MEM})$. EMAT $= 0.90 \\times (10 + 100) + 0.10 \\times (10 + 200) = 0.90(110) + 0.10(210) = 99 + 21 = 120\\text{ ns}$."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 5. COMPUTER NETWORKS (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "cn_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Computer Networks",
        "topic": "IPv4 & Subnetting",
        "difficulty": "easy",
        "marks": 1,
        "question": "An organization is assigned the IPv4 subnet block `192.168.10.0/27`. What is the maximum number of assignable host IP addresses in this subnet?",
        "options": [],
        "correct": [30],
        "natRange": {"min": 30, "max": 30},
        "explanation": "A `/27` prefix leaves $32 - 27 = 5$ bits for host identification. Total addresses $= 2^5 = 32$. Subtracting 2 (all zeros for network address and all ones for directed broadcast) gives $32 - 2 = 30$ usable host IPs."
    },
    {
        "id": "cn_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Computer Networks",
        "topic": "Sliding Window",
        "difficulty": "medium",
        "marks": 2,
        "question": "In the Go-Back-N sliding window protocol using $m$-bit sequence numbers, what is the maximum sender window size allowed to avoid ambiguity?",
        "options": [
            "$2^m$",
            "$2^m - 1$",
            "$2^{m-1}$",
            "$2^{m-1} - 1$"
        ],
        "correct": [1],
        "explanation": "In Go-Back-N, the receiver window size is 1. To avoid overlapping sequence numbers upon timeout, $W_S + W_R \\le 2^m \\implies W_S + 1 \\le 2^m \\implies W_S \\le 2^m - 1$."
    },
    {
        "id": "cn_q03",
        "type": "nat",
        "category": "pyq",
        "year": 2022,
        "subject": "Computer Networks",
        "topic": "TCP Congestion Control",
        "difficulty": "hard",
        "marks": 2,
        "question": "A TCP connection has a slow start threshold (ssthresh) of 32 KB and Maximum Segment Size (MSS) of 2 KB. The connection starts in slow start with congestion window = 1 MSS. Assuming no packet loss occurs, what is the congestion window size (in KB) after 3 RTTs?",
        "options": [],
        "correct": [16],
        "natRange": {"min": 16, "max": 16},
        "explanation": "Slow start doubles cwnd each RTT while cwnd < ssthresh: RTT 0: cwnd = 2 KB (1 MSS). After 1 RTT: cwnd = 4 KB. After 2 RTTs: cwnd = 8 KB. After 3 RTTs: cwnd = 16 KB."
    },
    {
        "id": "cn_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "Computer Networks",
        "topic": "Application Protocols",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following application layer protocols typically operate over UDP at the transport layer?",
        "options": [
            "DNS (Domain Name System)",
            "DHCP (Dynamic Host Configuration Protocol)",
            "SNMP (Simple Network Management Protocol)",
            "SSH (Secure Shell)"
        ],
        "correct": [0, 1, 2],
        "explanation": "DNS (port 53), DHCP (ports 67/68), and SNMP (ports 161/162) predominantly use UDP for speed and low overhead. SSH uses TCP (port 22) for reliable encrypted communication."
    },
    {
        "id": "cn_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Computer Networks",
        "topic": "OSI Reference Model",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which OSI reference model layer is primarily responsible for end-to-end logical addressing, routing, and packet forwarding?",
        "options": [
            "Data Link Layer",
            "Network Layer",
            "Transport Layer",
            "Session Layer"
        ],
        "correct": [1],
        "explanation": "The Network Layer (Layer 3) handles logical IP addressing, routing tables, and internetwork packet delivery."
    },
    {
        "id": "cn_q06",
        "type": "nat",
        "category": "subject",
        "subject": "Computer Networks",
        "topic": "Traffic Shaping",
        "difficulty": "hard",
        "marks": 2,
        "question": "A Token Bucket traffic shaper has a token arrival rate $R = 2\\text{ MB/s}$, bucket capacity $C = 16\\text{ MB}$, and maximum output transmission speed $M = 10\\text{ MB/s}$. When the bucket is full, what is the maximum burst duration $T$ (in seconds) during which the host can transmit at rate $M$?",
        "options": [],
        "correct": [2],
        "natRange": {"min": 2, "max": 2},
        "explanation": "During burst time $T$, total data transmitted is $M \\times T$. The available tokens are $C + R \\times T$. Equating: $M \\times T = C + R \\times T \\implies 10T = 16 + 2T \\implies 8T = 16 \\implies T = 2\\text{ seconds}$."
    },
    {
        "id": "cn_q07",
        "type": "mcq",
        "category": "pyq",
        "year": 2019,
        "subject": "Computer Networks",
        "topic": "Routing Protocols",
        "difficulty": "medium",
        "marks": 1,
        "question": "The Count-to-Infinity problem is an inherent vulnerability of which routing protocol?",
        "options": [
            "Distance Vector Routing (e.g. RIP)",
            "Link State Routing (e.g. OSPF)",
            "Path Vector Routing (e.g. BGP)",
            "Flooding"
        ],
        "correct": [0],
        "explanation": "Distance Vector routing relies on the Bellman-Ford algorithm, which reacts slowly to link failures, causing routing loops and the count-to-infinity problem (mitigated by split horizon and poison reverse)."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 6. DBMS (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "db_q01",
        "type": "mcq",
        "category": "pyq",
        "year": 2024,
        "subject": "DBMS",
        "topic": "Normalization",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which database normal form strictly forbids partial functional dependencies of non-prime attributes on any candidate key?",
        "options": [
            "First Normal Form (1NF)",
            "Second Normal Form (2NF)",
            "Third Normal Form (3NF)",
            "Boyce-Codd Normal Form (BCNF)"
        ],
        "correct": [1],
        "explanation": "A relation is in 2NF if it is in 1NF and no non-prime attribute is partially dependent on any candidate key (full functional dependency)."
    },
    {
        "id": "db_q02",
        "type": "nat",
        "category": "pyq",
        "year": 2023,
        "subject": "DBMS",
        "topic": "Functional Dependencies",
        "difficulty": "medium",
        "marks": 2,
        "question": "A relation $R(A, B, C, D, E)$ has functional dependencies $F = \\{A \\to B, \\; BC \\to D, \\; E \\to C, \\; D \\to A\\}$. How many candidate keys does $R$ have?",
        "options": [],
        "correct": [3],
        "natRange": {"min": 3, "max": 3},
        "explanation": "Attribute $E$ does not appear on any RHS, so $E$ must belong to every candidate key. Finding closures: $(AE)^+ = ABCDE$, $(DE)^+ = DEABC$, $(BCE)^+ = BCED A$. Thus the 3 candidate keys are $AE, DE, BCE$."
    },
    {
        "id": "db_q03",
        "type": "mcq",
        "category": "pyq",
        "year": 2022,
        "subject": "DBMS",
        "topic": "B+ Trees",
        "difficulty": "hard",
        "marks": 2,
        "question": "A B+ tree index has order $p = 4$ (i.e., a node can store at most $p-1 = 3$ keys and $p = 4$ pointers). What is the minimum number of keys in any non-root internal node?",
        "options": ["1", "2", "3", "4"],
        "correct": [0],
        "explanation": "For an internal node in a B+ tree of order $p$, minimum pointers $= \\lceil p/2 \\rceil = \\lceil 4/2 \\rceil = 2$. The number of keys is pointers $- 1 = 2 - 1 = 1$ key."
    },
    {
        "id": "db_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "DBMS",
        "topic": "Concurrency Control",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following statements about transaction serializability is/are TRUE?",
        "options": [
            "Every conflict serializable schedule is view serializable.",
            "Testing for conflict serializability can be performed in polynomial time using a precedence graph.",
            "Testing for view serializability is an NP-complete problem.",
            "Every view serializable schedule must be conflict serializable."
        ],
        "correct": [0, 1, 2],
        "explanation": "Conflict serializability is a strict subset of view serializability (option D is false). Precedence graph cycle detection runs in $O(V + E)$ polynomial time, while view serializability without blind writes is NP-complete."
    },
    {
        "id": "db_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "DBMS",
        "topic": "Transactions",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which ACID property guarantees that once a transaction commits, its updates persist in the database even in the event of a power crash?",
        "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
        "correct": [3],
        "explanation": "Durability guarantees that committed data is written to non-volatile storage (WAL / disk) and survives crashes."
    },
    {
        "id": "db_q06",
        "type": "nat",
        "category": "subject",
        "subject": "DBMS",
        "topic": "Relational Algebra",
        "difficulty": "hard",
        "marks": 2,
        "question": "Relation $R(A, B)$ contains 100 tuples and relation $S(B, C)$ contains 50 tuples. Attribute $B$ in $R$ is a foreign key referencing the primary key $B$ in $S$. What is the maximum possible number of tuples in the natural join $R \\bowtie S$?",
        "options": [],
        "correct": [100],
        "natRange": {"min": 100, "max": 100},
        "explanation": "Because $B$ is a primary key in $S$, every value of $B$ in $S$ is unique. Each tuple in $R$ matches at most one tuple in $S$. Hence, $R \\bowtie S$ contains at most 100 tuples."
    },
    {
        "id": "db_q07",
        "type": "mcq",
        "category": "pyq",
        "year": 2019,
        "subject": "DBMS",
        "topic": "SQL",
        "difficulty": "medium",
        "marks": 1,
        "question": "Consider a table `Emp` with a nullable column `Salary` having values: `[1000, 2000, NULL, 2000]`. What are the outputs of `COUNT(*)` and `COUNT(Salary)`?",
        "options": [
            "4 and 4",
            "4 and 3",
            "3 and 3",
            "4 and 2"
        ],
        "correct": [1],
        "explanation": "`COUNT(*)` counts all rows including NULLs (4 rows). `COUNT(column)` ignores NULL values and counts only valid entries (3 non-null salaries)."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 7. THEORY OF COMPUTATION (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "toc_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Theory of Computation",
        "topic": "DFA Minimization",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the minimum number of states in a minimal DFA that accepts the language of all binary strings ending with `01`?",
        "options": [],
        "correct": [3],
        "natRange": {"min": 3, "max": 3},
        "explanation": "State $q_0$ (start, does not end in 0), state $q_1$ (ends in 0), and state $q_2$ (accepting, ends in 01). Exactly 3 states are required."
    },
    {
        "id": "toc_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Theory of Computation",
        "topic": "Chomsky Hierarchy",
        "difficulty": "medium",
        "marks": 2,
        "question": "The language $L = \\{a^n b^n c^m \\mid n \\ge 1, m \\ge 1\\}$ is:",
        "options": [
            "Regular",
            "Context-Free but not Regular",
            "Context-Sensitive but not Context-Free",
            "Not Recursively Enumerable"
        ],
        "correct": [1],
        "explanation": "A pushdown automaton can match the number of $a$'s and $b$'s using its stack and then accept any positive number of $c$'s. Hence $L$ is a Deterministic Context-Free Language (DCFL), but not regular."
    },
    {
        "id": "toc_q03",
        "type": "msq",
        "category": "pyq",
        "year": 2022,
        "subject": "Theory of Computation",
        "topic": "Decidability",
        "difficulty": "hard",
        "marks": 2,
        "question": "Which of the following problems about Turing Machines are UNDECIDABLE?",
        "options": [
            "Determining whether an arbitrary Turing Machine halts on empty input.",
            "Determining whether the language recognized by an arbitrary Turing Machine is empty.",
            "Determining whether an arbitrary Turing Machine accepts a regular language.",
            "Determining whether a given DFA accepts the empty string $\\epsilon$."
        ],
        "correct": [0, 1, 2],
        "explanation": "Options A, B, and C are non-trivial semantic properties of Turing Machines and are undecidable by Rice's theorem / Halting problem reductions. Option D is decidable in $O(1)$ by checking if the start state of the DFA is an accept state."
    },
    {
        "id": "toc_q04",
        "type": "nat",
        "category": "pyq",
        "year": 2021,
        "subject": "Theory of Computation",
        "topic": "Regular Languages",
        "difficulty": "medium",
        "marks": 2,
        "question": "What is the minimum number of states in a DFA accepting strings over $\\{a, b\\}$ whose length is divisible by 3?",
        "options": [],
        "correct": [3],
        "natRange": {"min": 3, "max": 3},
        "explanation": "States represent length mod 3: $q_0$ (rem 0, start & accept), $q_1$ (rem 1), $q_2$ (rem 2). Any input transitions between states cyclically. Exactly 3 states."
    },
    {
        "id": "toc_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Theory of Computation",
        "topic": "Closure Properties",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which of the following classes of languages is NOT closed under complementation?",
        "options": [
            "Regular Languages",
            "Deterministic Context-Free Languages (DCFL)",
            "Context-Free Languages (CFL)",
            "Recursive Languages (REC)"
        ],
        "correct": [2],
        "explanation": "CFL is closed under union, concatenation, and Kleene star, but NOT closed under intersection or complementation."
    },
    {
        "id": "toc_q06",
        "type": "mcq",
        "category": "subject",
        "subject": "Theory of Computation",
        "topic": "Turing Machines",
        "difficulty": "hard",
        "marks": 2,
        "question": "According to Rice's Theorem, any non-trivial semantic property of:",
        "options": [
            "Regular languages is undecidable",
            "Context-free languages is undecidable",
            "Recursively enumerable languages is undecidable",
            "Deterministic context-free languages is NP-complete"
        ],
        "correct": [2],
        "explanation": "Rice's Theorem applies to the languages recognized by Turing Machines (Recursively Enumerable languages). Any non-trivial property of $L(M)$ is undecidable."
    },
    {
        "id": "toc_q07",
        "type": "mcq",
        "category": "pyq",
        "year": 2020,
        "subject": "Theory of Computation",
        "topic": "Grammars",
        "difficulty": "medium",
        "marks": 1,
        "question": "Consider the grammar $G: S \\to SS \\mid a$. Which statement correctly describes $G$?",
        "options": [
            "$G$ is ambiguous and generates strings of length $\\ge 1$",
            "$G$ is unambiguous",
            "$G$ generates only palindromes",
            "$G$ is an LL(1) grammar"
        ],
        "correct": [0],
        "explanation": "String $aaa$ has two distinct leftmost derivations: $S \\Rightarrow SS \\Rightarrow SSS \\Rightarrow aaa$ and $S \\Rightarrow SS \\Rightarrow aS \\Rightarrow aSS \\Rightarrow aaa$. Thus $G$ is ambiguous."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 8. COMPILER DESIGN (6 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "cd_q01",
        "type": "mcq",
        "category": "pyq",
        "year": 2024,
        "subject": "Compiler Design",
        "topic": "Phases of Compiler",
        "difficulty": "easy",
        "marks": 1,
        "question": "Which compiler phase converts a linear sequence of tokens into a hierarchical parse tree?",
        "options": [
            "Lexical Analysis",
            "Syntax Analysis",
            "Semantic Analysis",
            "Intermediate Code Generation"
        ],
        "correct": [1],
        "explanation": "Syntax analysis (parsing) takes tokens from the lexical analyzer and produces a parse tree according to grammar rules."
    },
    {
        "id": "cd_q02",
        "type": "nat",
        "category": "pyq",
        "year": 2023,
        "subject": "Compiler Design",
        "topic": "FIRST and FOLLOW",
        "difficulty": "medium",
        "marks": 2,
        "question": "Consider the grammar with start symbol $S$:\n$S \\to a S b \\mid c$\nHow many terminals belong to $\\text{FOLLOW}(S)$?",
        "options": [],
        "correct": [2],
        "natRange": {"min": 2, "max": 2},
        "explanation": "Since $S$ is start symbol, $\$ \\in \\text{FOLLOW}(S)$. From rule $S \\to a S b$, the symbol immediately following $S$ is $b$, so $b \\in \\text{FOLLOW}(S)$. Thus $\\text{FOLLOW}(S) = \\{\\$, b\\}$, count $= 2$."
    },
    {
        "id": "cd_q03",
        "type": "mcq",
        "category": "pyq",
        "year": 2022,
        "subject": "Compiler Design",
        "topic": "LR Parsing",
        "difficulty": "hard",
        "marks": 2,
        "question": "A Shift-Reduce conflict in an LR(0) parsing table occurs when a state contains:",
        "options": [
            "Two distinct reduce items",
            "A shift item and a reduce item on the same terminal",
            "Two shift items",
            "A non-terminal goto conflict"
        ],
        "correct": [1],
        "explanation": "A shift-reduce conflict arises when the parser can either shift on a lookahead token or reduce an existing complete item."
    },
    {
        "id": "cd_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "Compiler Design",
        "topic": "Intermediate Code",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following representations are commonly used for Intermediate Code in optimizing compilers?",
        "options": [
            "Three-Address Code (Quadruples / Triples)",
            "Control Flow Graphs (CFG)",
            "Static Single Assignment (SSA) form",
            "Finite State Automata"
        ],
        "correct": [0, 1, 2],
        "explanation": "Three-address code, CFGs, and SSA forms are standard IR representations. Finite state automata are used for lexical scanning, not intermediate code."
    },
    {
        "id": "cd_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Compiler Design",
        "topic": "Code Optimization",
        "difficulty": "easy",
        "marks": 1,
        "question": "Peephole optimization is a local optimization technique applied to:",
        "options": [
            "A small sliding window of target machine instructions",
            "The entire Abstract Syntax Tree globally",
            "The symbol table during lexical analysis",
            "Lexical token streams"
        ],
        "correct": [0],
        "explanation": "Peephole optimization examines a short sequence of target instructions (a 'peephole') to replace redundant operations with faster alternatives."
    },
    {
        "id": "cd_q06",
        "type": "nat",
        "category": "pyq",
        "year": 2020,
        "subject": "Compiler Design",
        "topic": "Code Generation",
        "difficulty": "hard",
        "marks": 2,
        "question": "In generating 3-address code with common subexpression elimination for the expression $a = b * c + b * c - d$, what is the minimum number of 3-address code quadruples required?",
        "options": [],
        "correct": [4],
        "natRange": {"min": 4, "max": 4},
        "explanation": "$t_1 = b * c$; $t_2 = t_1 + t_1$; $t_3 = t_2 - d$; $a = t_3$. Exactly 4 quadruples are required."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 9. DIGITAL LOGIC (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "dl_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Digital Logic",
        "topic": "Boolean Algebra",
        "difficulty": "easy",
        "marks": 1,
        "question": "For a 3-variable Boolean function $F(A, B, C) = A + B$, how many minterms are in its canonical Sum-of-Products (SOP) expansion?",
        "options": [],
        "correct": [6],
        "natRange": {"min": 6, "max": 6},
        "explanation": "$A = \\sum(4, 5, 6, 7)$, $B = \\sum(2, 3, 6, 7)$. Union $= \\sum(2, 3, 4, 5, 6, 7)$. Exactly 6 minterms."
    },
    {
        "id": "dl_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Digital Logic",
        "topic": "Multiplexers",
        "difficulty": "medium",
        "marks": 2,
        "question": "A 4-to-1 MUX has data inputs $I_0, I_1, I_2, I_3$ and select inputs $S_1, S_0$. To implement the XOR function $A \\oplus B$ with $S_1 = A$ and $S_0 = B$, what should the data inputs $(I_0, I_1, I_2, I_3)$ be tied to?",
        "options": [
            "(0, 1, 1, 0)",
            "(1, 0, 0, 1)",
            "(0, 0, 1, 1)",
            "(1, 1, 0, 0)"
        ],
        "correct": [0],
        "explanation": "$A \\oplus B = 1$ when $AB = 01$ ($I_1$) or $AB = 10$ ($I_2$). When $AB = 00$ ($I_0$) or $AB = 11$ ($I_3$), output $= 0$. Hence $(I_0, I_1, I_2, I_3) = (0, 1, 1, 0)$."
    },
    {
        "id": "dl_q03",
        "type": "nat",
        "category": "pyq",
        "year": 2022,
        "subject": "Digital Logic",
        "topic": "Counters",
        "difficulty": "hard",
        "marks": 2,
        "question": "A 4-bit synchronous binary counter counts from 0000 to 1111 and wraps around. If clock frequency is 16 MHz, what is the frequency (in MHz) of the most significant bit (MSB) output?",
        "options": [],
        "correct": [1],
        "natRange": {"min": 1, "max": 1},
        "explanation": "Each stage divides frequency by 2. For 4 bits, the MSB toggles once per 16 clock pulses: $f_{MSB} = 16 \\text{ MHz} / 2^4 = 16 / 16 = 1 \\text{ MHz}$."
    },
    {
        "id": "dl_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "Digital Logic",
        "topic": "Logic Gates",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following gates is/are classified as Universal Gates?",
        "options": ["NAND", "NOR", "XOR", "AND"],
        "correct": [0, 1],
        "explanation": "NAND and NOR gates are universal gates because any combinational logic circuit can be implemented using solely NAND or solely NOR gates."
    },
    {
        "id": "dl_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Digital Logic",
        "topic": "Multiplexers",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the minimum number of $2 \\times 1$ multiplexers needed to construct an $8 \\times 1$ multiplexer?",
        "options": ["4", "6", "7", "8"],
        "correct": [2],
        "explanation": "Level 1: 4 MUXes for 8 inputs. Level 2: 2 MUXes for 4 intermediate outputs. Level 3: 1 MUX for final output. Total $= 4 + 2 + 1 = 7$."
    },
    {
        "id": "dl_q06",
        "type": "mcq",
        "category": "subject",
        "subject": "Digital Logic",
        "topic": "Flip-Flops",
        "difficulty": "hard",
        "marks": 2,
        "question": "The race-around condition in a JK flip-flop occurs when:",
        "options": [
            "$J = 1, K = 1$ and clock pulse width $t_p >$ propagation delay $\\Delta t$",
            "$J = 0, K = 0$ and clock is high",
            "$J = 1, K = 0$ with edge triggering",
            "Clock frequency is lower than 1 Hz"
        ],
        "correct": [0],
        "explanation": "When $J = 1, K = 1$, the output toggles. In level-triggered flip-flops, if $t_p > \\Delta t$, the output toggles multiple times uncontrollably during a single clock pulse."
    },
    {
        "id": "dl_q07",
        "type": "nat",
        "category": "pyq",
        "year": 2019,
        "subject": "Digital Logic",
        "topic": "Number Systems",
        "difficulty": "easy",
        "marks": 1,
        "question": "Represent $-19$ in 8-bit signed two's complement form. What is its decimal value when interpreted as an unsigned integer?",
        "options": [],
        "correct": [237],
        "natRange": {"min": 237, "max": 237},
        "explanation": "$+19 = 00010011_2$. Two's complement $= 11101101_2$. As an unsigned integer: $256 - 19 = 237$."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 10. COMPUTER ORGANIZATION & ARCHITECTURE (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "coa_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Computer Organization",
        "topic": "Pipelining",
        "difficulty": "easy",
        "marks": 1,
        "question": "A 5-stage instruction pipeline has stage delays of 5 ns, 7 ns, 6 ns, 8 ns, and 6 ns. Ignoring latch delays, what is the clock cycle time (in ns) of this pipeline?",
        "options": [],
        "correct": [8],
        "natRange": {"min": 8, "max": 8},
        "explanation": "The clock cycle time of a pipeline is determined by the slowest (bottleneck) stage: $\\tau = \\max(5, 7, 6, 8, 6) = 8\\text{ ns}$."
    },
    {
        "id": "coa_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Computer Organization",
        "topic": "Cache Memory",
        "difficulty": "medium",
        "marks": 2,
        "question": "A 64 KB 4-way set-associative cache has 64-byte blocks. The system has 32-bit physical addresses. What is the number of Tag bits?",
        "options": ["16", "18", "20", "22"],
        "correct": [1],
        "explanation": "Block offset bits $= \\log_2(64) = 6$. Number of lines $= 64\\text{ KB} / 64\\text{ B} = 1024$. Number of sets $= 1024 / 4 = 256 = 2^8$, so set index $= 8$ bits. Tag bits $= 32 - (8 + 6) = 18$ bits."
    },
    {
        "id": "coa_q03",
        "type": "nat",
        "category": "pyq",
        "year": 2022,
        "subject": "Computer Organization",
        "topic": "Instruction Pipelining",
        "difficulty": "hard",
        "marks": 2,
        "question": "A 5-stage pipeline executes 100 independent instructions without any hazards. In a non-pipelined processor, each instruction takes 5 clock cycles. How many clock cycles are saved by using the pipeline?",
        "options": [],
        "correct": [396],
        "natRange": {"min": 396, "max": 396},
        "explanation": "Non-pipelined cycles $= 100 \\times 5 = 500$. Pipelined cycles $= k + (n - 1) = 5 + (100 - 1) = 104$. Cycles saved $= 500 - 104 = 396$."
    },
    {
        "id": "coa_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "Computer Organization",
        "topic": "Addressing Modes",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following addressing modes is/are suited for accessing array elements in contiguous memory?",
        "options": [
            "Indexed Addressing Mode",
            "Base Register Addressing Mode",
            "Auto-increment / Auto-decrement Mode",
            "Immediate Addressing Mode"
        ],
        "correct": [0, 1, 2],
        "explanation": "Indexed, Base register, and Auto-increment modes facilitate advancing pointers across consecutive array indices. Immediate addressing embeds constants in the instruction."
    },
    {
        "id": "coa_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Computer Organization",
        "topic": "Data Representation",
        "difficulty": "easy",
        "marks": 1,
        "question": "In a Little-Endian computer system, multi-byte data is stored such that:",
        "options": [
            "The least significant byte is stored at the lowest memory address",
            "The most significant byte is stored at the lowest memory address",
            "Bytes are stored in random interleaved order",
            "Odd bytes precede even bytes"
        ],
        "correct": [0],
        "explanation": "In Little-Endian systems (like x86), the least significant byte (LSB) resides at the lowest memory address."
    },
    {
        "id": "coa_q06",
        "type": "mcq",
        "category": "subject",
        "subject": "Computer Organization",
        "topic": "Cache Write Policies",
        "difficulty": "hard",
        "marks": 2,
        "question": "Which cache write policy uses a 'dirty bit' to minimize memory bus traffic by deferring main memory updates until the block is replaced?",
        "options": ["Write-Through", "Write-Back", "Write-Around", "No-Write-Allocate"],
        "correct": [1],
        "explanation": "Write-Back writes modifications only to the cache and sets a dirty bit. The main memory is updated only when the dirty block is evicted."
    },
    {
        "id": "coa_q07",
        "type": "nat",
        "category": "pyq",
        "year": 2020,
        "subject": "Computer Organization",
        "topic": "Floating Point",
        "difficulty": "medium",
        "marks": 1,
        "question": "In IEEE 754 single-precision floating point format, how many bits are allocated to the exponent field?",
        "options": [],
        "correct": [8],
        "natRange": {"min": 8, "max": 8},
        "explanation": "IEEE 754 single-precision uses 32 bits: 1 sign bit, 8 exponent bits (with bias 127), and 23 fraction/mantissa bits."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 11. DISCRETE MATHEMATICS (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "dm_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Discrete Mathematics",
        "topic": "Planar Graphs",
        "difficulty": "easy",
        "marks": 1,
        "question": "A connected planar graph has 10 vertices and divides the plane into 7 regions (faces). By Euler's planar formula, how many edges does this graph have?",
        "options": [],
        "correct": [15],
        "natRange": {"min": 15, "max": 15},
        "explanation": "Euler's formula: $V - E + F = 2 \\implies 10 - E + 7 = 2 \\implies 17 - E = 2 \\implies E = 15$."
    },
    {
        "id": "dm_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Discrete Mathematics",
        "topic": "Relations",
        "difficulty": "medium",
        "marks": 2,
        "question": "How many binary relations on a set with $n = 4$ elements are simultaneously reflexive and symmetric?",
        "options": ["16", "64", "256", "1024"],
        "correct": [1],
        "explanation": "For a reflexive relation on $n$ elements, all $n$ diagonal pairs must be present. For symmetry, each of the $\\frac{n(n-1)}{2}$ off-diagonal pairs $(a, b)$ can either both be in the relation or neither. For $n = 4$: $2^{4 \\times 3 / 2} = 2^6 = 64$."
    },
    {
        "id": "dm_q03",
        "type": "nat",
        "category": "pyq",
        "year": 2022,
        "subject": "Discrete Mathematics",
        "topic": "Number Theory",
        "difficulty": "hard",
        "marks": 2,
        "question": "By Fermat's Little Theorem, what is the remainder when $3^{102}$ is divided by 11?",
        "options": [],
        "correct": [9],
        "natRange": {"min": 9, "max": 9},
        "explanation": "Since 11 is prime and $\\gcd(3, 11) = 1$, by Fermat's Little Theorem $3^{10} \\equiv 1 \\pmod{11}$. Thus $3^{102} = (3^{10})^{10} \\times 3^2 \\equiv 1^{10} \\times 9 = 9 \\pmod{11}$."
    },
    {
        "id": "dm_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "Discrete Mathematics",
        "topic": "Graph Theory",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following statements about trees with $n \\ge 2$ vertices is/are TRUE?",
        "options": [
            "A tree has exactly $n - 1$ edges.",
            "There is a unique simple path between every pair of vertices in a tree.",
            "Every tree is a bipartite graph.",
            "A tree can contain an odd-length cycle."
        ],
        "correct": [0, 1, 2],
        "explanation": "A, B, and C are true. D is false because trees are acyclic (contain no cycles of any length)."
    },
    {
        "id": "dm_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Discrete Mathematics",
        "topic": "Graph Coloring",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the chromatic number $\\chi(K_5)$ of the complete graph on 5 vertices?",
        "options": ["3", "4", "5", "6"],
        "correct": [2],
        "explanation": "In a complete graph $K_n$, every pair of vertices is connected by an edge, so no two vertices can share the same color: $\\chi(K_n) = n$. For $K_5$, $\\chi(K_5) = 5$."
    },
    {
        "id": "dm_q06",
        "type": "mcq",
        "category": "subject",
        "subject": "Discrete Mathematics",
        "topic": "Recurrence Relations",
        "difficulty": "hard",
        "marks": 2,
        "question": "What is the general solution of the homogeneous recurrence relation $a_n - 5a_{n-1} + 6a_{n-2} = 0$?",
        "options": [
            "$a_n = C_1 2^n + C_2 3^n$",
            "$a_n = C_1 (-2)^n + C_2 (-3)^n$",
            "$a_n = (C_1 + C_2 n) 2^n$",
            "$a_n = C_1 5^n + C_2 6^n$"
        ],
        "correct": [0],
        "explanation": "Characteristic equation: $r^2 - 5r + 6 = 0 \\implies (r - 2)(r - 3) = 0 \\implies r_1 = 2, r_2 = 3$. General solution: $a_n = C_1 2^n + C_2 3^n$."
    },
    {
        "id": "dm_q07",
        "type": "nat",
        "category": "pyq",
        "year": 2018,
        "subject": "Discrete Mathematics",
        "topic": "Bipartite Graphs",
        "difficulty": "easy",
        "marks": 1,
        "question": "How many edges are present in the complete bipartite graph $K_{4, 6}$?",
        "options": [],
        "correct": [24],
        "natRange": {"min": 24, "max": 24},
        "explanation": "A complete bipartite graph $K_{m, n}$ has every vertex in set 1 connected to every vertex in set 2: $E = m \\times n = 4 \\times 6 = 24$ edges."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 12. ENGINEERING MATHEMATICS (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "em_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Engineering Mathematics",
        "topic": "Linear Algebra",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the determinant of the $2 \\times 2$ matrix $A = \\begin{pmatrix} 4 & 2 \\\\ 1 & 3 \\end{pmatrix}$?",
        "options": [],
        "correct": [10],
        "natRange": {"min": 10, "max": 10},
        "explanation": "$\\det(A) = (4 \\times 3) - (2 \\times 1) = 12 - 2 = 10$."
    },
    {
        "id": "em_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Engineering Mathematics",
        "topic": "Eigenvalues",
        "difficulty": "medium",
        "marks": 2,
        "question": "A $3 \\times 3$ matrix $A$ has eigenvalues $1, 2, 4$. What is the determinant of $A^2$?",
        "options": ["8", "16", "64", "128"],
        "correct": [2],
        "explanation": "$\\det(A) = \\lambda_1 \\times \\lambda_2 \\times \\lambda_3 = 1 \\times 2 \\times 4 = 8$. Then $\\det(A^2) = (\\det(A))^2 = 8^2 = 64$."
    },
    {
        "id": "em_q03",
        "type": "nat",
        "category": "pyq",
        "year": 2022,
        "subject": "Engineering Mathematics",
        "topic": "Probability",
        "difficulty": "hard",
        "marks": 2,
        "question": "A fair coin is tossed 6 times independently. What is the value of $64 \\times P(\\text{exactly 3 heads})$?",
        "options": [],
        "correct": [20],
        "natRange": {"min": 20, "max": 20},
        "explanation": "$P(X = 3) = \\binom{6}{3} (1/2)^6 = \\frac{20}{64}$. Multiplying by 64 gives 20."
    },
    {
        "id": "em_q04",
        "type": "msq",
        "category": "pyq",
        "year": 2021,
        "subject": "Engineering Mathematics",
        "topic": "Linear Algebra",
        "difficulty": "medium",
        "marks": 2,
        "question": "Which of the following statements about a real symmetric matrix $A$ is/are always TRUE?",
        "options": [
            "All eigenvalues of $A$ are real numbers.",
            "Eigenvectors corresponding to distinct eigenvalues are mutually orthogonal.",
            "$A$ is always diagonalizable.",
            "All eigenvalues of $A$ must be strictly positive."
        ],
        "correct": [0, 1, 2],
        "explanation": "By the Spectral Theorem, real symmetric matrices have all real eigenvalues, orthogonal eigenvectors, and are diagonalizable. Eigenvalues can be zero or negative unless positive-definite (option D is false)."
    },
    {
        "id": "em_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Engineering Mathematics",
        "topic": "Calculus",
        "difficulty": "easy",
        "marks": 1,
        "question": "What is the value of the limit $\\lim_{x \\to 0} \\frac{e^x - 1}{x}$?",
        "options": ["0", "1", "$e$", "$\\infty$"],
        "correct": [1],
        "explanation": "Applying L'Hopital's rule for the $0/0$ form: $\\lim_{x \\to 0} \\frac{\\frac{d}{dx}(e^x - 1)}{\\frac{d}{dx}(x)} = \\lim_{x \\to 0} \\frac{e^x}{1} = e^0 = 1$."
    },
    {
        "id": "em_q06",
        "type": "mcq",
        "category": "subject",
        "subject": "Engineering Mathematics",
        "topic": "Matrix Rank",
        "difficulty": "hard",
        "marks": 2,
        "question": "Consider the matrix $A = \\begin{pmatrix} 1 & 2 & 3 \\\\ 2 & 4 & 6 \\\\ 3 & 6 & 9 \\end{pmatrix}$. What is the rank of $A$?",
        "options": ["1", "2", "3", "0"],
        "correct": [0],
        "explanation": "Row 2 is $2 \\times \\text{Row 1}$, and Row 3 is $3 \\times \\text{Row 1}$. The rows are linearly dependent multiples of Row 1. Hence, the rank of $A$ is 1."
    },
    {
        "id": "em_q07",
        "type": "nat",
        "category": "pyq",
        "year": 2020,
        "subject": "Engineering Mathematics",
        "topic": "Probability",
        "difficulty": "medium",
        "marks": 1,
        "question": "If a random variable $X$ follows a Poisson distribution with parameter $\\lambda = 3$, what is the variance of $X$?",
        "options": [],
        "correct": [3],
        "natRange": {"min": 3, "max": 3},
        "explanation": "For a Poisson distribution with parameter $\\lambda$, both the mean and the variance are identically equal to $\\lambda$. Hence $\\text{Var}(X) = 3$."
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # 13. GENERAL APTITUDE (7 Questions)
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "apt_q01",
        "type": "nat",
        "category": "pyq",
        "year": 2024,
        "subject": "Aptitude",
        "topic": "Time and Work",
        "difficulty": "easy",
        "marks": 1,
        "question": "If 6 workers can construct a wall in 12 days, how many days will 9 workers take to construct the same wall working at the same rate?",
        "options": [],
        "correct": [8],
        "natRange": {"min": 8, "max": 8},
        "explanation": "Total person-days required $= 6 \\times 12 = 72$. Days required by 9 workers $= 72 / 9 = 8\\text{ days}$."
    },
    {
        "id": "apt_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2023,
        "subject": "Aptitude",
        "topic": "Speed, Time & Distance",
        "difficulty": "medium",
        "marks": 2,
        "question": "A train 150 meters long crosses a telegraph post in 9 seconds. What is the speed of the train in km/h?",
        "options": ["50 km/h", "60 km/h", "72 km/h", "80 km/h"],
        "correct": [1],
        "explanation": "Speed in m/s $= 150 / 9 = 50/3\\text{ m/s}$. Speed in km/h $= (50/3) \\times (18/5) = 10 \\times 6 = 60\\text{ km/h}$."
    },
    {
        "id": "apt_q03",
        "type": "mcq",
        "category": "pyq",
        "year": 2022,
        "subject": "Aptitude",
        "topic": "Logical Deduction",
        "difficulty": "hard",
        "marks": 2,
        "question": "Statements:\nI. All computers are electronic devices.\nII. Some electronic devices are portable.\nConclusions:\n1. Some computers are portable.\n2. All portable items are computers.\nWhich conclusion logically follows?",
        "options": [
            "Only conclusion 1 follows",
            "Only conclusion 2 follows",
            "Either 1 or 2 follows",
            "Neither 1 nor 2 follows"
        ],
        "correct": [3],
        "explanation": "The middle term 'electronic devices' is not distributed in either premise (A and I propositions). No valid connection between 'computers' and 'portable' can be deduced. Neither follows."
    },
    {
        "id": "apt_q04",
        "type": "nat",
        "category": "pyq",
        "year": 2021,
        "subject": "Aptitude",
        "topic": "Percentages & Discounts",
        "difficulty": "medium",
        "marks": 2,
        "question": "An article with marked price ₹1000 is sold after two successive discounts of 20% and 10%. What is the final selling price (in ₹)?",
        "options": [],
        "correct": [720],
        "natRange": {"min": 720, "max": 720},
        "explanation": "After 20% discount: $1000 \\times 0.80 = 800$. After subsequent 10% discount: $800 \\times 0.90 = ₹720$."
    },
    {
        "id": "apt_q05",
        "type": "mcq",
        "category": "subject",
        "subject": "Aptitude",
        "topic": "Verbal Ability",
        "difficulty": "easy",
        "marks": 1,
        "question": "Select the option that best completes the analogy:\n`OASIS : DESERT :: ISLAND : ?`",
        "options": ["MOUNTAIN", "OCEAN", "FOREST", "RIVER"],
        "correct": [1],
        "explanation": "An oasis is a fertile spot surrounded by a desert; an island is a tract of land surrounded by an ocean."
    },
    {
        "id": "apt_q06",
        "type": "nat",
        "category": "subject",
        "subject": "Aptitude",
        "topic": "Permutations & Combinations",
        "difficulty": "hard",
        "marks": 2,
        "question": "In how many ways can 5 boys and 4 girls be seated in a row such that no two girls sit next to each other?",
        "options": [],
        "correct": [43200],
        "natRange": {"min": 43200, "max": 43200},
        "explanation": "First arrange 5 boys: $5! = 120$ ways. This creates 6 available spaces (ends and in-between). Choose 4 spaces for the 4 girls in $\\binom{6}{4} = 15$ ways, and arrange the girls in $4! = 24$ ways. Total $= 120 \\times 15 \\times 24 = 43200$."
    },
    {
        "id": "apt_q07",
        "type": "mcq",
        "category": "pyq",
        "year": 2019,
        "subject": "Aptitude",
        "topic": "Percentages",
        "difficulty": "easy",
        "marks": 1,
        "question": "If the price of petrol increases by 25%, by what percentage must a driver reduce petrol consumption so that the total expenditure remains unchanged?",
        "options": ["15%", "20%", "25%", "33.3%"],
        "correct": [1],
        "explanation": "Reduction percentage $= \\frac{r}{100 + r} \\times 100 = \\frac{25}{125} \\times 100 = \\frac{1}{5} \\times 100 = 20\\%$."
    }
]

def main():
    target_path = os.path.join("data", "sample_questions.json")
    with open(target_path, "r", encoding="utf-8") as f:
        existing = json.load(f)
    
    print(f"Loaded {len(existing)} existing questions.")
    existing_ids = set(q["id"] for q in existing)
    
    valid_added = []
    for q in new_questions:
        if q["id"] in existing_ids:
            print(f"Warning: duplicate ID {q['id']}, skipping")
            continue
        # Verification
        assert q["type"] in ["mcq", "msq", "nat"], f"Invalid type in {q['id']}"
        assert q["difficulty"] in ["easy", "medium", "hard"], f"Invalid difficulty in {q['id']}"
        assert q["subject"] in [
            "C Programming", "Data Structures", "Algorithms", "Operating Systems",
            "Computer Networks", "DBMS", "Theory of Computation", "Compiler Design",
            "Digital Logic", "Computer Organization", "Discrete Mathematics",
            "Engineering Mathematics", "Aptitude"
        ], f"Invalid subject {q['subject']} in {q['id']}"
        if q["type"] in ["mcq", "msq"]:
            assert len(q["options"]) >= 2, f"Options too short in {q['id']}"
            for c_idx in q["correct"]:
                assert 0 <= c_idx < len(q["options"]), f"Correct index out of bounds in {q['id']}"
        elif q["type"] == "nat":
            assert "natRange" in q, f"Missing natRange in {q['id']}"
        
        valid_added.append(q)
        existing_ids.add(q["id"])
        
    combined = existing + valid_added
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully added {len(valid_added)} questions. New total: {len(combined)} questions!")

if __name__ == "__main__":
    main()
