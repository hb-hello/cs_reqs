from .solver import Solver
from .course_catalog import (
    catalog, upper_division, COURSE_OFFERED_TERMS,
    Passed, Taken, Major, Standing, UnsupportedRequirement, Permission,
    CourseReq, And, Or, get_courses, get_reqs, Requirement, History, grade_to_points,
    MAX_SEM, SEM_NAMES, CREDIT_LIMIT
)

def C_or_higher(grade): return grade in {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}

## whether a class is upper-division, i.e., 300-level or above
def upper_division(course): return int(course[4:]) >= 300

class Semester(CourseReq): pass   ## predicate to represent semester in which a course is taken
class Grade(CourseReq): pass   ## predicate to represent grade that student has achieved in a course
class UsedInSci(CourseReq): pass # to track the sci subset

# provides range of (year, semester) tuples
def semester_range(start, count):
    y, s = start
    for _ in range(count):
        yield (y, s)
        s += 1
        if s > 4: s, y = 1, y + 1

# pre-process raw history: one entry per course, best known grade, ignoring in-progress (None) entries
def best_attempts(history):
    best = {}
    for h in history:
        if h.grade not in grade_to_points:
            continue
        if h.id not in best or grade_to_points[h.grade] > grade_to_points[best[h.id].grade]:
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
        print(f"  year:{yr} semester:{SEM_NAMES[sn]} ({total} cr): {', '.join(fmt(c, grades) for c in sorted(by_sem[s]))}")

# history is the list of taken namedtuples — pre-processed to one entry per course
# student_reqs are additional attributes of the student such as major, standing, etc.
# must_exclude courses are always excluded when planning
# must_include are always included when planning
# check flag controls the checker vs planner mode
# starting semester indicates the starting semester from which to start planning
# course_offered_terms is a dict of course ID : {sem names}, e.g., 'CSE 114': {'Fall', 'Spring'}
# debug_print enables verbose solver output
def plan_courses(history, *student_reqs, must_exclude=set(), must_include=set(), check=False, starting_semester=(1, 1), course_offered_terms=None, debug_print=False):

    if must_include & must_exclude:
        return None # infeasible

    solver = Solver(ignore=(UnsupportedRequirement, Permission))

    # set up student requirements in the model
    for req in student_reqs:
        solver.ensure(req, 1)

    course_offered_terms = COURSE_OFFERED_TERMS if course_offered_terms is None else course_offered_terms

    # setting up the domain of the grade variable, order is important to enable comparisons below
    Grade.domain = sorted(grade_to_points.keys(), key=grade_to_points.get)

    # setting up the domain for semesters
    base = min((h.when for h in history), default=starting_semester)
    Semester.domain = list(semester_range(base, MAX_SEM))

    history_ids = {h.id: h for h in history}
    excluded = history_ids.keys() | must_exclude

    to_plan_from = catalog.keys() - excluded

    for cid, h in history_ids.items():
        solver.ensure(Grade(cid), h.grade)
        solver.ensure(Taken(cid), 1)
        solver.ensure(Semester(cid), h.when)

    for cid in to_plan_from | (must_exclude - history_ids.keys()):
        # grade is assigned iff course is taken (needed in both check/plan modes)
        solver.iff(Taken(cid), Grade(cid))

    # plan mode
    if not check:
        for cid in to_plan_from:
            # course has semester assigned if and only if we take the course
            solver.iff(Taken(cid), Semester(cid))
            allowed_terms = course_offered_terms.get(cid)
            if allowed_terms:
                # term-restricted: must land in one of the valid allowed slots
                allowed_slots = [sem for sem in Semester.domain[1:] if sem >= starting_semester and SEM_NAMES[sem[1]] in allowed_terms]
                if allowed_slots:
                    # if we take the course, it has to be in one of the allowed semesters
                    solver.implies(Taken(cid), Or(*[solver.exactly(Semester(cid), sem) for sem in allowed_slots]))
                else: # can't take the course if it is not offered in any of the semesters
                    solver.ensure(Taken(cid), 0)
            else:
                # unrestricted: any semester from starting_semester onwards
                solver.implies(Taken(cid), solver.at_least(Semester(cid), starting_semester))

        # hardcoded must_exclude courses to zero
        for cid in must_exclude - history_ids.keys():
            solver.ensure(Taken(cid), 0)

        # hardcoded must_include courses to 1
        for cid in must_include:
            solver.ensure(Taken(cid), 1)

    # Passed(c, g) is true if the course was taken with grade >= g
    # this will be called when we process a Passed(c, g) value
    solver[Passed] = lambda c, g: solver.at_least(Grade(c), g)

    # use actual credits earned from history if available, else for future courses get credits from the catalog
    credits = lambda c: history_ids[c].credits if c in history_ids else catalog[c].credits

    reqs = {}
    witnesses = {}
    # 1. Required Introductory Courses
    prog = {'CSE 114', 'CSE 214', 'CSE 216'}
    # prog = {*map(Passed, {{'CSE 114', 'CSE 214', 'CSE 216'}})} is this better as it expresses the Passed requirement right here in prog itself?
    prog2 = {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'}  ## Honors
    dmath = {'CSE 215'}
    dmath2 = {'CSE 150'}  # Honors
    sys = {'CSE 220'}
    intro_courses = prog | prog2 | dmath | dmath2 | sys

    reqs["intro"] = And(Or(And(*map(Passed, prog)), And(*map(Passed, prog2))), Or(And(*map(Passed, dmath)), And(*map(Passed, dmath2))), And(*map(Passed, sys)))
    witnesses["intro"] = get_reqs(reqs["intro"])

    # 2. Required Advanced Courses
    theory = {'CSE 303'}
    theory2 = {'CSE 350'}  # Honors
    algo = {'CSE 373'}
    algo2 = {'CSE 385'}  # Honors
    other = {'CSE 310', 'CSE 316', 'CSE 320', 'CSE 416'}
    adv_courses = theory | theory2 | algo | algo2 | other
    reqs["adv"] = And(Or(And(*map(Passed, theory)), And(*map(Passed, theory2))), Or(And(*map(Passed, algo)), And(*map(Passed, algo2))), And(*map(Passed, other)))
    witnesses["adv"] = get_reqs(reqs["adv"])


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

    reqs["elect"] = solver.at_least(sum(solver.constraint(Passed(c)) for c in electives), 4)
    witnesses["elect"] = {Passed(c) for c in electives}

    # 4. AMS 151, AMS 161 Applied Calculus I, II
    calc = {'AMS 151', 'AMS 161'}
    calc2 = {'MAT 125', 'MAT 126', 'MAT 127'}
    calc3 = {'MAT 131', 'MAT 132'}
    reqs["calc"] = Or(And(*map(Passed, calc)), And(*map(Passed, calc2)), And(*map(Passed, calc3)))
    witnesses["calc"] = get_reqs(reqs["calc"])

    # 5. One of the following linear algebra courses
    alg = {'MAT 211'}
    alg2 = {'AMS 210'}
    reqs["alg"] = Or(And(*map(Passed, alg)), And(*map(Passed, alg2))) # wrap in And just in case courses are added to the sets
    witnesses["alg"] = get_reqs(reqs["alg"])

    # 6. Both of the following:
    fmath = {'AMS 301'}
    sta =   {'AMS 310'}
    sta2 =  {'AMS 311'}
    reqs["sta"] = And(And(*map(Passed, fmath)), Or(And(*map(Passed, sta)), And(*map(Passed, sta2))))
    witnesses["sta"] = get_reqs(reqs["sta"])

    # 7. At least one natural science lecture/laboratory combination
    # each comb is a pair that must both be taken — Or across all valid pairs
    bio  = {'BIO 201', 'BIO 204'}; bio2 = {'BIO 202', 'BIO 204'}; bio3 = {'BIO 203', 'BIO 204'}
    che  = {'CHE 131', 'CHE 133'}; che2 = {'CHE 152', 'CHE 154'}
    phy  = {'PHY 126', 'PHY 133'}; phy2 = {'PHY 131', 'PHY 133'}; phy3 = {'PHY 141', 'PHY 133'}
    sci_combs = [bio, bio2, bio3, che, che2, phy, phy2, phy3]

    reqs["sci_combo"] = Or(*[And(*[UsedInSci(cid) for cid in comb]) for comb in sci_combs])
    witnesses["sci_combo"] = get_reqs(reqs["sci_combo"])

    # 8. Additional natural science courses selected from above and following list
    # The courses selected in 7 and 8 must carry at least 9 credits total
    sci_more = {'AST 203', 'AST 205',
                'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332',
                'GEO 102', 'GEO 103', 'GEO 112', 'GEO 123', 'GEO 122',
                'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142',
                'PHY 251', 'PHY 252'}

    sci_ids  = sorted(set().union(*sci_combs) | sci_more)

    for cid in sci_ids:     # used is a subset of taken
        solver.implies(UsedInSci(cid), Taken(cid))

    # gpa_exprs: returns (weighted_sum, gpa_credits) linear expressions
    def gpa_exprs(course_ids, pred):
        w_sum, c_total = 0, 0
        for cid in course_ids:
            pv = solver[pred(cid)]
            cr = credits(cid)
            if cid in history_ids:
                grade = history_ids[cid].grade
                w_sum   += pv * int(grade_to_points[grade] * 100) * cr
            else:
                w_sum   += solver.apply(Grade(cid), lambda g, cr=cr: int(grade_to_points[g] * 100) * cr, iff=pred(cid))
            c_total += pv * cr
        return w_sum, c_total

    used_weighted_sum, gpa_credit_total = gpa_exprs(sci_ids, pred=UsedInSci)
    # unique-course credits for the 9-credit minimum (counts each course once, not each attempt)
    unique_credit_total = sum(solver[UsedInSci(cid)] * credits(cid) for cid in sci_ids)

    # The grade point average for the courses in Requirements 7 and 8 must be
    # at least 2.00.
    # GPA >= 2.0  i.e.,  weighted_sum >= 200 * total_credits  (scaled by 100)
    reqs["sci"] = And(reqs["sci_combo"],
                      solver.at_least(unique_credit_total, 9),
                      solver.at_least(used_weighted_sum, 200 * gpa_credit_total))
    witnesses["sci"] = {UsedInSci(cid) for cid in sci_ids}

    # 9. Professional Ethics
    ethics_courses = {'CSE 312'}
    reqs["ethics"] = And(*map(Passed, ethics_courses))
    witnesses["ethics"] = get_reqs(reqs["ethics"])

    # 10. Upper-Division Writing Requirement
    writing_courses = {'CSE 300'}
    reqs["writing"] = And(*map(Passed, writing_courses))
    witnesses["writing"] = get_reqs(reqs["writing"])

    # At least 24 credits from items 1 to 3, and at least 18 from 2 and 3, at Stony Brook
    transfer_ids = {h.id for h in history if h.where != 'SB'}
    items123_courses = (intro_courses | adv_courses | electives) - transfer_ids
    items23_courses  = (adv_courses | electives) - transfer_ids
    reqs['credits_at_SB'] = And(solver.at_least(sum(solver[Passed(c)] * credits(c) for c in items123_courses), 24),
        solver.at_least(sum(solver[Passed(c)] * credits(c) for c in items23_courses), 18))

    grades = {h.id: h.grade for h in history}
    req_vars = {name: solver.constraint(expr) for name, expr in reqs.items()}

    if check:
        for cid in to_plan_from: # ensure the solver can't plan any more courses
            solver.ensure(Taken(cid), 0)
        solver.model.maximize(sum(req_vars.values()))
    else:
        for v in req_vars.values():
            solver.require(v)

        # calculate total number of new courses taken
        new_courses = sum(solver[Taken(cid)] for cid in to_plan_from)

        # pre-req course requirement
        prereqs = {cid: c.prereq for cid, c in catalog.items() if c.prereq}

        for cid, expr in prereqs.items():
            # not checking pre-reqs in history
            if cid in excluded: continue
            solver.implies(Taken(cid), expr)

            for p in get_courses(expr):
                solver.implies(Taken(cid), solver[Semester(cid)] > solver[Semester(p)])

        # coreq: must be taken same semester or before (≤ rather than <)
        for cid, c in catalog.items():
            if not c.coreq or cid in excluded: continue
            solver.implies(Taken(cid), c.coreq)
            for p in get_courses(c.coreq):
                solver.implies(Taken(cid), solver[Semester(p)] <= solver[Semester(cid)])

        # anti_req: cannot take this course if these courses are taken (before or with)
        for cid, c in catalog.items():
            if not c.anti_req or cid in excluded: continue
            solver.forbids(Taken(cid), c.anti_req)

        # enforce credit limit per semester using the same encoded semester domain
        # to avoid comparing against semesters that are outside Semester.domain.
        for sem in (s for s in Semester.domain if s >= starting_semester):
            sem_credits = [credits(cid) * solver.exactly(Semester(cid), sem) for cid in to_plan_from]
            if sem_credits:
                solver.require(solver.at_most(sum(sem_credits), CREDIT_LIMIT))

        # to minimize the grades possible
        grade_sum = sum(solver.apply(Grade(cid), lambda g: int(grade_to_points[g] * 100), iff=Taken(cid)) for cid in to_plan_from)

        # to minimize the number of semesters needed to graduate
        last_sem = solver.max_of(solver[Semester(cid)] for cid in to_plan_from)

        # minimizes the expressions in order of priority given
        solver.minimize([last_sem, new_courses, grade_sum])

    # run the solver
    status, obj = solver.solve()
    if debug_print: solver.print_metrics()

    if obj is None:
        print("No solution:", status)
        return {}

    if debug_print:
        if check:
            print(f"Status: {status} — {obj} / {len(req_vars)} requirements met\n")

    planned = {}
    if not check:
        planned = {cid: solver.value(Semester(cid))
                   for cid in to_plan_from if solver.value(Semester(cid))}
        if debug_print:
            print(f"Status: {status} — {len(set(planned.values()))} more semester(s)\n")

        for cid in planned:
            if cid not in grades:
                grades[cid] = solver.value(Grade(cid))

    # report which courses satisfy which requirements (witness)
    items123_cr = sum(credits(c) for c in items123_courses if solver.value(Passed(c)))
    items23_cr  = sum(credits(c) for c in items23_courses  if solver.value(Passed(c)))
    witnesses['credits_at_SB'] = {f"items123 = {items123_cr}", f"items23 = {items23_cr}"}

    checked = {}
    for name in sorted(witnesses):
        wit = sorted(req.arguments[0] for req in witnesses[name] if isinstance(req, Requirement) and solver.value(req))
        wit += sorted(req for req in witnesses[name] if isinstance(req, str))
        satisfied = bool(solver.value(req_vars[name])) if check and name in req_vars else True
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

    if debug_print:
        solver.print_metrics()
        print(checked)
        print(planned)
    return checked, planned, grades

def fmt(cid, grades):
    return f"{cid} ({grades[cid]})" if cid in grades else cid

if __name__ == '__main__':
    # Test: student has taken intro programming + CSE 220
    taken_ids = {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 220'}
    history   = [History(cid, catalog[cid].credits, "A", (2024, 1), "SB") for cid in taken_ids]
    plan_courses(history, Major("CSE"), Standing("U4"), starting_semester=(2024, 2), check=False, debug_print=True)
