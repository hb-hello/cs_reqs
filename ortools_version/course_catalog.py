import json, re
from collections import namedtuple
from course_kb.course_kb import (
    Taken as TakenReq, Passed as PassedReq, Major, Standing, Permission, UnsupportedRequirement,
    And, Or, get_courses, get_reqs, Requirement, transform_leaves, course_of,
    MAX_SEMS_ALLOWED, SEM_NAMES, CREDIT_LIMIT, grade_points, COURSE_OFFERED_TERMS
)
from course_kb.build_kb import ASTDecoder

# ── Course record & catalog ────────────────────────────────────

class TakenId(Requirement): pass
class PassedId(Requirement):
    ## by default, we assume passing means C or higher because that's the only case in cse courses.
    ## other programs may have 'passed with B or higher'.
    def __init__(self, *arguments):
        if len(arguments) == 1:
            arguments = (arguments[0], 'C')
        super().__init__(*arguments)

## record of a course taken by the student
Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])
## record of relevant course information
Course = namedtuple('Course', ['id', 'credits', 'prereq', 'coreq', 'anti_req'], defaults=[None, None, None])

catalog = {}

def upper_division(cid): return int(cid[4:]) >= 300

# ── Load CSE courses from KB ───────────────────────────────────

def _parse_credits(s): return int(s.split('-')[-1])

def _load_kb(path):
    # strip // comments (kb_cse_degree.json has comment lines)
    with open(path) as f:
        text = re.sub(r'^\s*//.*$', '', f.read(), flags=re.MULTILINE)
    return json.loads(text, cls=ASTDecoder)

# convert Taken and Passed from prereqs to TakenId and PassedId to not conflict with Taken defined above
def _rewrite_req_ids(expr):
    if expr is None:
        return None

    def rewrite(leaf):
        if isinstance(leaf, TakenReq):
            return TakenId(*leaf.arguments)
        if isinstance(leaf, PassedReq):
            return PassedId(*leaf.arguments)
        return leaf

    return transform_leaves(expr, rewrite)

import os
_kb_path = os.path.join(os.path.dirname(__file__), '..', 'course_kb', 'kb_cse_degree.json')
for kc in _load_kb(_kb_path):
    catalog[kc.id] = Course(
        kc.id,
        _parse_credits(kc.credits),
        _rewrite_req_ids(kc.prereq),
        _rewrite_req_ids(kc.coreq),
        _rewrite_req_ids(kc.anti_req),
    )

# ── Non-CSE courses used in degree requirements ────────────────

def _stub(id, credits):
    if id not in catalog:
        catalog[id] = Course(id, credits)

_stub('AMS 151', 3)
_stub('AMS 161', 3)
_stub('AMS 210', 3)
_stub('AMS 301', 3)
_stub('AMS 310', 3)
_stub('AMS 311', 3)
_stub('AMS 333', 3)

_stub('MAT 125', 3)
_stub('MAT 126', 3)
_stub('MAT 127', 3)
_stub('MAT 131', 3)
_stub('MAT 132', 3)
_stub('MAT 211', 3)

_stub('BIO 201', 3)
_stub('BIO 202', 3)
_stub('BIO 203', 3)
_stub('BIO 204', 1)    # lab

_stub('CHE 131', 3)
_stub('CHE 132', 3)
_stub('CHE 133', 1)    # lab
_stub('CHE 152', 3)
_stub('CHE 154', 1)    # lab
_stub('CHE 321', 3)
_stub('CHE 322', 3)
_stub('CHE 331', 3)
_stub('CHE 332', 3)

_stub('PHY 125', 3)
_stub('PHY 126', 3)
_stub('PHY 127', 3)
_stub('PHY 131', 3)
_stub('PHY 132', 3)
_stub('PHY 133', 1)    # lab
_stub('PHY 134', 1)    # lab
_stub('PHY 141', 3)
_stub('PHY 142', 3)
_stub('PHY 251', 3)
_stub('PHY 252', 3)

_stub('AST 203', 3)
_stub('AST 205', 3)

_stub('GEO 102', 3)
_stub('GEO 103', 3)
_stub('GEO 112', 3)
_stub('GEO 122', 3)
_stub('GEO 123', 3)

# referenced in prereqs but not degree requirements
_stub('ESE 440', 3)
_stub('ESE 441', 3)

# ── External courses referenced in prereqs (stubs) ────────────

_stub('WRT 102', 3)
_stub('ISE 108', 3)
_stub('ISE 208', 3)
_stub('ISE 218', 3)
_stub('ESE 124', 3)
_stub('ESE 280', 3)
_stub('ESG 111', 3)
_stub('BME 120', 3)
_stub('MEC 102', 3)
_stub('MEC 262', 3)
_stub('AMS 110', 3)
_stub('MAT 200', 3)
_stub('MAT 250', 3)
