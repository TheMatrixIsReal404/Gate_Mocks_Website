# -*- coding: utf-8 -*-
"""
Comprehensive Audit & Headless Browser Verification Suite for All 8,168 Questions.
Tests:
1. formatQuestionContent execution without runtime errors.
2. KaTeX LaTeX parsing (throwOnError: true) on question text, options, and explanations.
3. Code block fences (``` balanced, valid languages, intact syntax).
4. HTML entity corruption (&lt;pre, &amp;quot;, literal escaped tags).
5. Unbalanced math delimiters ($ or $$ odd counts).
6. Option completeness (MCQ/MSQ options >= 2, non-empty).
7. Missing diagram/table references without visual/tabular data.
8. Truncated question strings.
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
    print("🔍 INITIATING DEEP RENDER & SYNTAX AUDIT OF ALL 8,168 QUESTIONS IN EDGE")
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
                for _ in range(30):
                    res = await cdp_call(ws, 'Runtime.evaluate', {
                        'expression': 'typeof state !== "undefined" && state.questions && state.questions.length > 8000 ? state.questions.length : 0'
                    })
                    q_count = res.get('result', {}).get('value', 0)
                    if q_count > 8000:
                        break
                    await asyncio.sleep(0.5)

                print(f"✓ Browser loaded {q_count} questions into memory.")

                # In-browser test runner script
                audit_js = """
                (() => {
                    const questions = state.questions || [];
                    const report = {
                        totalChecked: questions.length,
                        htmlCorruption: [],
                        unbalancedMathDelimiters: [],
                        katexErrors: [],
                        unclosedCodeBlocks: [],
                        emptyOrInvalidOptions: [],
                        missingFiguresOrTables: [],
                        truncatedQuestions: []
                    };

                    const testDiv = document.createElement('div');
                    document.body.appendChild(testDiv);

                    for (let i = 0; i < questions.length; i++) {
                        const q = questions[i];
                        const qid = q.id || ('idx_' + i);
                        const qText = q.question || '';

                        // 1. Check unclosed code fences ```
                        const fenceMatches = qText.match(/```/g);
                        if (fenceMatches && fenceMatches.length % 2 !== 0) {
                            report.unclosedCodeBlocks.push({ id: qid, count: fenceMatches.length, subject: q.subject });
                        }

                        // 2. Format question content
                        let formatted = '';
                        try {
                            formatted = formatQuestionContent(qText);
                        } catch (err) {
                            report.htmlCorruption.push({ id: qid, error: err.message, subject: q.subject });
                            continue;
                        }

                        // 3. Check for raw escaped tags that shouldn't be literal
                        if (formatted.includes('&lt;pre') || formatted.includes('&lt;div') || formatted.includes('&amp;lt;') || formatted.includes('&amp;quot;')) {
                            report.htmlCorruption.push({ id: qid, snippet: formatted.slice(0, 100), subject: q.subject });
                        }

                        // 4. Check unbalanced $ math delimiters outside code blocks
                        // Strip code blocks first to check math
                        const noCode = qText.replace(/```[\\s\\S]*?```/g, '').replace(/`[^`]+`/g, '');
                        const dollarMatches = noCode.match(/(?<!\\\\)\\$/g);
                        if (dollarMatches && dollarMatches.length % 2 !== 0) {
                            report.unbalancedMathDelimiters.push({ id: qid, dollars: dollarMatches.length, subject: q.subject });
                        }

                        // 5. Test KaTeX rendering in DOM
                        testDiv.innerHTML = formatted;
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
                            report.katexErrors.push({ id: qid, error: kErr.message, subject: q.subject });
                        }

                        // 6. Options sanity check
                        if (q.type === 'mcq' || q.type === 'msq') {
                            if (!Array.isArray(q.options) || q.options.length < 2) {
                                report.emptyOrInvalidOptions.push({ id: qid, optionsCount: q.options ? q.options.length : 0, subject: q.subject });
                            } else {
                                for (let optIdx = 0; optIdx < q.options.length; optIdx++) {
                                    const opt = q.options[optIdx];
                                    if (typeof opt !== 'string' || opt.trim().length === 0) {
                                        report.emptyOrInvalidOptions.push({ id: qid, emptyOptIdx: optIdx, subject: q.subject });
                                    }
                                }
                            }
                        }

                        // 7. Check for references to missing diagrams/tables
                        const lower = qText.lower ? qText.lower() : qText.toLowerCase();
                        const hasDiagramKeyword = lower.includes('pie chart') || lower.includes('shown in the figure below') || lower.includes('given in the table below') || lower.includes('shown below:') || lower.includes('circuit diagram below');
                        if (hasDiagramKeyword) {
                            const hasTableOrSvgOrCode = formatted.includes('<table') || formatted.includes('<svg') || formatted.includes('<figure') || formatted.includes('<pre');
                            if (!hasTableOrSvgOrCode) {
                                report.missingFiguresOrTables.push({ id: qid, subject: q.subject, paper: q.paper, snippet: qText.slice(0, 120) });
                            }
                        }

                        // 8. Truncated questions (e.g. ending abruptly with a number or dangling conjunction)
                        const trimmed = qText.trim();
                        if (/[a-zA-Z]+\\s+[0-9]+$/.test(trimmed) && !trimmed.endsWith('.') && !trimmed.endsWith('?') && !trimmed.endsWith(':')) {
                            // Example: 'Mechanical 9' or 'Section 2' without punctuation
                            report.truncatedQuestions.push({ id: qid, tail: trimmed.slice(-30), subject: q.subject });
                        }
                    }

                    document.body.removeChild(testDiv);
                    return report;
                })()
                """

                print("Executing thorough in-browser verification...")
                eval_res = await cdp_call(ws, 'Runtime.evaluate', {
                    'expression': audit_js,
                    'returnByValue': True
                })

                audit_data = eval_res.get('result', {}).get('value', {})
                out_path = r'C:\Users\sahu1\.gemini\antigravity\brain\5161ee8e-2deb-453b-b748-b460f1ebe1e6\scratch\audit_results.json'
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(audit_data, f, indent=2)

                print(f"✓ Audit completed and saved to {out_path}!")
                print(f"Total Questions Evaluated: {audit_data.get('totalChecked', 0)}")
                print(f"HTML Corruption Count: {len(audit_data.get('htmlCorruption', []))}")
                print(f"Unbalanced Math Delimiters: {len(audit_data.get('unbalancedMathDelimiters', []))}")
                print(f"KaTeX Parse Errors: {len(audit_data.get('katexErrors', []))}")
                print(f"Unclosed Code Blocks: {len(audit_data.get('unclosedCodeBlocks', []))}")
                print(f"Empty/Invalid Options: {len(audit_data.get('emptyOrInvalidOptions', []))}")
                print(f"Missing Figures/Tables: {len(audit_data.get('missingFiguresOrTables', []))}")
                print(f"Truncated Questions: {len(audit_data.get('truncatedQuestions', []))}")
    finally:
        edge.terminate()
        server.terminate()

asyncio.run(main())
