# -*- coding: utf-8 -*-
import json

def main():
    with open('data/sample_questions.json', encoding='utf-8') as f:
        d = {q['id']: q for q in json.load(f)}

    pairs = [
        ('os001', 'pyq_2016_cs_q12'),
        ('os005', 'pyq_2007_cs_q05'),
        ('os_q06', 'pyq_2007_cs_q05'),
        ('em002', 'pyq_2014_cs_q16'),
        ('ds011', 'pyq_2013_cs_q24'),
        ('ds_q02', 'pyq_2013_cs_q24'),
        ('em_q06', 'pyq_2009_cs_q08'),
        ('pyq_2014_cs_q04', 'pyq_2012_cs_q03'),
        ('pyq_2013_cs_q15', 'pyq_2015_cs_q09')
    ]

    for a, b in pairs:
        print(f"=== {a} vs {b} ===")
        qa, qb = d[a], d[b]
        print(f"[{a}] (Year: {qa.get('year')}, Cat: {qa.get('category')}): {qa['question'][:90]}...")
        print(f"[{b}] (Year: {qb.get('year')}, Cat: {qb.get('category')}): {qb['question'][:90]}...")
        print(f"Options match: {qa.get('options') == qb.get('options')}")
        print(f"Correct match: {qa.get('correct') == qb.get('correct')}")
        print()

if __name__ == '__main__':
    main()
