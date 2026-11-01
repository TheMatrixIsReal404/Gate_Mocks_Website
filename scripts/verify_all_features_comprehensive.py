# -*- coding: utf-8 -*-
import subprocess
import time
import json
import urllib.request
import asyncio
import aiohttp
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
        '-m', 'http.server', '8097'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9232',
        'http://localhost:8097/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    results = {}

    try:
        with urllib.request.urlopen('http://127.0.0.1:9232/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8097' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                # 1. Login as guest and wait for master questions (8,168)
                await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.continueAsGuest()",
                    "awaitPromise": True
                })
                print("1. Guest login initialized...")
                q_count = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "new Promise(resolve => { const check = () => { if (window.state?.questions?.length > 5000) resolve(window.state.questions.length); else setTimeout(check, 250); }; check(); })",
                    "awaitPromise": True,
                    "returnByValue": True
                })
                total_qs = q_count.get('result', {}).get('value')
                print(f"   Loaded {total_qs} questions in state!")
                results['total_questions'] = total_qs

                # ─────────────────────────────────────────────────────────────
                # 2. TEST DIFFICULTY SORT (MOCK TESTS)
                # ─────────────────────────────────────────────────────────────
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('mocks'); window.switchMockTab('all');"})
                await asyncio.sleep(0.5)

                # Easy-first sort
                r_easy = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setMockSort('easy-first');
                        const badges = Array.from(document.querySelectorAll('.mock-card .q-badge:first-of-type')).slice(0, 5).map(b => b.textContent.trim().toUpperCase());
                        return JSON.stringify(badges);
                    })()""",
                    "returnByValue": True
                })
                easy_badges = json.loads(r_easy.get('result', {}).get('value', '[]'))
                print("2a. Mock Sort [Easy First] top 5 badges:", easy_badges)
                results['mock_sort_easy_first'] = len(easy_badges) == 5 and all('EASY' in b for b in easy_badges)

                # Hard-first sort
                r_hard = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setMockSort('hard-first');
                        const badges = Array.from(document.querySelectorAll('.mock-card .q-badge:first-of-type')).slice(0, 5).map(b => b.textContent.trim().toUpperCase());
                        return JSON.stringify(badges);
                    })()""",
                    "returnByValue": True
                })
                hard_badges = json.loads(r_hard.get('result', {}).get('value', '[]'))
                print("2b. Mock Sort [Hard First] top 5 badges:", hard_badges)
                results['mock_sort_hard_first'] = len(hard_badges) == 5 and all('HARD' in b for b in hard_badges)

                # ─────────────────────────────────────────────────────────────
                # 3. TEST RECENT EXAM SORT & FILTERS (PYQ EXAMS)
                # ─────────────────────────────────────────────────────────────
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('pyq-exams');"})
                await asyncio.sleep(0.5)

                # Default Year-Desc (Recent exams first: 2025, 2024...)
                r_recent_exams = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const titles = Array.from(document.querySelectorAll('.mock-card .mock-title')).slice(0, 3).map(t => t.textContent.trim());
                        return JSON.stringify(titles);
                    })()""",
                    "returnByValue": True
                })
                recent_titles = json.loads(r_recent_exams.get('result', {}).get('value', '[]'))
                print("3a. PYQ Exams [Recent First - year-desc]:", recent_titles)
                results['pyq_recent_sort'] = any('2025' in t for t in recent_titles)

                # Oldest first (year-asc)
                r_oldest_exams = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setPyqExamSort('year-asc');
                        const titles = Array.from(document.querySelectorAll('.mock-card .mock-title')).slice(0, 3).map(t => t.textContent.trim());
                        return JSON.stringify(titles);
                    })()""",
                    "returnByValue": True
                })
                oldest_titles = json.loads(r_oldest_exams.get('result', {}).get('value', '[]'))
                print("3b. PYQ Exams [Oldest First - year-asc]:", oldest_titles)
                results['pyq_oldest_sort'] = any('2011' in t or '2012' in t or '2013' in t for t in oldest_titles)

                # Era Filter: 'recent' (2020-2025)
                r_era_recent = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setPyqExamEraFilter('recent');
                        return document.querySelectorAll('.mock-card').length;
                    })()""",
                    "returnByValue": True
                })
                era_recent_count = r_era_recent.get('result', {}).get('value')
                print(f"3c. PYQ Exams Era Filter [Recent 2020-2025]: {era_recent_count} exams")
                results['pyq_era_recent'] = era_recent_count >= 6

                # Reset PYQ filters
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.setPyqExamEraFilter('all'); window.setPyqExamSort('year-desc');"})

                # ─────────────────────────────────────────────────────────────
                # 4. TEST PAGINATION (PRACTICE QUESTIONS & MOCK PAPERS)
                # ─────────────────────────────────────────────────────────────
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
                print("4a. Practice Pagination Page 1:", pag1)
                results['practice_page_1'] = ('1–20' in pag1.get('info', '') or '1-20' in pag1.get('info', '')) and pag1.get('items') == 20

                # Switch to Page 2
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
                print("4b. Practice Pagination Page 2:", pag2)
                results['practice_page_2'] = ('21–40' in pag2.get('info', '') or '21-40' in pag2.get('info', '')) and pag2.get('items') == 20

                # Switch Page Size to 50
                r_pag_size = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.setPracticePageSize(50);
                        const info = document.querySelector('.pagination-info')?.textContent?.trim();
                        const items = document.querySelectorAll('.pyq-item').length;
                        return JSON.stringify({ info, items });
                    })()""",
                    "returnByValue": True
                })
                pag_sz = json.loads(r_pag_size.get('result', {}).get('value', '{}'))
                print("4c. Practice Pagination Page Size 50:", pag_sz)
                results['practice_page_size_50'] = ('1–50' in pag_sz.get('info', '') or '1-50' in pag_sz.get('info', '')) and pag_sz.get('items') == 50

                # Test Mock Paper Pagination (20/page on 65-question mock)
                r_mock_paper = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.viewMockPaper('mock-med-01', 1);
                        const info = document.querySelector('.pagination-info')?.textContent?.trim();
                        const items = document.querySelectorAll('#mock-questions-grid .pyq-item').length;
                        const totalPages = document.querySelectorAll('.pagination-btn').length;
                        return JSON.stringify({ info, items, totalPages });
                    })()""",
                    "returnByValue": True
                })
                mp_pag = json.loads(r_mock_paper.get('result', {}).get('value', '{}'))
                print("4d. Mock Paper 65 Qs Pagination:", mp_pag)
                results['mock_paper_pagination'] = ('1–20' in mp_pag.get('info', '') or '1-20' in mp_pag.get('info', '')) and mp_pag.get('items') == 20
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.closeMockPaperView();"})

                # ─────────────────────────────────────────────────────────────
                # 5. TEST NEW FEATURES
                # ─────────────────────────────────────────────────────────────
                # 5a. Mistake Vault
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('mistakes');"})
                await asyncio.sleep(0.5)
                r_mv = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const hasHero = !!document.querySelector('.mistake-hero');
                        const hasRetestBtn = !!document.querySelector('.mistake-controls-bar button.btn-primary');
                        const pills = document.querySelectorAll('.mistake-stat-pill').length;
                        return JSON.stringify({ hasHero, hasRetestBtn, pills });
                    })()""",
                    "returnByValue": True
                })
                mv_data = json.loads(r_mv.get('result', {}).get('value', '{}'))
                print("5a. Mistake Vault UI:", mv_data)
                results['mistake_vault'] = mv_data.get('hasHero') and mv_data.get('hasRetestBtn') and mv_data.get('pills') == 4

                # 5b. GATE Score & AIR Simulator
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('performance');"})
                await asyncio.sleep(0.5)
                r_pred = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.updatePredictorMarks(80);
                        const score = document.querySelector('.predictor-score-huge')?.textContent?.trim();
                        const air = document.querySelector('.predictor-air-huge')?.textContent?.trim();
                        const elig = document.querySelector('.predictor-eligibility-badge')?.textContent?.trim();
                        return JSON.stringify({ score, air, elig });
                    })()""",
                    "returnByValue": True
                })
                pred_data = json.loads(r_pred.get('result', {}).get('value', '{}'))
                print("5b. GATE Score Predictor (80 Marks):", pred_data)
                results['gate_score_predictor'] = '917' in pred_data.get('score', '') and 'AIR 1 – 100' in pred_data.get('air', '')

                # 5c. Draggable TCS iON Calculator
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
                print("5c. Draggable Calculator Setup:", calc_data)
                results['draggable_calc'] = calc_data.get('isOpen') and calc_data.get('isDragInit')

                # 5d. Exam Mode: Fullscreen Button, Pacing Timer & Code Syntax
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.startMockTest('mock-med-01'); window.jumpToTestQ(17);"})
                await asyncio.sleep(0.5)
                r_exam = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const hasFullscreenBtn = !!document.getElementById('exam-fullscreen-btn');
                        const hasTimer = !!document.getElementById('test-timer-display');
                        const hasCodeBlock = !!document.querySelector('.code-block-container');
                        const hasCopyBtn = !!document.querySelector('.code-copy-btn');
                        const timePerQInit = Array.isArray(window.state?.activeTest?.timePerQ);
                        return JSON.stringify({ hasFullscreenBtn, hasTimer, hasCodeBlock, hasCopyBtn, timePerQInit });
                    })()""",
                    "returnByValue": True
                })
                exam_data = json.loads(r_exam.get('result', {}).get('value', '{}'))
                print("5d. Exam Mode Enhancements (Q18 Code, Timer, Fullscreen):", exam_data)
                results['exam_enhancements'] = all(exam_data.values())

                # 5e. Submitting Mock Test & Verifying Pacing Analytics & PDF Print Option
                r_review = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(async () => {
                        await window.submitMockTest();
                        const hasPacingGrid = !!document.querySelector('.pacing-analytics-grid');
                        const hasTimeBadges = document.querySelectorAll('.time-spent-badge').length > 0;
                        const hasPrintBtn = !!document.querySelector('button[onclick*="printTestReport"]');
                        const hasMistakeLink = !!document.querySelector('button[onclick*="mistakes"]');
                        window.closeResult();
                        return JSON.stringify({ hasPacingGrid, hasTimeBadges, hasPrintBtn, hasMistakeLink });
                    })()""",
                    "awaitPromise": True,
                    "returnByValue": True
                })
                print("5e raw result:", r_review)
                review_val = r_review.get('result', {}).get('value')
                if isinstance(review_val, str):
                    review_data = json.loads(review_val)
                else:
                    review_data = review_val or {}
                print("5e. Test Result Pacing Analytics & PDF Print:", review_data)
                results['result_pacing_and_print'] = all(review_data.values()) if review_data else False

    except Exception as e:
        print("CDP Verification Error:", e)
        results['error'] = str(e)
    finally:
        edge_proc.terminate()
        server_proc.terminate()

    print("\n" + "="*50)
    print("FINAL TEST MATRIX RESULTS:")
    print("="*50)
    all_ok = True
    for k, v in results.items():
        print(f" - {k}: {v}")
        if v is not True and k != 'total_questions':
            all_ok = False
    print("="*50)
    if all_ok:
        print(">>> ALL VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<")
    else:
        print(">>> SOME VERIFICATION CHECKS FAILED! <<<")

if __name__ == '__main__':
    asyncio.run(main())
