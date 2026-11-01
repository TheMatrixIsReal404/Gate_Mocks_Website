import asyncio
import json
import subprocess
import urllib.request
import aiohttp
import sys

cmd_id = 0

async def cdp_call(ws, method, params=None):
    global cmd_id
    cmd_id += 1
    my_id = cmd_id
    msg = {"id": my_id, "method": method}
    if params:
        msg["params"] = params
    await ws.send_json(msg)
    while True:
        resp = await ws.receive_json()
        if resp.get("id") == my_id:
            return resp.get("result", {})

async def main():
    server_proc = subprocess.Popen([
        sys.executable,
        '-m', 'http.server', '8122'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9252',
        'http://localhost:8122/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    results = {}

    try:
        with urllib.request.urlopen('http://127.0.0.1:9252/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8122' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                # 1. Login as guest and wait for master questions (8,168)
                for _ in range(30):
                    r_ready = await cdp_call(ws, "Runtime.evaluate", {
                        "expression": "typeof window.continueAsGuest === 'function'",
                        "returnByValue": True
                    })
                    if r_ready.get('result', {}).get('value') is True:
                        break
                    await asyncio.sleep(0.3)

                await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.continueAsGuest()",
                    "awaitPromise": True
                })
                print("1. Guest login initialized...")

                total_qs = 0
                for _ in range(40):
                    await asyncio.sleep(0.3)
                    st = await cdp_call(ws, "Runtime.evaluate", {
                        "expression": "JSON.stringify({ len: window.state?.questions?.length || 0, page: window.state?.currentPage })",
                        "returnByValue": True
                    })
                    st_val = json.loads(st.get('result', {}).get('value', '{}'))
                    if st_val.get('len', 0) > 5000 and st_val.get('page') == 'dashboard':
                        total_qs = st_val.get('len')
                        break

                print(f"   Loaded {total_qs} questions in state!")
                results['total_questions'] = total_qs

                # ─────────────────────────────────────────────────────────────
                # PART A: VERIFY PREVIOUS 24 FEATURES
                # ─────────────────────────────────────────────────────────────
                # 2. Mock Difficulty Sort: Easy-first & Hard-first
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('mocks'); window.switchMockTab('all');"})
                await asyncio.sleep(0.5)

                r_easy = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setMockSort('easy-first');
                        const badges = Array.from(document.querySelectorAll('.mock-card .q-badge:first-of-type')).slice(0, 5).map(b => b.textContent.trim().toUpperCase());
                        return JSON.stringify(badges);
                    })()""",
                    "returnByValue": True
                })
                easy_badges = json.loads(r_easy.get('result', {}).get('value', '[]'))
                results['1_mock_sort_easy_first'] = len(easy_badges) == 5 and all('EASY' in b for b in easy_badges)

                r_hard = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setMockSort('hard-first');
                        const badges = Array.from(document.querySelectorAll('.mock-card .q-badge:first-of-type')).slice(0, 5).map(b => b.textContent.trim().toUpperCase());
                        return JSON.stringify(badges);
                    })()""",
                    "returnByValue": True
                })
                hard_badges = json.loads(r_hard.get('result', {}).get('value', '[]'))
                results['2_mock_sort_hard_first'] = len(hard_badges) == 5 and all('HARD' in b for b in hard_badges)

                # 3. PYQ Exams: Recent sort (year-desc), Oldest sort (year-asc), Era Filter (recent)
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('pyq-exams');"})
                await asyncio.sleep(0.5)

                r_recent_exams = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const titles = Array.from(document.querySelectorAll('.mock-card .mock-title')).slice(0, 3).map(t => t.textContent.trim());
                        return JSON.stringify(titles);
                    })()""",
                    "returnByValue": True
                })
                recent_titles = json.loads(r_recent_exams.get('result', {}).get('value', '[]'))
                results['3_pyq_recent_sort'] = any('2025' in t or '2026' in t for t in recent_titles)

                r_oldest_exams = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setPyqExamSort('year-asc');
                        const titles = Array.from(document.querySelectorAll('.mock-card .mock-title')).slice(0, 3).map(t => t.textContent.trim());
                        return JSON.stringify(titles);
                    })()""",
                    "returnByValue": True
                })
                oldest_titles = json.loads(r_oldest_exams.get('result', {}).get('value', '[]'))
                results['4_pyq_oldest_sort'] = any('2011' in t or '2012' in t or '2013' in t for t in oldest_titles)

                r_era_recent = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setPyqExamEraFilter('recent');
                        return document.querySelectorAll('.mock-card').length;
                    })()""",
                    "returnByValue": True
                })
                results['5_pyq_era_recent'] = r_era_recent.get('result', {}).get('value', 0) >= 6
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.setPyqExamEraFilter('all'); window.setPyqExamSort('year-desc');"})

                # 4. Pagination (Practice P1, P2, PageSize 50, Mock Paper 20/page)
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('practice');"})
                await asyncio.sleep(0.5)

                r_pag1 = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const info = document.querySelector('.pagination-info')?.textContent?.trim();
                        const items = document.querySelectorAll('.pyq-item').length;
                        return JSON.stringify({ info, items });
                    })()""",
                    "returnByValue": True
                })
                pag1 = json.loads(r_pag1.get('result', {}).get('value', '{}'))
                results['6_practice_pagination_p1'] = ('1–20' in pag1.get('info', '') or '1-20' in pag1.get('info', '')) and pag1.get('items') == 20

                r_pag2 = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setPracticePage(2);
                        const info = document.querySelector('.pagination-info')?.textContent?.trim();
                        const items = document.querySelectorAll('.pyq-item').length;
                        return JSON.stringify({ info, items });
                    })()""",
                    "returnByValue": True
                })
                pag2 = json.loads(r_pag2.get('result', {}).get('value', '{}'))
                results['7_practice_pagination_p2'] = ('21–40' in pag2.get('info', '') or '21-40' in pag2.get('info', '')) and pag2.get('items') == 20

                r_pag_sz = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setPracticePageSize(50);
                        const info = document.querySelector('.pagination-info')?.textContent?.trim();
                        const items = document.querySelectorAll('.pyq-item').length;
                        return JSON.stringify({ info, items });
                    })()""",
                    "returnByValue": True
                })
                pag_sz = json.loads(r_pag_sz.get('result', {}).get('value', '{}'))
                results['8_practice_page_size_50'] = ('1–50' in pag_sz.get('info', '') or '1-50' in pag_sz.get('info', '')) and pag_sz.get('items') == 50

                r_mp = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.viewMockPaper('mock-med-01', 1);
                        const info = document.querySelector('.pagination-info')?.textContent?.trim();
                        const items = document.querySelectorAll('#mock-questions-grid .pyq-item').length;
                        return JSON.stringify({ info, items });
                    })()""",
                    "returnByValue": True
                })
                mp_data = json.loads(r_mp.get('result', {}).get('value', '{}'))
                results['9_mock_paper_pagination'] = ('1–20' in mp_data.get('info', '') or '1-20' in mp_data.get('info', '')) and mp_data.get('items') == 20
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.closeMockPaperView();"})

                # 10. Mistake Vault
                await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const q1 = window.state.questions[0];
                        window.state.attempts.push({ questionId: q1.id, correct: false, date: Date.now() - 5000, uid: 'guest' });
                    })()"""
                })
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('mistakes');"})
                await asyncio.sleep(0.5)

                r_mv = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const heroTitle = document.querySelector('.mistake-hero-text h2')?.textContent?.trim();
                        const unresolvedCount = document.querySelectorAll('.mistake-card').length;
                        return JSON.stringify({ heroTitle, unresolvedCount });
                    })()""",
                    "returnByValue": True
                })
                mv_data = json.loads(r_mv.get('result', {}).get('value', '{}'))
                results['10_mistake_vault'] = 'Mistake Vault' in mv_data.get('heroTitle', '') and mv_data.get('unresolvedCount', 0) >= 1

                # 11. GATE Score Predictor
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('performance');"})
                await asyncio.sleep(0.5)
                r_pred = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.updatePredictorMarks(80);
                        return JSON.stringify({
                            score: document.querySelector('.predictor-score-huge')?.textContent?.trim(),
                            air: document.querySelector('.predictor-air-huge')?.textContent?.trim()
                        });
                    })()""",
                    "returnByValue": True
                })
                pred_data = json.loads(r_pred.get('result', {}).get('value', '{}'))
                results['11_gate_score_predictor'] = '917' in pred_data.get('score', '') and 'AIR 1 – 100' in pred_data.get('air', '')

                # 12. Draggable TCS iON Calculator
                r_calc = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.toggleGateCalc(true);
                        const isOpen = document.getElementById('gate-calc-modal')?.classList.contains('active');
                        const isDragInit = !!document.getElementById('gate-calc-modal')?._dragInitialized;
                        window.toggleGateCalc(false);
                        return JSON.stringify({ isOpen, isDragInit });
                    })()""",
                    "returnByValue": True
                })
                calc_data = json.loads(r_calc.get('result', {}).get('value', '{}'))
                results['12_draggable_calc'] = calc_data.get('isOpen') and calc_data.get('isDragInit')

                # 13. Fullscreen Exam Mode button in Exam Header
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.startMockTest('mock-med-01'); window.jumpToTestQ(17);"})
                await asyncio.sleep(0.5)
                r_exam_header = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "!!document.getElementById('exam-fullscreen-btn')",
                    "returnByValue": True
                })
                results['13_fullscreen_exam_mode'] = bool(r_exam_header.get('result', {}).get('value'))

                # 14. Code Syntax & Copy
                r_code = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        return JSON.stringify({
                            hasCode: !!document.querySelector('.code-block-container'),
                            hasCopy: !!document.querySelector('.code-copy-btn')
                        });
                    })()""",
                    "returnByValue": True
                })
                code_data = json.loads(r_code.get('result', {}).get('value', '{}'))
                results['14_code_syntax_and_copy'] = code_data.get('hasCode') and code_data.get('hasCopy')

                # 15. Pacing Analytics & PDF Report
                r_review = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(async () => {
                        await window.submitMockTest();
                        const hasPacing = !!document.querySelector('.pacing-analytics-grid');
                        const hasBadges = document.querySelectorAll('.time-spent-badge').length > 0;
                        const hasPrint = !!document.querySelector('button[onclick*="printTestReport"]');
                        window.closeResult();
                        return JSON.stringify({ hasPacing, hasBadges, hasPrint });
                    })()""",
                    "awaitPromise": True,
                    "returnByValue": True
                })
                review_val = r_review.get('result', {}).get('value')
                review_data = json.loads(review_val) if isinstance(review_val, str) else (review_val or {})
                results['15_pacing_analytics_and_pdf'] = review_data.get('hasPacing') and review_data.get('hasBadges') and review_data.get('hasPrint')

                # 16. Feature 1: Exam Crash Protection & Auto-Save
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.startMockTest('mock-med-02');"})
                await asyncio.sleep(0.5)
                r_autosave = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(async () => {
                        const raw = localStorage.getItem('gate_active_test_autosave_v1');
                        await window.submitMockTest();
                        window.closeResult();
                        return !!raw && raw.includes('mock-med-02');
                    })()""",
                    "awaitPromise": True,
                    "returnByValue": True
                })
                auto_val = r_autosave.get('result', {}).get('value')
                results['16_exam_crash_protection_autosave'] = bool(auto_val)

                # 17. Feature 2: Authentic 5-State TCS iON Question Palette & Legend
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.startMockTest('mock-med-03');"})
                await asyncio.sleep(0.5)
                r_tcs_palette = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(async () => {
                        const q0Init = document.getElementById('pb-0')?.className;
                        document.querySelector('.option-item')?.click();
                        window.saveAndNextTestQ();
                        const q0Answered = document.getElementById('pb-0')?.className;
                        window.markForReview();
                        const q1Marked = document.getElementById('pb-1')?.className;
                        const has5Legends = !!document.getElementById('palette-legend-container') && !!document.getElementById('cnt-ans');
                        await window.submitMockTest();
                        window.closeResult();
                        return JSON.stringify({ q0Answered, q1Marked, has5Legends });
                    })()""",
                    "awaitPromise": True,
                    "returnByValue": True
                })
                tcs_raw = r_tcs_palette.get('result', {}).get('value')
                tcs_data = json.loads(tcs_raw) if isinstance(tcs_raw, str) else (tcs_raw or {})
                results['17_tcs_5_state_palette'] = 'answered' in tcs_data.get('q0Answered', '') and 'marked' in tcs_data.get('q1Marked', '') and bool(tcs_data.get('has5Legends'))

                # 18. Feature 3: GATE Syllabus Mastery Matrix & Weightage Heatmap
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('performance');"})
                await asyncio.sleep(0.5)
                r_mastery = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const hasCard = !!document.querySelector('.mastery-matrix-card');
                        const pillars = document.querySelectorAll('.mastery-pillar-box').length;
                        const text = document.querySelector('.mastery-matrix-card')?.textContent || '';
                        return JSON.stringify({ hasCard, pillars, hasGA: text.includes('General Aptitude'), hasCS: text.includes('Core Computer Science') });
                    })()""",
                    "returnByValue": True
                })
                mastery_data = json.loads(r_mastery.get('result', {}).get('value', '{}'))
                results['18_gate_syllabus_mastery_matrix'] = mastery_data.get('hasCard') and mastery_data.get('pillars') == 3 and mastery_data.get('hasGA') and mastery_data.get('hasCS')

                # 19. Feature 4: Custom Mock Exam & Practice Drill Generator
                r_drill = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.toggleCustomDrillModal(true);
                        const isOpen = document.getElementById('custom-drill-modal')?.style.display !== 'none';
                        const subjectCount = document.querySelectorAll('.drill-subject-item').length;
                        window.toggleCustomDrillModal(false);
                        const isClosed = document.getElementById('custom-drill-modal')?.style.display === 'none';
                        return JSON.stringify({ isOpen, subjectCount, isClosed });
                    })()""",
                    "returnByValue": True
                })
                drill_data = json.loads(r_drill.get('result', {}).get('value', '{}'))
                results['19_custom_drill_generator'] = drill_data.get('isOpen') and drill_data.get('subjectCount') >= 10 and drill_data.get('isClosed')

                # 20. Feature 5: 1-Click User Data Portability (Export & Restore Progress)
                r_portability = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const hasCard = !!document.querySelector('.data-portability-card');
                        const hasExport = typeof window.exportUserData === 'function';
                        const hasRestore = typeof window.triggerRestoreFilePrompt === 'function';
                        return JSON.stringify({ hasCard, hasExport, hasRestore });
                    })()""",
                    "returnByValue": True
                })
                port_data = json.loads(r_portability.get('result', {}).get('value', '{}'))
                results['20_user_data_portability'] = port_data.get('hasCard') and port_data.get('hasExport') and port_data.get('hasRestore')

                # 21. Feature 6: Personal Question Revision Notes (Scratchpad)
                r_notes = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.saveQuestionNote('mock-med-01-q18', 'Key Formula: Bellman Ford detects negative cycles');
                        const raw = localStorage.getItem('gate_question_notes');
                        return !!raw && raw.includes('Bellman Ford');
                    })()""",
                    "returnByValue": True
                })
                results['21_personal_question_notes'] = bool(r_notes.get('result', {}).get('value'))

                # 22. Feature 7: Exam Pacing Countdown Web Audio Chimes
                r_chimes = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const initial = localStorage.getItem('gate_exam_chimes');
                        window.toggleExamChimes();
                        const toggled = localStorage.getItem('gate_exam_chimes');
                        window.toggleExamChimes();
                        return typeof window.toggleExamChimes === 'function' && initial !== toggled;
                    })()""",
                    "returnByValue": True
                })
                results['22_pacing_countdown_chimes'] = bool(r_chimes.get('result', {}).get('value'))

                # 23. Feature 8: Formula Flashcards (Spaced Repetition) & Practice Hints
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('practice');"})
                await asyncio.sleep(0.5)
                r_flashcards = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const firstQ = state.questions[0];
                        window.openSingleQuestion(firstQ.id);
                        window.togglePracticeHint(true);
                        const hintBox = document.getElementById('practice-hint-box');
                        const hintVisible = hintBox && hintBox.style.display !== 'none';
                        window.openFormulaFlashcardsModal('card-masters-theorem');
                        const modal = document.getElementById('flashcard-modal-backdrop');
                        const modalActive = modal && modal.classList.contains('active');
                        window.flipActiveFlashcard();
                        const inner = document.getElementById('active-flashcard-inner');
                        const isFlipped = inner && inner.classList.contains('is-flipped');
                        window.rateFlashcard('mastered');
                        const stats = state.flashcardStats['card-masters-theorem'];
                        window.toggleFormulaFlashcards(false);
                        window.closePracticeMode();
                        const hasCards = FORMULA_FLASHCARDS.length >= 9;
                        return JSON.stringify({
                            hintVisible,
                            modalActive,
                            isFlipped,
                            isMastered: stats?.status === 'mastered',
                            hasCards
                        });
                    })()""",
                    "returnByValue": True
                })
                fc_data = json.loads(r_flashcards.get('result', {}).get('value', '{}'))
                results['23_formula_flashcards_srs'] = (
                    fc_data.get('hintVisible') and
                    fc_data.get('modalActive') and
                    fc_data.get('isFlipped') and
                    fc_data.get('isMastered') and
                    fc_data.get('hasCards')
                )

                # 24. Topic-Wise PYQ Hub
                r_topic_pyqs = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.navigate('pyqs');
                        const heroTitle = document.querySelector('.topic-pyq-title-wrap h2')?.textContent?.trim();
                        const statCards = Array.from(document.querySelectorAll('.topic-pyq-stat-card .stat-num')).map(el => el.textContent.trim());
                        const pills = Array.from(document.querySelectorAll('.topic-subject-pill')).map(p => p.textContent.trim());
                        const topicCardsCount = document.querySelectorAll('.topic-card').length;
                        window.setTopicPyqSubject('Operating Systems');
                        const osTopics = document.querySelectorAll('.topic-card').length;
                        window.setTopicPyqTab('list');
                        const isListTab = document.querySelectorAll('.pyq-item').length > 0;
                        window.setTopicPyqTab('chapters');
                        window.setTopicPyqSubject('all');
                        return JSON.stringify({
                            hasHero: heroTitle && heroTitle.includes('Topic-Wise'),
                            hasStatCards: statCards.length === 4,
                            hasPills: pills.length >= 14,
                            topicCardsCount: topicCardsCount >= 80,
                            hasOsTopics: osTopics >= 8,
                            isListTab
                        });
                    })()""",
                    "returnByValue": True
                })
                top_data = json.loads(r_topic_pyqs.get('result', {}).get('value', '{}'))
                results['24_topic_wise_pyqs_hub'] = bool(
                    top_data.get('hasHero') and
                    top_data.get('hasStatCards') and
                    top_data.get('hasPills') and
                    top_data.get('topicCardsCount') and
                    top_data.get('hasOsTopics') and
                    top_data.get('isListTab')
                )

                # ─────────────────────────────────────────────────────────────
                # PART B: VERIFY 5 NEW ELITE GATE INTELLIGENCE MODULES
                # ─────────────────────────────────────────────────────────────
                # 25. Loss Diagnosis & Error Tagging
                r_loss = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const q1 = window.state.questions[0];
                        window.setErrorTag(q1.id, 'silly');
                        const isSilly = window.state.errorTags[q1.id] === 'silly';
                        const diag = window.getLossDiagnosis(
                            { score: 50, maxScore: 100 },
                            [q1],
                            [999] // wrong answer
                        );
                        const hasUnforced = diag.sillyLost > 0 && diag.potentialScore > 50;
                        const html = window.buildLossDiagnosisHTML({ score: 50, maxScore: 100 }, [q1], [999]);
                        return JSON.stringify({ isSilly, hasUnforced, hasHtml: html.includes('Post-Exam Loss Diagnosis') });
                    })()""",
                    "returnByValue": True
                })
                loss_data = json.loads(r_loss.get('result', {}).get('value', '{}'))
                results['25_loss_diagnosis_and_error_tagging'] = bool(
                    loss_data.get('isSilly') and
                    loss_data.get('hasUnforced') and
                    loss_data.get('hasHtml')
                )

                # 26. GATE PYQ Weightage Heatmap & Topic Trend Engine
                r_heatmap = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setTopicPyqTab('heatmap');
                        const h2 = document.querySelector('.heatmap-hero-text h2')?.textContent?.trim();
                        const subBars = document.querySelectorAll('.heatmap-sub-bar-card').length;
                        const topChapters = document.querySelectorAll('.calibration-table tbody tr').length;
                        window.setTopicPyqTab('chapters');
                        return JSON.stringify({
                            hasTitle: h2 && h2.includes('Weightage Heatmap'),
                            subBarsCount: subBars >= 10,
                            topChaptersCount: topChapters >= 20
                        });
                    })()""",
                    "returnByValue": True
                })
                heat_data = json.loads(r_heatmap.get('result', {}).get('value', '{}'))
                results['26_pyq_weightage_heatmap_trend_engine'] = bool(
                    heat_data.get('hasTitle') and
                    heat_data.get('subBarsCount') and
                    heat_data.get('topChaptersCount')
                )

                # 27. Speed vs Accuracy 4-Quadrant Matrix (Time-Sink Detector)
                r_quad = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const html = window.buildQuadrantAnalysisHTML();
                        return JSON.stringify({
                            hasTitle: html.includes('Speed vs Accuracy Matrix'),
                            hasSweetSpot: html.includes('Sweet Spot'),
                            hasBlackHole: html.includes('The Black Hole')
                        });
                    })()""",
                    "returnByValue": True
                })
                quad_data = json.loads(r_quad.get('result', {}).get('value', '{}'))
                results['27_speed_accuracy_quadrant_matrix'] = bool(
                    quad_data.get('hasTitle') and
                    quad_data.get('hasSweetSpot') and
                    quad_data.get('hasBlackHole')
                )

                # 28. Smart Playlists & Revision Buckets
                r_pls = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.navigate('playlists');
                        const cardsCount = document.querySelectorAll('.playlist-card').length;
                        const q1 = window.state.questions[0];
                        window.openPlaylistModal(q1.id);
                        const isModalActive = document.getElementById('playlist-modal')?.classList.contains('active');
                        window.toggleQuestionInPlaylist('smart-nats', q1.id, true);
                        const isAdded = window.state.playlists['smart-nats']?.qIds?.includes(q1.id);
                        window.closePlaylistModal();
                        return JSON.stringify({
                            cardsCount: cardsCount >= 3,
                            isModalActive,
                            isAdded
                        });
                    })()""",
                    "returnByValue": True
                })
                pls_data = json.loads(r_pls.get('result', {}).get('value', '{}'))
                results['28_smart_playlists_revision_buckets'] = bool(
                    pls_data.get('cardsCount') and
                    pls_data.get('isModalActive') and
                    pls_data.get('isAdded')
                )

                # 29. Multi-Method Explanations & Student Shortcut Notes
                r_multi = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const q1 = window.state.questions[0];
                        const multiHtml = window.buildMultiMethodExplanationHTML(q1);
                        const noteHtml = window.buildStudentShortcutNoteHTML(q1.id);
                        window.saveStudentQuestionNote(q1.id, 'Shortcut note with math $O(1)$');
                        const isSaved = window.state.questionNotes[q1.id] === 'Shortcut note with math $O(1)$';
                        return JSON.stringify({
                            hasMethod1: multiHtml.includes('Method 1'),
                            hasMethod2: multiHtml.includes('Method 2'),
                            hasNoteHtml: noteHtml.includes('My Shortcut / Personal Derivation Note'),
                            isSaved
                        });
                    })()""",
                    "returnByValue": True
                })
                multi_data = json.loads(r_multi.get('result', {}).get('value', '{}'))
                results['29_multi_method_and_shortcut_notes'] = bool(
                    multi_data.get('hasMethod1') and
                    multi_data.get('hasMethod2') and
                    multi_data.get('hasNoteHtml') and
                    multi_data.get('isSaved')
                )

                # 30. Official Syllabus Guide (IIT Madras Standards)
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('subjects')"})
                await asyncio.sleep(0.5)

                r_syl = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const card = document.querySelector('.syllabus-guide-card');
                        const secCards = document.querySelectorAll('.syllabus-sec-card');
                        window.toggleSyllabusGuide();
                        const isHidden = document.getElementById('syllabus-guide-body')?.style.display === 'none';
                        window.toggleSyllabusGuide();
                        return JSON.stringify({
                            hasCard: !!card,
                            secCardCount: secCards.length,
                            isHidden
                        });
                    })()""",
                    "returnByValue": True
                })
                syl_data = json.loads(r_syl.get('result', {}).get('value', '{}'))
                results['30_official_syllabus_guide_iit_madras'] = bool(
                    syl_data.get('hasCard') and
                    syl_data.get('secCardCount') == 11 and
                    syl_data.get('isHidden')
                )

                # 31. Universal Global Search across 8,168 Questions
                r_search = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.openGlobalSearch();
                        const modal = document.getElementById('global-search-modal');
                        const isModalActive = modal && modal.classList.contains('active');
                        window.executeGlobalSearch('Dijkstra');
                        const resultsItems = document.querySelectorAll('.search-result-item');
                        window.closeGlobalSearch();
                        return JSON.stringify({
                            isModalActive,
                            resultsCount: resultsItems.length
                        });
                    })()""",
                    "returnByValue": True
                })
                s_data = json.loads(r_search.get('result', {}).get('value', '{}'))
                results['31_universal_global_search_8168_qs'] = bool(
                    s_data.get('isModalActive') and
                    s_data.get('resultsCount') > 0
                )

                # 32. Exam Countdown & Daily Study Streak Engine
                r_streak = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const cd = window.getExamCountdownData();
                        const cdText = document.getElementById('countdown-text')?.textContent || '';
                        window.recordDailyAttemptForStreak();
                        const streakText = document.getElementById('streak-text')?.textContent || '';
                        return JSON.stringify({
                            hasDays: cd && cd.days > 0,
                            cdTextMatches: cdText.includes('GATE'),
                            streakTextHasQ: streakText.includes('Q')
                        });
                    })()""",
                    "returnByValue": True
                })
                st_data = json.loads(r_streak.get('result', {}).get('value', '{}'))
                results['32_exam_countdown_and_daily_streak'] = bool(
                    st_data.get('hasDays') and
                    st_data.get('cdTextMatches') and
                    st_data.get('streakTextHasQ')
                )

                # 33. 10-Spoke Subject Mastery Radar Chart
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('performance')"})
                await asyncio.sleep(0.5)

                r_radar = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const card = document.querySelector('.radar-chart-card');
                        const poly = document.querySelector('.radar-polygon');
                        const pts = document.querySelectorAll('.radar-point');
                        const spokes = document.querySelectorAll('.radar-spoke');
                        return JSON.stringify({
                            hasCard: !!card,
                            hasPoly: !!poly,
                            pointsCount: pts.length,
                            spokesCount: spokes.length
                        });
                    })()""",
                    "returnByValue": True
                })
                rd_data = json.loads(r_radar.get('result', {}).get('value', '{}'))
                results['33_mastery_radar_chart_10_spokes'] = bool(
                    rd_data.get('hasCard') and
                    rd_data.get('hasPoly') and
                    rd_data.get('pointsCount') == 10 and
                    rd_data.get('spokesCount') == 10
                )

                # 34. Expected Value (E) Risk Analyzer & Confidence Selectors
                r_ev = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const mcq = window.state.questions.find(q => q.type === 'mcq' && q.marks === 1);
                        const evAnalysis = window.getExpectedValueAnalysis(mcq);
                        const evHtml = window.buildExpectedValueCardHTML(mcq);
                        window.setQuestionConfidence(mcq.id, 'high');
                        const isConfidenceSaved = window.state.confidenceTags[mcq.id] === 'high';
                        return JSON.stringify({
                            ev0: evAnalysis.ev0,
                            ev2: evAnalysis.ev2,
                            hasEvHtml: evHtml.includes('Expected Value'),
                            isConfidenceSaved
                        });
                    })()""",
                    "returnByValue": True
                })
                ev_data = json.loads(r_ev.get('result', {}).get('value', '{}'))
                results['34_ev_risk_analyzer_and_confidence'] = bool(
                    ev_data.get('ev0') == 0.0 and
                    ev_data.get('ev2') == 0.33 and
                    ev_data.get('hasEvHtml') and
                    ev_data.get('isConfidenceSaved')
                )

                # 35. 60-Second Formula Blitz Mode
                r_blitz = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.startFormulaBlitz();
                        const timeEl = document.getElementById('blitz-time-text');
                        window.advanceBlitzCard(true);
                        const score = parseInt(document.querySelector('.blitz-view-container')?.textContent.match(/Score:\\s*(\\d+)/)?.[1] || '0');
                        window.stopFormulaBlitz();
                        return JSON.stringify({
                            hasTime: !!timeEl,
                            scoreIncreased: score >= 10
                        });
                    })()""",
                    "returnByValue": True
                })
                blitz_data = json.loads(r_blitz.get('result', {}).get('value', '{}'))
                results['35_60s_formula_blitz_mode'] = bool(
                    blitz_data.get('hasTime') and
                    blitz_data.get('scoreIncreased')
                )

                # 36. NAT Precision & Rounding Trap Inspector
                r_nat = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const natQ = window.state.questions.find(q => q.type === 'nat');
                        const natHtml = window.buildNatToleranceHTML(natQ);
                        return JSON.stringify({
                            hasBounds: natHtml.includes('Numerical Acceptance Bounds'),
                            hasTrapAdvisory: natHtml.includes('Rounding Trap Advisory')
                        });
                    })()""",
                    "returnByValue": True
                })
                nat_data = json.loads(r_nat.get('result', {}).get('value', '{}'))
                results['36_nat_precision_rounding_inspector'] = bool(
                    nat_data.get('hasBounds') and
                    nat_data.get('hasTrapAdvisory')
                )

                # 37. 2-Column Printable Practice Worksheet Generator
                r_ws = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.generatePrintableWorksheet(window.state.questions.slice(0, 4), 'Audit Verification Worksheet');
                        const container = document.getElementById('printable-worksheet-container');
                        const qItems = container.querySelectorAll('.ws-q-item');
                        const keyRows = container.querySelectorAll('.ws-key-table tbody tr');
                        return JSON.stringify({
                            qCount: qItems.length,
                            keyCount: keyRows.length
                        });
                    })()""",
                    "returnByValue": True
                })
                ws_data = json.loads(r_ws.get('result', {}).get('value', '{}'))
                results['37_printable_2_column_pdf_worksheet'] = bool(
                    ws_data.get('qCount') == 4 and
                    ws_data.get('keyCount') == 4
                )

    except Exception as e:
        print("CDP Verification Error:", e)
        results['error'] = str(e)
    finally:
        edge_proc.terminate()
        server_proc.terminate()

    print("\n" + "="*60)
    print("COMPLETE 37-FEATURE FULL-SITE VERIFICATION AUDIT MATRIX:")
    print("="*60)
    all_ok = True
    for k, v in results.items():
        print(f" {k:<42}: {v}")
        if v is not True and k != 'total_questions':
            all_ok = False
    print("="*60)
    if all_ok:
        print(">>> ALL 37 VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<")
    else:
        print(">>> SOME VERIFICATION CHECKS FAILED! <<<")

if __name__ == '__main__':
    asyncio.run(main())
