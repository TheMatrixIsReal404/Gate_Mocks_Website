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

                # Check dashboard series grid cards
                card_stats = await cdp('Runtime.evaluate', {
                    'expression': '''(() => {
                        const cards = Array.from(document.querySelectorAll(".dashboard-series-grid .series-card"));
                        return JSON.stringify(cards.map(c => ({
                            title: c.querySelector(".series-title")?.innerText,
                            height: Math.round(c.getBoundingClientRect().height),
                            width: Math.round(c.getBoundingClientRect().width)
                        })));
                    })()'''
                })
                data = json.loads(card_stats.get('result',{}).get('value', '[]'))
                print("Dashboard Series Cards on 1600x1000 screen:")
                for idx, c in enumerate(data, 1):
                    print(f"  {idx}. {c['title']} -> Width: {c['width']}px, Height: {c['height']}px")

                # Take screenshot to verify visually
                screenshot_data = await cdp('Page.captureScreenshot')
                if 'data' in screenshot_data:
                    import base64
                    with open('scripts/dashboard_fixed.png', 'wb') as sf:
                        sf.write(base64.b64decode(screenshot_data['data']))
                    print("Saved screenshot to scripts/dashboard_fixed.png")

    finally:
        edge.kill()
        server.kill()

if __name__ == '__main__':
    asyncio.run(test_ui())
