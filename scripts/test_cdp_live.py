# -*- coding: utf-8 -*-
import asyncio
import json
import urllib.request
import aiohttp
import sys
import subprocess

async def main():
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '8996'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1)
    edge = subprocess.Popen([
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        '--headless=new',
        '--remote-debugging-port=9234',
        'http://localhost:8996/index.html?guest=1'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3)

    try:
        with urllib.request.urlopen('http://127.0.0.1:9234/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if '8996' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                await ws.send_json({'id': 1, 'method': 'Runtime.enable'})
                for _ in range(30):
                    await ws.send_json({'id': 10, 'method': 'Runtime.evaluate', 'params': {'expression': 'state && state.questions ? state.questions.length : 0'}})
                    while True:
                        resp = await ws.receive_json()
                        if resp.get('id') == 10:
                            break
                    cnt = resp.get('result', {}).get('result', {}).get('value', 0)
                    if cnt > 19000:
                        break
                    await asyncio.sleep(0.5)

                eval_script = """
                (() => {
                    const q = state.questions.find(x => x.id === 'zeal_dld_009');
                    const div = document.createElement('div');
                    div.innerHTML = formatQuestionContent(q.question);
                    document.body.appendChild(div);
                    renderMath(div);
                    const errors = div.querySelectorAll('.katex-error');
                    const res = {
                        html: div.innerHTML.slice(0, 300),
                        errorCount: errors.length,
                        errorTexts: Array.from(errors).map(e => e.textContent)
                    };
                    document.body.removeChild(div);
                    return res;
                })()
                """
                await ws.send_json({'id': 20, 'method': 'Runtime.evaluate', 'params': {'expression': eval_script, 'returnByValue': True}})
                while True:
                    resp = await ws.receive_json()
                    if resp.get('id') == 20:
                        break
                print('zeal_dld_009 render result:', resp.get('result', {}).get('result', {}).get('value'))
    finally:
        edge.terminate()
        server.terminate()

if __name__ == '__main__':
    asyncio.run(main())
