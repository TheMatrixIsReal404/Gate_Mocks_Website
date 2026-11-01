# -*- coding: utf-8 -*-
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

funcs = [
  'navigate',
  'switchMockTab',
  'setMockSort',
  'setMockLevelFilter',
  'showMockRatingMatrix',
  'closeMockModal',
  'toggleCalibrationTable',
  'viewMockPaper',
  'closeMockPaperView',
  'startMockTest',
  'startMockPaperPractice',
  'setPyqExamEraFilter',
  'setPyqExamDiffFilter',
  'setPyqExamSort',
  'startPYQPractice',
  'updatePYQFilter',
  'updatePYQSearch',
  'startPracticeMode',
  'closePracticeMode',
  'updateFilter',
  'updatePracticeSearch',
  'jumpToPracticeQ',
  'nextPracticeQuestion',
  'prevPracticeQuestion',
  'submitPracticeAnswer',
  'openSingleQuestion',
  'skipQuestion',
  'toggleBookmark',
  'toggleGateCalc',
  'toggleShortcutsModal',
  'jumpToTestQ',
  'saveAndNextTestQ',
  'markForReview',
  'clearTestResponse',
  'confirmSubmitTest',
  'closeResult',
  'saveNATAnswer',
  'toggleTestPalette',
  'switchUploadTab',
  'handleFileUpload',
  'downloadSampleJSON',
  'handleDeleteQ',
  'clearAllQuestions',
  'clearManualForm',
  'submitManualQuestion',
  'onCategoryChange',
  'onTypeChange',
  'addOptRow',
  'ingestEasyMocks',
  'pushAllQuestionsToCloud'
]

missing = []
for fn in funcs:
    if f'function {fn}' not in text and f'const {fn}' not in text and f'let {fn}' not in text and f'window.{fn}' not in text:
        missing.append(fn)

print("Missing functions:", missing)
print(f"Verified {len(funcs) - len(missing)} / {len(funcs)} functions!")
