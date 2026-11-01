import re
import json
import shutil

def run():
    print("Reading app.js...")
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    shutil.copyfile('app.js', 'app.js.bak2')
    print("Created backup app.js.bak2")

    # Match MOCK_TESTS
    m = re.search(r'(const MOCK_TESTS = \[)([\s\S]*?)(\n\];)', content)
    if not m:
        raise Exception("MOCK_TESTS not found")

    header, mock_block, footer = m.groups()

    # Track index counters per series
    counters = {
        'easy-30': 0,
        'med-30': 0,
        'flm-20': 0,
        'full-5': 0,
        'cat': 0,
        'gate-2025': 0,
        'go': 0,
        'me': 0,
        'practice': 0
    }

    # Define a function to process each mock object
    def process_mock(obj_str):
        id_m = re.search(r'id:\s*[\'"]([^\'"]+)[\'"]', obj_str)
        if not id_m:
            return obj_str
        mid = id_m.group(1)

        type_m = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', obj_str)
        mtype = type_m.group(1) if type_m else 'full'

        if mtype == 'subwise':
            return obj_str

        # Determine series group and index
        num = None
        series_name = ''
        
        if mid.startswith('mock-easy-'):
            counters['easy-30'] += 1
            num = counters['easy-30']
            new_name = f"Mock {num}"
            coaching_desc = f"[Provider: Curated GATE CS Easy Series] Foundational Easy Mock Exam #{num:02d}. Difficulty: Easy (Rating: 3.5/10). Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-med-'):
            counters['med-30'] += 1
            num = counters['med-30']
            new_name = f"Mock {num}"
            coaching_desc = f"[Provider: Curated GATE CS Standard Series] Standard GATE Medium Mock Exam #{num:02d}. Difficulty: Medium (Rating: 4.8/10). Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-flm-'):
            counters['flm-20'] += 1
            num = counters['flm-20']
            new_name = f"Mock {num}"
            coaching_desc = f"[Provider: Curated GATE CS Compendium Series] Compendium Full Mock Exam #{num:02d}. Difficulty: Standard/Advanced GATE (Rating: 5.5/10). Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-full-'):
            counters['full-5'] += 1
            num = counters['full-5']
            new_name = f"Mock {num}"
            coaching_desc = f"[Provider: Curated Full GATE Simulation] Full-Length Mock Exam #{num:02d}. Comprehensive GATE CSE standard simulation across all subjects (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-cat'):
            counters['cat'] += 1
            num = counters['cat']
            new_name = f"Mock {num}"
            coaching_desc = f"[Provider: Curated Category Mock Series] Category Core CS Full Mock Exam #{num:02d}. High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-gate-2025'):
            counters['gate-2025'] += 1
            num = counters['gate-2025']
            new_name = f"Mock {num}"
            set_num = 1 if 's1' in mid else 2
            coaching_desc = f"[Provider: Official GATE Exam (IIT Roorkee)] Official GATE 2025 Computer Science Examination (Set {set_num}). The authentic 65-question computer-based exam paper (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-go-') or mid.startswith('mock-go25-'):
            counters['go'] += 1
            num = counters['go']
            new_name = f"Mock {num}"
            
            # Determine GO specifics
            if 'aim' in mid:
                aim_num = re.search(r'aim-([0-9a-z\-]+)', mid).group(1).upper()
                coaching_desc = f"[Coaching: GO Classes & Gate Overflow] Official All-India Mock (AIM) Test {aim_num}. Full-length exam created jointly by GO Classes & Gate Overflow replicating official GATE pattern with in-depth solutions (65 Questions • 180 Mins • 100 Marks)."
            elif 'ts25-mg' in mid:
                mg_num = mid.split('mg-')[1]
                coaching_desc = f"[Coaching: GO Classes & Gate Overflow] Official GO Classes Mock GATE Exam #{mg_num}. Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions • 180 Mins • 100 Marks)."
            else:
                mg_num = mid.split('mg-')[1]
                coaching_desc = f"[Coaching: Gate Overflow] Official Gate Overflow Test Series Mock GATE #{mg_num}. Full-syllabus GATE CS mock paper created by Gate Overflow team with verified community solutions (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-me24-') or mid.startswith('mock-me23-'):
            counters['me'] += 1
            num = counters['me']
            new_name = f"Mock {num}"

            # Determine Made Easy specifics
            year = "2024" if "me24" in mid else "2023"
            if "-adv" in mid:
                adv_num = mid[-1]
                coaching_desc = f"[Coaching: Made Easy | Made Easy Prime Test Series] Made Easy {year} Advance Level Full Syllabus Test #{adv_num}. High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions • 180 Mins • 100 Marks)."
            elif "-bsc" in mid:
                bsc_num = mid[-1]
                coaching_desc = f"[Coaching: Made Easy | Made Easy Prime Test Series] Made Easy {year} Basic Level Full Syllabus Test #{bsc_num}. Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions • 180 Mins • 100 Marks)."
            else:
                mock_num = mid[-1]
                coaching_desc = f"[Coaching: Made Easy | Made Easy Prime Test Series] Made Easy {year} Nationwide All-India GATE Mock Test #{mock_num}. Authentic nationwide mock exam simulating official GATE testing conditions across the complete syllabus (65 Questions • 180 Mins • 100 Marks)."
        elif mtype == 'practice-set':
            counters['practice'] += 1
            num = counters['practice']
            new_name = f"Practice Set {num}"
            coaching_desc = None
        else:
            return obj_str

        # Replace name
        obj_str = re.sub(r'name:\s*[\'"][^\'"]+[\'"]', lambda m: f"name: {json.dumps(new_name)}", obj_str, count=1)
        
        # Replace or update desc
        if coaching_desc:
            # Preserve difficulty and rating info in desc
            diff_m = re.search(r'difficulty:\s*[\'"]([^\'"]+)[\'"]', obj_str)
            rate_m = re.search(r'rating:\s*([0-9.]+)', obj_str)
            d_val = diff_m.group(1).capitalize() if diff_m else 'Medium'
            r_val = rate_m.group(1) if rate_m else '6.0'

            # Append difficulty info to coaching_desc
            enhanced_desc = f"{coaching_desc} Difficulty: {d_val} (Rating: {r_val}/10)."
            replacement_val = f"desc: {json.dumps(enhanced_desc)}"
            obj_str = re.sub(r'desc:\s*[\'"][^\'"]*?[\'"]', lambda m: replacement_val, obj_str, count=1)

        return obj_str

    # Find and update every object in mock_block
    pattern = re.compile(r'(\{\s*id:\s*[\'"][^\'"]+[\'"][\s\S]*?\n  \})')
    new_mock_block = pattern.sub(lambda match: process_mock(match.group(1)), mock_block)

    print(f"Counters: {counters}")

    content = content[:m.start()] + header + new_mock_block + footer + content[m.end():]

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

    print("app.js updated successfully with uniform titles (Mock 1, Mock 2, ...), difficulty tags, and coaching descriptions!")

if __name__ == '__main__':
    run()
