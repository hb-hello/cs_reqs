from ortools.sat.python import cp_model, Domain
from collections.abc import Iterable
from .course_catalog import (
    CATALOG, upper_division, COURSE_OFFERED_TERMS,
    TakenId, Taken, C_or_higher, B_or_higher, B_plus_or_higher, D_or_higher, Major, Standing, UnsupportedRequirement, Permission,
    And, Or, get_reqs, Requirement, grade_points, semester_range,
    MAX_SEMS_ALLOWED, CREDIT_LIMIT, transform_leaves, cid_from,
    get_sem_distance, sem_to_int, int_to_sem, rel_sem_to_term, Coregister
)

class Vars(dict): # technically a var holder?
    def __init__(self, domain:Iterable=None, model:ORModel=None):
        self.domain = domain
        self.integer = True if domain and len(domain) > 2 else False
        self.model = model
        super().__init__()

    def __getitem__(self, key):
        if key not in super():
            self.__setitem__(key, self.model.new_var(self.domain, self.is_integer))
        return super().__getitem__(key)
    
    def __setitem__(self, key, value):
        if key in super():
            raise "can't replace existing var"
        if not isinstance(value, cp_model.IntVar):
            raise "can only store values of type cp_model.IntVar"
        super().__setitem__(self, key, value)

class LogicalExpr(Vars):
    pass
        
class ORModel:
    def __init__(self, ignore=(), plan=False):
        self.model   = cp_model.CpModel()
        self.counter = 0 #monotonic id for vars
        self.indices = {}
        self.requirements = {} # populated with a tree on each require call

    def vars(self, domain=None):
        return Vars(domain, self.model)
    
    def var(self, expr):
        if isinstance(expr, cp_model.BoundedLinearExpression):
            v = self.new_var()
            self.model.add(expr).only_enforce_if(v)
            return v
    
    def new_var(self, domain, is_integer=False):
        self.counter += 1
        name = f"var_{self.counter}"
        if is_integer and domain:
            d = cp_model.Domain.from_values(domain)
            return self.model.new_int_var_from_domain(d, name)
        else: return self.model.new_bool_var(name)

if __name__ == "__main__":
    m = ORModel(ignore=(UnsupportedRequirement, Permission), plan=False)

    GRADES = sorted(grade_points.keys(), key=grade_points.get)
    int_grade = {grade: i for i, grade in enumerate(GRADES, start=1)}
    grade_of_int = {i: grade for grade, i in int_grade.items()}
    
    grade = m.vars(domain=sorted(int_grade.values()))
    credits = m.vars(domain=[1, 2, 3])

    def c_or_higher(course): return grade[course] >= int_grade['C']
    def b_or_higher(course): return grade[course] >= int_grade['B']
    def b_plus_or_higher(course): return grade[course] >= int_grade['B+']
    def d_or_higher(course): return grade[course] >= int_grade['D']

    reqs = {}
    # 1. Required Introductory Courses
    prog = {'CSE 114', 'CSE 214', 'CSE 216'}
    # prog = {*map(PassedId, {{'CSE 114', 'CSE 214', 'CSE 216'}})} is this better as it expresses the PassedId requirement right here in prog itself?
    prog2 = {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'}  ## Honors
    dmath = {'CSE 215'}
    dmath2 = {'CSE 150'}  # Honors
    sys = {'CSE 220'}
    intro_courses = prog | prog2 | dmath | dmath2 | sys

    And[Or[And[*map(c_or_higher, prog)]]]

    #should c_or_higher be a function we call? or should it be a dict of vars like grade and credits?

    reqs["intro"] = m.require(And(Or(And(*map(c_or_higher, prog)), And(*map(c_or_higher, prog2))), Or(And(*map(c_or_higher, dmath)), And(*map(c_or_higher, dmath2))), And(*map(c_or_higher, sys))), "intro")

    #python-like 
    prog <= c_or_higher and prog2 <= c_or_higher

    # subset as func?
    Or(c_or_higher.subset(prog), c_or_higher.subset(prog))

    Or[(c_or_higher[cid] for cid in prog)]

    # if c_or_higher is 


