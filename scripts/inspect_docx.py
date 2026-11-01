# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_docx_paragraphs_and_tables(path):
    with zipfile.ZipFile(path) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    # Let's walk through body children in order (paragraphs and tables)
    body = tree.find('.//w:body', namespaces)
    elements = []
    for child in body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            texts = [t.text for t in child.iterfind('.//w:t', namespaces) if t.text]
            if texts:
                elements.append(('p', ''.join(texts)))
        elif tag == 'tbl':
            rows = []
            for tr in child.iterfind('.//w:tr', namespaces):
                row = []
                for tc in tr.iterfind('.//w:tc', namespaces):
                    tc_texts = []
                    for p in tc.iterfind('.//w:p', namespaces):
                        p_txt = ''.join([t.text for t in p.iterfind('.//w:t', namespaces) if t.text])
                        if p_txt:
                            tc_texts.append(p_txt)
                    row.append('\n'.join(tc_texts))
                rows.append(row)
            elements.append(('tbl', rows))
    return elements

if __name__ == '__main__':
    path = r'c:\Users\sahu1\Downloads\GATE(Easy_to_Medium_Mocks)\GATE_CSE_Mock_Category1_Set1.docx'
    elements = get_docx_paragraphs_and_tables(path)
    print(f"Total elements: {len(elements)}")
    for i, (el_type, content) in enumerate(elements[:60]):
        if el_type == 'p':
            print(f"[{i+1}] P: {content}")
        else:
            print(f"[{i+1}] TBL with {len(content)} rows:")
            for r in content[:5]:
                print("   ", r)
