# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import urllib.request
import subprocess
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def test_search():
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

                # 1. Navigate to mocks
                await cdp('Runtime.evaluate', {'expression': 'navigate("mocks")'})
                await asyncio.sleep(1)

                # 2. Search for "Made Easy"
                res_me = await cdp('Runtime.evaluate', {
                    'expression': '''(() => {
                        updateMockSearch("Made Easy");
                        const cards = Array.from(document.querySelectorAll(".mock-card"));
                        return JSON.stringify({
                            count: cards.length,
                            titles: cards.slice(0, 3).map(c => c.querySelector(".mock-title")?.innerText)
                        });
                    })()'''
                })
                me_data = json.loads(res_me.get('result',{}).get('value', '{}'))
                print("Made Easy search result count:", me_data.get('count'), "Sample titles:", me_data.get('titles'))
                assert me_data.get('count') == 21, f"Expected 21 Made Easy cards, got {me_data.get('count')}"

                # 3. Search for "Gate Overflow"
                res_go = await cdp('Runtime.evaluate', {
                    'expression': '''(() => {
                        updateMockSearch("Gate Overflow");
                        const cards = Array.from(document.querySelectorAll(".mock-card"));
                        return JSON.stringify({
                            count: cards.length,
                            titles: cards.slice(0, 3).map(c => c.querySelector(".mock-title")?.innerText)
                        });
                    })()'''
                })
                go_data = json.loads(res_go.get('result',{}).get('value', '{}'))
                print("Gate Overflow search result count:", go_data.get('count'), "Sample titles:", go_data.get('titles'))
                assert go_data.get('count') == 27, f"Expected 27 Gate Overflow cards, got {go_data.get('count')}"

                print(">>> ALL PROVIDER SEARCH TESTS PASSED WITH 100% SUCCESS! <<<")

    finally:
        edge.kill()
        server.kill()

if __name__ == '__main__':
    asyncio.run(test_search())
