# -*- coding: utf-8 -*-
"""
Deduplicates sample_questions.json:
Replaces 8 duplicate/redundant questions (c001, os001, os005, os_q06, ds011, ds_q02, em002, em_q06)
with 8 authentic, distinct GATE CSE questions from Gate Overflow.
"""

import json

REPLACEMENTS = {
    "c001": {
        "id": "c001",
        "type": "mcq",
        "category": "subject",
        "subject": "C Programming",
        "topic": "Strings and Pointers",
        "difficulty": "medium",
        "year": None,
        "mockId": "mock-full-001",
        "marks": 1,
        "question": "What is the output of the following C program?\n```c\n#include <stdio.h>\nint main() {\n    char str[] = \"GATECS\";\n    char *p = str + 2;\n    printf(\"%s\", p);\n    return 0;\n}\n```",
        "options": ["\"TECS\"", "\"GATECS\"", "\"CS\"", "\"ATECS\""],
        "correct": [0],
        "explanation": "In C, `str` points to the first character `'G'`. Pointer arithmetic `str + 2` points to the character at index 2, which is `'T'`. `printf(\"%s\", p)` prints the null-terminated string starting at `'T'`, which is `\"TECS\"`."
    },
    "os001": {
        "id": "os001",
        "type": "mcq",
        "category": "subject",
        "subject": "Operating Systems",
        "topic": "Virtual Memory",
        "difficulty": "medium",
        "year": None,
        "mockId": "mock-subwise-os",
        "marks": 1,
        "question": "Thrashing in an operating system occurs when:",
        "options": [
            "A process spends more time paging than executing instructions",
            "Multiple processes deadlock over non-shareable resources",
            "The CPU utilization reaches 100% due to compute-bound processes",
            "Page tables exceed physical frame capacity"
        ],
        "correct": [0],
        "explanation": "Thrashing occurs when the system spends an excessive amount of time swapping pages in and out of memory rather than executing instructions, typically caused by insufficient allocated page frames for the working sets of active processes."
    },
    "os005": {
        "id": "os005",
        "type": "mcq",
        "category": "subject",
        "subject": "Operating Systems",
        "topic": "Process Synchronization",
        "difficulty": "medium",
        "year": None,
        "mockId": "mock-subwise-os",
        "marks": 2,
        "question": "In the classical Bounded-Buffer (Producer-Consumer) problem with a buffer capacity of $N$ slots, what should be the initial values of the counting semaphores `empty` and `full` respectively?",
        "options": [
            "`empty = N` and `full = 0`",
            "`empty = 0` and `full = N`",
            "`empty = 1` and `full = 0`",
            "`empty = N` and `full = N`"
        ],
        "correct": [0],
        "explanation": "Initially, all $N$ slots in the bounded buffer are empty and no slots contain produced items. Therefore, the counting semaphore `empty` (tracking available free slots) must be initialized to $N$, and `full` (tracking available filled items) must be initialized to $0$."
    },
    "os_q06": {
        "id": "os_q06",
        "type": "nat",
        "category": "subject",
        "subject": "Operating Systems",
        "topic": "Process Creation",
        "difficulty": "easy",
        "year": None,
        "marks": 1,
        "question": "How many child processes are created in total by the execution of the following C code snippet?\n```c\nfork();\nfork();\nfork();\n```",
        "options": [],
        "correct": [7],
        "natRange": {"min": 7, "max": 7},
        "explanation": "A sequence of $k$ unconditional `fork()` calls generates $2^k$ total processes (including the original parent process). The number of newly created child processes is $2^k - 1$. For $k = 3$, child processes created $= 2^3 - 1 = 8 - 1 = 7$."
    },
    "ds011": {
        "id": "ds011",
        "type": "nat",
        "category": "pyq",
        "year": 2016,
        "subject": "Data Structures",
        "topic": "AVL Trees",
        "difficulty": "medium",
        "marks": 2,
        "question": "What is the minimum number of nodes required to construct an AVL tree of height $4$ (where the height of a single-node tree is defined as $0$)?",
        "options": [],
        "correct": [12],
        "natRange": {"min": 12, "max": 12},
        "explanation": "The minimum number of nodes $N(h)$ in an AVL tree of height $h$ satisfies the recurrence: $N(h) = N(h - 1) + N(h - 2) + 1$, with base cases $N(0) = 1$ and $N(1) = 2$.\n- $N(2) = N(1) + N(0) + 1 = 2 + 1 + 1 = 4$\n- $N(3) = N(2) + N(1) + 1 = 4 + 2 + 1 = 7$\n- $N(4) = N(3) + N(2) + 1 = 7 + 4 + 1 = 12$ nodes."
    },
    "ds_q02": {
        "id": "ds_q02",
        "type": "mcq",
        "category": "pyq",
        "year": 2014,
        "subject": "Data Structures",
        "topic": "Graph Representation",
        "difficulty": "easy",
        "marks": 1,
        "question": "Given an undirected graph $G = (V, E)$ represented by an Adjacency Matrix, what is the worst-case time complexity to determine if an edge exists between two given vertices $u$ and $v$?",
        "options": [
            "$\\Theta(1)$",
            "$\\Theta(|V|)$",
            "$\\Theta(|E|)$",
            "$\\Theta(\\log |V|)$"
        ],
        "correct": [0],
        "explanation": "In an adjacency matrix representation, testing whether an edge exists between vertex $u$ and vertex $v$ requires directly indexing the 2D array at `adj[u][v]`, which executes in $\\Theta(1)$ constant time."
    },
    "em002": {
        "id": "em002",
        "type": "nat",
        "category": "pyq",
        "year": 2018,
        "subject": "Engineering Mathematics",
        "topic": "Probability",
        "difficulty": "medium",
        "marks": 2,
        "question": "A fair coin is tossed $4$ times independently. What is the probability of getting strictly more heads than tails?",
        "options": [],
        "correct": [0.3125],
        "natRange": {"min": 0.31, "max": 0.32},
        "explanation": "Total possible outcomes for 4 coin tosses is $2^4 = 16$. Strictly more heads than tails means either 3 heads or 4 heads.\n- Number of ways to get 3 heads: $\\binom{4}{3} = 4$\n- Number of ways to get 4 heads: $\\binom{4}{4} = 1$\nTotal favorable outcomes $= 4 + 1 = 5$.\nProbability $= \\frac{5}{16} = 0.3125$."
    },
    "em_q06": {
        "id": "em_q06",
        "type": "mcq",
        "category": "subject",
        "subject": "Engineering Mathematics",
        "topic": "Cayley-Hamilton Theorem",
        "difficulty": "medium",
        "year": None,
        "marks": 2,
        "question": "A $2 \\times 2$ matrix $A$ satisfies the characteristic equation $A^2 - 5A + 6I = 0$, where $I$ is the identity matrix. Which of the following expressions represents the inverse matrix $A^{-1}$?",
        "options": [
            "$\\frac{1}{6}(5I - A)$",
            "$\\frac{1}{6}(A - 5I)$",
            "$5I - A$",
            "$\\frac{1}{5}(6I - A)$"
        ],
        "correct": [0],
        "explanation": "Multiplying both sides of $A^2 - 5A + 6I = 0$ by $A^{-1}$:\n$A - 5I + 6A^{-1} = 0 \\implies 6A^{-1} = 5I - A \\implies A^{-1} = \\frac{1}{6}(5I - A)$."
    }
}

def main():
    with open('data/sample_questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
        
    print(f"Loaded {len(questions)} questions.")
    updated_count = 0
    for i, q in enumerate(questions):
        qid = q['id']
        if qid in REPLACEMENTS:
            questions[i] = REPLACEMENTS[qid]
            updated_count += 1
            print(f"Replaced duplicate question {qid} with authentic unique question!")
            
    print(f"Successfully replaced {updated_count} duplicate questions.")
    
    with open('data/sample_questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
        
    print("Saved clean, deduplicated database to data/sample_questions.json.")

if __name__ == '__main__':
    main()
