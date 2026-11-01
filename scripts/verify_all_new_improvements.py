# scripts/verify_all_new_improvements.py
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
        '-m', 'http.server', '8125'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9255',
        'http://localhost:8125/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    results = {}

    try:
        with urllib.request.urlopen('http://127.0.0.1:9255/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8125' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                # 1. Login as guest
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

                # Wait for state to populate
                for _ in range(40):
                    await asyncio.sleep(0.3)
                    st = await cdp_call(ws, "Runtime.evaluate", {
                        "expression": "window.state?.questions?.length || 0",
                        "returnByValue": True
                    })
                    if st.get('result', {}).get('value', 0) > 5000:
                        break

                total_qs = (await cdp_call(ws, "Runtime.evaluate", {"expression": "window.state.questions.length", "returnByValue": True})).get('result', {}).get('value')
                print(f"   Questions loaded: {total_qs}")
                results['total_questions'] = total_qs

                # ─────────────────────────────────────────────────────────────
                # TEST 1: Universal Global Search across 8,168 questions
                # ─────────────────────────────────────────────────────────────
                r_search = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.openGlobalSearch();
                        const modal = document.getElementById('global-search-modal');
                        const isModalActive = modal && modal.classList.contains('active');
                        
                        window.executeGlobalSearch('Dijkstra');
                        const resultsItems = document.querySelectorAll('.search-result-item');
                        const countText = document.getElementById('global-search-count')?.textContent || '';
                        
                        window.closeGlobalSearch();
                        const isModalClosed = !modal.classList.contains('active');

                        return JSON.stringify({
                            isModalActive,
                            isModalClosed,
                            resultsCount: resultsItems.length,
                            countText
                        });
                    })()""",
                    "returnByValue": True
                })
                s_data = json.loads(r_search.get('result', {}).get('value', '{}'))
                results['new_1_universal_global_search'] = bool(
                    s_data.get('isModalActive') and
                    s_data.get('isModalClosed') and
                    s_data.get('resultsCount') > 0
                )

                # ─────────────────────────────────────────────────────────────
                # TEST 2: Exam Countdown & Daily Study Streak
                # ─────────────────────────────────────────────────────────────
                r_streak = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const cd = window.getExamCountdownData();
                        const cdText = document.getElementById('countdown-text')?.textContent || '';
                        const initialStreak = window.state.dailyStreak?.todayCount || 0;
                        window.recordDailyAttemptForStreak();
                        const newStreak = window.state.dailyStreak?.todayCount || 0;
                        const streakText = document.getElementById('streak-text')?.textContent || '';

                        return JSON.stringify({
                            hasCdDays: cd && cd.days > 0,
                            cdTextMatches: cdText.includes('GATE'),
                            streakIncremented: newStreak === initialStreak + 1,
                            streakTextHasQ: streakText.includes('Q')
                        });
                    })()""",
                    "returnByValue": True
                })
                st_data = json.loads(r_streak.get('result', {}).get('value', '{}'))
                results['new_2_exam_countdown_and_streak'] = bool(
                    st_data.get('hasCdDays') and
                    st_data.get('cdTextMatches') and
                    st_data.get('streakIncremented') and
                    st_data.get('streakTextHasQ')
                )

                # ─────────────────────────────────────────────────────────────
                # TEST 3: 10-Spoke Subject Mastery Radar Chart
                # ─────────────────────────────────────────────────────────────
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('performance')"})
                await asyncio.sleep(0.5)

                r_radar = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const card = document.querySelector('.radar-chart-card');
                        const poly = document.querySelector('.radar-polygon');
                        const pts = document.querySelectorAll('.radar-point');
                        const spokes = document.querySelectorAll('.radar-spoke');
                        const legendItems = document.querySelectorAll('.radar-legend-item');

                        return JSON.stringify({
                            hasCard: !!card,
                            hasPoly: !!poly,
                            pointsCount: pts.length,
                            spokesCount: spokes.length,
                            legendCount: legendItems.length
                        });
                    })()""",
                    "returnByValue": True
                })
                rd_data = json.loads(r_radar.get('result', {}).get('value', '{}'))
                results['new_3_mastery_radar_chart'] = bool(
                    rd_data.get('hasCard') and
                    rd_data.get('hasPoly') and
                    rd_data.get('pointsCount') == 10 and
                    rd_data.get('spokesCount') == 10 and
                    rd_data.get('legendCount') == 10
                )

                # ─────────────────────────────────────────────────────────────
                # TEST 4: Expected Value (E) Risk Analyzer & Confidence Selectors
                # ─────────────────────────────────────────────────────────────
                r_ev = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const mcq = window.state.questions.find(q => q.type === 'mcq' && q.marks === 1);
                        const evAnalysis = window.getExpectedValueAnalysis(mcq);
                        const evHtml = window.buildExpectedValueCardHTML(mcq);
                        const confHtml = window.buildConfidenceSelectorHTML(mcq.id);

                        window.setQuestionConfidence(mcq.id, 'high');
                        const isConfidenceSaved = window.state.confidenceTags[mcq.id] === 'high';

                        return JSON.stringify({
                            ev0: evAnalysis.ev0,
                            ev1: evAnalysis.ev1,
                            ev2: evAnalysis.ev2,
                            hasEvHtml: evHtml.includes('Expected Value'),
                            hasConfHtml: confHtml.includes('Confidence:'),
                            isConfidenceSaved
                        });
                    })()""",
                    "returnByValue": True
                })
                ev_data = json.loads(r_ev.get('result', {}).get('value', '{}'))
                results['new_4_ev_risk_and_confidence'] = bool(
                    ev_data.get('ev0') == 0.0 and
                    ev_data.get('ev2') == 0.33 and
                    ev_data.get('hasEvHtml') and
                    ev_data.get('hasConfHtml') and
                    ev_data.get('isConfidenceSaved')
                )

                # ─────────────────────────────────────────────────────────────
                # TEST 5: 60-Second Formula Blitz Mode
                # ─────────────────────────────────────────────────────────────
                r_blitz = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.startFormulaBlitz();
                        const timeEl = document.getElementById('blitz-time-text');
                        const formulaBox = document.getElementById('blitz-formula-content');
                        
                        window.advanceBlitzCard(true); // +10 pts
                        const scoreAfter = parseInt(document.querySelector('.blitz-view-container')?.textContent.match(/Score:\\s*(\\d+)/)?.[1] || '0');
                        
                        window.stopFormulaBlitz();

                        return JSON.stringify({
                            hasTime: !!timeEl,
                            hasFormulaBox: !!formulaBox,
                            scoreIncreased: scoreAfter >= 10
                        });
                    })()""",
                    "returnByValue": True
                })
                blitz_data = json.loads(r_blitz.get('result', {}).get('value', '{}'))
                results['new_5_formula_blitz_mode'] = bool(
                    blitz_data.get('hasTime') and
                    blitz_data.get('hasFormulaBox') and
                    blitz_data.get('scoreIncreased')
                )

                # ─────────────────────────────────────────────────────────────
                # TEST 6: NAT Precision & Rounding Trap Inspector
                # ─────────────────────────────────────────────────────────────
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
                results['new_6_nat_precision_inspector'] = bool(
                    nat_data.get('hasBounds') and
                    nat_data.get('hasTrapAdvisory')
                )

                # ─────────────────────────────────────────────────────────────
                # TEST 7: 2-Column Printable Practice Worksheet Generator
                # ─────────────────────────────────────────────────────────────
                r_ws = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.generatePrintableWorksheet(window.state.questions.slice(0, 4), 'Verification Test Worksheet');
                        const container = document.getElementById('printable-worksheet-container');
                        const qItems = container.querySelectorAll('.ws-q-item');
                        const keyRows = container.querySelectorAll('.ws-key-table tbody tr');
                        const title = container.querySelector('.ws-title')?.textContent || '';

                        return JSON.stringify({
                            qCount: qItems.length,
                            keyCount: keyRows.length,
                            titleMatches: title.includes('Verification Test Worksheet')
                        });
                    })()""",
                    "returnByValue": True
                })
                ws_data = json.loads(r_ws.get('result', {}).get('value', '{}'))
                results['new_7_printable_worksheet'] = bool(
                    ws_data.get('qCount') == 4 and
                    ws_data.get('keyCount') == 4 and
                    ws_data.get('titleMatches')
                )

    except Exception as e:
        print("CDP Verification Error:", e)
        results['error'] = str(e)
    finally:
        edge_proc.terminate()
        server_proc.terminate()

    print("\n" + "="*60)
    print("NEW ADVANCED IMPROVEMENTS VERIFICATION AUDIT MATRIX:")
    print("="*60)
    all_ok = True
    for k, v in results.items():
        print(f" {k:<42}: {v}")
        if v is not True and k != 'total_questions':
            all_ok = False
    print("="*60)
    if all_ok:
        print(">>> ALL 7 NEW ADVANCED IMPROVEMENTS PASSED 100%! <<<")
    else:
        print(">>> SOME VERIFICATION CHECKS FAILED! <<<")

if __name__ == '__main__':
    asyncio.run(main())
