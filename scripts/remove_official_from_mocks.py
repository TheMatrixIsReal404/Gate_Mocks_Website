import re
import json
import shutil

# 150 mocks without the 2 official gate papers
ORDERED_IDS = [
    # ── 1. Made Easy 2024 & 2023 Full Syllabus Mocks (Mock 1 to Mock 21) ──
    'mock-me24-f-adv1',
    'mock-me24-f-adv2',
    'mock-me24-f-adv3',
    'mock-me24-f-adv4',
    'mock-me24-f-bsc1',
    'mock-me24-f-bsc2',
    'mock-me24-f-bsc3',
    'mock-me24-f-bsc4',
    'mock-me24-mock-3',
    'mock-me24-mock-4',
    'mock-me23-f-adv1',
    'mock-me23-f-adv2',
    'mock-me23-f-adv3',
    'mock-me23-f-adv4',
    'mock-me23-f-bsc1',
    'mock-me23-f-bsc2',
    'mock-me23-f-bsc3',
    'mock-me23-f-bsc4',
    'mock-me23-mock-2',
    'mock-me23-mock-3',
    'mock-me23-mock-4',

    # ── 2. Gate Overflow & GO Classes Mocks (Mock 22 to Mock 48) ──
    'mock-go-ts25-aim-02',
    'mock-go-ts25-aim-03',
    'mock-go-ts25-aim-04',
    'mock-go-ts25-aim-05',
    'mock-go-ts26-aim-01',
    'mock-go-ts26-aim-02',
    'mock-go-ts26-aim-03',
    'mock-go-ts26-aim-04',
    'mock-go-ts26-aim-05-s1',
    'mock-go-ts26-aim-05-s2',
    'mock-go-ts26-aim-06',
    'mock-go-ts25-mg-01',
    'mock-go-ts25-mg-02',
    'mock-go-ts25-mg-03',
    'mock-go-ts25-mg-04',
    'mock-go-ts25-mg-05',
    'mock-go-ts25-mg-06',
    'mock-go-ts25-mg-07',
    'mock-go-ts25-mg-08',
    'mock-go-ts25-mg-09',
    'mock-go-ts25-mg-14',
    'mock-go25-mg-01',
    'mock-go25-mg-02',
    'mock-go25-mg-03',
    'mock-go25-mg-04',
    'mock-go25-mg-05',
    'mock-go25-mg-06',

    # ── 3. Compendium FLM Series (Mock 49 to Mock 68) ──
    'mock-flm-01',
    'mock-flm-02',
    'mock-flm-03',
    'mock-flm-04',
    'mock-flm-05',
    'mock-flm-06',
    'mock-flm-07',
    'mock-flm-08',
    'mock-flm-09',
    'mock-flm-10',
    'mock-flm-11',
    'mock-flm-12',
    'mock-flm-13',
    'mock-flm-14',
    'mock-flm-15',
    'mock-flm-16',
    'mock-flm-17',
    'mock-flm-18',
    'mock-flm-19',
    'mock-flm-20',

    # ── 4. Standard Full Simulation & Masters (Mock 69 to Mock 73) ──
    'mock-full-easy',
    'mock-full-med',
    'mock-full-hard',
    'mock-full-001',
    'mock-full-002',

    # ── 5. Category 1 & Category 2 Core CS (Mock 74 to Mock 83) ──
    'mock-cat1-set1',
    'mock-cat1-set2',
    'mock-cat1-set3',
    'mock-cat1-set4',
    'mock-cat1-set5',
    'mock-cat2-set1',
    'mock-cat2-set2',
    'mock-cat2-set3',
    'mock-cat2-set4',
    'mock-cat2-set5',

    # ── 6. 30 Medium Standard Series (Mock 84 to Mock 113) ──
    'mock-med-01',
    'mock-med-02',
    'mock-med-03',
    'mock-med-04',
    'mock-med-05',
    'mock-med-06',
    'mock-med-07',
    'mock-med-08',
    'mock-med-09',
    'mock-med-10',
    'mock-med-11',
    'mock-med-12',
    'mock-med-13',
    'mock-med-14',
    'mock-med-15',
    'mock-med-16',
    'mock-med-17',
    'mock-med-18',
    'mock-med-19',
    'mock-med-20',
    'mock-med-21',
    'mock-med-22',
    'mock-med-23',
    'mock-med-24',
    'mock-med-25',
    'mock-med-26',
    'mock-med-27',
    'mock-med-28',
    'mock-med-29',
    'mock-med-30',

    # ── 7. 30 Easy Foundational Series (Mock 114 to Mock 143) ──
    'mock-easy-01',
    'mock-easy-02',
    'mock-easy-03',
    'mock-easy-04',
    'mock-easy-05',
    'mock-easy-06',
    'mock-easy-07',
    'mock-easy-08',
    'mock-easy-09',
    'mock-easy-10',
    'mock-easy-11',
    'mock-easy-12',
    'mock-easy-13',
    'mock-easy-14',
    'mock-easy-15',
    'mock-easy-16',
    'mock-easy-17',
    'mock-easy-18',
    'mock-easy-19',
    'mock-easy-20',
    'mock-easy-21',
    'mock-easy-22',
    'mock-easy-23',
    'mock-easy-24',
    'mock-easy-25',
    'mock-easy-26',
    'mock-easy-27',
    'mock-easy-28',
    'mock-easy-29',
    'mock-easy-30',

    # ── 8. Practice Sets (Mock 144 to Mock 150) ──
    'paper-full-1',
    'paper-full-2',
    'paper-dsa',
    'paper-systems',
    'paper-theory',
    'paper-maths',
    'paper-gate-overflow-decade'
]

def run():
    print(f"Total ordered full mocks specified: {len(ORDERED_IDS)}")
    assert len(ORDERED_IDS) == 150, f"Expected 150, got {len(ORDERED_IDS)}"

    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    shutil.copyfile('app.js', 'app.js.bak4')
    print("Created backup app.js.bak4")

    m = re.search(r'(const MOCK_TESTS = \[)([\s\S]*?)(\n\];)', content)
    header, mock_block, footer = m.groups()

    raw_objects = []
    depth = 0
    start = -1
    for i, ch in enumerate(mock_block):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start != -1:
                raw_objects.append(mock_block[start:i+1])
                start = -1

    obj_by_id = {}
    subwise_objs = []
    for raw in raw_objects:
        id_m = re.search(r'id:\s*[\'"]([^\'"]+)[\'"]', raw)
        if id_m:
            mid = id_m.group(1)
            if 'subwise' in mid:
                subwise_objs.append(raw)
            else:
                obj_by_id[mid] = raw

    # Re-order and rename each object
    new_objs = []
    for idx, mid in enumerate(ORDERED_IDS):
        raw = obj_by_id[mid]
        mock_num = idx + 1
        new_name = f"Mock {mock_num}"

        # Determine provider tag
        if mid.startswith('mock-me24-') or mid.startswith('mock-me23-'):
            provider = 'Made Easy'
            year = "2024" if "me24" in mid else "2023"
            if "-adv" in mid:
                adv_num = mid[-1]
                desc = f"[Provider: Made Easy | Prime Test Series] Made Easy {year} Advance Level Full Syllabus Test #{adv_num}. High-difficulty capstone mock testing multi-concept analytical questions and intricate derivations (65 Questions • 180 Mins • 100 Marks)."
            elif "-bsc" in mid:
                bsc_num = mid[-1]
                desc = f"[Provider: Made Easy | Prime Test Series] Made Easy {year} Basic Level Full Syllabus Test #{bsc_num}. Balanced full-length test designed to build speed, accuracy, and foundational confidence (65 Questions • 180 Mins • 100 Marks)."
            else:
                mock_num_str = mid[-1]
                desc = f"[Provider: Made Easy | Prime Test Series] Made Easy {year} Nationwide All-India GATE Mock Test #{mock_num_str}. Authentic nationwide mock exam simulating official GATE testing conditions across the complete syllabus (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-go-') or mid.startswith('mock-go25-'):
            if 'aim' in mid:
                provider = 'GO Classes & Gate Overflow'
                aim_num = re.search(r'aim-([0-9a-z\-]+)', mid).group(1).upper()
                desc = f"[Provider: GO Classes & Gate Overflow] Official All-India Mock (AIM) Test {aim_num}. Full-length exam created jointly by GO Classes & Gate Overflow replicating official GATE pattern with in-depth solutions (65 Questions • 180 Mins • 100 Marks)."
            elif 'ts25-mg' in mid:
                provider = 'GO Classes & Gate Overflow'
                mg_num = mid.split('mg-')[1]
                desc = f"[Provider: GO Classes & Gate Overflow] Official GO Classes Mock GATE Exam #{mg_num}. Full-syllabus mock testing core CS subjects and GA with standard GATE difficulty (65 Questions • 180 Mins • 100 Marks)."
            else:
                provider = 'Gate Overflow'
                mg_num = mid.split('mg-')[1]
                desc = f"[Provider: Gate Overflow] Official Gate Overflow Test Series Mock GATE #{mg_num}. Full-syllabus GATE CS mock paper created by Gate Overflow team with verified community solutions (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-flm-'):
            provider = 'Compendium FLM'
            flm_num = mid.split('flm-')[1]
            desc = f"[Provider: Compendium Mock Series] Compendium Full Mock Exam #{flm_num}. Comprehensive full-syllabus simulation covering multi-topic numerical and conceptual challenges (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-full-'):
            provider = 'Standard Full Mock'
            desc = f"[Provider: Standard GATE Full Simulation] Full-Length Mock Exam #{mock_num}. Comprehensive GATE CSE standard simulation across all subjects (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-cat'):
            provider = 'Category Core CS'
            cat_num = mid.split('set')[1] if 'set' in mid else '1'
            desc = f"[Provider: Category Core CS Series] Category Core CS Full Mock Exam #{cat_num}. High-weightage topic-focused full-syllabus mock covering core concepts (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-med-'):
            provider = 'Standard Series'
            med_num = mid.split('med-')[1]
            desc = f"[Provider: Curated GATE CS Standard Series] Standard GATE Medium Mock Exam #{med_num}. Standard official GATE difficulty with balanced distribution of MCQs, MSQs, and NATs across all subjects (65 Questions • 180 Mins • 100 Marks)."
        elif mid.startswith('mock-easy-'):
            provider = 'Easy Series'
            easy_num = mid.split('easy-')[1]
            desc = f"[Provider: Curated GATE CS Easy Series] Foundational Easy Mock Exam #{easy_num}. Direct formula application, fundamental definitions, and standard scoring problems across all 13 subjects (65 Questions • 180 Mins • 100 Marks)."
        else:
            provider = 'Practice Paper'
            desc = f"[Provider: Curated Practice Paper] Curated Practice Set #{mock_num}. Topic-focused practice questions with detailed step-by-step solutions."

        # Extract difficulty and rating to append to desc
        diff_m = re.search(r'difficulty:\s*[\'"]([^\'"]+)[\'"]', raw)
        rate_m = re.search(r'rating:\s*([0-9.]+)', raw)
        d_val = diff_m.group(1).capitalize() if diff_m else 'Medium'
        r_val = rate_m.group(1) if rate_m else '6.0'

        enhanced_desc = f"{desc} Difficulty: {d_val} (Rating: {r_val}/10)."

        # Update raw object
        raw = re.sub(r'name:\s*[\'"][^\'"]+[\'"]', lambda m: f"name: {json.dumps(new_name)}", raw, count=1)
        if 'provider:' in raw:
            raw = re.sub(r'provider:\s*[\'"][^\'"]+[\'"]', lambda m: f"provider: {json.dumps(provider)}", raw, count=1)
        else:
            raw = re.sub(r'(id:\s*[\'"][^\'"]+[\'"],)', lambda m: f"{m.group(1)}\n    provider: {json.dumps(provider)},", raw, count=1)
        raw = re.sub(r'desc:\s*[\'"][^\'"]*?[\'"]', lambda m: f"desc: {json.dumps(enhanced_desc)}", raw, count=1)

        new_objs.append(raw)

    print(f"Prepared {len(new_objs)} re-ordered full mocks (Official papers removed).")

    all_mock_objs = new_objs + subwise_objs
    new_mock_block_str = "\n  " + ",\n  ".join([obj.strip() for obj in all_mock_objs]) + "\n"

    new_content = content[:m.start()] + header + new_mock_block_str + footer + content[m.end():]

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("app.js updated successfully without official gate papers in MOCK_TESTS!")

if __name__ == '__main__':
    run()
