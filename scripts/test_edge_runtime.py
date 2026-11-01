# -*- coding: utf-8 -*-
import subprocess
import time
import json
import urllib.request

# Start Edge with remote debugging
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
cmd = [
    edge_path,
    '--headless=new',
    '--remote-debugging-port=9223',
    'file:///G:/0.Gate_Lectures/0.Gate_Mocks_Website/index.html'
]

proc = subprocess.Popen(cmd)
time.sleep(2)

try:
    # Query targets
    targets_url = 'http://127.0.0.1:9223/json'
    with urllib.request.urlopen(targets_url) as resp:
        targets = json.loads(resp.read().decode())
    
    ws_url = targets[0]['webSocketDebuggerUrl']
    print("Edge running! Target URL:", targets[0]['url'])
except Exception as e:
    print("Could not connect to Edge debugger:", e)
finally:
    proc.terminate()
