# scripts/check_syntax_error.py
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
        '-m', 'http.server', '8127'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9257',
        'about:blank'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    try:
        with urllib.request.urlopen('http://127.0.0.1:9257/json') as r:
            tabs = json.loads(r.read().decode())
        ws_url = tabs[0]['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                await cdp_call(ws, "Runtime.enable")
                await cdp_call(ws, "Page.enable")
                
                # Navigate to the page
                await cdp_call(ws, "Page.navigate", {"url": "http://localhost:8127/index.html"})
                
                # Listen for messages
                for _ in range(20):
                    resp = await ws.receive_json()
                    if resp.get("method") == "Runtime.exceptionThrown":
                        print("Exception thrown:", json.dumps(resp.get("params", {}), indent=2))
                        break

    finally:
        edge_proc.terminate()
        server_proc.terminate()

if __name__ == '__main__':
    asyncio.run(main())
