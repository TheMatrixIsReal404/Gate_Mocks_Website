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
        '-m', 'http.server', '8089'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9226',
        'http://localhost:8089/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    try:
        with urllib.request.urlopen('http://127.0.0.1:9226/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8089' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                # 1. Login as guest
                await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.continueAsGuest()",
                    "awaitPromise": True
                })
                print("1. continueAsGuest executed")
                await asyncio.sleep(2)

                # 2. Check Mistake Vault route
                r_mistake = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.navigate('mistakes'); JSON.stringify({ title: document.getElementById('topbar-title')?.textContent, hasHero: !!document.querySelector('.mistake-hero'), pills: document.querySelectorAll('.mistake-stat-pill').length })",
                    "returnByValue": True
                })
                print("2. Mistake Vault Page Navigation:", r_mistake.get('result', {}).get('value'))

                # 3. Check Performance Page & GATE Predictor Card
                r_perf = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.navigate('performance'); JSON.stringify({ hasPredictor: !!document.getElementById('gate-predictor-container'), sliderVal: document.querySelector('.predictor-slider')?.value, scoreText: document.querySelector('.predictor-score-huge')?.textContent?.trim() })",
                    "returnByValue": True
                })
                print("3. Performance Predictor UI:", r_perf.get('result', {}).get('value'))

                # 4. Check Predictor Reactive Slider Update
                r_slider = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.updatePredictorMarks(75); JSON.stringify({ scoreText: document.querySelector('.predictor-score-huge')?.textContent?.trim(), airText: document.querySelector('.predictor-air-huge')?.textContent?.trim() })",
                    "returnByValue": True
                })
                print("4. Predictor Slider Update (75 marks):", r_slider.get('result', {}).get('value'))

                # 5. Check Calculator Draggable Handle Initialization
                r_calc = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "JSON.stringify({ hasCalc: !!document.getElementById('gate-calc-modal'), dragInit: !!document.getElementById('gate-calc-modal')?._dragInitialized })",
                    "returnByValue": True
                })
                print("5. GATE Calculator Drag Setup:", r_calc.get('result', {}).get('value'))

                # 6. Check Fullscreen & Keyboard Shortcuts Wiring
                r_shortcuts = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "typeof window.toggleExamFullscreen === 'function' && typeof window.printTestReport === 'function' && typeof window.startMistakeReTest === 'function'",
                    "returnByValue": True
                })
                print("6. New Core Functions Available on Window:", r_shortcuts.get('result', {}).get('value'))

    except Exception as e:
        print("CDP Error:", e)
    finally:
        edge_proc.terminate()
        server_proc.terminate()

if __name__ == '__main__':
    asyncio.run(main())
