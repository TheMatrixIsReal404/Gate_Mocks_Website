# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any backslash-escaped double quotes inside renderMocks and buildMockSortBar
content = content.replace(r'\"tab-btn', '"tab-btn')
content = content.replace(r'\"button\"', '"button"')
content = content.replace(r'\"mock-subseries-pill', '"mock-subseries-pill')
content = content.replace(r"\'go\',this)\"", "'go',this)\"")
content = content.replace(r"\'made-easy\',this)\"", "'made-easy',this)\"")
content = content.replace(r"\'go-mocks\')\"", "'go-mocks')\"")
content = content.replace(r"\'me-mocks\')\"", "'me-mocks')\"")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned up backslashes in app.js")
