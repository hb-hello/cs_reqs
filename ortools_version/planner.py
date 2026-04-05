from pprint import pprint

from .solver import ORModel
from .course_catalog import (
    catalog, upper_division, COURSE_OFFERED_TERMS,
    PassedId, TakenId, Taken, Major, Standing, UnsupportedRequirement, Permission,
    And, Or, get_reqs, Requirement, grade_points, semester_range,
    MAX_SEMS_ALLOWED, CREDIT_LIMIT, transform_leaves, course_of
)

def C_or_higher(grade): return grade in {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}

## whether a class is upper-division, i.e., 300-level or above
def upper_division(course): return int(course[4:]) >= 300

class Semester(Requirement): pass   ## predicate to represent semester in which a course is taken
class Grade(Requirement): pass   ## predicate to represent grade that student has achieved in a course
class SciSubset(Requirement): pass # to track the sci subset
class Prereq(Requirement): pass
class Coreq(Requirement): pass
class Antireq(Requirement): pass

# pre-process raw history: one entry per course, best known grade, ignoring in-progress (None) entries
def best_attempts(history):
    best = {}
    for h in history:
        if h.grade not in grade_points:
            continue
        if h.id not in best or grade_points[h.grade] > grade_points[best[h.id].grade]:
            best[h.id] = h
    return list(best.values())

def print_schedule(planned, grades, credits_fn):
    by_sem = {}
    for cid, s in planned.items():
        by_sem.setdefault(s, []).append(cid)
    print(f"New courses to take ({len(planned)}):")
    for s in sorted(by_sem):
        yr, sn = s
        total = sum(credits_fn(c) for c in by_sem[s])
        print(f"  year:{yr} semester:{sn} ({total} cr): {', '.join(fmt(c, grades) for c in sorted(by_sem[s]))}")

# history is the list of taken namedtuples — pre-processed to one entry per course
# student_reqs are additional attributes of the student such as major, standing, etc.
# must_exclude courses are always excluded when planning
# must_include are always included when planning
# check flag controls the checker vs planner mode
# starting semester indicates the starting semester from which to start planning
# course_offered_terms is a dict of course ID : {sem names}, e.g., 'CSE 114': {'Fall', 'Spring'}
# debug_print enables verbose solver output
def plan_courses(taken, *student_reqs, must_exclude=set(), must_include=set(), check=False, starting_semester=(1, 1), ending_semester=None, course_offered_terms=None, debug_print=False):

    if must_include & must_exclude:
        return None # infeasible

    or_model = ORModel(ignore=(UnsupportedRequirement, Permission))

    # set up student requirements in the model
    for student_req in student_reqs:
        or_model[student_req] = 1

    course_offered_terms = COURSE_OFFERED_TERMS if course_offered_terms is None else course_offered_terms

    # setting up the domain of the grade variable, order is important to enable comparisons below
    Grade.domain = sorted(grade_points.keys(), key=grade_points.get)

    # setting up the domain for semesters; base anchors the domain, starting_semester clamped within it
    base = min((h.when for h in taken), default=starting_semester)
    Semester.domain = list(semester_range(base, ending_semester))
    starting_semester = max(starting_semester, base)

    history_ids = {h.id: h for h in taken}
    # excluded = history_ids.keys() | must_exclude

    to_plan_from = catalog.keys() - (history_ids.keys() | must_exclude)
    to_plan_from &= course_offered_terms.keys()

    for cid, h in history_ids.items():
        or_model[Grade(cid)]    = h.grade
        or_model[TakenId(cid)]    = 1
        or_model[Semester(cid)] = h.when

    for cid in to_plan_from | (must_exclude - history_ids.keys()):
        # grade is assigned iff course is taken (needed in both check/plan modes)
        or_model.iff(TakenId(cid), Grade(cid))

    # plan mode
    if not check:
        for cid in to_plan_from:
            # course has semester assigned if and only if we take the course
            or_model.iff(TakenId(cid), Semester(cid))
            offered_terms = course_offered_terms.get(cid)
            if offered_terms:
                # term-restricted: must land in one of the valid allowed slots
                offered_sems = [sem for sem in Semester.domain[1:] if sem >= starting_semester and sem[1] in offered_terms]
                if offered_sems:
                    # if we take the course, it has to be in one of the allowed semesters
                    or_model.implies(TakenId(cid), Or(*[or_model.exactly(Semester(cid), sem) for sem in offered_sems]))
                else: # can't take the course if it is not offered in any of the semesters
                    or_model[TakenId(cid)] = 0
            else:
                # unrestricted: any semester from starting_semester onwards
                or_model.implies(TakenId(cid), or_model.at_least(Semester(cid), starting_semester))

        # hardcoded must_exclude courses to zero
        for cid in must_exclude - history_ids.keys():
            or_model[TakenId(cid)] = 0

        # hardcoded must_include courses to 1
        for cid in must_include:
            or_model[TakenId(cid)] = 1

    # PassedId(c, g) is true if the course was taken with grade >= g
    # this will be called when we process a PassedId(c, g) value
    or_model[PassedId] = lambda c, g: or_model.at_least(Grade(c), g)

    # use actual credits earned from history if available, else for future courses get credits from the catalog
    credits = lambda c: history_ids[c].credits if c in history_ids else catalog[c].credits

    reqs = {}
    # 1. Required Introductory Courses
    prog = {'CSE 114', 'CSE 214', 'CSE 216'}
    # prog = {*map(PassedId, {{'CSE 114', 'CSE 214', 'CSE 216'}})} is this better as it expresses the PassedId requirement right here in prog itself?
    prog2 = {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'}  ## Honors
    dmath = {'CSE 215'}
    dmath2 = {'CSE 150'}  # Honors
    sys = {'CSE 220'}
    intro_courses = prog | prog2 | dmath | dmath2 | sys

    reqs["intro"] = And(Or(And(*map(PassedId, prog)), And(*map(PassedId, prog2))), Or(And(*map(PassedId, dmath)), And(*map(PassedId, dmath2))), And(*map(PassedId, sys)))

    # 2. Required Advanced Courses
    theory = {'CSE 303'}
    theory2 = {'CSE 350'}  # Honors
    algo = {'CSE 373'}
    algo2 = {'CSE 385'}  # Honors
    other = {'CSE 310', 'CSE 316', 'CSE 320', 'CSE 416'}
    adv_courses = theory | theory2 | algo | algo2 | other
    reqs["adv"] = And(Or(And(*map(PassedId, theory)), And(*map(PassedId, theory2))), Or(And(*map(PassedId, algo)), And(*map(PassedId, algo2))), And(*map(PassedId, other)))


    # 3. Computer Science Electives  ## simpler than 2025
    #
    # Four upper-division technical CSE electives, each of which must carry at
    # least three credits. Technical electives do not include teaching practica
    # (CSE 475), the senior honors project (CSE 495, 496), and courses
    # designated as non-technical in the course description (such as CSE 301).
    elect_exclude = {'CSE 475', 'CSE 495', 'CSE 300', 'CSE 301', 'CSE 312'}

    ## list of eligible electives
    electives = {
        c for c in catalog
        if c[:3] == 'CSE'
        and upper_division(c)
        and credits(c) >= 3
        and c not in adv_courses | elect_exclude
    }

    reqs["elect"] = or_model.at_least(sum(or_model.resolve(PassedId(c)) for c in electives), 4)

    # 4. AMS 151, AMS 161 Applied Calculus I, II
    calc = {'AMS 151', 'AMS 161'}
    calc2 = {'MAT 125', 'MAT 126', 'MAT 127'}
    calc3 = {'MAT 131', 'MAT 132'}
    reqs["calc"] = Or(And(*map(PassedId, calc)), And(*map(PassedId, calc2)), And(*map(PassedId, calc3)))

    # 5. One of the following linear algebra courses
    alg = {'MAT 211'}
    alg2 = {'AMS 210'}
    reqs["alg"] = Or(And(*map(PassedId, alg)), And(*map(PassedId, alg2))) # wrap in And just in case courses are added to the sets

    # 6. Both of the following:
    fmath = {'AMS 301'}
    sta =   {'AMS 310'}
    sta2 =  {'AMS 311'}
    reqs["sta"] = And(And(*map(PassedId, fmath)), Or(And(*map(PassedId, sta)), And(*map(PassedId, sta2))))

    # 7. At least one natural science lecture/laboratory combination
    # each comb is a pair that must both be taken — Or across all valid pairs
    bio  = {'BIO 201', 'BIO 204'}; bio2 = {'BIO 202', 'BIO 204'}; bio3 = {'BIO 203', 'BIO 204'}
    che  = {'CHE 131', 'CHE 133'}; che2 = {'CHE 152', 'CHE 154'}
    phy  = {'PHY 126', 'PHY 133'}; phy2 = {'PHY 131', 'PHY 133'}; phy3 = {'PHY 141', 'PHY 133'}
    sci_combs = [bio, bio2, bio3, che, che2, phy, phy2, phy3]

    reqs["sci_combo"] = Or(*[And(*[SciSubset(cid) for cid in comb]) for comb in sci_combs])

    # 8. Additional natural science courses selected from above and following list
    # The courses selected in 7 and 8 must carry at least 9 credits total
    sci_more = {'AST 203', 'AST 205',
                'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332',
                'GEO 102', 'GEO 103', 'GEO 112', 'GEO 123', 'GEO 122',
                'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142',
                'PHY 251', 'PHY 252'}

    sci_ids  = sorted(set().union(*sci_combs) | sci_more)

    for cid in sci_ids:     # used is a subset of taken
        or_model.implies(SciSubset(cid), TakenId(cid))

    # Grade(cid) is pinned for history courses, decision variable for future ones — apply works for both
    sci_subset_grade_points = sum(or_model.apply(Grade(cid), 
                                                 lambda g, cr=credits(cid): int(grade_points[g] * 100) * cr, 
                                                 iff=SciSubset(cid)) 
                                                 for cid in sci_ids)
    # unique_credit_total: counts each sci course once (for 9-credit min and GPA denominator)
    sci_subset_credits = sum(or_model[SciSubset(cid)] * credits(cid) for cid in sci_ids)

    # The grade point average for the courses in Requirements 7 and 8 must be
    # at least 2.00.
    # GPA >= 2.0  i.e.,  weighted_sum >= 200 * total_credits  (scaled by 100)
    reqs["sci"] = And(reqs["sci_combo"],
                      or_model.at_least(sci_subset_credits, 9),
                      or_model.at_least(sci_subset_grade_points, 200 * sci_subset_credits))

    # 9. Professional Ethics
    ethics_courses = {'CSE 312'}
    reqs["ethics"] = And(*map(PassedId, ethics_courses))

    # 10. Upper-Division Writing Requirement
    writing_courses = {'CSE 300'}
    reqs["writing"] = And(*map(PassedId, writing_courses))

    # collect all reqs into witnesses
    witnesses = {req: get_reqs(expr) for req, expr in reqs.items()}
    # collect sci witness as the reqs entry is not a straightforward and/or expression
    witnesses["elect"] = {PassedId(c) for c in electives}
    witnesses["sci"] = {SciSubset(c) for c in sci_ids}

    # At least 24 credits from items 1 to 3, and at least 18 from 2 and 3, at Stony Brook
    transfer_ids = {h.id for h in taken if h.where != 'SB'}
    items123_courses = (intro_courses | adv_courses | electives) - transfer_ids
    items23_courses  = (adv_courses | electives) - transfer_ids
    reqs['credits_at_SB'] = And(or_model.at_least(sum(or_model[PassedId(c)] * credits(c) for c in items123_courses), 24),
        or_model.at_least(sum(or_model[PassedId(c)] * credits(c) for c in items23_courses), 18))

    grades = {h.id: h.grade for h in taken}
    req_vars = {name: or_model.resolve(expr) for name, expr in reqs.items()}

    if check:
        for cid in to_plan_from: # ensure the solver can't plan any more courses
            or_model[TakenId(cid)] = 0
        or_model.maximize(sum(req_vars.values()))
    else:
        for v in req_vars.values():
            or_model.require(v)

        # calculate total number of new courses taken
        new_courses = sum(or_model[TakenId(cid)] for cid in to_plan_from)

        # define what the predicates prereqs, coreqs and antireqs should resolve into
        # prereq: must be taken before (<)
        or_model[Prereq] = lambda cid, req: or_model.resolve(
            And(req, or_model.at_least(or_model[Semester(cid)] - or_model[Semester(course_of(req))], 1)))
        # coreq: must be taken same semester or before (= rather than <)
        or_model[Coreq] = lambda cid, req: or_model.resolve(
            And(req, or_model.exactly(or_model[Semester(cid)] - or_model[Semester(course_of(req))], 0)))
        # anti_req: cannot take this course if these courses are taken    
        or_model[Antireq] = lambda cid, req: or_model.resolve(req).negated()

        # pre-req course requirement

        # for cid, c in catalog.items():
        #     if not c.prereq or cid in excluded: continue
        #     or_model.implies(TakenId(cid), transform_leaves(c.prereq, lambda req, c=cid: Prereq(c, req)))

        # for cid, c in catalog.items():
        #     if not c.coreq or cid in excluded: continue
        #     or_model.implies(TakenId(cid), transform_leaves(c.coreq, lambda req, c=cid: Coreq(c, req)))

        # for cid, c in catalog.items():
        #     if not c.anti_req or cid in excluded: continue
        #     or_model.forbids(TakenId(cid), c.anti_req)

        for cid in to_plan_from:
            for expr, pred in ((catalog[cid].prereq, Prereq), (catalog[cid].coreq, Coreq)):
                if expr: or_model.implies(TakenId(cid), transform_leaves(expr, lambda req, c=cid, P=pred: P(c, req)))
            if catalog[cid].anti_req: or_model.forbids(TakenId(cid), catalog[cid].anti_req)

        # enforce credit limit per semester using the same encoded semester domain
        # to avoid comparing against semesters that are outside Semester.domain.
        for sem in (s for s in Semester.domain if s >= starting_semester):
            sem_credits = [credits(cid) * or_model.exactly(Semester(cid), sem) for cid in to_plan_from]
            if sem_credits: or_model.require(or_model.at_most(sum(sem_credits), CREDIT_LIMIT))

        # to minimize the grades possible
        grade_sum = sum(or_model.apply(Grade(cid), lambda g: int(grade_points[g] * 100), iff=TakenId(cid)) for cid in to_plan_from)

        # to minimize the number of semesters needed to graduate
        last_sem = or_model.max_of(or_model[Semester(cid)] for cid in to_plan_from)

        # minimizes the expressions in order of priority given
        or_model.minimize([last_sem, new_courses, grade_sum])

    # run the solver
    solution = or_model.solve()
    if debug_print: solution.print_metrics()

    if solution.obj is None:
        print("No solution:", solution.status)
        return {}

    if debug_print:
        if check:
            print(f"Status: {solution.status} — {solution.obj} / {len(req_vars)} requirements met\n")

    planned = {}
    if not check:
        planned = {cid: solution.value(Semester(cid))
                   for cid in to_plan_from if solution.value(Semester(cid))}
        if debug_print:
            print(f"Status: {solution.status} — {len(set(planned.values()))} more semester(s)\n")

        for cid in planned:
            if cid not in grades:
                grades[cid] = solution.value(Grade(cid))

    # report which courses satisfy which requirements (witness)
    items123_cr = sum(credits(c) for c in items123_courses if solution.value(PassedId(c)))
    items23_cr  = sum(credits(c) for c in items23_courses  if solution.value(PassedId(c)))
    witnesses['credits_at_SB'] = {f"items123 = {items123_cr}", f"items23 = {items23_cr}"}

    checked = {}
    for name in sorted(witnesses):
        wit = sorted(req.arguments[0] for req in witnesses[name] if isinstance(req, Requirement) and solution.value(req))
        wit += sorted(req for req in witnesses[name] if isinstance(req, str))
        satisfied = bool(solution.value(req_vars[name])) if check and name in req_vars else True
        checked[name] = (satisfied, wit)
        if debug_print: print(f"{name} : {', '.join(fmt(c, grades) for c in wit)}")

    checked['degree'] = (all(v for v, _ in checked.values()), [])

    if not check:
        witnessed = {c for (_, wit) in checked.values() for c in wit if c in catalog}
        additional = sorted(c for c in planned if c not in witnessed)
        checked['additional'] = (True, additional)
        if debug_print:
            print(f"additional : {', '.join(fmt(c, grades) for c in additional)}")
            print_schedule(planned, grades, credits)

    if debug_print: solution.print_metrics()
    return checked, planned, solution.metrics()

def fmt(cid, grades):
    return f"{cid} ({grades[cid]})" if cid in grades else cid

if __name__ == '__main__':
    # Test: student has taken intro programming + CSE 220
    taken_ids = {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 220'}
    print([COURSE_OFFERED_TERMS[t] for t in taken_ids])
    history   = [Taken(cid, catalog[cid].credits, "A", (2024, 1), "SB") for cid in taken_ids]
    plan_courses(history, Major("CSE"), Standing("U4"), starting_semester=(2024, 2), ending_semester=(2025, 4), check=False, debug_print=True)
