# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import urllib.request
import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def test_full_suite():
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '8999'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1)
    edge = subprocess.Popen([
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        '--headless=new', '--remote-debugging-port=9238', '--window-size=1600,1000', 'http://localhost:8999/index.html?guest=1'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3)
    
    try:
        with urllib.request.urlopen('http://127.0.0.1:9238/json') as r:
            tabs = json.loads(r.read().decode())
        ws_url = [t for t in tabs if '8999' in t.get('url','')][0]['webSocketDebuggerUrl']
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                cmd_id = 0
                async def cdp(method, params=None):
                    nonlocal cmd_id
                    cmd_id += 1
                    msg = {'id': cmd_id, 'method': method}
                    if params: msg['params'] = params
                    await ws.send_json(msg)
                    while True:
                        resp = await ws.receive_json()
                        if resp.get('id') == cmd_id:
                            return resp.get('result', {})
                
                await cdp('Runtime.enable')
                await asyncio.sleep(2)

                print("--- 1. Testing Mock Navigation & Layout Toggle ---")
                await cdp('Runtime.evaluate', {'expression': 'navigate("mocks")'})
                await asyncio.sleep(1)

                # Default should be grid view
                grid_cards = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll(".mock-card").length'
                })
                count_grid = grid_cards.get('result',{}).get('value', 0)
                print(f"  Grid view mock cards count: {count_grid}")
                assert count_grid == 150, f"Expected 150 grid cards, got {count_grid}"

                # Switch to compact list view
                await cdp('Runtime.evaluate', {'expression': 'setMockViewMode("compact")'})
                await asyncio.sleep(1)
                compact_rows = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll(".mock-compact-row").length'
                })
                count_compact = compact_rows.get('result',{}).get('value', 0)
                print(f"  Compact view mock rows count: {count_compact}")
                assert count_compact == 150, f"Expected 150 compact rows, got {count_compact}"

                # Switch back to grid view
                await cdp('Runtime.evaluate', {'expression': 'setMockViewMode("grid")'})
                await asyncio.sleep(1)

                print("--- 2. Testing Pinning / Target Mocks ---")
                # Pin Mock 1 (id: 'mock-me24-f-adv1') and Mock 22 (id: 'mock-go-ts25-aim-02')
                await cdp('Runtime.evaluate', {'expression': 'togglePinMock("mock-me24-f-adv1")'})
                await cdp('Runtime.evaluate', {'expression': 'togglePinMock("mock-go-ts25-aim-02")'})
                await asyncio.sleep(1)

                # Filter by pinned target mocks
                await cdp('Runtime.evaluate', {'expression': 'setMockSubSeries("pinned")'})
                await asyncio.sleep(1)
                pinned_cards = await cdp('Runtime.evaluate', {
                    'expression': '''(() => {
                        const cards = Array.from(document.querySelectorAll(".mock-card"));
                        return JSON.stringify(cards.map(c => c.querySelector(".mock-title")?.innerText));
                    })()'''
                })
                pinned_titles = json.loads(pinned_cards.get('result',{}).get('value', '[]'))
                print(f"  Target Mocks filtered count: {len(pinned_titles)}, titles: {pinned_titles}")
                assert len(pinned_titles) == 2, f"Expected 2 pinned mocks, got {len(pinned_titles)}"
                assert 'Mock 1' in pinned_titles and 'Mock 22' in pinned_titles

                # Reset to all mocks
                await cdp('Runtime.evaluate', {'expression': 'setMockSubSeries("all")'})
                await asyncio.sleep(1)

                print("--- 3. Testing Provider Search Filtering ---")
                await cdp('Runtime.evaluate', {'expression': 'updateMockSearch("Made Easy")'})
                await asyncio.sleep(1)
                me_count = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll(".mock-card").length'
                })
                print(f"  Made Easy search count: {me_count.get('result',{}).get('value')}")
                assert me_count.get('result',{}).get('value') == 21

                await cdp('Runtime.evaluate', {'expression': 'updateMockSearch("Gate Overflow")'})
                await asyncio.sleep(1)
                go_count = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll(".mock-card").length'
                })
                print(f"  Gate Overflow search count: {go_count.get('result',{}).get('value')}")
                assert go_count.get('result',{}).get('value') == 27
                await cdp('Runtime.evaluate', {'expression': 'updateMockSearch("")'})
                await asyncio.sleep(1)

                print("--- 4. Testing Compound Multi-Token Practice Search ---")
                await cdp('Runtime.evaluate', {'expression': 'navigate("practice")'})
                await asyncio.sleep(1)
                await cdp('Runtime.evaluate', {'expression': 'updatePracticeSearch("OS Deadlock")'})
                await asyncio.sleep(1)
                practice_q = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll("#practice-questions-grid .pyq-item").length'
                })
                pq_count = practice_q.get('result',{}).get('value', 0)
                print(f"  Compound search 'OS Deadlock' matched cards on page: {pq_count}")
                assert pq_count > 0, "Expected at least 1 match for compound OS Deadlock"

                print("--- 5. Testing Mock Test Live Execution Topbar & Submission ---")
                await cdp('Runtime.evaluate', {'expression': 'startMockTest("mock-me24-f-adv1")'})
                await asyncio.sleep(2)
                
                # Check topbar title
                topbar_title = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelector(".test-title")?.innerText'
                })
                title_text = topbar_title.get('result',{}).get('value', '')
                print(f"  Live Exam Topbar Title: '{title_text}'")
                assert "Mock 1" in title_text and "Made Easy" in title_text

                # Submit test
                await cdp('Runtime.evaluate', {'expression': 'submitMockTest()'})
                await asyncio.sleep(2)

                # Check result screen
                res_sub = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelector(".result-subtitle")?.innerText'
                })
                sub_text = res_sub.get('result',{}).get('value', '')
                print(f"  Result Screen Subtitle: '{sub_text}'")
                assert "Mock 1" in sub_text and "Made Easy" in sub_text

                # Check pacing warnings and GATE score predictor
                pacing_el = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelector(".pacing-analytics-grid") !== null'
                })
                print(f"  Pacing Analytics Grid present: {pacing_el.get('result',{}).get('value')}")
                assert pacing_el.get('result',{}).get('value') is True

                print("\n=======================================================")
                print(">>> ALL 5 NEW FEATURES VERIFIED WITH 100% SUCCESS! <<<")
                print("=======================================================")

    finally:
        edge.kill()
        server.kill()

if __name__ == '__main__':
    asyncio.run(test_full_suite())
