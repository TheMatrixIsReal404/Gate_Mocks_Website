# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

brace_stack = []
paren_stack = []
bracket_stack = []

in_string = None
escape = False
in_line_comment = False
in_block_comment = False

line = 1
col = 1

for i, ch in enumerate(text):
    if ch == '\n':
        line += 1
        col = 1
        in_line_comment = False
        continue
    else:
        col += 1

    if in_line_comment:
        continue

    if in_block_comment:
        if ch == '/' and text[i-1] == '*':
            in_block_comment = False
        continue

    if in_string:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == in_string:
            in_string = None
        continue

    if ch in ('"', "'", '`'):
        in_string = ch
        continue

    if ch == '/' and i + 1 < len(text):
        if text[i+1] == '/':
            in_line_comment = True
            continue
        elif text[i+1] == '*':
            in_block_comment = True
            continue

    if ch == '{': brace_stack.append((line, col))
    elif ch == '}':
        if not brace_stack:
            print(f'Unmatched }} at {line}:{col}')
            break
        brace_stack.pop()

    if ch == '(': paren_stack.append((line, col))
    elif ch == ')':
        if not paren_stack:
            print(f'Unmatched ) at {line}:{col}')
            break
        paren_stack.pop()

    if ch == '[': bracket_stack.append((line, col))
    elif ch == ']':
        if not bracket_stack:
            print(f'Unmatched ] at {line}:{col}')
            break
        bracket_stack.pop()

print('Braces left:', len(brace_stack))
print('Parens left:', len(paren_stack))
print('Brackets left:', len(bracket_stack))
if brace_stack:
    print('Unclosed brace at:', brace_stack[-1])
if paren_stack:
    print('Unclosed paren at:', paren_stack[-1])
if bracket_stack:
    print('Unclosed bracket at:', bracket_stack[-1])
