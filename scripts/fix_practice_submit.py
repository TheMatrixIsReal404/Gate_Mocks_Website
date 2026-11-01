# scripts/fix_practice_submit.py
with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

bad_block = """  const expBox = document.getElementById('explanation-box');
  if (expBox) {
    expBox.innerHTML = 
      
      
      
      
      
    ;
    expBox.classList.add('show');
    renderMath(expBox);
  }"""

fixed_block = """  const expBox = document.getElementById('explanation-box');
  if (expBox) {
    expBox.innerHTML = `
      ${buildConfidenceSelectorHTML(q.id)}
      ${buildExpectedValueCardHTML(q)}
      ${q.type === 'nat' ? buildNatToleranceHTML(q) : ''}
      ${buildMultiMethodExplanationHTML(q)}
      ${buildStudentShortcutNoteHTML(q.id)}
    `;
    expBox.classList.add('show');
    renderMath(expBox);
  }"""

if bad_block in content:
    content = content.replace(bad_block, fixed_block, 1)
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed practice submit syntax error successfully!")
else:
    print("bad_block not found!")
