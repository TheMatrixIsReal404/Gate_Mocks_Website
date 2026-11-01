import re
import json
import shutil
from target_mocks_dict import TARGET_MOCKS

def run():
    print("Reading app.js...")
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    shutil.copyfile('app.js', 'app.js.bak')
    print("Created app.js.bak backup.")

    # 1. Update the MOCK_TESTS definitions
    # Match the MOCK_TESTS array
    m = re.search(r'(const MOCK_TESTS = \[)([\s\S]*?)(\n\];)', content)
    if not m:
        raise Exception("MOCK_TESTS array not found in app.js")

    header, mock_block, footer = m.groups()

    # Split objects in mock_block
    # Every mock object has format:
    #   {
    #     id: '...',
    #     ...
    #   },
    def update_mock_obj(obj_str):
        id_m = re.search(r'id:\s*[\'"]([^\'"]+)[\'"]', obj_str)
        if not id_m:
            return obj_str
        mid = id_m.group(1)

        # If it's one of the 48 TARGET_MOCKS
        if mid in TARGET_MOCKS:
            info = TARGET_MOCKS[mid]
            new_lines = [
                "  {",
                f"    id: '{mid}',",
                f"    provider: '{info['provider']}',",
                f"    type: '{info['type']}',",
                f"    difficulty: '{info['difficulty']}',",
                f"    rating: {info['rating']},",
                f"    cutoff: '{info['cutoff']}',",
                f"    air100: '{info['air100']}',",
                f"    tier: '{info['tier']}',",
                f"    name: {json.dumps(info['name'])},",
                "    subject: null,",
                f"    questions: {info['questions']},",
                f"    duration: {info['duration']},",
                f"    marks: {info['marks']},",
                f"    desc: {json.dumps(info['desc'])}",
                "  }"
            ]
            return "\n".join(new_lines)
        
        # Other mocks: add provider tag and clarify descriptions if not present
        provider = None
        if mid.startswith('mock-gate-2025'):
            provider = 'Official GATE (IIT Roorkee)'
        elif mid.startswith('mock-cat1-'):
            provider = 'Curated Category 1 Mock Series'
        elif mid.startswith('mock-cat2-'):
            provider = 'Curated Category 2 Mock Series'
        elif mid.startswith('mock-easy-'):
            provider = 'Curated GATE CS Easy Series'
        elif mid.startswith('mock-med-'):
            provider = 'Curated GATE CS Standard Series'
        elif mid.startswith('mock-flm-'):
            provider = 'Curated GATE CS Compendium Series'
        elif mid.startswith('mock-full-'):
            provider = 'Curated GATE CS Simulation'

        if provider:
            # Check if provider already in obj_str
            if 'provider:' not in obj_str:
                obj_str = re.sub(r'(id:\s*[\'"][^\'"]+[\'"],)', rf"\1\n    provider: '{provider}',", obj_str, count=1)
            # Prepend provider to desc if not already there
            desc_m = re.search(r'desc:\s*([\'"])(.*?)([\'"])', obj_str)
            if desc_m and not desc_m.group(2).startswith('[Provider:'):
                old_desc = desc_m.group(2)
                new_desc = f"[Provider: {provider}] {old_desc}"
                obj_str = obj_str.replace(desc_m.group(0), f"desc: {json.dumps(new_desc)}")

        return obj_str

    # Process all objects in mock_block
    pattern = re.compile(r'(\{\s*id:\s*[\'"][^\'"]+[\'"][\s\S]*?\n  \})')
    
    replaced_count = 0
    def replacer(match):
        nonlocal replaced_count
        replaced_count += 1
        return update_mock_obj(match.group(1))

    new_mock_block = pattern.sub(replacer, mock_block)
    print(f"Updated {replaced_count} mock definitions in MOCK_TESTS.")

    content = content[:m.start()] + header + new_mock_block + footer + content[m.end():]

    # 2. Update getFilteredAndSortedMocks in app.js for comprehensive sub-series filtering
    old_subseries_block = """  // 1. Sub-series filter

  if (subSeries === 'med-30') {

    list = list.filter(m => m.id.startsWith('mock-med-'));

  } else if (subSeries === 'easy-30') {

    list = list.filter(m => m.id.startsWith('mock-easy-'));

  } else if (subSeries === 'flm-20') {

    list = list.filter(m => m.id.startsWith('mock-flm-'));

    } else if (subSeries === 'cat-10') {
    list = list.filter(m => m.id.startsWith('mock-cat'));
  } else if (subSeries === 'go-mocks') {
    list = list.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-'));
  } else if (subSeries === 'me-mocks') {
    list = list.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-'));
  } else if (subSeries === 'practice-sets') {

    list = list.filter(m => m.type === 'practice-set');

  }"""

    new_subseries_block = """  // 1. Sub-series filter
  if (subSeries === 'med-30') {
    list = list.filter(m => m.id.startsWith('mock-med-'));
  } else if (subSeries === 'easy-30') {
    list = list.filter(m => m.id.startsWith('mock-easy-'));
  } else if (subSeries === 'flm-20') {
    list = list.filter(m => m.id.startsWith('mock-flm-'));
  } else if (subSeries === 'cat-10') {
    list = list.filter(m => m.id.startsWith('mock-cat'));
  } else if (subSeries === 'go-mocks') {
    list = list.filter(m => m.id.startsWith('mock-go-') || m.id.startsWith('mock-go25-'));
  } else if (subSeries === 'go-aim') {
    list = list.filter(m => m.id.includes('-aim-'));
  } else if (subSeries === 'go-ts25-mg') {
    list = list.filter(m => m.id.startsWith('mock-go-ts25-mg'));
  } else if (subSeries === 'go25-mg') {
    list = list.filter(m => m.id.startsWith('mock-go25-mg'));
  } else if (subSeries === 'me-mocks') {
    list = list.filter(m => m.id.startsWith('mock-me24-') || m.id.startsWith('mock-me23-'));
  } else if (subSeries === 'me-2024') {
    list = list.filter(m => m.id.startsWith('mock-me24-'));
  } else if (subSeries === 'me-2023') {
    list = list.filter(m => m.id.startsWith('mock-me23-'));
  } else if (subSeries === 'me-adv') {
    list = list.filter(m => m.id.includes('-f-adv'));
  } else if (subSeries === 'me-bsc') {
    list = list.filter(m => m.id.includes('-f-bsc'));
  } else if (subSeries === 'me-aim') {
    list = list.filter(m => m.id.includes('-mock-'));
  } else if (subSeries === 'practice-sets') {
    list = list.filter(m => m.type === 'practice-set');
  }"""

    if old_subseries_block in content:
        content = content.replace(old_subseries_block, new_subseries_block)
        print("Updated sub-series filters in getFilteredAndSortedMocks.")
    else:
        # Normalize whitespace match if needed
        print("Note: Exact subseries block match check...")
        pattern_subseries = re.compile(r'// 1\. Sub-series filter[\s\S]*?list = list\.filter\(m => m\.type === \'practice-set\'\);\s*\}')
        content = pattern_subseries.sub(new_subseries_block, content, count=1)
        print("Updated sub-series filters via regex.")

    # 3. Update tabs in renderMocks to ensure clean text and clean quotes
    pattern_tabs = re.compile(r'<div class="tabs" id="mock-tabs">[\s\S]*?</div>\s*<div id="mock-tab-content">')
    new_tabs_html = """<div class="tabs" id="mock-tabs">
      <button class="tab-btn ${activeTab==='all'?'active':''}" onclick="switchMockTab('all',this)" type="button">📋 All (${fullMocks.length})</button>
      <button class="tab-btn ${activeTab==='easy'?'active':''}" onclick="switchMockTab('easy',this)" type="button">🟢 Easy (${easyCount})</button>
      <button class="tab-btn ${activeTab==='medium'?'active':''}" onclick="switchMockTab('medium',this)" type="button">🟡 Medium (${medCount})</button>
      <button class="tab-btn ${activeTab==='hard'?'active':''}" onclick="switchMockTab('hard',this)" type="button">🔴 Hard (${hardCount})</button>
      <button class="tab-btn ${activeTab==='go'?'active':''}" onclick="switchMockTab('go',this)" type="button">🌐 Gate Overflow / GO Classes (${goCount})</button>
      <button class="tab-btn ${activeTab==='made-easy'?'active':''}" onclick="switchMockTab('made-easy',this)" type="button">📘 Made Easy (${meCount})</button>
      <button class="tab-btn ${activeTab==='practice-sets'?'active':''}" onclick="switchMockTab('practice-sets',this)" type="button">📝 Practice Sets (${psetsCount})</button>
      <button class="tab-btn ${activeTab==='subwise'?'active':''}" onclick="switchMockTab('subwise',this)" type="button">📂 Subject Mocks</button>
      <button class="tab-btn ${activeTab==='history'?'active':''}" onclick="switchMockTab('history',this)" type="button">📊 My History</button>
    </div>
    <div id="mock-tab-content">"""
    
    content = pattern_tabs.sub(new_tabs_html, content, count=1)
    print("Updated mock tabs in renderMocks.")

    # 4. Update getMockTabHTML labels
    content = content.replace("buildMockSortBar(list, 'Gate Overflow All-India Mocks')", "buildMockSortBar(list, 'Gate Overflow / GO Classes All-India Mocks')")
    content = content.replace("buildMockSortBar(list, 'Made Easy Full Syllabus Mocks')", "buildMockSortBar(list, 'Made Easy Prime Full Syllabus Mocks')")

    # 5. Update buildMockSortBar to have rich pills for all tabs
    pattern_sortbar_pills = re.compile(r'let pillsHtml = \'\';[\s\S]*?return `\s*<div class="mock-controls-bar">')
    new_sortbar_pills = """let pillsHtml = '';
  if (currentTab === 'medium') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Medium (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='go-mocks'?'active':''}" onclick="setMockSubSeries('go-mocks')">🌐 Gate Overflow / GO Classes</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Made Easy Basic & Mocks</button>
        <button class="mock-subseries-pill ${subSeries==='med-30'?'active':''}" onclick="setMockSubSeries('med-30')">⚡ 30 Medium Series (30)</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 Compendium Mocks (10)</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Core CS (5)</button>
      </div>`;
  } else if (currentTab === 'hard') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Hard (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Made Easy Advance (9)</button>
        <button class="mock-subseries-pill ${subSeries==='go-mocks'?'active':''}" onclick="setMockSubSeries('go-mocks')">🌐 GO Classes & Gate Overflow (10)</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 Compendium Hard Mocks (10)</button>
      </div>`;
  } else if (currentTab === 'easy') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Easy (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Made Easy Basic (1)</button>
        <button class="mock-subseries-pill ${subSeries==='easy-30'?'active':''}" onclick="setMockSubSeries('easy-30')">🌟 30 Easy Series (30)</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Topic Sets (5)</button>
      </div>`;
  } else if (currentTab === 'go') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All GO Tests (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='go-aim'?'active':''}" onclick="setMockSubSeries('go-aim')">🎯 GO Classes AIM (11)</button>
        <button class="mock-subseries-pill ${subSeries==='go-ts25-mg'?'active':''}" onclick="setMockSubSeries('go-ts25-mg')">⚡ GO Mock GATE TS25 (10)</button>
        <button class="mock-subseries-pill ${subSeries==='go25-mg'?'active':''}" onclick="setMockSubSeries('go25-mg')">🌐 Gate Overflow TS25 (6)</button>
      </div>`;
  } else if (currentTab === 'made-easy') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All Made Easy (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='me-2024'?'active':''}" onclick="setMockSubSeries('me-2024')">📘 2024 Series (10)</button>
        <button class="mock-subseries-pill ${subSeries==='me-2023'?'active':''}" onclick="setMockSubSeries('me-2023')">📙 2023 Series (11)</button>
        <button class="mock-subseries-pill ${subSeries==='me-adv'?'active':''}" onclick="setMockSubSeries('me-adv')">🔴 Advance Level (8)</button>
        <button class="mock-subseries-pill ${subSeries==='me-bsc'?'active':''}" onclick="setMockSubSeries('me-bsc')">🟡 Basic Level (8)</button>
        <button class="mock-subseries-pill ${subSeries==='me-aim'?'active':''}" onclick="setMockSubSeries('me-aim')">🏆 National Mocks (5)</button>
      </div>`;
  } else if (currentTab === 'all') {
    pillsHtml = `
      <div class="mock-subseries-pills">
        <span style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase">Series:</span>
        <button class="mock-subseries-pill ${subSeries==='all'?'active':''}" onclick="setMockSubSeries('all')">All (${list.length})</button>
        <button class="mock-subseries-pill ${subSeries==='go-mocks'?'active':''}" onclick="setMockSubSeries('go-mocks')">🌐 Gate Overflow / GO Classes (27)</button>
        <button class="mock-subseries-pill ${subSeries==='me-mocks'?'active':''}" onclick="setMockSubSeries('me-mocks')">📘 Made Easy (21)</button>
        <button class="mock-subseries-pill ${subSeries==='med-30'?'active':''}" onclick="setMockSubSeries('med-30')">⚡ 30 Medium Series</button>
        <button class="mock-subseries-pill ${subSeries==='easy-30'?'active':''}" onclick="setMockSubSeries('easy-30')">🌟 30 Easy Series</button>
        <button class="mock-subseries-pill ${subSeries==='flm-20'?'active':''}" onclick="setMockSubSeries('flm-20')">🏆 20 Compendium Mocks</button>
        <button class="mock-subseries-pill ${subSeries==='cat-10'?'active':''}" onclick="setMockSubSeries('cat-10')">📚 Category Mocks</button>
      </div>`;
  }

  return `
    <div class="mock-controls-bar">"""
    
    content = pattern_sortbar_pills.sub(new_sortbar_pills, content, count=1)
    print("Updated buildMockSortBar pills.")

    # 6. Update buildMockGrid to include provider badge and clear layout
    pattern_mockgrid = re.compile(r'function buildMockGrid\(mocks\)\{[\s\S]*?return `<div class="mock-grid">\$\{mocks\.map\(m=>\{[\s\S]*?const badgeType = m\.type === \'practice-set\' \? \'📝 Practice Set\' : m\.type === \'full\' \? \'🏆 Full Mock\' : \'📂 Subject Mock\';[\s\S]*?return `<div class="mock-card">[\s\S]*?\}\)\.join\(\'\'\)\}<\/div>`;\s*\}')
    
    new_mockgrid = """function buildMockGrid(mocks){
  if (!mocks.length) return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No tests available for selected filter</div><div class="empty-state-sub">Try selecting "All" or another tab.</div></div>';

  return `<div class="mock-grid">${mocks.map(m=>{
    const past = state.testSessions.filter(s => s.mockId === m.id);
    const best = past.length ? Math.max(...past.map(s => s.percentage)) : null;
    const questionsCount = getMockQuestions(m.id).length || m.questions;
    const totalPages = Math.ceil(questionsCount / 20) || 1;
    const diffLabel = m.difficulty ? m.difficulty.toUpperCase() : 'MEDIUM';
    const ratingBadge = m.rating ? `<span class="q-badge" style="background:rgba(245,158,11,0.14);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);font-weight:700">⭐ ${m.rating.toFixed(1)}/10</span>` : '';
    const targetsRow = (m.cutoff && m.air100) ? `
      <div class="mock-targets-banner">
        <span>🎯 <strong>Cutoff:</strong> ${m.cutoff} M</span>
        <span>🏆 <strong>AIR &lt; 100:</strong> ${m.air100} M</span>
      </div>` : '';
    const badgeType = m.type === 'practice-set' ? '📝 Practice Set' : m.type === 'full' ? '🏆 Full Mock' : '📂 Subject Mock';

    let providerBadge = '';
    const provName = m.provider || (m.tier && m.tier.includes('Made Easy') ? 'Made Easy' : (m.tier && (m.tier.includes('Gate Overflow') || m.tier.includes('GO Classes')) ? 'GO Classes & Gate Overflow' : null));
    if (provName) {
      const isME = provName.includes('Made Easy');
      const isGO = provName.includes('Gate Overflow') || provName.includes('GO Classes');
      const isOfficial = provName.includes('Official');
      const style = isME ? 'background:rgba(59,130,246,0.12);color:#3b82f6;border:1px solid rgba(59,130,246,0.3);' :
                    isGO ? 'background:rgba(16,185,129,0.12);color:#10b981;border:1px solid rgba(16,185,129,0.3);' :
                    isOfficial ? 'background:rgba(239,68,68,0.12);color:#ef4444;border:1px solid rgba(239,68,68,0.3);' :
                    'background:rgba(100,116,139,0.12);color:#64748b;border:1px solid rgba(100,116,139,0.3);';
      const icon = isME ? '📘' : isGO ? '🌐' : isOfficial ? '🏛️' : '📚';
      providerBadge = `<span class="q-badge" style="${style}font-weight:700">${icon} ${provName}</span>`;
    }

    return `<div class="mock-card">
      <div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:6px">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
            <div class="mock-type-badge ${m.type}">${badgeType}</div>
            ${providerBadge}
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <span class="q-badge ${m.difficulty || 'medium'}">${diffLabel}</span>
            ${ratingBadge}
          </div>
        </div>
        <div class="mock-title">${m.name}</div>
        <div class="text-sm text-muted" style="margin-bottom:8px;line-height:1.5">${m.desc}</div>
        ${targetsRow}
        <div class="mock-meta">
          <div class="mock-meta-item">📚 ${questionsCount} Questions</div>
          <div class="mock-meta-item">⏱️ ${m.duration} Min</div>
          <div class="mock-meta-item">🏅 ${m.marks} Marks</div>
          ${best !== null ? `<div class="mock-meta-item" style="color:var(--green);font-weight:600">🏆 Best: ${best}%</div>` : ''}
        </div>
      </div>
      <div class="mock-card-actions">
        <button class="btn btn-secondary btn-sm" onclick="viewMockPaper('${m.id}')" title="Browse questions in sets of 20 per page with solutions" type="button">📖 Practice Paper (20/page)</button>
        <button class="btn btn-primary btn-sm" onclick="startMockTest('${m.id}')" title="Start timed exam simulation" type="button">▶ Timed Exam</button>
      </div>
      ${past.length ? `<div class="text-sm text-muted mt-2">Attempted ${past.length} time${past.length > 1 ? 's' : ''}</div>` : ''}
    </div>`;
  }).join('')}</div>`;
}"""

    content = pattern_mockgrid.sub(new_mockgrid, content, count=1)
    print("Updated buildMockGrid with provider badges.")

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully saved updated app.js!")

if __name__ == '__main__':
    run()
