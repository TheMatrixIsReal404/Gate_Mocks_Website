# -*- coding: utf-8 -*-
import subprocess
import time
import json
import urllib.request
import asyncio
try:
    import websockets
except ImportError:
    pass

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
proc = subprocess.Popen([
    edge_path,
    '--headless=new',
    '--remote-debugging-port=9224',
    'https://gate-cse-practice.netlify.app'
])
time.sleep(3)

try:
    with urllib.request.urlopen('http://127.0.0.1:9224/json') as r:
        tabs = json.loads(r.read().decode())
    print("Found tabs:", len(tabs))
    target = [t for t in tabs if 'gate-cse-practice' in t.get('url', '')]
    if target:
        print("Target tab:", target[0]['url'])
        print("WebSocket:", target[0]['webSocketDebuggerUrl'])
except Exception as e:
    print("Error:", e)
finally:
    proc.terminate()
