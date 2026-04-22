from .solver import ORModel
from .course_catalog import (
    CATALOG, upper_division, COURSE_OFFERED_TERMS,
    Passed, Taken, Major, Standing, UnsupportedRequirement, Permission,
    CourseReq, And, Or, get_courses, get_reqs, Requirement, Taken
)

def C_or_higher(grade): return grade in {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}

## whether a class is upper-division, i.e., 300-level or above
def upper_division(course): return int(course[4:]) >= 300

# For the purpose of determining grade point average, grades are assigned
# point values as follows:
grade_to_points = {
  'A': 4.00, 'A-': 3.67,
  'B+': 3.33, 'B': 3.00, 'B-': 2.67,
  'C+': 2.33, 'C': 2.00, 'C-': 1.67,
  'D+': 1.33, 'D': 1.00,
  'F': 0.00, 'I/F': 0.00, 'Q': 0.00
}
GRADES = sorted(grade_to_points.keys(), key=grade_to_points.get)

MAX_SEM = 40       # upper bound on future semesters
CREDIT_LIMIT = 15  # max credits per semester

SEM_NAMES = {1: 'Fall', 2: 'Winter', 3: 'Spring', 4: 'Summer'}

# provides range of (year, semester) tuples
def semester_range(start, count):
    y, s = start
    for _ in range(count):
        yield (y, s)
        s += 1
        if s > 4: s, y = 1, y + 1

class UsedInSci(CourseReq): pass

# history is the list of taken namedtuples
# student_reqs are additional attributes of the student such as major, standing, etc.
# must_exclude course are always excluded when planning
# must_include are always included when planning
# check flag controls the checker vs planner mode
# starting semester indicates the starting semester from which to start planning
# course_offered_terms is a dict of course ID : {sem names}, e.g., 'CSE 114': {'Fall', 'Spring'}
def plan_courses(history, *student_reqs, must_exclude=set(), must_include=set(), check=False, starting_semester=(1, 1), course_offered_terms=None):

    if must_include & must_exclude:
        return None # infeasible

    solver = ORModel(ignore=(UnsupportedRequirement, Permission))
    model = solver.model

    # set up student requirements (Major, Standing, etc.) in the model
    for req in student_reqs:
        solver.ensure(req, 1)

    course_offered_terms = COURSE_OFFERED_TERMS if course_offered_terms is None else course_offered_terms

    # list of all possible semesters - from history's first semester to MAX_SEM semesters after that
    base = min((h.when for h in history), default=starting_semester)
    all_sems = list(semester_range(base, MAX_SEM))

    # record history (store multiple attempts as well)
    history_ids = {}
    for h in history:
        history_ids.setdefault(h.id, []).append({'g': h.grade, 's': h.when})

    # fetch credits earned for each course
    hist_credits = {h.id: h.credits for h in history}
    # use actual credits earned from history if available, else for future courses get credits from the catalog
    credits = lambda c: hist_credits.get(c, CATALOG[c].credits)

    for c in CATALOG:
        offered_terms = course_offered_terms.get(c)
        for g in GRADES:
            for s in all_sems:
                if c in history_ids:
                    # hardcode history grades
                    solver.ensure(Taken(c, g, s), 1 if {'g': g, 's': s} in history_ids[c] else 0)
                elif c in must_exclude:
                    # ensure these course are not included in plan
                    solver.ensure(Taken(c, g, s), 0)
                else:
                    if s < starting_semester: continue
                    # ensure course can't be taken in semesters it isn't offered in
                    if offered_terms and SEM_NAMES[s[1]] not in offered_terms: solver.ensure(Taken(c, g, s), 0)
                    solver[Taken(c, g, s)]

        if c in must_include - history_ids.keys():
            # these courses must be included
            model.add_exactly_one(solver[Taken(c, g, s)] for g in GRADES for s in all_sems)
        elif c not in history_ids.keys() | must_exclude:
            # plan at most one c, g combo for everything else
            model.add_at_most_one(solver[Taken(c, g, s)] for g in GRADES for s in all_sems)

    # Passed(c, gr) is true if the course was taken with grade >= gr
    solver[Passed] = lambda c, gr: solver.resolve(Or(*[Taken(c, g, s) for g in GRADES if grade_to_points[g] >= grade_to_points[gr] for s in all_sems]))

    reqs = {}
    witnesses = {}
    # 1. Required Introductory Courses
    prog = {'CSE 114', 'CSE 214', 'CSE 216'}
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

    # 3. Computer Science Electives
    #
    # Four upper-division technical CSE electives, each of which must carry at
    # least three credits. Technical electives do not include teaching practica
    # (CSE 475), the senior honors project (CSE 495, 496), and courses
    # designated as non-technical in the course description (such as CSE 301).
    elect_exclude = {'CSE 475', 'CSE 495', 'CSE 300', 'CSE 301', 'CSE 312'}

    ## list of eligible electives
    electives = {
        c for c in CATALOG
        if c[:3] == 'CSE'
        and upper_division(c)
        and credits(c) >= 3
        and c not in adv_courses | elect_exclude
    }

    reqs["elect"] = solver.ge(sum(solver.resolve(Passed(c)) for c in electives), 4)
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

    for cid in sci_ids:
        for g in GRADES:
            # creating a new predicate to track the sci subset
            solver.implies(UsedInSci(cid, g), Or(*[Taken(cid, g, s) for s in all_sems]))
        solver[UsedInSci(cid)] = Or(*[UsedInSci(cid, g) for g in GRADES])
        # for history courses, all attempt grades must count in GPA when the course is used
        if cid in history_ids:
            for attempt in history_ids[cid]:
                if attempt['g'] in grade_to_points:
                    solver.implies(UsedInSci(cid), UsedInSci(cid, attempt['g']))

    sci_weighted = 0
    sci_credit_total = 0
    for cid in sci_ids:
        for g in GRADES:
            sci_weighted += solver[UsedInSci(cid, g)] * int(grade_to_points[g] * 100) * credits(cid)
            sci_credit_total += solver[UsedInSci(cid, g)] * credits(cid)

    # unique-course credits for the 9-credit minimum (counts each course once, not each attempt)
    unique_credit_total = sum(solver[UsedInSci(cid)] * credits(cid) for cid in sci_ids)

    # The grade point average for the courses in Requirements 7 and 8 must be
    # at least 2.00.
    # GPA >= 2.0  i.e.,  weighted_sum >= 200 * total_credits  (scaled by 100)
    reqs["sci"] = And(reqs["sci_combo"],
                      solver.ge(unique_credit_total, 9),
                      solver.ge(sci_weighted, 200 * sci_credit_total))
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
    reqs['credits_at_SB'] = And(solver.ge(sum(solver[Passed(c)] * credits(c) for c in items123_courses), 24),
        solver.ge(sum(solver[Passed(c)] * credits(c) for c in items23_courses), 18))

    grades = {h.id: h.grade for h in history}
    req_vars = {name: solver.resolve(expr) for name, expr in reqs.items()}

    to_plan_from = CATALOG.keys() - (history_ids.keys() | must_exclude)

    if check:
        # no future BoolVars were created; just maximize satisfied requirements
        for c in to_plan_from:
            for g in GRADES:
                for s in all_sems:
                    solver.ensure(Taken(c, g, s), 0)
        model.maximize(sum(req_vars.values()))
    else:
        for v in req_vars.values():
            solver.require(v)

        for c in to_plan_from:
            for s in all_sems:
                solver[UsedInSci(cid)] = Or(*[UsedInSci(cid, g) for g in GRADES])
                solver[Taken(c, s)] = Or(*[Taken(c, g, s) for g in GRADES])

        # calculate total number of new courses taken
        for c in to_plan_from:
            solver[Taken(c)] = Or(*[Taken(c, g, s) for g in GRADES for s in all_sems])

        # set up 1-arg and 2-arg Taken for history courses so coreq/prereq exprs referencing them resolve correctly
        for c in history_ids:
            for s in all_sems:
                solver[Taken(c, s)] = Or(*[Taken(c, g, s) for g in GRADES])
            solver[Taken(c)] = Or(*[Taken(c, g, s) for g in GRADES for s in all_sems])

        new_courses = sum(solver[Taken(cid)] for cid in to_plan_from)

        prereqs = {cid: c.prereq for cid, c in CATALOG.items() if c.prereq}

        for cid, expr in prereqs.items():
            # we're not checking pre-reqs in history
            if cid in history_ids.keys() | must_exclude: continue

            solver.implies(Taken(cid), expr)

            for p in get_courses(expr):
                for s in all_sems:
                    if s < starting_semester: continue
                    prior_taken = [Taken(p, ps) for ps in all_sems if ps < s]
                    if prior_taken:
                        # prereq p must be taken in some earlier semester
                        solver.implies(Taken(cid, s), Or(*prior_taken))
                    elif p not in history_ids:
                        # first possible semester and prereq not in history — can't take cid here
                        for g in GRADES:
                            solver.ensure(Taken(cid, g, s), 0)

        # coreq: must be taken same semester or before (≤ rather than < for prereqs)
        for cid, c in CATALOG.items():
            if not c.coreq or cid in history_ids.keys() | must_exclude: continue
            solver.implies(Taken(cid), c.coreq)
            for p in get_courses(c.coreq):
                for s in all_sems:
                    if s < starting_semester: continue
                    same_or_prior = [Taken(p, ps) for ps in all_sems if ps <= s]
                    if same_or_prior:
                        solver.implies(Taken(cid, s), Or(*same_or_prior))

        # anti_req: cannot take this course if these courses are taken (before or with)
        for cid, c in CATALOG.items():
            if not c.anti_req or cid in history_ids.keys() | must_exclude: continue
            solver.forbids(Taken(cid), c.anti_req)

        # credit limit per semester to spread courses out (only for new semesters)
        future_sems = list(semester_range(starting_semester, MAX_SEM))
        for s in future_sems:
            solver.require(solver.le(sum(solver[Taken(c, s)] * credits(c) for c in to_plan_from), CREDIT_LIMIT))

        sem_idx = lambda s: s[0] * 4 + s[1]
        # for each course: linear expr = semester index when taken, 0 if not taken
        course_sems = [sum(sem_idx(s) * solver[Taken(c, s)] for s in future_sems) for c in to_plan_from]
        last_sem = solver.max_of(course_sems, hi=max(sem_idx(s) for s in future_sems)) if course_sems else 0

        # grade sum: direct weighted sum (no element constraint needed)
        grade_sum = sum(solver[Taken(c, g)] * int(grade_to_points[g] * 100) for c in to_plan_from for g in GRADES)
        objectives = [last_sem, new_courses, grade_sum]
        solver.minimize(objectives)


    status, obj = solver.solve()
    solver.print_metrics()

    if obj is None:
        print("No solution:", status)
        return {}

    if check:
        print(f"Status: {status} — {obj} / {len(req_vars)} requirements met\n")

    planned = {}
    if not check:
        # extract grades and semesters directly from active ground BoolVars
        for cid in to_plan_from | (must_include - history_ids.keys()):
            picked = False
            for g in GRADES:
                for s in all_sems:
                    if solver.value(Taken(cid, g, s)):
                        grades[cid] = g
                        planned[cid] = s
                        picked = True
                        break
                if picked:
                    break
        print(f"Status: {status} — {len(set(planned.values()))} more semester(s)\n")

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
        print(f"{name} : {', '.join(fmt(c, grades) for c in wit)}")

    checked['degree'] = (all(v for v, _ in checked.values()), [])

    if not check:
        witnessed = {c for (_, wit) in checked.values() for c in wit if c in CATALOG}
        additional = sorted(c for c in planned if c not in witnessed)
        checked['additional'] = (True, additional)
        print(f"additional : {', '.join(fmt(c, grades) for c in additional)}")
        # printing semester-wise schedule of courses
        by_s = {}
        for cid, s in planned.items():
            by_s.setdefault(s, []).append(cid)
        print(f"New courses to take ({len(planned)}):")
        if not by_s:
            print("  none")
        for s in sorted(by_s):
            yr, sn = s
            total = sum(credits(c) for c in by_s[s])
            print(f"  year:{yr} semester:{SEM_NAMES[sn]} ({total} cr): {', '.join(fmt(c, grades) for c in sorted(by_s[s]))}")

    return checked, planned, grades

def fmt(cid, grades):
    return f"{cid} ({grades[cid]})" if cid in grades else cid

if __name__ == '__main__':
    # Test: student has taken intro programming + CSE 220
    taken_ids = {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 220'}
    history   = [Taken(cid, CATALOG[cid].credits, "A", (1, 1), "SB") for cid in taken_ids]
    plan_courses([], Major("CSE"), Standing("U4"), check=False)
