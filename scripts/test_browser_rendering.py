# -*- coding: utf-8 -*-
"""
test_browser_rendering.py
Automated Headless Edge CDP verification script to test actual DOM and KaTeX rendering.
"""
import asyncio
import json
import subprocess
import urllib.request
import aiohttp
import sys
import os

cmd_id = 1000

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
    print("=" * 70)
    print("LAUNCHING HEADLESS EDGE CDP RENDER TEST FOR GATE PLATFORM")
    print("=" * 70)

    server = subprocess.Popen([sys.executable, '-m', 'http.server', '8995'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9233',
        '--window-size=1200,800',
        'http://localhost:8995/index.html?guest=1'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3)

    try:
        with urllib.request.urlopen('http://127.0.0.1:9233/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if '8995' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                await cdp_call(ws, 'Runtime.enable')

                # Wait for state.questions to load
                q_count = 0
                for _ in range(40):
                    res = await cdp_call(ws, 'Runtime.evaluate', {
                        'expression': 'typeof state !== "undefined" && state.questions ? state.questions.length : 0'
                    })
                    q_count = res.get('result', {}).get('value', 0)
                    if q_count > 19000:
                        break
                    await asyncio.sleep(0.5)

                print(f"Browser loaded {q_count} questions into memory.")

                # Test rendering sample of questions across newly added and existing papers
                test_js = """
                (() => {
                    const questions = state.questions || [];
                    const report = {
                        totalChecked: 0,
                        katexErrors: [],
                        htmlCorruption: [],
                        unclosedCodeBlocks: [],
                        brokenImages: []
                    };

                    const testDiv = document.createElement('div');
                    document.body.appendChild(testDiv);

                    // Check all newly added OCR questions specifically + sample of existing
                    const ocrQuestions = questions.filter(q => q.id.startsWith('zeal_cp_') || q.id.startsWith('zeal_dld_') || q.id.startsWith('zeal_em_') || q.id.startsWith('me24_pds_'));
                    const sampleOther = questions.filter(q => !q.id.startsWith('zeal_cp_') && !q.id.startsWith('zeal_dld_') && !q.id.startsWith('zeal_em_') && !q.id.startsWith('me24_pds_')).slice(0, 1000);
                    const toTest = ocrQuestions.concat(sampleOther);
                    report.totalChecked = toTest.length;

                    for (let i = 0; i < toTest.length; i++) {
                        const q = toTest[i];
                        const qid = q.id;
                        const qText = q.question || '';

                        // Format
                        let formatted = '';
                        try {
                            formatted = formatQuestionContent(qText);
                        } catch (err) {
                            report.htmlCorruption.push({ id: qid, error: err.message });
                            continue;
                        }

                        // DOM insertion
                        testDiv.innerHTML = formatted;

                        // Check KaTeX with throwOnError: true
                        try {
                            window.renderMathInElement(testDiv, {
                                delimiters: [
                                    { left: '$$', right: '$$', display: true },
                                    { left: '$', right: '$', display: false },
                                    { left: '\\\\(', right: '\\\\)', display: false },
                                    { left: '\\\\[', right: '\\\\]', display: true }
                                ],
                                strict: 'warn',
                                throwOnError: true
                            });
                        } catch (kErr) {
                            report.katexErrors.push({ id: qid, error: kErr.message, snippet: qText.slice(0, 80) });
                        }
                    }

                    document.body.removeChild(testDiv);
                    return report;
                })()
                """

                print("Executing thorough in-browser rendering audit...")
                eval_res = await cdp_call(ws, 'Runtime.evaluate', {
                    'expression': test_js,
                    'returnByValue': True
                })

                result = eval_res.get('result', {}).get('value', {})
                print(f"Total Questions Evaluated in DOM: {result.get('totalChecked', 0)}")
                print(f"HTML Corruption Count: {len(result.get('htmlCorruption', []))}")
                print(f"KaTeX Parse Errors: {len(result.get('katexErrors', []))}")
                if result.get('katexErrors'):
                    print("Sample KaTeX Errors:")
                    for err in result.get('katexErrors')[:10]:
                        print(f"  * [{err.get('id')}]: {err.get('error')} -> {err.get('snippet')}")

    finally:
        edge.terminate()
        server.terminate()

if __name__ == '__main__':
    asyncio.run(main())
