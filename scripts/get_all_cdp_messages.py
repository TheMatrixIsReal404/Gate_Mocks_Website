# scripts/get_all_cdp_messages.py
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
        '-m', 'http.server', '8130'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9260',
        'http://localhost:8130/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    try:
        with urllib.request.urlopen('http://127.0.0.1:9260/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8130' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                await cdp_call(ws, "Runtime.enable")
                await cdp_call(ws, "Console.enable")
                await cdp_call(ws, "Log.enable")

                # Reload the page so we see all parse events from scratch
                await cdp_call(ws, "Page.enable")
                await cdp_call(ws, "Page.reload")

                for _ in range(30):
                    try:
                        msg = await asyncio.wait_for(ws.receive_json(), timeout=1.0)
                        method = msg.get("method", "")
                        if "exception" in method.lower() or "console" in method.lower() or "log" in method.lower():
                            print(f"EVENT {method}:", json.dumps(msg.get("params", {}), indent=2))
                    except asyncio.TimeoutError:
                        break

    finally:
        edge_proc.terminate()
        server_proc.terminate()

if __name__ == '__main__':
    asyncio.run(main())
