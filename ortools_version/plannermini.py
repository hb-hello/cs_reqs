from pprint import pprint
from .solver import ORModel
from .course_catalog import CATALOG, upper_division, COURSE_OFFERED_TERMS, Passed, TakenId, Taken, Major, Standing, UnsupportedRequirement, Permission, And, Or, get_reqs, Requirement, grade_points, MAX_SEMS_ALLOWED, CREDIT_LIMIT, transform_leaves, course_of, semester_range
def C_or_higher(grade): return grade in {'A','A-','B+','B','B-','C+','C'}
def upper_division(course): return int(course[4:])>=300
class Semester(Requirement): pass
class Grade(Requirement): pass
class SciSubset(Requirement): pass
class Prereq(Requirement): pass
class Coreq(Requirement): pass
class Antireq(Requirement): pass
def best_attempts(history):
    best={}
    for h in history:
        if h.grade not in grade_points: continue
        if h.id not in best or grade_points[h.grade]>grade_points[best[h.id].grade]: best[h.id]=h
    return list(best.values())
def print_schedule(planned,grades,credits_fn):
    by_sem={}
    for cid,s in planned.items(): by_sem.setdefault(s,[]).append(cid)
    print(f"New courses to take ({len(planned)}):")
    for s in sorted(by_sem):
        yr,sn=s
        total=sum(credits_fn(c) for c in by_sem[s])
        print(f"  year:{yr} semester:{sn} ({total} cr): {', '.join(fmt(c,grades) for c in sorted(by_sem[s]))}")
def plan_courses(taken,*student_reqs,must_exclude=set(),must_include=set(),check=False,starting_semester=(1,1),ending_semester=None,course_offered_terms=None,debug_print=False):
    if must_include & must_exclude: return None
    or_model=ORModel(ignore=(UnsupportedRequirement,Permission))
    for student_req in student_reqs: or_model[student_req]=1
    course_offered_terms=COURSE_OFFERED_TERMS if course_offered_terms is None else course_offered_terms
    Grade.domain=sorted(grade_points.keys(),key=grade_points.get)
    base=min((h.when for h in taken),default=starting_semester)
    sem_domain_limit=ending_semester if ending_semester is not None else MAX_SEMS_ALLOWED
    Semester.domain=list(semester_range(base,sem_domain_limit))
    starting_semester=max(starting_semester,base)
    history_ids={h.id:h for h in taken}
    to_plan_from=CATALOG.keys()-(history_ids.keys()|must_exclude)
    to_plan_from&=course_offered_terms.keys()
    for cid,h in history_ids.items():
        or_model[Grade(cid)]=h.grade
        or_model[TakenId(cid)]=1
        or_model[Semester(cid)]=h.when
    for cid in to_plan_from|(must_exclude-history_ids.keys()): or_model.iff(TakenId(cid),Grade(cid))
    if not check:
        for cid in to_plan_from:
            or_model.iff(TakenId(cid),Semester(cid))
            offered_terms=course_offered_terms.get(cid)
            if offered_terms:
                offered_sems=[sem for sem in Semester.domain[1:] if sem>=starting_semester and sem[1] in offered_terms]
                if offered_sems: or_model.implies(TakenId(cid),Or(*[or_model.eq(Semester(cid),sem) for sem in offered_sems]))
                else: or_model[TakenId(cid)]=0
            else: or_model.implies(TakenId(cid),or_model.ge(Semester(cid),starting_semester))
        for cid in must_exclude-history_ids.keys(): or_model[TakenId(cid)]=0
        for cid in must_include: or_model[TakenId(cid)]=1
    or_model[Passed]=lambda c,g: or_model.ge(Grade(c),g)
    credits=lambda c: history_ids[c].credits if c in history_ids else CATALOG[c].credits
    reqs={}
    prog={'CSE 114','CSE 214','CSE 216'}
    prog2={'CSE 160','CSE 161','CSE 260','CSE 261'}
    dmath={'CSE 215'}
    dmath2={'CSE 150'}
    sys={'CSE 220'}
    intro_courses=prog|prog2|dmath|dmath2|sys
    reqs["intro"]=And(Or(And(*map(Passed,prog)),And(*map(Passed,prog2))),Or(And(*map(Passed,dmath)),And(*map(Passed,dmath2))),And(*map(Passed,sys)))
    theory={'CSE 303'}
    theory2={'CSE 350'}
    algo={'CSE 373'}
    algo2={'CSE 385'}
    other={'CSE 310','CSE 316','CSE 320','CSE 416'}
    adv_courses=theory|theory2|algo|algo2|other
    reqs["adv"]=And(Or(And(*map(Passed,theory)),And(*map(Passed,theory2))),Or(And(*map(Passed,algo)),And(*map(Passed,algo2))),And(*map(Passed,other)))
    elect_exclude={'CSE 475','CSE 495','CSE 300','CSE 301','CSE 312'}
    electives={c for c in CATALOG if c[:3]=='CSE' and upper_division(c) and credits(c)>=3 and c not in adv_courses|elect_exclude}
    reqs["elect"]=or_model.ge(sum(or_model.resolve(Passed(c)) for c in electives),4)
    calc={'AMS 151','AMS 161'}
    calc2={'MAT 125','MAT 126','MAT 127'}
    calc3={'MAT 131','MAT 132'}
    reqs["calc"]=Or(And(*map(Passed,calc)),And(*map(Passed,calc2)),And(*map(Passed,calc3)))
    alg={'MAT 211'}
    alg2={'AMS 210'}
    reqs["alg"]=Or(And(*map(Passed,alg)),And(*map(Passed,alg2)))
    fmath={'AMS 301'}
    sta={'AMS 310'}
    sta2={'AMS 311'}
    reqs["sta"]=And(And(*map(Passed,fmath)),Or(And(*map(Passed,sta)),And(*map(Passed,sta2))))
    bio={'BIO 201','BIO 204'}; bio2={'BIO 202','BIO 204'}; bio3={'BIO 203','BIO 204'}
    che={'CHE 131','CHE 133'}; che2={'CHE 152','CHE 154'}
    phy={'PHY 126','PHY 133'}; phy2={'PHY 131','PHY 133'}; phy3={'PHY 141','PHY 133'}
    sci_combs=[bio,bio2,bio3,che,che2,phy,phy2,phy3]
    reqs["sci_combo"]=Or(*[And(*[SciSubset(cid) for cid in comb]) for comb in sci_combs])
    sci_more={'AST 203','AST 205','CHE 132','CHE 321','CHE 322','CHE 331','CHE 332','GEO 102','GEO 103','GEO 112','GEO 123','GEO 122','PHY 125','PHY 127','PHY 132','PHY 134','PHY 142','PHY 251','PHY 252'}
    sci_ids=sorted(set().union(*sci_combs)|sci_more)
    for cid in sci_ids: or_model.implies(SciSubset(cid),TakenId(cid))
    sci_subset_grade_points=sum(or_model.apply(Grade(cid),lambda g,cr=credits(cid):int(grade_points[g]*100)*cr,iff=SciSubset(cid)) for cid in sci_ids)
    sci_subset_credits=sum(or_model[SciSubset(cid)]*credits(cid) for cid in sci_ids)
    reqs["sci"]=And(reqs["sci_combo"],or_model.ge(sci_subset_credits,9),or_model.ge(sci_subset_grade_points,200*sci_subset_credits))
    ethics_courses={'CSE 312'}
    reqs["ethics"]=And(*map(Passed,ethics_courses))
    writing_courses={'CSE 300'}
    reqs["writing"]=And(*map(Passed,writing_courses))
    witnesses={req:get_reqs(expr) for req,expr in reqs.items()}
    witnesses["elect"]={Passed(c) for c in electives}
    witnesses["sci"]={SciSubset(c) for c in sci_ids}
    transfer_ids={h.id for h in taken if h.where!='SB'}
    items123_courses=(intro_courses|adv_courses|electives)-transfer_ids
    items23_courses=(adv_courses|electives)-transfer_ids
    reqs['credits_at_SB']=And(or_model.ge(sum(or_model[Passed(c)]*credits(c) for c in items123_courses),24),or_model.ge(sum(or_model[Passed(c)]*credits(c) for c in items23_courses),18))
    grades={h.id:h.grade for h in taken}
    req_vars={name:or_model.resolve(expr) for name,expr in reqs.items()}
    if check:
        for cid in to_plan_from: or_model[TakenId(cid)]=0
        or_model.maximize(sum(req_vars.values()))
    else:
        for v in req_vars.values(): or_model.require(v)
        new_courses=sum(or_model[TakenId(cid)] for cid in to_plan_from)
        or_model[Prereq]=lambda cid,req: or_model.resolve(And(req,or_model.ge(or_model[Semester(cid)]-or_model[Semester(course_of(req))],1)))
        or_model[Coreq]=lambda cid,req: or_model.resolve(And(req,or_model.eq(or_model[Semester(cid)]-or_model[Semester(course_of(req))],0)))
        or_model[Antireq]=lambda cid,req: or_model.resolve(req).negated()
        for cid in to_plan_from:
            for expr,pred in ((CATALOG[cid].prereq,Prereq),(CATALOG[cid].coreq,Coreq)):
                if expr: or_model.implies(TakenId(cid),transform_leaves(expr,lambda req,c=cid,P=pred: P(c,req)))
            if CATALOG[cid].anti_req: or_model.forbids(TakenId(cid),CATALOG[cid].anti_req)
        for sem in (s for s in Semester.domain if s>=starting_semester):
            sem_credits=[credits(cid)*or_model.eq(Semester(cid),sem) for cid in to_plan_from]
            if sem_credits: or_model.require(or_model.le(sum(sem_credits),CREDIT_LIMIT))
        grade_sum=sum(or_model.apply(Grade(cid),lambda g:int(grade_points[g]*100),iff=TakenId(cid)) for cid in to_plan_from)
        last_sem=or_model.max_of(or_model[Semester(cid)] for cid in to_plan_from)
        or_model.minimize([last_sem,new_courses,grade_sum])
    solution=or_model.solve()
    if debug_print: solution.print_metrics()
    if solution.obj is None:
        print("No solution:",solution.status)
        return {}
    if debug_print and check: print(f"Status: {solution.status} — {solution.obj} / {len(req_vars)} requirements met\n")
    planned={}
    if not check:
        planned={cid:solution.value(Semester(cid)) for cid in to_plan_from if solution.value(Semester(cid))}
        if debug_print: print(f"Status: {solution.status} — {len(set(planned.values()))} more semester(s)\n")
        for cid in planned:
            if cid not in grades: grades[cid]=solution.value(Grade(cid))
    items123_cr=sum(credits(c) for c in items123_courses if solution.value(Passed(c)))
    items23_cr=sum(credits(c) for c in items23_courses if solution.value(Passed(c)))
    witnesses['credits_at_SB']={f"items123 = {items123_cr}",f"items23 = {items23_cr}"}
    checked={}
    for name in sorted(witnesses):
        wit=sorted(req.arguments[0] for req in witnesses[name] if isinstance(req,Requirement) and solution.value(req))
        wit+=sorted(req for req in witnesses[name] if isinstance(req,str))
        satisfied=bool(solution.value(req_vars[name])) if check and name in req_vars else True
        checked[name]=(satisfied,wit)
        if debug_print: print(f"{name} : {', '.join(fmt(c,grades) for c in wit)}")
    checked['degree']=(all(v for v,_ in checked.values()),[])
    if not check:
        witnessed={c for (_,wit) in checked.values() for c in wit if c in CATALOG}
        additional=sorted(c for c in planned if c not in witnessed)
        checked['additional']=(True,additional)
        if debug_print:
            print(f"additional : {', '.join(fmt(c,grades) for c in additional)}")
            print_schedule(planned,grades,credits)
    if debug_print: solution.print_metrics()
    return checked,planned,solution.metrics()
def fmt(cid,grades): return f"{cid} ({grades[cid]})" if cid in grades else cid
if __name__=='__main__':
    taken_ids={'CSE 114','CSE 214','CSE 216','CSE 220'}
    print([COURSE_OFFERED_TERMS[t] for t in taken_ids])
    history=[Taken(cid,CATALOG[cid].credits,"A",(2024,1),"SB") for cid in taken_ids]
    plan_courses(history,Major("CSE"),Standing("U4"),starting_semester=(2024,2),ending_semester=(2025,4),check=False,debug_print=True)