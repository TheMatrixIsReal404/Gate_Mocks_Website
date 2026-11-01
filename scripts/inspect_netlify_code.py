# -*- coding: utf-8 -*-
import urllib.request

url = 'https://gate-cse-practice.netlify.app/app.js'
with urllib.request.urlopen(url) as resp:
    code = resp.read().decode('utf-8')

for term in ['function switchMockTab', 'function getMockTabHTML', 'function getFilteredAndSortedMocks', 'function setPyqExamEraFilter', 'function setMockSort']:
    idx = code.find(term)
    print(f"=== {term} at {idx} ===")
    if idx != -1:
        print(code[idx:idx+500])
