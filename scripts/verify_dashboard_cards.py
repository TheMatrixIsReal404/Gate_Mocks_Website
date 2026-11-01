import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'<div class="dashboard-series-grid">([\s\S]*?)<!-- ── QUESTION BANK DISTRIBUTION ── -->', content)
assert m, "dashboard-series-grid not found"
grid_html = m.group(1)

# Find all direct series-cards
cards = re.findall(r'<div class="series-card"[^>]*>[\s\S]*?<div class="series-title">([^<]+)</div>', grid_html)

print(f"Total series cards directly in grid: {len(cards)}")
for i, title in enumerate(cards, 1):
    print(f"  {i}. {title}")
