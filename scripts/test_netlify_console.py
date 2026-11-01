# -*- coding: utf-8 -*-
import subprocess

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
cmd = [
    edge_path,
    '--headless',
    '--enable-logging=stderr',
    '--v=1',
    '--dump-dom',
    'https://gate-cse-practice.netlify.app'
]

res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("STDOUT length:", len(res.stdout))
print("STDERR:")
print(res.stderr[:2000])
