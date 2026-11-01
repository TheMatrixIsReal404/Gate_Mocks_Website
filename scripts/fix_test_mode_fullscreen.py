# -*- coding: utf-8 -*-
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """      <div class="test-topbar-right">
        <button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()\""""

replacement = """      <div class="test-topbar-right">
        <button class="btn btn-secondary btn-sm" id="exam-fullscreen-btn" onclick="toggleExamFullscreen()" type="button" title="Toggle Fullscreen Exam Mode (F)">⛶ <span class="hide-xs">Fullscreen</span></button>
        <button class="btn btn-secondary btn-sm" onclick="toggleGateCalc()\""""

assert target in text, "target not found in app.js"
text = text.replace(target, replacement, 1)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully injected exam-fullscreen-btn into renderTestMode in app.js!")
