# scripts/verify_syllabus_guide.py
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
        '-m', 'http.server', '8124'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9254',
        'http://localhost:8124/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    try:
        with urllib.request.urlopen('http://127.0.0.1:9254/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8124' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                # 1. Login as guest
                for _ in range(30):
                    r_ready = await cdp_call(ws, "Runtime.evaluate", {
                        "expression": "typeof window.continueAsGuest === 'function'",
                        "returnByValue": True
                    })
                    if r_ready.get('result', {}).get('value') is True:
                        break
                    await asyncio.sleep(0.3)

                await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.continueAsGuest()",
                    "awaitPromise": True
                })
                print("1. Guest login initialized...")

                # Wait for state to populate
                for _ in range(30):
                    await asyncio.sleep(0.3)
                    st = await cdp_call(ws, "Runtime.evaluate", {
                        "expression": "window.state?.questions?.length || 0",
                        "returnByValue": True
                    })
                    if st.get('result', {}).get('value', 0) > 5000:
                        break

                # Navigate to subjects
                await cdp_call(ws, "Runtime.evaluate", {
                    "expression": "window.navigate('subjects')"
                })
                await asyncio.sleep(0.5)

                # Check syllabus guide elements
                eval_res = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const guideCard = document.querySelector('.syllabus-guide-card');
                        const secCards = document.querySelectorAll('.syllabus-sec-card');
                        const title = document.querySelector('.syllabus-guide-title')?.textContent || '';
                        
                        // Test toggle
                        window.toggleSyllabusGuide();
                        const hiddenDisplay = document.getElementById('syllabus-guide-body')?.style.display;
                        window.toggleSyllabusGuide();
                        const visibleDisplay = document.getElementById('syllabus-guide-body')?.style.display;
                        
                        // Test jumpToSubjectPYQs
                        window.jumpToSubjectPYQs('Operating Systems');
                        const pageAfterJump = window.state.currentPage;
                        const subAfterJump = window.state.selectedTopicPyqSubject;

                        return JSON.stringify({
                            hasGuideCard: !!guideCard,
                            secCardCount: secCards.length,
                            titleMatches: title.includes('Official GATE CSE Syllabus Guide'),
                            hiddenDisplay,
                            visibleDisplay,
                            pageAfterJump,
                            subAfterJump
                        });
                    })()""",
                    "returnByValue": True
                })

                data = json.loads(eval_res.get('result', {}).get('value', '{}'))
                print("Evaluation results:", json.dumps(data, indent=2))

                assert data.get('hasGuideCard') is True, "Guide card missing"
                assert data.get('secCardCount') == 11, f"Expected 11 section cards, got {data.get('secCardCount')}"
                assert data.get('titleMatches') is True, "Title mismatch"
                assert data.get('hiddenDisplay') == 'none', "Toggle hide failed"
                assert data.get('visibleDisplay') == 'grid', "Toggle show failed"
                assert data.get('pageAfterJump') == 'topic-pyqs', "Page navigation to topic-pyqs failed"
                assert data.get('subAfterJump') == 'Operating Systems', "Subject filter after jump failed"

                print("\n>>> ALL OFFICIAL SYLLABUS GUIDE TESTS PASSED! <<<")

    except Exception as e:
        print("Verification failed:", e)
        sys.exit(1)
    finally:
        edge_proc.terminate()
        server_proc.terminate()

if __name__ == '__main__':
    asyncio.run(main())
