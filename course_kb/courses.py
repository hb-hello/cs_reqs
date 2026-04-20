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
  'AST 203', 'AST 205', 'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332', 'GEO 102', 'GEO 103', 'GEO 112', 'GEO 123', 'GEO 122', 'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142', 'PHY 251', 'PHY 252',  ## sci_more
  ## missing prereq courses from the above courses
  'MAT 123', 'MAP 101', 'MAP 103', ## mat basics
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
    "CSE 101": {
        "anti_req": Not(Or([Passed("CSE 114", "C"), Passed("CSE 160", "C")]))
    },
    "CSE 160": {
        "coreq": Taken("CSE 161"),
        "advisory_prereq": Passed("CSE 101", "D")
    },
   "CSE 320": {
        "prereq": And([C_or_higher("CSE 220"), Major("CSE")])
    },
    "CSE 364": {
        "prereq": Or([Passed("CSE 334", "D"), Passed("ISE 334", "D")]),
    },
    "CSE 488": {
        "prereq": And([Major("CSE"), Or([Standing("U3"), Standing("U4")]), Permission("permission of department")]),
        "grading": "S/U",
    },
    "AMS 110": {
        "anti_req": Not(Or([Passed("AMS 310", "C"), Passed("MAT 203", "C")]))
    },
    "AMS 210": {
        "prereq": Or([Passed("AMS 151", "D"), Passed("MAT 131", "D"), Coregister("MAT 126"), UnsupportedRequirement("level 7 or higher on the mathematics placement exam")])
    },
    "AMS 311": {
        "prereq": Or([And([Passed("AMS 301", "D"), Passed("AMS 310", "D")]), Permission("permission of instructor")]),
    },
    "MAT 125": {
        "prereq": Or([C_or_higher("MAT 123"), UnsupportedRequirement("level 4 on the mathematics placement examination"), Coregister("MAT 130")])
    },
    "MAT 130": {
        "prereq": Or([Passed("MAT 122", "D"), UnsupportedRequirement("level 3 or higher on the mathematics placement examination"), Permission("permission of instructor")]),
    },
    "MAT 211": {
        "prereq": Or([C_or_higher("AMS 151"), C_or_higher("MAT 131"), C_or_higher("MAT 141"), Coregister("MAT 126"), UnsupportedRequirement("level 7 on the mathematics placement examination")])
    },
    "MAT 250": {
        "prereq": Or([Passed("MAT 131", "D"), UnsupportedRequirement("MAT 131 equivalent"), UnsupportedRequirement("level 7 or higher on mathematics placement examination")])
    },
    "BIO 202": {
        "prereq": Or([C_or_higher("CHE 129"), C_or_higher("CHE 131"), Coregister("CHE 152")])
    },
    "BIO 203": {
        "prereq": Or([Passed("CHE 129", "D"), Passed("CHE 131", "D"), Coregister("CHE 152")]),
    },
    "BIO 204": {
        "prereq": Or([And([Passed("CHE 129", "D"), Passed("CHE 131", "D")]), Coregister("CHE 152")]),
    },
    "CHE 131": {
        "prereq": UnsupportedRequirement("Online Chemistry Placement and Preparation (OCPP) Process. For information on the OCPP, copy and paste the following link into your browser. go.stonybrook.edu/ocpp"),
        "coreq": UnsupportedRequirement("Corequisite: MAT 125 or higher")
    },
    "CHE 132": {
        "prereq": Or([C_or_higher("CHE 129"), C_or_higher("CHE 131")]),
        "pre_or_coreq": And([UnsupportedRequirement("MAT 125 for those who took CHE 129 or 130 or BA BIO majors"), UnsupportedRequirement("all others MAT 126 or higher")])
    },
    "PHY 125": {
        "prereq": Or([Passed("MAT 125", "D"), UnsupportedRequirement("level 4 on the mathematics placement examination")]),
    },
    "PHY 131": {
        "prereq": UnsupportedRequirement("MAT 123 or level 5 on the mathematics placement examination"),
    },
    "PHY 133": {
        "pre_or_coreq": Or([And([Passed("PHY 125", "D"), Passed("PHY 126", "D")]), Passed("PHY 131", "D"), Passed("PHY 141", "D")])
    },
    "PHY 142": {
        "prereq": Or([C_or_higher("PHY 141"), Permission("permission of department")]),
    },
    "PHY 251": {
        "prereq": And([Or([And([Passed("PHY 122", "D"), Passed("PHY 124", "D")]), And([Passed("PHY 126", "D"), Passed("PHY 127", "D")]), Passed("PHY 132", "D"), Passed("PHY 142", "D")]), Passed("PHY 134", "D"), Or([C_or_higher("MAT 126"), C_or_higher("MAT 132"), C_or_higher("MAT 142"), C_or_higher("MAT 171"), C_or_higher("AMS 161")])])
    },
    "WRT 102": {
        "prereq": Or([UnsupportedRequirement("Writing Placement Score of 4"), C_or_higher("WRT 101"), UnsupportedRequirement("WRT 101 transfer equivalent"), UnsupportedRequirement("SAT EBRW >= 580"), UnsupportedRequirement("ACT ELA >=23"), UnsupportedRequirement("AP ELC or AP ELGC >=3")])
    }
}