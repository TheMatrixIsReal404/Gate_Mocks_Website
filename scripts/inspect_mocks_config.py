# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
easy = re.findall(r'mock-easy-\d+', text)
full = re.findall(r'mock-full-\d+', text)
practice = re.findall(r'paper-full-\d+', text)
pyq = re.findall(r'pyq-exam-[a-zA-Z0-9\-]+', text)

print("Unique easy mock IDs:", len(set(easy)))
print("Unique full mock IDs:", len(set(full)))
print("Unique practice set IDs:", len(set(practice)))
print("Unique pyq exam IDs:", len(set(pyq)))

# Check difficulty counts in MOCK_TESTS
idx1 = text.find('const MOCK_TESTS = [')
idx2 = text.find('];', idx1)
mock_tests_str = text[idx1:idx2]
print("\nIn MOCK_TESTS array:")
print("  easy:", mock_tests_str.count("difficulty: 'easy'") + mock_tests_str.count('difficulty: "easy"'))
print("  medium:", mock_tests_str.count("difficulty: 'medium'") + mock_tests_str.count('difficulty: "medium"'))
print("  hard:", mock_tests_str.count("difficulty: 'hard'") + mock_tests_str.count('difficulty: "hard"'))
print("  practice-set type:", mock_tests_str.count("type: 'practice-set'") + mock_tests_str.count('type: "practice-set"'))
print("  full type:", mock_tests_str.count("type: 'full'") + mock_tests_str.count('type: "full"'))
