# scripts/patch_blitz.py
with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = """function startFormulaBlitz() {
  const modal = document.getElementById('flashcard-modal-card');
  if (!modal) return;
  
  blitzDeck = [...(window.FLASHCARDS || [])].sort(() => Math.random() - 0.5);"""

replacement = """function startFormulaBlitz() {
  const backdrop = document.getElementById('flashcard-modal-backdrop');
  if (backdrop) backdrop.classList.add('active');
  const modal = document.getElementById('flashcard-modal-card');
  if (!modal) return;
  
  blitzDeck = [...(FORMULA_FLASHCARDS || [])].sort(() => Math.random() - 0.5);"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Blitz patched successfully!")
else:
    print("Target not found!")
