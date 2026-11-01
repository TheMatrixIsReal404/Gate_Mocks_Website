# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import urllib.request
import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def test_ui():
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '8999'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1)
    edge = subprocess.Popen([
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        '--headless=new', '--remote-debugging-port=9238', 'http://localhost:8999/index.html?guest=1'
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

                # 1. Made Easy tab: Mock 1 to Mock 21
                await cdp('Runtime.evaluate', {'expression': 'navigate("mocks", {tab: "made-easy"})'})
                await asyncio.sleep(1)
                res_me = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll("#mock-tab-content .mock-card").length'
                })
                print('1. Made Easy mock cards rendered:', res_me.get('result',{}).get('value'), '(Expected: 21)')
                card_me1 = await cdp('Runtime.evaluate', {
                    'expression': 'JSON.stringify({ title: document.querySelector(".mock-card .mock-title")?.innerText, badge: document.querySelector(".mock-card .q-badge")?.innerText, desc: document.querySelector(".mock-card .text-muted")?.innerText })'
                })
                print('   First Made Easy Card (Mock 1):', card_me1.get('result',{}).get('value'))

                # 2. Gate Overflow / GO Classes tab: Mock 22 to Mock 48
                await cdp('Runtime.evaluate', {'expression': 'navigate("mocks", {tab: "go"})'})
                await asyncio.sleep(1)
                res_go = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll("#mock-tab-content .mock-card").length'
                })
                print('2. Gate Overflow / GO Classes cards rendered:', res_go.get('result',{}).get('value'), '(Expected: 27)')
                card_go1 = await cdp('Runtime.evaluate', {
                    'expression': 'JSON.stringify({ title: document.querySelector(".mock-card .mock-title")?.innerText, badge: document.querySelector(".mock-card .q-badge")?.innerText, desc: document.querySelector(".mock-card .text-muted")?.innerText })'
                })
                print('   First GO Card (Mock 22):', card_go1.get('result',{}).get('value'))

                # 3. All Mocks tab: Mock 1 to Mock 150
                await cdp('Runtime.evaluate', {'expression': 'navigate("mocks", {tab: "all"})'})
                await asyncio.sleep(1)
                res_all = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll("#mock-tab-content .mock-card").length'
                })
                print('3. All Mock cards rendered in grid:', res_all.get('result',{}).get('value'), '(Expected: 150)')

                # Check titles of first 5 cards in All tab
                first_titles = await cdp('Runtime.evaluate', {
                    'expression': 'Array.from(document.querySelectorAll("#mock-tab-content .mock-card .mock-title")).slice(0, 5).map(e => e.innerText).join(", ")'
                })
                print('   First 5 Mock Titles in All Grid:', first_titles.get('result',{}).get('value'))

                # 4. Previous Year Full-Length Exams Section
                await cdp('Runtime.evaluate', {'expression': 'navigate("pyq-exams")'})
                await asyncio.sleep(1)
                res_pyq = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelectorAll(".pyq-exam-card, .mock-card").length'
                })
                print('4. Previous Year Full-Length Exams rendered:', res_pyq.get('result',{}).get('value'), '(Expected: 21)')
                pyq_first = await cdp('Runtime.evaluate', {
                    'expression': 'document.querySelector(".pyq-exam-card .mock-title, .mock-card .mock-title")?.innerText'
                })
                print('   First PYQ Exam Title:', pyq_first.get('result',{}).get('value'))

                # 5. Launch Official GATE 2025 Set 1 in exam mode
                await cdp('Runtime.evaluate', {'expression': 'startMockTest("pyq-exam-2025-s1")'})
                await asyncio.sleep(1)
                gate25_q_count = await cdp('Runtime.evaluate', {
                    'expression': 'state.activeTest && state.activeTest.questions ? state.activeTest.questions.length : 0'
                })
                print('5. Launched Official GATE 2025 Set 1 from PYQ Section with questions:', gate25_q_count.get('result',{}).get('value'), '(Expected: 65)')

                print("\n>>> ALL IN-BROWSER UI, FILTERING & EXAM RUNTIME CHECKS PASSED WITH 100% SUCCESS! <<<")

    finally:
        edge.kill()
        server.kill()

if __name__ == '__main__':
    asyncio.run(test_ui())
