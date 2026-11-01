# -*- coding: utf-8 -*-
import subprocess
import time
import json
import urllib.request
import asyncio
import aiohttp
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

_req_id = 0

async def cdp_call(ws, method, params=None):
    global _req_id
    _req_id += 1
    my_id = _req_id
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
        '-m', 'http.server', '8120'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9250',
        'http://localhost:8120/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    results = {}

    try:
        with urllib.request.urlopen('http://127.0.0.1:9250/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8120' in t.get('url', '')][0]
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
                # PART A: VERIFY ALL PREVIOUS 15 FEATURES (FROM SCREENSHOT)
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

                # 5. Mistake Vault
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('mistakes');"})
                await asyncio.sleep(0.5)
                r_mv = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        return JSON.stringify({
                            hasHero: !!document.querySelector('.mistake-hero'),
                            pills: document.querySelectorAll('.mistake-stat-pill').length,
                            hasRetestBtn: !!document.querySelector('.mistake-controls-bar button.btn-primary')
                        });
                    })()""",
                    "returnByValue": True
                })
                mv_data = json.loads(r_mv.get('result', {}).get('value', '{}'))
                results['10_mistake_vault'] = mv_data.get('hasHero') and mv_data.get('pills') == 4 and mv_data.get('hasRetestBtn')

                # 6. GATE Score & AIR Predictor (80 Marks)
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

                # 7. Draggable TCS iON Calculator
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

                # 8. Fullscreen Exam Mode button in Exam Header
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.startMockTest('mock-med-01'); window.jumpToTestQ(17);"})
                await asyncio.sleep(0.5)
                r_exam_header = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "!!document.getElementById('exam-fullscreen-btn')",
                    "returnByValue": True
                })
                results['13_fullscreen_exam_mode'] = bool(r_exam_header.get('result', {}).get('value'))

                # 9. Code Syntax & Copy
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

                # 10. Pacing Analytics & PDF Report
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

                # ─────────────────────────────────────────────────────────────
                # PART B: VERIFY THE 7 NEW HIGH-IMPACT UPGRADES
                # ─────────────────────────────────────────────────────────────
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
                        // Q0 is visited & not answered initially
                        const q0Init = document.getElementById('pb-0')?.className;
                        // Select an option for Q0
                        document.querySelector('.option-item')?.click();
                        window.saveAndNextTestQ(); // moves to Q1, Q0 is now answered
                        const q0Answered = document.getElementById('pb-0')?.className;
                        // Mark Q1 for review
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
                print("17. TCS 5-State Palette output:", tcs_data)
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
                        window.toggleExamChimes(); // restore
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

                # 24. Topic-Wise GATE CSE PYQs Hub
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

    except Exception as e:
        print("CDP Verification Error:", e)
        results['error'] = str(e)
    finally:
        edge_proc.terminate()
        server_proc.terminate()

    print("\n" + "="*60)
    print("COMPLETE 24-FEATURE FULL-SITE VERIFICATION AUDIT MATRIX:")
    print("="*60)
    all_ok = True
    for k, v in results.items():
        print(f" {k:<38}: {v}")
        if v is not True and k != 'total_questions':
            all_ok = False
    print("="*60)
    if all_ok:
        print(">>> ALL 24 VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<")
    else:
        print(">>> SOME VERIFICATION CHECKS FAILED! <<<")

if __name__ == '__main__':
    asyncio.run(main())
