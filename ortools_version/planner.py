from pprint import pprint

from .solver import ORModel
from .course_catalog import (
    CATALOG, upper_division, COURSE_OFFERED_TERMS,
    TakenId, Taken, C_or_higher, B_or_higher, B_plus_or_higher, D_or_higher, Major, Standing, UnsupportedRequirement, Permission,
    And, Or, get_reqs, Requirement, grade_points, semester_range,
    MAX_SEMS_ALLOWED, CREDIT_LIMIT, transform_leaves, cid_from,
    get_sem_distance, sem_to_int, int_to_sem, rel_sem_to_term, Coregister,
    Prereq, Coreq, AntiReq,
)

GRADES = sorted(grade_points.keys(), key=grade_points.get)
int_grade = {grade: i for i, grade in enumerate(GRADES, start=1)}
grade_of_int = {i: grade for grade, i in int_grade.items()}

## whether a class is upper-division, i.e., 300-level or above
def upper_division(course): return int(course[4:]) >= 300

class ReqWithDomain(Requirement):
    default_domain = None
    def __init__(self, cid, domain=None):
        self._domain = domain
        super().__init__(cid)
    @property
    def domain(self):
        return self._domain if self._domain is not None else self.default_domain

class Sem(ReqWithDomain): pass   ## predicate to represent grade that student has achieved in a course
class Grade(ReqWithDomain): pass   ## predicate to represent grade that student has achieved in a course
# class SciSubset(Requirement): pass # to track the sci subset


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
def plan_courses(taken, *student_reqs, must_exclude=set(), must_include=set(), check=False, start_sem=(1, 1), end_sem=None, course_offered_terms=None, debug_print=False, course_catalog=None):

    if must_include & must_exclude:
        return None # infeasible

    m = ORModel(ignore=(UnsupportedRequirement, Permission), plan=not check)

    # set up student requirements in the model
    for student_req in student_reqs:
        m[student_req] = 1

    course_offered_terms = course_offered_terms or COURSE_OFFERED_TERMS
    catalog = course_catalog or CATALOG
    # setting up the domain of the grade variable, order is important to enable comparisons below
    Grade.default_domain = sorted(int_grade.values())

    # setting up the domain for semesters; base anchors the domain, starting_semester clamped within it
    base = min((h.when for h in taken), default=start_sem)
    all_sems = list(semester_range(base, end_sem))
    Sem.default_domain = [i for i, _ in enumerate(all_sems, start=1)]
    start_sem = max(start_sem, base)
    sems_to_plan = list(semester_range(start_sem, end_sem))
    if end_sem is None and sems_to_plan:
        end_sem = sems_to_plan[-1]

    def int_sem(sem): return sem_to_int(sem, base)
    def decode_sem(encoded): return all_sems[encoded - 1]

    history = {h.id: h for h in taken}

    to_plan_from = catalog.keys() - (history.keys() | must_exclude)
    to_plan_from &= course_offered_terms.keys()

    # courses not in history and not plannable (not offered in any term) cannot be taken
    for cid in catalog.keys() - to_plan_from - history.keys():
        m[TakenId(cid)] = 0

    for cid, h in history.items():
        m[Grade(cid)] = int_grade[h.grade]
        m[TakenId(cid)] = 1
        m[Sem(cid)] = int_sem(h.when)

    for cid in to_plan_from | (must_exclude - history.keys()):
        # grade is assigned iff course is taken (needed in both check/plan modes)
        m.iff(TakenId(cid), Grade(cid))

    # plan mode
    if not check:
        for cid in to_plan_from:
            # course has semester assigned if and only if we take the course
            offered_sessions = course_offered_terms.get(cid)
            if offered_sessions:
                # term-restricted: must land in one of the valid allowed slots
                offered_sems = [int_sem(sem) for sem in sems_to_plan if sem[1] in offered_sessions]
                if offered_sems:
                    m.set_domain(Sem(cid), offered_sems)
                    m.iff(TakenId(cid), Sem(cid))
                else: # can't take the course if it is not offered in any of the semesters
                    m[TakenId(cid)] = 0
            else: # can't take the course if it is not offered in any of the semesters
                m[TakenId(cid)] = 0

        # hardcoded must_exclude courses to zero
        for cid in must_exclude - history.keys():
            m[TakenId(cid)] = 0

        # hardcoded must_include courses to 1
        for cid in must_include:
            m[TakenId(cid)] = 1

    # def passed(course, with_grade_at_least='C'): return m.resolve(m[Grade(course)] >= int_grade[with_grade_at_least])
    def c_or_higher(course): return m.resolve(m[Grade(course)] >= int_grade['C'])
    def b_or_higher(course): return m.resolve(m[Grade(course)] >= int_grade['B'])
    def b_plus_or_higher(course): return m.resolve(m[Grade(course)] >= int_grade['B+'])
    def d_or_higher(course): return m.resolve(m[Grade(course)] >= int_grade['D'])
    m[C_or_higher] = c_or_higher
    m[B_or_higher] = b_or_higher
    m[B_plus_or_higher] = b_plus_or_higher
    m[D_or_higher] = d_or_higher

    # use actual credits earned from history if available, else for future courses get credits from the catalog
    credits = lambda c: history[c].credits if c in history else catalog[c].credits

    reqs = {}
    # 1. Required Introductory Courses
    prog = {'CSE 114', 'CSE 214', 'CSE 216'}
    # prog = {*map(PassedId, {{'CSE 114', 'CSE 214', 'CSE 216'}})} is this better as it expresses the PassedId requirement right here in prog itself?
    prog2 = {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'}  ## Honors
    dmath = {'CSE 215'}
    dmath2 = {'CSE 150'}  # Honors
    sys = {'CSE 220'}
    intro_courses = prog | prog2 | dmath | dmath2 | sys

    reqs["intro"] = m.require(And(Or(And(*map(C_or_higher, prog)), And(*map(C_or_higher, prog2))), Or(And(*map(C_or_higher, dmath)), And(*map(C_or_higher, dmath2))), And(*map(C_or_higher, sys))), "intro")

    # 2. Required Advanced Courses
    theory = {'CSE 303'}
    theory2 = {'CSE 350'}  # Honors
    algo = {'CSE 373'}
    algo2 = {'CSE 385'}  # Honors
    other = {'CSE 310', 'CSE 316', 'CSE 320', 'CSE 416'}
    adv_courses = theory | theory2 | algo | algo2 | other
    reqs["adv"] = m.require(And(Or(And(*map(C_or_higher, theory)), And(*map(C_or_higher, theory2))), Or(And(*map(C_or_higher, algo)), And(*map(C_or_higher, algo2))), And(*map(C_or_higher, other))))


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

    # reqs["elect"] = or_model.at_least(sum(or_model.resolve(PassedId(c)) for c in electives), 4)
    # elect_wit = or_model.require_with_wit(Or(*map(PassedId, electives)))
    reqs["elect"] = m.require(sum(m[C_or_higher(c)] for c in electives) >= 4, "elect")
    # reqs["elect"] = elect_req

    # 4. AMS 151, AMS 161 Applied Calculus I, II
    calc = {'AMS 151', 'AMS 161'}
    calc2 = {'MAT 125', 'MAT 126', 'MAT 127'}
    calc3 = {'MAT 131', 'MAT 132'}
    reqs["calc"] = m.require(Or(And(*map(C_or_higher, calc)), And(*map(C_or_higher, calc2)), And(*map(C_or_higher, calc3))))

    # 5. One of the following linear algebra courses
    alg = {'MAT 211'}
    alg2 = {'AMS 210'}
    reqs["alg"] = m.require(Or(And(*map(C_or_higher, alg)), And(*map(C_or_higher, alg2)))) # wrap in And just in case courses are added to the sets

    # 6. Both of the following:
    fmath = {'AMS 301'}
    sta =   {'AMS 310'}
    sta2 =  {'AMS 311'}
    reqs["sta"] = m.require(And(And(*map(C_or_higher, fmath)), Or(And(*map(C_or_higher, sta)), And(*map(C_or_higher, sta2)))))

    # 7. At least one natural science lecture/laboratory combination
    # each comb is a pair that must both be taken — Or across all valid pairs
    bio  = {'BIO 201', 'BIO 204'}; bio2 = {'BIO 202', 'BIO 204'}; bio3 = {'BIO 203', 'BIO 204'}
    che  = {'CHE 131', 'CHE 133'}; che2 = {'CHE 152', 'CHE 154'}
    phy  = {'PHY 126', 'PHY 133'}; phy2 = {'PHY 131', 'PHY 133'}; phy3 = {'PHY 141', 'PHY 133'}
    sci_combs = [bio, bio2, bio3, che, che2, phy, phy2, phy3]

    # sci_combo = Or(*[And(*[SciSubset(cid) for cid in comb]) for comb in sci_combs])
    sci_combo = Or(*[And(*[TakenId(cid) for cid in comb]) for comb in sci_combs])

    # 8. Additional natural science courses selected from above and following list
    # The courses selected in 7 and 8 must carry at least 9 credits total
    sci_more = {'AST 203', 'AST 205',
                'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332',
                'GEO 102', 'GEO 103', 'GEO 112', 'GEO 123', 'GEO 122',
                'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142',
                'PHY 251', 'PHY 252'}

    sci_ids  = sorted(set().union(*sci_combs) | sci_more)

    sci_grade_points = sum(m.apply(Grade(cid), 
                            lambda g, cr=credits(cid): int(grade_points[grade_of_int[g]] * 100) * cr, 
                            iff=TakenId(cid)) for cid in sci_ids)
    # unique_credit_total: counts each sci course once (for 9-credit min and GPA denominator)
    sci_credits = sum(m[TakenId(cid)] * credits(cid) for cid in sci_ids)

    # The grade point average for the courses in Requirements 7 and 8 must be
    # at least 2.00.
    # GPA >= 2.0  i.e.,  weighted_sum >= 200 * total_credits  (scaled by 100)
    reqs["sci"] = m.require(And(sci_combo, sci_credits > 9, sci_grade_points >= 200 * sci_credits), "sci")

    # 9. Professional Ethics
    ethics_courses = {'CSE 312'}
    reqs["ethics"] = m.require(And(*map(C_or_higher, ethics_courses)))

    # 10. Upper-Division Writing Requirement
    writing_courses = {'CSE 300'}
    reqs["writing"] = m.require(And(*map(C_or_higher, writing_courses)))

    # collect all reqs into witnesses
    witnesses = {req: get_reqs(expr) for req, expr in reqs.items()}
    # collect sci witness as the reqs entry is not a straightforward and/or expression
    # witnesses["elect"] = {PassedId(c) for c in electives}
    witnesses["sci"] = {TakenId(c) for c in sci_ids}

    # At least 24 credits from items 1 to 3, and at least 18 from 2 and 3, at Stony Brook
    transfer_ids = {h.id for h in taken if h.where != 'SB'}
    items123_courses = (intro_courses | adv_courses | electives) - transfer_ids
    items23_courses  = (adv_courses | electives) - transfer_ids    
    reqs['credits_at_SB'] = m.require(And(sum(m[C_or_higher(c)] * credits(c) for c in items123_courses) >= 24,
                                             sum(m[C_or_higher(c)] * credits(c) for c in items23_courses) >= 18))

    grades = {h.id: h.grade for h in taken}

    if check:
        for cid in to_plan_from: # ensure the solver can't plan any more courses
            m[TakenId(cid)] = 0
    else:
        # prereqs / coreqs / antireqs
        # for cid in to_plan_from:
        #     if catalog[cid].prereq:
        #         prereq, leaves = m.reify(catalog[cid].prereq, with_leaves=True)
        #         m.implies(TakenId(cid), prereq)
        #         for leaf, chosen in leaves.items():
        #             if isinstance(leaf, Coregister): m.implies(chosen, m[Sem(cid_from(leaf))] == m[Sem(cid)])
        #             else: m.implies(chosen, m[Sem(cid_from(leaf))] < m[Sem(cid)])
        #     if catalog[cid].coreq:
        #         coreq, leaves = m.reify(catalog[cid].coreq, with_leaves=True)
        #         m.implies(TakenId(cid), coreq)
        #         for leaf, chosen in leaves.items():
        #             m.implies(chosen, m[Sem(cid_from(leaf))] == m[Sem(cid)])
        #     if catalog[cid].pre_or_coreq:
        #         pre_or_coreq, leaves = m.reify(catalog[cid].pre_or_coreq, with_leaves=True)
        #         m.implies(TakenId(cid), pre_or_coreq)
        #         for leaf, chosen in leaves.items():
        #             m.implies(chosen, m[Sem(cid_from(leaf))] <= m[Sem(cid)])
        #     if catalog[cid].anti_req:
        #         anti_req, leaves = m.reify(catalog[cid].anti_req, with_leaves=True)
        #         m.implies(TakenId(cid), anti_req)
        #         for leaf, chosen in leaves.items():
        #             m.implies(chosen, m[Sem(cid_from(leaf))] < m[Sem(cid)])

        # prereqs / coreqs / antireqs via allreqs
        for cid in to_plan_from:
            if not catalog[cid].allreqs: continue
            sat, cid_cond = m.reify_new(catalog[cid].allreqs, negated=(AntiReq,))
            m.implies(TakenId(cid), sat)
            for (req_cid, conditions), chosen in cid_cond.items():
                if Major in conditions or Standing in conditions:
                    continue
                if Prereq in conditions or AntiReq in conditions:
                    m.implies(chosen, m[Sem(req_cid)] < m[Sem(cid)])
                elif Coreq in conditions:
                    m.implies(chosen, m[Sem(req_cid)] == m[Sem(cid)])

        # enforce credit limit per semester using the same encoded semester domain
        # to avoid comparing against semesters that are outside Semester.domain.
        for sem in range(int_sem(start_sem), int_sem(end_sem) + 1):
            sem_credits = [credits(cid) * m.eq(Sem(cid), sem) for cid in to_plan_from]
            if sem_credits: m.require(sum(sem_credits) <= CREDIT_LIMIT)

        # calculate total number of new courses taken
        new_courses = sum(m[TakenId(cid)] for cid in to_plan_from)

        # to minimize the grades possible
        grade_sum = sum(m.apply(Grade(cid), lambda g: int(grade_points[grade_of_int[g]] * 100), iff=TakenId(cid)) for cid in to_plan_from)

        # to minimize the number of semesters needed to graduate
        last_sem = m.max_of(m[Sem(cid)] for cid in to_plan_from)

        # minimizes the expressions in order of priority given
        m.minimize([last_sem, new_courses, grade_sum])

    # run the solver
    sol = m.solve()
    if debug_print: sol.print_metrics()

    if sol.obj is None:
        print("No solution:", sol.status)
        return None, {}, {}

    if debug_print:
        if check:
            print(f"Status: {sol.status} — {sol.obj} / {len(reqs)} requirements met\n")

    planned = {}
    if not check:
        planned = {
            cid: decode_sem(sol.value(Sem(cid)))
            for cid in to_plan_from
            if sol.value(TakenId(cid)) == 1
        }
        if debug_print:
            print(f"Status: {sol.status} — {len(set(planned.values()))} more semester(s)\n")

        for cid in planned:
            if cid not in grades:
                i = sol.value(Grade(cid))
                grades[cid] = grade_of_int[i] if i > 0 else None

    checked = {name: (bool(sol.value(v)), sorted({cid_from(leaf) for leaf in sol.chosen(v)})) for name, v in reqs.items()}
    items123_cr = sum(credits(c) for c in items123_courses if sol.value(c_or_higher(c)))
    items23_cr  = sum(credits(c) for c in items23_courses  if sol.value(c_or_higher(c)))
    checked['credits_at_SB'] = {f"items123 = {items123_cr}", f"items23 = {items23_cr}"}

    checked['degree'] = (all(v for v, _ in checked.values()), [])

    if not check:
        witnessed = {c for (_, wit) in checked.values() for c in wit if c in catalog}
        additional = sorted(c for c in planned if c not in witnessed)
        checked['additional'] = (True, additional)
        if debug_print:
            print_schedule(planned, grades, credits)

    if debug_print: 
        pprint(checked)
        sol.print_metrics()
    return checked, planned, sol.metrics()

def fmt(cid, grades):
    return f"{cid} ({grades[cid]})" if cid in grades else cid

if __name__ == '__main__':
    # Test: student has taken intro programming + CSE 220
    taken_ids = {'CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220'}
    FULL = {
        'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',                  ## intro
        'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',       ## adv
        'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',       ## elect
        'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',                  ## calc, sta, alg
        'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                             ## sci
        'CSE 300', 'CSE 312',                                                   ## writing, ethics
    }

    # pprint(CATALOG)
    # print(len(FULL))
    # print([COURSE_OFFERED_TERMS[t] for t in taken_ids])
    # history = [Taken('CSE 114', CATALOG['CSE 114'].credits, "A", (2024, 1), "SB")]
    history = [Taken(cid, CATALOG[cid].credits, "A", (2024, 1), "SB") for cid in FULL - {'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',}]
    plan_courses(history, Major("CSE"), Standing("U4"), start_sem=(2024, 1), end_sem=(2025, 4), check=False, debug_print=True)
