from course_kb.course_kb import *

COURSES_CSE_DEGREE = {
  ## courses listed in the degree requirements.
  'CSE 114', 'CSE 214', 'CSE 216',  ## prog
  'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261',  ## prog2
  'CSE 215',  ## dmath
  'CSE 150',  ## dmath2
  'CSE 220',  ## sys
  'CSE 303',  ## theory
  'CSE 350',  ## theory2
  'CSE 373',  ## algo
  'CSE 385',  ## algo2
  'CSE 310', 'CSE 316', 'CSE 320', 'CSE 416',  ## common
  'AMS 151', 'AMS 161',  ## calc
  'MAT 125', 'MAT 126', 'MAT 127',  ## calc2
  'MAT 131', 'MAT 132',  ## calc3
  'MAT 211',  ## alg
  'AMS 210',  ## alg2
  'AMS 301',  ## fmath
  'AMS 310',  ## sta
  'AMS 311',  ## sta2
  'BIO 201', 'BIO 204',  ## bio
  'BIO 202', 'BIO 204',  ## bio2
  'BIO 203', 'BIO 204',  ## bio3
  'CHE 131', 'CHE 133',  ## che
  'CHE 152', 'CHE 154',  ## che2
  'PHY 126', 'PHY 133',  ## phy
  'PHY 131', 'PHY 133',  ## phy2
  'PHY 141', 'PHY 133',  ## phy3
  'CSE 312',  ## ethics
  'CSE 300',  ## writing
  'WRT 101', 'WRT 102', ## needed for writing
  'CSE 475', 'CSE 495', 'CSE 300', 'CSE 301', 'CSE 312',  ## elect_exclude
  'AST 203', 'AST 205', 'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332', 'GEO 102', 'GEO 103', 'GEO 112', 'GEO 123', 'GEO 122', 'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142', 'PHY 251', 'PHY 252'  ## sci_more
  ## missing prereq courses from the above courses
  'AMS 110', 'AMS 261', 'AMS 361', 'AMS 412',  ## ams
  'BME 120',  ## bme
  'CHE 129', 'CHE 130', 'CHE 383',  ## che
  'ESE 124', 'ESE 280',  ## ese
  'ESG 111',  ## esg
  'ISE 108', 'ISE 208', 'ISE 218', 'ISE 334',  ## ise
  'MAT 130', 'MAT 141', 'MAT 142', 'MAT 171',  ## mat calc & prep
  'MAT 200', 'MAT 203', 'MAT 205', 'MAT 250',  ## mat intermediate
  'MAT 303', 'MAT 307',  ## mat advanced
  'MEC 102', 'MEC 262',  ## mec
  'PHY 122', 'PHY 124'   ## phy
}

## courses in CSE that can't be handled by the current parsing logic.
## Partial field overrides keyed by course id.
## Only include fields that should be changed from parsed output.
COURSES_OVERRIDES = {
  # CSE 364: Advanced Multimedia Techniques
  # Prerequisites: CSE/ISE 334
  # 3 credits
  "CSE 364": {
    "prereq": Or([Taken("CSE 334"), Taken("ISE 334")]),
  },
  # CSE 488: Internship in Computer Science
  # Prerequisites: CSE major, U3 or U4 standing; permission of department
  # SBC:     EXP+
  # 3 credits, S/U grading
  "CSE 488": {
    "prereq": And([Major("CSE"), Or([Standing("U3"), Standing("U4")]), Permission("permission of department")]),
    "grading": "S/U",
  },
}
