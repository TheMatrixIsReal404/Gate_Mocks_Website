# -*- coding: utf-8 -*-
import subprocess
import time
import json
import urllib.request
import os

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

# Launch Edge with remote debugging on port 9225
file_url = 'file:///' + os.path.abspath('index.html').replace('\\', '/')
cmd = [
    edge_path,
    '--headless=new',
    '--remote-debugging-port=9225',
    file_url
]

proc = subprocess.Popen(cmd)
time.sleep(2.5)

try:
    with urllib.request.urlopen('http://127.0.0.1:9225/json') as resp:
        tabs = json.loads(resp.read().decode())
    print("Edge loaded page successfully! Tab count:", len(tabs))
finally:
    proc.terminate()
