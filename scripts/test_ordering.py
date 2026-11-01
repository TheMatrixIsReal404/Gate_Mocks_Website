import re
import json

def test_ordering():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    m = re.search(r'const MOCK_TESTS = \[([\s\S]*?)\n\];', content)
    mock_block = m.group(1)

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

    print(f"Total non-subwise mocks found: {len(obj_by_id)}")
    print(f"Total subwise mocks: {len(subwise_objs)}")

if __name__ == '__main__':
    test_ordering()
