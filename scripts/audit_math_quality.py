# -*- coding: utf-8 -*-
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/sample_questions.json', encoding='utf-8') as f:
    master = json.load(f)

print(f"Loaded {len(master)} questions.")

nested_dollars = []
words_in_math = []
bad_commands = []
private_use_chars = []

BAD_WORDS = {'where', 'then', 'such', 'that', 'maximum', 'minimum', 'value', 'greater', 'less', 'which', 'following', 'function', 'equation', 'relation', 'between'}

for q in master:
    qid = q['id']
    q_text = q.get('question', '')
    
    # 1. Private use characters
    pua = [c for c in q_text if 0xE000 <= ord(c) <= 0xF8FF]
    if pua:
        private_use_chars.append((qid, [hex(ord(c)) for c in pua], q_text[:80]))
        
    # 2. Bad commands
    for bc in [r'\summ', r'\prodM', r'\prodm', r'\sqrtsin']:
        if bc in q_text:
            bad_commands.append((qid, bc))
            
    # 3. Strip code blocks
    no_code = re.sub(r'```[\s\S]*?```', '', q_text)
    no_code = re.sub(r'`[^`\n]+`', '', no_code)
    
    # 4. Math blocks
    # Check if there are nested dollars like $...$...$
    # or $$ inside $
    # Find all $...$
    math_segments = re.findall(r'\$([^\$]+)\$', no_code)
    for seg in math_segments:
        # check words inside
        tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', seg.lower()))
        clash = tokens.intersection(BAD_WORDS)
        if len(clash) >= 2:
            words_in_math.append((qid, clash, seg[:80]))
            
    # Check if question has odd number of unescaped $
    # (excluding escaped \$)
    escaped_clean = re.sub(r'\\\$', '', no_code)
    # remove $$ ... $$
    escaped_clean = re.sub(r'\$\$[\s\S]*?\$\$', '', escaped_clean)
    dollars = len(re.findall(r'\$', escaped_clean))
    if dollars % 2 != 0:
        nested_dollars.append((qid, dollars, q_text[:80]))

print(f"1. Questions with Private Use Area unicode characters: {len(private_use_chars)}")
for qid, pua, snip in private_use_chars[:5]:
    print(f"  {qid}: {pua} -> {snip}")

print(f"\n2. Questions with bad LaTeX commands (\\summ, \\prodM, etc.): {len(bad_commands)}")
for qid, bc in bad_commands[:5]:
    print(f"  {qid}: {bc}")

print(f"\n3. Questions with English sentences trapped in math ($...$): {len(words_in_math)}")
for qid, clash, snip in words_in_math[:5]:
    print(f"  {qid}: {clash} -> ${snip}$")

print(f"\n4. Questions with odd/unbalanced unescaped dollar signs: {len(nested_dollars)}")
for qid, d, snip in nested_dollars[:5]:
    print(f"  {qid}: {d} dollars -> {snip}")
