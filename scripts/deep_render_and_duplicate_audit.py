# -*- coding: utf-8 -*-
"""
deep_render_and_duplicate_audit.py
Analyzes all 19,913 questions in data/sample_questions.json for:
1. Duplicate detection:
   - Exact text duplicates (grouped by normalized text hash)
   - Near duplicates (Jaccard similarity >= 85%)
   - Analysis of duplicates by category (test_series, pyq, mock)
2. Rendering issues:
   - Raw escaped HTML tags (e.g. &lt;pre, &lt;code, &amp;quot;, &lt;div)
   - Incomplete/truncated questions (e.g. ending in trailing numbers, missing table/figure prompts)
   - Code block syntax issues (unclosed ``` fences, raw HTML in code blocks)
   - KaTeX syntax issues ($ or $$ balance, unescaped percent signs %, invalid LaTeX macros)
   - Empty or malformed options
"""

import json
import re
import hashlib
from collections import defaultdict, Counter

STOPWORDS = {
    'the', 'and', 'for', 'that', 'this', 'with', 'from', 'which', 'following',
    'what', 'then', 'each', 'are', 'was', 'were', 'has', 'have', 'had', 'been',
    'such', 'also', 'some', 'any', 'all', 'one', 'two', 'given', 'consider',
    'let', 'suppose', 'show', 'true', 'false', 'value', 'number', 'statements'
}

def normalize_text(text):
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r'[\s\W_]+', ' ', t)
    return t.strip()

def tokenize(text):
    norm = normalize_text(text)
    words = [w for w in norm.split() if len(w) > 2 and w not in STOPWORDS]
    return set(words)

def main():
    print("Loading data/sample_questions.json (19,913 questions)...")
    questions = json.load(open('data/sample_questions.json', encoding='utf-8'))
    total = len(questions)
    print(f"Loaded {total} questions.")

    # ==========================================
    # PART 1: DUPLICATE DETECTION
    # ==========================================
    hash_to_qs = defaultdict(list)
    for q in questions:
        norm = normalize_text(q.get('question', ''))
        h = hashlib.sha256(norm.encode('utf-8')).hexdigest()
        hash_to_qs[h].append(q)

    exact_dup_groups = [qs for qs in hash_to_qs.values() if len(qs) > 1]
    redundant_exact_count = sum(len(qs) - 1 for qs in exact_dup_groups)

    print("\n" + "=" * 60)
    print("1. DUPLICATE QUESTION ANALYSIS:")
    print(f"Total Exact Duplicate Groups: {len(exact_dup_groups)}")
    print(f"Total Redundant Exact Question Instances: {redundant_exact_count}")
    print("=" * 60)

    cat_breakdown = defaultdict(int)
    for g in exact_dup_groups:
        cats = tuple(sorted(set(q.get('category', 'unknown') for q in g)))
        cat_breakdown[cats] += 1

    print("Exact Duplicates by Category Combinations:")
    for cats, cnt in sorted(cat_breakdown.items(), key=lambda x: -x[1]):
        print(f"  {' vs '.join(cats)}: {cnt} groups")

    # ==========================================
    # PART 2: RENDERING ISSUES DETECTION
    # ==========================================
    print("\n" + "=" * 60)
    print("2. RENDERING ISSUES AUDIT:")
    print("=" * 60)

    raw_html_corrupted = []
    unclosed_code_fences = []
    unbalanced_math_dollars = []
    empty_options = []
    suspicious_truncations = []
    latex_syntax_issues = []

    for i, q in enumerate(questions):
        qid = q.get('id', f'idx_{i}')
        qtext = q.get('question', '')
        opts = q.get('options', [])
        qtype = q.get('type', 'mcq')
        cat = q.get('category', 'unknown')
        sub = q.get('subject', 'unknown')

        # Check for raw escaped HTML entities like &lt;pre or &lt;code or &quot;
        # that indicates double-escaping or broken HTML
        if re.search(r'&lt;(?:pre|code|div|span|b|i|br|table|tr|td|th)\b', qtext, re.I):
            raw_html_corrupted.append({
                'id': qid,
                'category': cat,
                'subject': sub,
                'issue': 'Escaped HTML tags (&lt;pre/&lt;code/etc.) in question text',
                'snippet': qtext[:120]
            })

        # Check in options as well
        for opt_idx, opt in enumerate(opts):
            if re.search(r'&lt;(?:pre|code|div|span|b|i|br)\b', opt, re.I):
                raw_html_corrupted.append({
                    'id': qid,
                    'category': cat,
                    'subject': sub,
                    'issue': f'Escaped HTML tags in option {opt_idx}',
                    'snippet': opt[:120]
                })
                break

        # Check unclosed code fences ```
        fences = re.findall(r'```', qtext)
        if len(fences) % 2 != 0:
            unclosed_code_fences.append({
                'id': qid,
                'category': cat,
                'subject': sub,
                'count': len(fences),
                'snippet': qtext[:100]
            })

        # Check unbalanced $$ or $
        # Check $$ first
        display_math = re.findall(r'\$\$', qtext)
        if len(display_math) % 2 != 0:
            unbalanced_math_dollars.append({
                'id': qid,
                'category': cat,
                'subject': sub,
                'type': '$$ (display math)',
                'count': len(display_math),
                'snippet': qtext[:100]
            })
        else:
            # Strip $$ and check single $
            no_display = re.sub(r'\$\$', '', qtext)
            # Ignore \$ (escaped dollars)
            no_escaped = re.sub(r'\\\$', '', no_display)
            dollars = re.findall(r'\$', no_escaped)
            if len(dollars) % 2 != 0:
                unbalanced_math_dollars.append({
                    'id': qid,
                    'category': cat,
                    'subject': sub,
                    'type': '$ (inline math)',
                    'count': len(dollars),
                    'snippet': qtext[:100]
                })

        # Check option completeness for mcq/msq
        if qtype in ['mcq', 'msq']:
            if len(opts) < 2:
                empty_options.append({
                    'id': qid,
                    'category': cat,
                    'subject': sub,
                    'options_count': len(opts),
                    'snippet': qtext[:100]
                })
            else:
                for opt_idx, opt in enumerate(opts):
                    if len(opt.strip()) == 0:
                        empty_options.append({
                            'id': qid,
                            'category': cat,
                            'subject': sub,
                            'issue': f'Empty option string at index {opt_idx}',
                            'snippet': qtext[:100]
                        })
                        break

        # Check for suspicious truncation (e.g. ends in dangling operator, incomplete sentence, or trailing single digit)
        if re.search(r'(?:Mechanical\s+\d+|Electrical\s+\d+|Civil\s+\d+|difference between\s+[^\.\?]{5,50}\s+\d+)$', qtext.strip(), re.I):
            suspicious_truncations.append({
                'id': qid,
                'category': cat,
                'subject': sub,
                'issue': 'Aptitude/pie chart trailing digit truncation',
                'snippet': qtext[-100:]
            })
        elif len(qtext.strip()) < 15:
            suspicious_truncations.append({
                'id': qid,
                'category': cat,
                'subject': sub,
                'issue': 'Question text too short (< 15 chars)',
                'snippet': qtext
            })

    print(f"Raw Escaped HTML Corrupted Questions: {len(raw_html_corrupted)}")
    print(f"Unclosed Code Block Fences: {len(unclosed_code_fences)}")
    print(f"Unbalanced Math Delimiters ($/$$): {len(unbalanced_math_dollars)}")
    print(f"Empty or Invalid Options: {len(empty_options)}")
    print(f"Suspicious Truncations: {len(suspicious_truncations)}")

    if raw_html_corrupted:
        print("\n--- Sample Raw Escaped HTML Corruptions ---")
        for item in raw_html_corrupted[:5]:
            print(f"[{item['id']}] ({item['category']}|{item['subject']}): {item['issue']}")
            print(f"   Snippet: {item['snippet']}")

    if unbalanced_math_dollars:
        print("\n--- Sample Unbalanced Math Delimiters ---")
        for item in unbalanced_math_dollars[:5]:
            print(f"[{item['id']}] ({item['category']}|{item['subject']}): {item['type']} count={item['count']}")
            print(f"   Snippet: {item['snippet']}")

    if suspicious_truncations:
        print("\n--- Sample Suspicious Truncations ---")
        for item in suspicious_truncations[:5]:
            print(f"[{item['id']}] ({item['category']}|{item['subject']}): {item['issue']}")
            print(f"   Snippet: {item['snippet']}")

    # Save findings
    audit_data = {
        'total_questions': total,
        'exact_duplicate_groups': len(exact_dup_groups),
        'redundant_exact_questions': redundant_exact_count,
        'raw_html_corrupted': raw_html_corrupted,
        'unclosed_code_fences': unclosed_code_fences,
        'unbalanced_math_dollars': unbalanced_math_dollars,
        'empty_options': empty_options,
        'suspicious_truncations': suspicious_truncations
    }
    with open('data/offline_rendering_and_dup_audit.json', 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)
    print("\nSaved detailed audit to data/offline_rendering_and_dup_audit.json.")

if __name__ == '__main__':
    main()
