# -*- coding: utf-8 -*-
with open('scripts/test_all_new_features.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'document.querySelectorAll(".practice-q-card, .question-card, .card").length',
    'document.querySelectorAll("#practice-questions-grid .pyq-item").length'
)

with open('scripts/test_all_new_features.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated test query to .pyq-item!')
