# scripts/patch_index_html.py
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Topbar additions
topbar_target = """    <div class="topbar-right">
      <button class="topbar-quick-btn" id="pwa-install-btn\""""

topbar_replace = """    <div class="topbar-right">
      <div class="topbar-countdown-badge hide-xs" id="topbar-countdown" title="Countdown to GATE Examination">
        ⏳ <span id="countdown-text">Exam in 100d</span>
      </div>
      <div class="topbar-streak-badge hide-xs" id="topbar-streak" title="Daily Study Streak">
        🔥 <span id="streak-text">1d (0/20 Q)</span>
      </div>
      <button class="topbar-quick-btn" onclick="openGlobalSearch()" title="Global Search 8,168 Questions (/)" type="button">
        <span class="btn-icon">🔍</span><span class="btn-label hide-xs">Search</span>
      </button>
      <button class="topbar-quick-btn" id="pwa-install-btn\""""

if topbar_target in content:
    content = content.replace(topbar_target, topbar_replace, 1)
    print("Topbar updated successfully!")
else:
    print("Topbar target not found!")

# 2. Flashcard modal header blitz button
fc_target = """    <div class="flashcard-modal-header">
      <div class="flashcard-modal-title">📇 GATE Formula Flashcards <span style="font-size:12px;color:var(--text-muted);font-weight:normal">(Spaced Repetition)</span></div>
      <button class="shortcuts-close-btn" onclick="toggleFormulaFlashcards(false)" type="button">✕</button>
    </div>"""

fc_replace = """    <div class="flashcard-modal-header">
      <div class="flashcard-modal-title">📇 GATE Formula Flashcards <span style="font-size:12px;color:var(--text-muted);font-weight:normal">(Spaced Repetition)</span></div>
      <div style="display:flex;align-items:center;gap:8px">
        <button class="btn btn-warning btn-sm" onclick="startFormulaBlitz()" type="button" style="padding:2px 10px;font-size:11px;font-weight:700">⚡ 60s Blitz</button>
        <button class="shortcuts-close-btn" onclick="toggleFormulaFlashcards(false)" type="button">✕</button>
      </div>
    </div>"""

if fc_target in content:
    content = content.replace(fc_target, fc_replace, 1)
    print("Flashcard header updated successfully!")
else:
    print("Flashcard header target not found!")

# 3. Add Global Search Modal & Worksheet container
modal_target = """<!-- ─── SERVICE WORKER REGISTRATION ─── -->"""
modal_addition = """<!-- ─── UNIVERSAL GLOBAL QUESTION SEARCH MODAL (8,168 Qs) ─── -->
<div class="global-search-backdrop" id="global-search-backdrop" onclick="closeGlobalSearch()"></div>
<div class="global-search-modal" id="global-search-modal">
  <div class="global-search-header">
    <span class="search-input-icon">🔍</span>
    <input type="text" id="global-search-input" placeholder="Search 8,168 questions by topic, algorithm, theorem, keyword (Press /)..." oninput="handleGlobalSearchInput(this.value)" autocomplete="off" />
    <button class="shortcuts-close-btn" onclick="closeGlobalSearch()" type="button">✕</button>
  </div>
  <div class="global-search-subbar">
    <span id="global-search-count">8,168 questions indexed</span>
    <div class="global-search-filters">
      <button class="chip active" onclick="setGlobalSearchFilter('all', this)" type="button">All</button>
      <button class="chip" onclick="setGlobalSearchFilter('mcq', this)" type="button">MCQ</button>
      <button class="chip" onclick="setGlobalSearchFilter('msq', this)" type="button">MSQ</button>
      <button class="chip" onclick="setGlobalSearchFilter('nat', this)" type="button">NAT</button>
    </div>
  </div>
  <div class="global-search-results" id="global-search-results">
    <div style="padding:32px 16px;text-align:center;color:var(--text-muted);font-size:13px">
      Search 8,168 questions by theorem, concept, formula, or code snippet (e.g. <em>Dijkstra, LRU, B+ Tree, Pipelining, Master Theorem</em>)
    </div>
  </div>
</div>

<!-- ─── PRINTABLE 2-COLUMN WORKSHEET CONTAINER ─── -->
<div id="printable-worksheet-container" class="printable-worksheet-container"></div>

<!-- ─── SERVICE WORKER REGISTRATION ─── -->"""

if modal_target in content:
    content = content.replace(modal_target, modal_addition, 1)
    print("Modals added successfully!")
else:
    print("Modal target not found!")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html patched successfully!")
