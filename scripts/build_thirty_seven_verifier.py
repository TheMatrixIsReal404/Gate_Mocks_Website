# scripts/build_thirty_seven_verifier.py
with open('scripts/verify_all_twenty_nine_features.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace ports to avoid clash
code = code.replace("'8122'", "'8133'")
code = code.replace("'9252'", "'9263'")
code = code.replace('localhost:8122', 'localhost:8133')
code = code.replace('127.0.0.1:9252', '127.0.0.1:9263')

target_end = """                results['29_multi_method_and_shortcut_notes'] = bool(
                    multi_data.get('hasMethod1') and
                    multi_data.get('hasMethod2') and
                    multi_data.get('hasNoteHtml') and
                    multi_data.get('isSaved')
                )"""

new_checks = """                results['29_multi_method_and_shortcut_notes'] = bool(
                    multi_data.get('hasMethod1') and
                    multi_data.get('hasMethod2') and
                    multi_data.get('hasNoteHtml') and
                    multi_data.get('isSaved')
                )

                # 30. Official Syllabus Guide (IIT Madras Standards)
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('subjects')"})
                await asyncio.sleep(0.5)

                r_syl = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        const card = document.querySelector('.syllabus-guide-card');
                        const secCards = document.querySelectorAll('.syllabus-sec-card');
                        window.toggleSyllabusGuide();
                        const isHidden = document.getElementById('syllabus-guide-body')?.style.display === 'none';
                        window.toggleSyllabusGuide();
                        return JSON.stringify({
                            hasCard: !!card,
                            secCardCount: secCards.length,
                            isHidden
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                syl_data = json.loads(r_syl.get('result', {}).get('value', '{}'))
                results['30_official_syllabus_guide_iit_madras'] = bool(
                    syl_data.get('hasCard') and
                    syl_data.get('secCardCount') == 11 and
                    syl_data.get('isHidden')
                )

                # 31. Universal Global Search across 8,168 Questions
                r_search = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        window.openGlobalSearch();
                        const modal = document.getElementById('global-search-modal');
                        const isModalActive = modal && modal.classList.contains('active');
                        window.executeGlobalSearch('Dijkstra');
                        const resultsItems = document.querySelectorAll('.search-result-item');
                        window.closeGlobalSearch();
                        return JSON.stringify({
                            isModalActive,
                            resultsCount: resultsItems.length
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                s_data = json.loads(r_search.get('result', {}).get('value', '{}'))
                results['31_universal_global_search_8168_qs'] = bool(
                    s_data.get('isModalActive') and
                    s_data.get('resultsCount') > 0
                )

                # 32. Exam Countdown & Daily Study Streak Engine
                r_streak = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        const cd = window.getExamCountdownData();
                        const cdText = document.getElementById('countdown-text')?.textContent || '';
                        window.recordDailyAttemptForStreak();
                        const streakText = document.getElementById('streak-text')?.textContent || '';
                        return JSON.stringify({
                            hasDays: cd && cd.days > 0,
                            cdTextMatches: cdText.includes('GATE'),
                            streakTextHasQ: streakText.includes('Q')
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                st_data = json.loads(r_streak.get('result', {}).get('value', '{}'))
                results['32_exam_countdown_and_daily_streak'] = bool(
                    st_data.get('hasDays') and
                    st_data.get('cdTextMatches') and
                    st_data.get('streakTextHasQ')
                )

                # 33. 10-Spoke Subject Mastery Radar Chart
                await cdp_call(ws, "Runtime.evaluate", {"expression": "window.navigate('performance')"})
                await asyncio.sleep(0.5)

                r_radar = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        const card = document.querySelector('.radar-chart-card');
                        const poly = document.querySelector('.radar-polygon');
                        const pts = document.querySelectorAll('.radar-point');
                        const spokes = document.querySelectorAll('.radar-spoke');
                        return JSON.stringify({
                            hasCard: !!card,
                            hasPoly: !!poly,
                            pointsCount: pts.length,
                            spokesCount: spokes.length
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                rd_data = json.loads(r_radar.get('result', {}).get('value', '{}'))
                results['33_mastery_radar_chart_10_spokes'] = bool(
                    rd_data.get('hasCard') and
                    rd_data.get('hasPoly') and
                    rd_data.get('pointsCount') == 10 and
                    rd_data.get('spokesCount') == 10
                )

                # 34. Expected Value (E) Risk Analyzer & Confidence Selectors
                r_ev = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        const mcq = window.state.questions.find(q => q.type === 'mcq' && q.marks === 1);
                        const evAnalysis = window.getExpectedValueAnalysis(mcq);
                        const evHtml = window.buildExpectedValueCardHTML(mcq);
                        window.setQuestionConfidence(mcq.id, 'high');
                        const isConfidenceSaved = window.state.confidenceTags[mcq.id] === 'high';
                        return JSON.stringify({
                            ev0: evAnalysis.ev0,
                            ev2: evAnalysis.ev2,
                            hasEvHtml: evHtml.includes('Expected Value'),
                            isConfidenceSaved
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                ev_data = json.loads(r_ev.get('result', {}).get('value', '{}'))
                results['34_ev_risk_analyzer_and_confidence'] = bool(
                    ev_data.get('ev0') == 0.0 and
                    ev_data.get('ev2') == 0.33 and
                    ev_data.get('hasEvHtml') and
                    ev_data.get('isConfidenceSaved')
                )

                # 35. 60-Second Formula Blitz Mode
                r_blitz = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        window.startFormulaBlitz();
                        const timeEl = document.getElementById('blitz-time-text');
                        window.advanceBlitzCard(true);
                        const score = parseInt(document.querySelector('.blitz-view-container')?.textContent.match(/Score:\\\\s*(\\\\d+)/)?.[1] || '0');
                        window.stopFormulaBlitz();
                        return JSON.stringify({
                            hasTime: !!timeEl,
                            scoreIncreased: score >= 10
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                blitz_data = json.loads(r_blitz.get('result', {}).get('value', '{}'))
                results['35_60s_formula_blitz_mode'] = bool(
                    blitz_data.get('hasTime') and
                    blitz_data.get('scoreIncreased')
                )

                # 36. NAT Precision & Rounding Trap Inspector
                r_nat = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        const natQ = window.state.questions.find(q => q.type === 'nat');
                        const natHtml = window.buildNatToleranceHTML(natQ);
                        return JSON.stringify({
                            hasBounds: natHtml.includes('Numerical Acceptance Bounds'),
                            hasTrapAdvisory: natHtml.includes('Rounding Trap Advisory')
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                nat_data = json.loads(r_nat.get('result', {}).get('value', '{}'))
                results['36_nat_precision_rounding_inspector'] = bool(
                    nat_data.get('hasBounds') and
                    nat_data.get('hasTrapAdvisory')
                )

                # 37. 2-Column Printable Practice Worksheet Generator
                r_ws = await cdp_call(ws, "Runtime.evaluate", {
                    "expression": \"\"\"(() => {
                        window.generatePrintableWorksheet(window.state.questions.slice(0, 4), 'Audit Verification Worksheet');
                        const container = document.getElementById('printable-worksheet-container');
                        const qItems = container.querySelectorAll('.ws-q-item');
                        const keyRows = container.querySelectorAll('.ws-key-table tbody tr');
                        return JSON.stringify({
                            qCount: qItems.length,
                            keyCount: keyRows.length
                        });
                    })()\"\"\",
                    "returnByValue": True
                })
                ws_data = json.loads(r_ws.get('result', {}).get('value', '{}'))
                results['37_printable_2_column_pdf_worksheet'] = bool(
                    ws_data.get('qCount') == 4 and
                    ws_data.get('keyCount') == 4
                )"""

code = code.replace(target_end, new_checks, 1)

code = code.replace("COMPLETE 29-FEATURE FULL-SITE VERIFICATION AUDIT MATRIX:", "COMPLETE 37-FEATURE FULL-SITE VERIFICATION AUDIT MATRIX:")
code = code.replace(">>> ALL 29 VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<", ">>> ALL 37 VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<")

with open('scripts/verify_all_thirty_seven_features.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Generated scripts/verify_all_thirty_seven_features.py successfully!")
