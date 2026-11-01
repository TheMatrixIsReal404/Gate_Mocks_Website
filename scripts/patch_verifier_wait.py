# scripts/patch_verifier_wait.py
with open('scripts/verify_all_thirty_seven_features.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    try:
        with urllib.request.urlopen('http://127.0.0.1:9263/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8133' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']"""

replacement = """    try:
        tabs = None
        for _ in range(25):
            try:
                with urllib.request.urlopen('http://127.0.0.1:9263/json') as r:
                    tabs = json.loads(r.read().decode())
                if tabs and any('localhost:8133' in t.get('url', '') for t in tabs):
                    break
            except Exception:
                pass
            await asyncio.sleep(0.5)

        target = [t for t in tabs if 'localhost:8133' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']"""

if target in code:
    code = code.replace(target, replacement, 1)
    with open('scripts/verify_all_thirty_seven_features.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Verifier wait patched successfully!")
else:
    print("Target not found!")
