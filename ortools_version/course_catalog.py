import json, re
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from course_kb.course_kb import (
    Taken as TakenReq, Passed as PassedReq, Major, Standing, Permission, UnsupportedRequirement,
    And, Or, Not, get_courses, get_reqs, Requirement, course_of, transform_leaves, Coregister,
    MAX_SEMS_ALLOWED, SEM_NAMES, CREDIT_LIMIT, grade_points, COURSE_OFFERED_TERMS, 
    get_sem_distance, sem_to_int, int_to_sem, rel_sem_to_term
)
from course_kb.build_kb import ASTDecoder

# ── Course record & catalog ────────────────────────────────────

class TakenId(Requirement): pass
class Passed(Requirement):
    ## by default, we assume passing means C or higher because that's the only case in cse courses.
    ## other programs may have 'passed with B or higher'.
    def __init__(self, *arguments):
        if len(arguments) == 1:
            arguments = (arguments[0], 'C')
        super().__init__(*arguments)

## record of a course taken by the student
Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])
## record of relevant course information
Course = namedtuple('Course', ['id', 'credits', 'prereq', 'coreq', 'anti_req', 'pre_or_coreq'], defaults=[None, None, None, None])

CATALOG = {}
COURSE_ID_RE = re.compile(r'^[A-Z]{3} \d{3}$')

def upper_division(cid): return int(cid[4:]) >= 300

# provides range of (year, semester) tuples
def semester_range(start, end_or_count=MAX_SEMS_ALLOWED):
    y, s = start
    if end_or_count is None: end_or_count = MAX_SEMS_ALLOWED
    if isinstance(end_or_count, int):
        for _ in range(end_or_count):
            yield (y, s)
            s += 1
            if s > 4: s, y = 1, y + 1
        return
    while (y, s) <= end_or_count:
        yield (y, s)
        s += 1
        if s > 4: s, y = 1, y + 1

# ── Load CSE courses from KB ───────────────────────────────────

# credits is either a single int or a (min_credits, max_credits) list,
# in the latter case we take the max_credits
def _parse_credits(credits): return credits[-1] if isinstance(credits, list) else credits

def _load_kb(path):
    # strip // comments (kb_cse_degree.json has comment lines)
    with open(path) as f:
        text = re.sub(r'^\s*//.*$', '', f.read(), flags=re.MULTILINE)
    return json.loads(text, cls=ASTDecoder)

# convert Taken/Passed to TakenId/PassedId; prune UnsupportedRequirement and Permission leaves.
# transform_leaves skips those types, so we do a direct recursive walk instead.
def _rewrite_req_ids(expr):
    if expr is None:
        return None
    if isinstance(expr, Not):
        child = _rewrite_req_ids(expr.operands[0])
        return None if child is None else Not(child)
    if isinstance(expr, (And, Or)):
        operands = [_rewrite_req_ids(op) for op in expr.operands]
        operands = [op for op in operands if op is not None]
        if not operands: return None
        if len(operands) == 1: return operands[0]
        return type(expr)(*operands)
    if isinstance(expr, TakenReq):  return TakenId(*expr.arguments)
    if isinstance(expr, PassedReq): return Passed(*expr.arguments)
    if isinstance(expr, (UnsupportedRequirement, Permission, Major, Standing)): return None
    return expr

import os
_kb_path = os.path.join(os.path.dirname(__file__), '..', 'course_kb', 'kb_cse_degree.json')
for kc in _load_kb(_kb_path):
    CATALOG[kc.id] = Course(
        kc.id,
        _parse_credits(kc.credits),
        _rewrite_req_ids(kc.prereq),
        _rewrite_req_ids(kc.coreq),
        _rewrite_req_ids(kc.anti_req),
        _rewrite_req_ids(kc.pre_or_coreq),
    )

# ── Non-CSE courses used in degree requirements ────────────────

def _stub(id, credits):
    if id not in CATALOG:
        CATALOG[id] = Course(id, credits)

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


def _filter_unknown_ids(expr, valid_ids):
    if expr is None: return None
    if isinstance(expr, Not):
        child = _filter_unknown_ids(expr.operands[0], valid_ids)
        return None if child is None else Not(child)
    if isinstance(expr, (And, Or)):
        ops = [_filter_unknown_ids(op, valid_ids) for op in expr.operands]
        ops = [op for op in ops if op is not None]
        if not ops: return None
        if len(ops) == 1: return ops[0]
        return type(expr)(*ops)
    if isinstance(expr, Requirement):
        return expr if course_of(expr) in valid_ids else None
    return expr

_valid_ids = set(CATALOG.keys())
for _cid in list(CATALOG):
    _c = CATALOG[_cid]
    CATALOG[_cid] = Course(_c.id, _c.credits,
        _filter_unknown_ids(_c.prereq,        _valid_ids),
        _filter_unknown_ids(_c.coreq,         _valid_ids),
        _filter_unknown_ids(_c.anti_req,      _valid_ids),
        _filter_unknown_ids(_c.pre_or_coreq,  _valid_ids))

# prereq options calculation for benchmarking

def _req_course_ids(expr):
    if expr is None:
        return set()
    return {course_of(req) for req in get_reqs(expr)}


def _course_req_expr(cid):
    course = CATALOG.get(cid)
    if not course:
        return None
    exprs = [e for e in (course.prereq, course.coreq) if e is not None]
    if not exprs:
        return None
    return exprs[0] if len(exprs) == 1 else And(*exprs)


def _dep_tree_from_expr(expr, seen):
    if isinstance(expr, And):
        parts = [p for p in (_dep_tree_from_expr(op, seen) for op in expr.operands) if p]
        if not parts:
            return ''
        return parts[0] if len(parts) == 1 else '(' + ' AND '.join(parts) + ')'
    if isinstance(expr, Or):
        parts = [p for p in (_dep_tree_from_expr(op, seen) for op in expr.operands) if p]
        if not parts:
            return ''
        return parts[0] if len(parts) == 1 else '(' + ' OR '.join(parts) + ')'
    if isinstance(expr, Requirement):
        dep = course_of(expr)
        if not COURSE_ID_RE.match(dep):
            return ''
        dep_expr = _course_req_expr(dep)
        if dep_expr is None or dep in seen:
            return dep
        child = _dep_tree_from_expr(dep_expr, seen | {dep})
        return dep if not child else f'{dep}=>{child}'
    return str(expr)


def dependency_tree(cid):
    expr = _course_req_expr(cid)
    if expr is None:
        return '-'
    tree = _dep_tree_from_expr(expr, {cid})
    return tree if tree else '-'


def _option_count_from_expr(expr, prereq_counts, seen, ignore_course=None):
    if isinstance(expr, And):
        total = 1
        for op in expr.operands:
            total *= _option_count_from_expr(op, prereq_counts, seen, ignore_course)
        return total
    if isinstance(expr, Or):
        total = 0
        for op in expr.operands:
            total += _option_count_from_expr(op, prereq_counts, seen, ignore_course)
        return total
    if isinstance(expr, Requirement):
        dep = course_of(expr)
        if ignore_course and dep == ignore_course:
            return 1
        dep_expr = _course_req_expr(dep)
        if dep_expr is None or dep in seen:
            return max(1, prereq_counts.get(dep, 0))
        return _option_count_from_expr(dep_expr, prereq_counts, seen | {dep}, ignore_course)
    return 1


def prerequisite_options(cid, prereq_counts, ignore_course=None):
    expr = _course_req_expr(cid)
    if expr is None:
        return max(1, prereq_counts.get(cid, 0))
    return _option_count_from_expr(expr, prereq_counts, {cid}, ignore_course)


def options_opened_up(cid, dependents, prereq_counts):
    # Sum dependent options when this course is treated as already satisfied in their req chains.
    return sum(prerequisite_options(dep, prereq_counts, ignore_course=cid) for dep in dependents.get(cid, []))


def requisite_counts_by_course(kb_path=None):
    path = _kb_path if kb_path is None else kb_path
    counts = {}
    for kc in _load_kb(path):
        prereq_ids = _req_course_ids(_rewrite_req_ids(kc.prereq))
        coreq_ids = _req_course_ids(_rewrite_req_ids(kc.coreq))
        counts[kc.id] = (len(prereq_ids), len(coreq_ids), len(prereq_ids) + len(coreq_ids))
    return counts


def prerequisite_dependents():
    dependents = {cid: [] for cid in CATALOG}
    for dep_cid, course in CATALOG.items():
        req_ids = set()
        if course.prereq is not None:
            req_ids |= _req_course_ids(course.prereq)
        if course.coreq is not None:
            req_ids |= _req_course_ids(course.coreq)
        if not req_ids:
            continue
        for req_cid in sorted(req_ids):
            if req_cid in dependents:
                dependents[req_cid].append(dep_cid)

    for cid in dependents:
        dependents[cid].sort()
    return dependents


def top_requisite_courses(n=10, kb_path=None):
    rows = [(cid, prereq_n, coreq_n, total)
            for cid, (prereq_n, coreq_n, total) in requisite_counts_by_course(kb_path).items()]

    rows.sort(key=lambda r: (-r[3], -r[1], -r[2], r[0]))
    return rows[:n]


def main():

    FULL = [
        'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',                  ## intro
        'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',       ## adv
        'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',       ## elect
        'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',                  ## calc, sta, alg
        'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                             ## sci
        'CSE 300', 'CSE 312',                                                   ## writing, ethics
    ]
    counts = requisite_counts_by_course(_kb_path)
    dependents = prerequisite_dependents()
    prereq_counts = {cid: vals[0] for cid, vals in counts.items()}
    print('course_id | prereq | options | dependents | options_opened_up | dep_tree')
    rows = []
    for cid in FULL:
        prereq_n = counts.get(cid, (None, None, None))[0]
        if prereq_n is None:
            print(f'{cid:8} | not found | not found | not found | not found | not found')
            rows.append({
                'course_id': cid,
                'prereq': None,
                'options': None,
                'dependents_count': None,
                'dependents': None,
                'options_opened_up': None,
                'dep_tree': None,
            })
            continue
        options = prerequisite_options(cid, prereq_counts)
        course_dependents = dependents.get(cid, [])
        dependents_count = len(course_dependents)
        opened = options_opened_up(cid, dependents, prereq_counts)
        tree = dependency_tree(cid)
        print(f'{cid:8} | {prereq_n:6} | {options:7} | {dependents_count:10} | {opened:17} | {tree}')
        rows.append({
            'course_id': cid,
            'prereq': prereq_n,
            'options': options,
            'dependents_count': dependents_count,
            'dependents': course_dependents,
            'options_opened_up': opened,
            'dep_tree': tree,
        })

    out_dir = Path(__file__).resolve().parents[1] / 'benchmarks' / 'prereq_stats'
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    out_path = out_dir / f'prereq_stats_{stamp}.json'
    with out_path.open('w') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'rows': rows}, f, indent=2)
    print(f'Wrote {out_path}')


if __name__ == '__main__':
    # main()
    print(CATALOG['AMS 151'])
    print(CATALOG['MAT 123'])
