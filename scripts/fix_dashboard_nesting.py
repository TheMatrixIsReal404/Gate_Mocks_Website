import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = """      <div class=\"series-card\" style=\"--series-color:#38bdf8\" onclick=\"navigate('pyq-exams')\">

        <div>

          <div class=\"series-badge\" style=\"background:rgba(56,189,248,0.15);color:#38bdf8\">🏛️ OFFICIAL PAPERS</div>

          <div class=\"series-title\">21 Full-Length PYQ Exams</div>

          <div class=\"series-sub\">Complete authentic year-wise examination papers from 2007 to 2025 in a realistic 180-minute timed environment.</div>

        
      <div class=\"series-card\" style=\"--series-color:#06b6d4\" onclick=\"navigate('mocks',{tab:'go'})\">
        <div>
          <div class=\"series-badge\" style=\"background:rgba(6,182,212,0.15);color:#06b6d4\">🌐 ALL-INDIA MOCKS</div>
          <div class=\"series-title\">27 Gate Overflow Mocks</div>
          <div class=\"series-sub\">Rigorous full-length All-India Mock Tests (2025–2026) crafted by the Gate Overflow community for peak exam calibration.</div>
        </div>
        <div class=\"series-footer\">
          <span>1,568 Qs • 27 Full Tests • 7.2/10</span>
          <span class=\"series-footer-action\">Explore →</span>
        </div>
      </div>
      <div class=\"series-card\" style=\"--series-color:#8b5cf6\" onclick=\"navigate('mocks',{tab:'made-easy'})\">
        <div>
          <div class=\"series-badge\" style=\"background:rgba(139,92,246,0.15);color:#a78bfa\">📘 ELITE COACHING</div>
          <div class=\"series-title\">21 Made Easy Full Mocks</div>
          <div class=\"series-sub\">High-resolution visual question cards, Advance & Basic Level Full Syllabus Tests, and National Mock Exams (2023–2024).</div>
        </div>
        <div class=\"series-footer\">
          <span>1,409 Qs • 21 Full Tests • 7.5/10</span>
          <span class=\"series-footer-action\">Explore →</span>
        </div>
      </div>
    </div>

        <div class=\"series-footer\">

          <span>2,224+ PYQs • 2007–2025 • Official</span>

          <span class=\"series-footer-action\">Practice →</span>

        </div>

      </div>"""

replacement = """      <div class="series-card" style="--series-color:#06b6d4" onclick="navigate('mocks',{tab:'go'})">
        <div>
          <div class="series-badge" style="background:rgba(6,182,212,0.15);color:#06b6d4">🌐 ALL-INDIA MOCKS</div>
          <div class="series-title">27 Gate Overflow Mocks</div>
          <div class="series-sub">Rigorous full-length All-India Mock Tests (2025–2026) crafted by the Gate Overflow community for peak exam calibration.</div>
        </div>
        <div class="series-footer">
          <span>1,568 Qs • 27 Full Tests • 7.2/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>

      <div class="series-card" style="--series-color:#8b5cf6" onclick="navigate('mocks',{tab:'made-easy'})">
        <div>
          <div class="series-badge" style="background:rgba(139,92,246,0.15);color:#a78bfa">📘 ELITE COACHING</div>
          <div class="series-title">21 Made Easy Full Mocks</div>
          <div class="series-sub">High-resolution visual question cards, Advance & Basic Level Full Syllabus Tests, and National Mock Exams (2023–2024).</div>
        </div>
        <div class="series-footer">
          <span>1,409 Qs • 21 Full Tests • 7.5/10</span>
          <span class="series-footer-action">Explore →</span>
        </div>
      </div>

      <div class="series-card" style="--series-color:#38bdf8" onclick="navigate('pyq-exams')">
        <div>
          <div class="series-badge" style="background:rgba(56,189,248,0.15);color:#38bdf8">🏛️ OFFICIAL PAPERS</div>
          <div class="series-title">21 Full-Length PYQ Exams</div>
          <div class="series-sub">Complete authentic year-wise examination papers from 2007 to 2025 in a realistic 180-minute timed environment.</div>
        </div>
        <div class="series-footer">
          <span>2,224+ PYQs • 2007–2025 • Official</span>
          <span class="series-footer-action">Practice →</span>
        </div>
      </div>"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully un-nested cards in app.js!")
else:
    print("Exact target string not found, trying regex...")
    pattern = re.compile(r'<div class="series-card" style="--series-color:#38bdf8" onclick="navigate\(\'pyq-exams\'\)[\s\S]*?Practice →[\s\S]*?<\/div>\s*<\/div>')
    if pattern.search(content):
        content = pattern.sub(replacement, content, count=1)
        with open('app.js', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully un-nested cards via regex!")
    else:
        print("Could not match pattern.")
