# -*- coding: utf-8 -*-
import subprocess
import time
import json
import urllib.request
import asyncio
import aiohttp
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

_req_id = 0

async def cdp_call(ws, method, params=None):
    global _req_id
    _req_id += 1
    my_id = _req_id
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
        '-m', 'http.server', '8097'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1.5)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    edge_proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--remote-debugging-port=9232',
        'http://localhost:8097/index.html'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(3.0)

    try:
        with urllib.request.urlopen('http://127.0.0.1:9232/json') as r:
            tabs = json.loads(r.read().decode())
        target = [t for t in tabs if 'localhost:8097' in t.get('url', '')][0]
        ws_url = target['webSocketDebuggerUrl']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                # 1. Guest login & check questions
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.continueAsGuest();"})
                await asyncio.sleep(1.0)

                # 2. Open practice mode for a question
                r_practice = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.navigate('practice');
                        const firstQ = state.questions[0];
                        window.openSingleQuestion(firstQ.id);
                        const hintBox = document.getElementById('practice-hint-box');
                        const hasHintBtn = !!document.querySelector('button[onclick*="togglePracticeHint"]');
                        const hasFlashcardsBtn = !!document.querySelector('button[onclick*="openFormulaFlashcardsModal"]');
                        return JSON.stringify({
                            hasHintBox: !!hintBox,
                            hasHintBtn,
                            hasFlashcardsBtn
                        });
                    })()""",
                    "returnByValue": True
                })
                p_data = json.loads(r_practice.get('result', {}).get('value', '{}'))
                print("1. Practice Hint UI presence:", p_data)
                assert p_data.get('hasHintBox'), "Missing practice-hint-box"
                assert p_data.get('hasHintBtn'), "Missing togglePracticeHint button"
                assert p_data.get('hasFlashcardsBtn'), "Missing openFormulaFlashcardsModal button"

                # 3. Toggle Practice Hint Box
                r_toggle_hint = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.togglePracticeHint(true);
                        const box = document.getElementById('practice-hint-box');
                        const isVisible = box && box.style.display !== 'none';
                        const text = box ? box.textContent : '';
                        return JSON.stringify({
                            isVisible,
                            hasFormulaText: text.includes('Formula') || text.includes('Hint')
                        });
                    })()""",
                    "returnByValue": True
                })
                hint_data = json.loads(r_toggle_hint.get('result', {}).get('value', '{}'))
                print("2. Toggle Practice Hint:", hint_data)
                assert hint_data.get('isVisible'), "Practice hint not visible after toggle"

                # 4. Open Formula Flashcards Modal
                r_fc_modal = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.openFormulaFlashcardsModal('card-masters-theorem');
                        const modal = document.getElementById('flashcard-modal-backdrop');
                        const isActive = modal && modal.classList.contains('active');
                        const frontText = document.getElementById('fc-face-front')?.textContent || '';
                        return JSON.stringify({
                            isActive,
                            hasMasters: frontText.includes("Master's Theorem")
                        });
                    })()""",
                    "returnByValue": True
                })
                modal_data = json.loads(r_fc_modal.get('result', {}).get('value', '{}'))
                print("3. Open Flashcards Modal (Master's Theorem):", modal_data)
                assert modal_data.get('isActive'), "Flashcard modal not active"
                assert modal_data.get('hasMasters'), "Modal not opened to Master's Theorem"

                # 5. Flip Card (3D CSS flip)
                r_flip = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.flipActiveFlashcard();
                        const inner = document.getElementById('active-flashcard-inner');
                        const isFlipped = inner && inner.classList.contains('is-flipped');
                        const backText = document.getElementById('fc-face-back')?.textContent || '';
                        return JSON.stringify({
                            isFlipped,
                            hasCase1: backText.includes('Case 1') || backText.includes('Standard Form')
                        });
                    })()""",
                    "returnByValue": True
                })
                flip_data = json.loads(r_flip.get('result', {}).get('value', '{}'))
                print("4. Flip Card (Back face):", flip_data)
                assert flip_data.get('isFlipped'), "Card not flipped"

                # 6. Rate Card (SRS)
                r_rate = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        window.rateFlashcard('mastered');
                        const stats = state.flashcardStats['card-masters-theorem'];
                        const storage = localStorage.getItem('gate_formula_flashcards_srs');
                        return JSON.stringify({
                            srsStatus: stats?.status,
                            reps: stats?.reps,
                            inStorage: !!storage && storage.includes('mastered')
                        });
                    })()""",
                    "returnByValue": True
                })
                rate_data = json.loads(r_rate.get('result', {}).get('value', '{}'))
                print("5. SRS Rating (Mastered):", rate_data)
                assert rate_data.get('srsStatus') == 'mastered', "SRS status not mastered"
                assert rate_data.get('inStorage'), "SRS status not in localStorage"

                # 7. Verify all 4 required high-frequency formulas in FORMULA_FLASHCARDS
                r_deck = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": """(() => {
                        const ids = FORMULA_FLASHCARDS.map(c => c.id);
                        return JSON.stringify({
                            hasMasters: ids.includes('card-masters-theorem'),
                            hasGraph: ids.includes('card-graph-invariants'),
                            hasCPU: ids.includes('card-cpu-scheduling'),
                            hasSubnet: ids.includes('card-subnetting-rules'),
                            totalCards: FORMULA_FLASHCARDS.length
                        });
                    })()""",
                    "returnByValue": True
                })
                deck_data = json.loads(r_deck.get('result', {}).get('value', '{}'))
                print("6. Formula Flashcards Deck completeness:", deck_data)
                assert deck_data.get('hasMasters'), "Missing Master's Theorem card"
                assert deck_data.get('hasGraph'), "Missing Graph Invariants card"
                assert deck_data.get('hasCPU'), "Missing CPU Scheduling card"
                assert deck_data.get('hasSubnet'), "Missing Subnetting card"
                assert deck_data.get('totalCards') >= 9, f"Expected at least 9 cards, got {deck_data.get('totalCards')}"

                # 8. Close modal
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.toggleFormulaFlashcards(false);"})
                print("\n>>> ALL FORMULA FLASHCARD (SPACED REPETITION) TESTS PASSED 100%! <<<")
    finally:
        edge_proc.kill()
        server_proc.kill()

if __name__ == '__main__':
    asyncio.run(main())
