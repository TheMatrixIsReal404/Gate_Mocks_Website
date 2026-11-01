# scripts/append_new_styles.py
with open('style.css', 'r', encoding='utf-8') as f:
    css = f.read()

new_styles = """
/* ─── EXAM COUNTDOWN & DAILY STUDY STREAK (TOPBAR) ─── */
.topbar-countdown-badge, .topbar-streak-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  user-select: none;
}
.topbar-countdown-badge {
  color: #38bdf8;
  border-color: rgba(56, 189, 248, 0.3);
  background: rgba(56, 189, 248, 0.08);
}
.topbar-streak-badge {
  color: #f97316;
  border-color: rgba(249, 115, 22, 0.3);
  background: rgba(249, 115, 22, 0.08);
}

/* ─── UNIVERSAL GLOBAL QUESTION SEARCH (8,168 QUESTIONS) ─── */
.global-search-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  z-index: 1050;
  display: none;
}
.global-search-backdrop.active {
  display: block;
}
.global-search-modal {
  position: fixed;
  top: 10%;
  left: 50%;
  transform: translateX(-50%) scale(0.96);
  width: min(720px, 94vw);
  max-height: 80vh;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
  z-index: 1051;
  display: none;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
  opacity: 0;
}
.global-search-modal.active {
  display: flex;
  transform: translateX(-50%) scale(1);
  opacity: 1;
}
.global-search-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
}
.search-input-icon {
  font-size: 18px;
  color: var(--text-muted);
}
#global-search-input {
  flex: 1;
  background: transparent;
  border: none;
  font-size: 16px;
  color: var(--text-primary);
  outline: none;
}
#global-search-input::placeholder {
  color: var(--text-muted);
}
.global-search-subbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  background: rgba(0, 0, 0, 0.15);
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-muted);
}
.global-search-filters {
  display: flex;
  gap: 6px;
}
.global-search-results {
  flex: 1;
  overflow-y: auto;
  max-height: 60vh;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.search-result-item {
  padding: 12px 14px;
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.15s ease;
}
.search-result-item:hover, .search-result-item.selected {
  border-color: var(--accent);
  background: rgba(108, 99, 255, 0.08);
}
.search-result-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 11px;
}
.search-result-snippet {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.search-highlight {
  background: rgba(245, 158, 11, 0.25);
  color: #fbbf24;
  font-weight: 700;
  border-radius: 2px;
  padding: 0 2px;
}

/* ─── 10-SPOKE SUBJECT MASTERY RADAR CHART ─── */
.radar-chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 28px;
}
.radar-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 16px;
}
.radar-svg-wrap {
  width: 100%;
  max-width: 440px;
}
.radar-svg {
  width: 100%;
  height: auto;
  overflow: visible;
}
.radar-grid-ring {
  fill: none;
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 1;
}
.radar-spoke {
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 1;
}
.radar-polygon {
  fill: rgba(108, 99, 255, 0.25);
  stroke: var(--accent);
  stroke-width: 2.5;
  transition: all 0.3s ease;
}
.radar-point {
  fill: var(--accent);
  stroke: #fff;
  stroke-width: 1.5;
  cursor: pointer;
  transition: r 0.2s;
}
.radar-point:hover {
  r: 5;
  fill: #38bdf8;
}
.radar-label {
  font-size: 10px;
  fill: var(--text-secondary);
  text-anchor: middle;
  font-weight: 600;
}
.radar-legend-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 240px;
}
.radar-legend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  font-size: 12px;
}

/* ─── EXPECTED VALUE (E) RISK ANALYZER & CONFIDENCE MARKING ─── */
.confidence-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}
.conf-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
}
.conf-btn-group {
  display: flex;
  gap: 6px;
}
.conf-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.conf-btn:hover {
  border-color: var(--accent);
  color: var(--text-primary);
}
.conf-btn.active.conf-high {
  background: rgba(34, 197, 94, 0.2);
  border-color: #22c55e;
  color: #4ade80;
}
.conf-btn.active.conf-educated {
  background: rgba(234, 179, 8, 0.2);
  border-color: #eab308;
  color: #facc15;
}
.conf-btn.active.conf-blind {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  color: #f87171;
}

.ev-card {
  margin: 12px 0;
  padding: 12px 14px;
  background: rgba(108, 99, 255, 0.05);
  border: 1px solid rgba(108, 99, 255, 0.2);
  border-radius: var(--radius);
}
.ev-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.ev-title {
  font-size: 12px;
  font-weight: 800;
  color: var(--accent);
  display: flex;
  align-items: center;
  gap: 6px;
}
.ev-matrix-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.ev-stat-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px;
  text-align: center;
}
.ev-stat-val {
  font-size: 15px;
  font-weight: 800;
}
.ev-stat-lbl {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* ─── 60-SECOND FORMULA BLITZ MODE ─── */
.blitz-view-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  text-align: center;
}
.blitz-timer-bar {
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}
.blitz-timer-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #eab308, #ef4444);
  width: 100%;
  transition: width 1s linear;
}
.blitz-score-badge {
  font-size: 28px;
  font-weight: 900;
  color: #eab308;
}
.blitz-card-topic {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.blitz-card-formula {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  line-height: 1.5;
}
.blitz-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* ─── NAT PRECISION & ROUNDING TRAP INSPECTOR ─── */
.nat-tolerance-box {
  margin: 10px 0;
  padding: 10px 12px;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.nat-tolerance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  color: #38bdf8;
}
.nat-trap-alert {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.4;
  background: rgba(0, 0, 0, 0.2);
  padding: 6px 8px;
  border-radius: 4px;
}

/* ─── 2-COLUMN PRINTABLE PRACTICE WORKSHEET ─── */
.printable-worksheet-container {
  display: none;
}
@media print {
  body * {
    visibility: hidden;
  }
  .printable-worksheet-container, .printable-worksheet-container * {
    visibility: visible;
  }
  .printable-worksheet-container {
    display: block !important;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    background: #fff !important;
    color: #111 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 20px;
  }
  .ws-header {
    border-bottom: 2px solid #000;
    padding-bottom: 12px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .ws-title {
    font-size: 20px;
    font-weight: 800;
    color: #000;
  }
  .ws-meta {
    font-size: 11px;
    color: #444;
  }
  .ws-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    column-rule: 1px solid #ccc;
  }
  .ws-q-item {
    break-inside: avoid;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px dashed #ddd;
    font-size: 12px;
    line-height: 1.5;
  }
  .ws-q-num {
    font-weight: 800;
    margin-bottom: 4px;
  }
  .ws-options {
    margin-top: 6px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .ws-opt {
    display: flex;
    align-items: baseline;
    gap: 6px;
  }
  .ws-box {
    display: inline-block;
    width: 10px;
    height: 10px;
    border: 1px solid #666;
  }
  .ws-page-break {
    page-break-before: always;
  }
  .ws-key-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 14px;
    font-size: 11px;
  }
  .ws-key-table th, .ws-key-table td {
    border: 1px solid #999;
    padding: 4px 8px;
    text-align: left;
  }
}
"""

with open('style.css', 'a', encoding='utf-8') as f:
    f.write(new_styles)

print("style.css appended successfully!")
