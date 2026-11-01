# -*- coding: utf-8 -*-
exams = [
  {"id": "pyq-exam-2026-1", "year": 2026, "difficulty": "medium"},
  {"id": "pyq-exam-2026-2", "year": 2026, "difficulty": "hard"},
  {"id": "pyq-exam-2025-s1", "year": 2025, "difficulty": "medium"},
  {"id": "pyq-exam-2025-s2", "year": 2025, "difficulty": "hard"},
  {"id": "pyq-exam-2024", "year": 2024, "difficulty": "hard"},
  {"id": "pyq-exam-2023", "year": 2023, "difficulty": "medium"},
  {"id": "pyq-exam-2022", "year": 2022, "difficulty": "medium"},
  {"id": "pyq-exam-2021", "year": 2021, "difficulty": "medium"},
  {"id": "pyq-exam-2020", "year": 2020, "difficulty": "medium"},
  {"id": "pyq-exam-2019", "year": 2019, "difficulty": "medium"},
  {"id": "pyq-exam-2018", "year": 2018, "difficulty": "medium"},
  {"id": "pyq-exam-2017", "year": 2017, "difficulty": "medium"},
  {"id": "pyq-exam-2016", "year": 2016, "difficulty": "medium"},
  {"id": "pyq-exam-2015-s1", "year": 2015, "difficulty": "medium"},
  {"id": "pyq-exam-2015-s2", "year": 2015, "difficulty": "hard"},
  {"id": "pyq-exam-2015-s3", "year": 2015, "difficulty": "medium"},
  {"id": "pyq-exam-2014-s1", "year": 2014, "difficulty": "medium"},
  {"id": "pyq-exam-2014-s2", "year": 2014, "difficulty": "medium"},
  {"id": "pyq-exam-2014-s3", "year": 2014, "difficulty": "hard"},
  {"id": "pyq-exam-2011", "year": 2011, "difficulty": "easy"},
  {"id": "pyq-exam-decade", "year": "2014–2024", "difficulty": "medium"}
]

def filter_era(era):
    if era == 'recent':
        return [e for e in exams if isinstance(e['year'], int) and e['year'] >= 2020]
    elif era == 'decade':
        return [e for e in exams if (isinstance(e['year'], int) and 2014 <= e['year'] <= 2019) or 'decade' in e['id']]
    elif era == 'classic':
        return [e for e in exams if isinstance(e['year'], int) and e['year'] <= 2013]
    return exams

print("All count:", len(filter_era('all')))
print("Recent count:", len(filter_era('recent')))
print("Decade count:", len(filter_era('decade')))
print("Classic count:", len(filter_era('classic')))
