# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Provider in search query
target_search = '''      (m.tier && m.tier.toLowerCase().includes(query)) ||\n\n      (m.id && m.id.toLowerCase().includes(query))'''
if target_search not in content:
    target_search = '''      (m.tier && m.tier.toLowerCase().includes(query)) ||\r\n\r\n      (m.id && m.id.toLowerCase().includes(query))'''

repl_search = '''      (m.tier && m.tier.toLowerCase().includes(query)) ||\n\n      (m.provider && m.provider.toLowerCase().includes(query)) ||\n\n      (m.id && m.id.toLowerCase().includes(query))'''
if '\r\n' in content:
    repl_search = repl_search.replace('\n', '\r\n')

assert target_search in content, 'target_search not found'
content = content.replace(target_search, repl_search)

# 2. Test overlay title with provider
target_title = '<div class="test-title" title="${mock.name}">${mock.name}</div>'
repl_title = '<div class="test-title" title="${mock.name}">${mock.name}${mock.provider ? ` <span style="font-size:12px;opacity:0.85;font-weight:500">(${mock.provider})</span>` : \'\'}</div>'
assert target_title in content, 'target_title not found'
content = content.replace(target_title, repl_title)

# 3. Session provider in submitMockTest
target_session = 'const session={mockId:mock.id,name:mock.name,date:Date.now()'
repl_session = 'const session={mockId:mock.id,name:mock.name,provider:mock.provider||\'\',date:Date.now()'
assert target_session in content, 'target_session not found'
content = content.replace(target_session, repl_session)

# 4. Result subtitle with provider
target_res_sub = '<div class="result-subtitle">${session.name}</div>'
repl_res_sub = '<div class="result-subtitle">${session.name}${session.provider ? ` • ${session.provider}` : \'\'}</div>'
assert target_res_sub in content, 'target_res_sub not found'
content = content.replace(target_res_sub, repl_res_sub)

# 5. Question telemetry dynamic counts in app.js
content = content.replace('8,168 verified GATE CS questions with detailed mathematical derivations', '${state.questions.length.toLocaleString()} verified GATE CS questions with detailed mathematical derivations')
content = content.replace('Browse All 8,168 Questions →', 'Browse All ${state.questions.length.toLocaleString()} Questions →')
content = content.replace('database of 8,168 authentic questions', 'database of ${state.questions.length.toLocaleString()} authentic questions')
content = content.replace('Search 8,168 questions by theorem', 'Search ${state.questions.length.toLocaleString()} questions by theorem')
content = content.replace('UNIVERSAL GLOBAL QUESTION SEARCH (8,168 QUESTIONS)', 'UNIVERSAL GLOBAL QUESTION SEARCH (21,502 QUESTIONS)')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('app.js successfully updated!')

# 6. index.html updates for 21,502 Qs
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('Global Search 8,168 Questions (/)', 'Global Search 21,502 Questions (/)')
html = html.replace('Global Search (8,168 Questions)', 'Global Search (21,502 Questions)')
html = html.replace('SEARCH MODAL (8,168 Qs)', 'SEARCH MODAL (21,502 Qs)')
html = html.replace('Search 8,168 questions by topic', 'Search 21,502 questions by topic')
html = html.replace('8,168 questions indexed', '21,502 questions indexed')
html = html.replace('Search 8,168 questions by theorem', 'Search 21,502 questions by theorem')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('index.html successfully updated!')

# 7. README.md cache version consistency
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

readme = readme.replace('gate-cse-v6.9', 'gate-cse-v7.6')
readme = readme.replace('gate-cse-v7.1', 'gate-cse-v7.6')
readme = readme.replace('gate-cse-v5', 'gate-cse-v7.6')

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme)

print('README.md successfully updated!')
