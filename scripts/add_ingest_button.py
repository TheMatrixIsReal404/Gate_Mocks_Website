# -*- coding: utf-8 -*-
import sys

with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add ingestEasyMocks function
target_func = 'window.pushAllQuestionsToCloud = async function() {'
replacement_func = '''window.ingestEasyMocks = async function() {
  showToast('Loading 30 Easy Mock Tests (1,950 questions)...', 'info', 2500);
  try {
    const res = await fetch('./data/gate_30_easy_mocks.json');
    if (!res.ok) throw new Error('File not found: ./data/gate_30_easy_mocks.json');
    const data = await res.json();
    await bulkImportQuestions(data);
  } catch(err) {
    showToast('Failed to load easy mocks: ' + err.message, 'error');
  }
};

window.pushAllQuestionsToCloud = async function() {'''

assert target_func in text, "Target pushAllQuestionsToCloud not found"
text = text.replace(target_func, replacement_func, 1)

# 2. Add button to buildJSONUploadUI
old_btns = """${USE_FB ? `<button class="btn btn-secondary" onclick="pushAllQuestionsToCloud()" style="background:rgba(20,184,166,0.15);color:var(--teal);border-color:var(--teal)">☁️ Push Questions to Cloud (${state.questions.length})</button>` : ''}"""
new_btns = """<button class="btn btn-secondary" onclick="ingestEasyMocks()" style="background:rgba(99,102,241,0.15);color:var(--primary);border-color:var(--primary)">⚡ Ingest 30 Easy Mocks (1,950 Q)</button>
            ${USE_FB ? `<button class="btn btn-secondary" onclick="pushAllQuestionsToCloud()" style="background:rgba(20,184,166,0.15);color:var(--teal);border-color:var(--teal)">☁️ Push Questions to Cloud (${state.questions.length})</button>` : ''}"""

assert old_btns in text, "Old buttons not found"
text = text.replace(old_btns, new_btns, 1)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("✅ Added window.ingestEasyMocks and ⚡ Ingest 30 Easy Mocks button!")
