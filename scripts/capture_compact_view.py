# -*- coding: utf-8 -*-
import asyncio, aiohttp, urllib.request, subprocess, json, sys, base64

async def snap():
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
                await cdp('Runtime.evaluate', {'expression': 'navigate("mocks")'})
                await asyncio.sleep(1)
                await cdp('Runtime.evaluate', {'expression': 'setMockViewMode("compact")'})
                await asyncio.sleep(1)
                shot = await cdp('Page.captureScreenshot')
                if 'data' in shot:
                    with open(r'C:\Users\sahu1\.gemini\antigravity\brain\88301f00-0c4e-441c-8598-16eb259966ed\mocks_compact_view.png', 'wb') as f:
                        f.write(base64.b64decode(shot['data']))
                    print('Screenshot saved successfully!')
    finally:
        edge.kill()
        server.kill()

if __name__ == '__main__':
    asyncio.run(snap())
