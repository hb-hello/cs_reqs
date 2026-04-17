from collections import namedtuple
import csv
from pathlib import Path

## Representation for course
## Each course: id, desc, prereqs, antireqs, coreqs, SBC, credits, ...
##   Fields are written in the order they appear in the input. Optional fields are None by default.
##   For requisites, we keep the original string as is. All requisites are optional.
Course = namedtuple('Course',
                    ['id',                  ## string: e.g. 'CSE 101'
                     'title',               ## string: e.g. 'Intro to Computer Science'
                    'desc',                 ## string: course description
                    'prereq',               ## optional, And/Or structure (see below)
                    'coreq',
                    'anti_req',
                    'pre_or_coreq',
                    'advisory_prereq',
                    'advisory_coreq',       ## same as prereq
                    'advisory_pre_or_coreq',
                    'category',             ## optional: set of tuples where the first element is the category name e.g. SBC,
                                            ##   second element is a list of category values, e.g. ('TECH', ...)
                    'credits',              ## string: (e.g. '3', '4', '0-3')
                    'grading',              ## optional, string: special grading, such as S/U
                    ])

class Expr:
    def __eq__(self, other):    return type(self) is type(other) and self.arguments == other.arguments
    def __hash__(self):         return hash((type(self), tuple(self.arguments)))

## Represent each requirement in requisites.
class Requirement(Expr):
    name: str = ""     ## "taken", "passed", ...

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.name = cls.__name__.lower()

    def __init__(self, *arguments):
        self.arguments = list(arguments)

    def __repr__(self):
        arg_str = ",".join(repr(arg) for arg in self.arguments)
        return f'{self.name}({arg_str})'

class Taken(Requirement):     ## e.g. taken_id("CSE 303"), taken_id("CSE 350")
                               ###    named taken_id to avoid clash with taken/5 in prolog and clingo.
    pass                       ###    TODO: better name?

class Passed(Requirement):
    def __init__(self, course_id, min_grade):
        self.course_id = course_id
        self.min_grade = min_grade
        super().__init__(course_id, min_grade)

    def __repr__(self):
        if type(self) is Passed:
            return f'Passed({self.course_id}, {self.min_grade})'
        return f'{type(self).__name__}({self.course_id})'

class C_or_higher(Passed):
    def __init__(self, course_id):
        super().__init__(course_id, 'C')

class B_or_higher(Passed):
    def __init__(self, course_id):
        super().__init__(course_id, 'B')

class Major(Requirement):     ## e.g. cse_major
    pass

class Standing(Requirement):   ## e.g. u3_standing
    pass

class Permission(Requirement):
    pass

class Coregister(Requirement):
    ## a course needs to be taken together with another course.
    ### 'hack' to represent prereq OR coreq logic such as: "prereq: C1 or coreq C2"
    ###    which is represented as prereq: Or([Taken("C1"), Coregister("C2")])
    pass

class UnsupportedRequirement(Requirement):    ## to wrap all unsupported formats
    name = "unsupported"   ## override: "unsupportedrequirement" would be wrong

    def __repr__(self):
        return f'unsupported("{self.arguments[0]}")'

class LogicalExpr(Expr):
    def __init__(self, *subexprs):
        if len(subexprs) == 1 and isinstance(subexprs[0], list):
            subexprs = subexprs[0]
        self.subexprs = list(subexprs)

    @property
    def operands(self): return self.subexprs   ## for solver compatibilty, should we name it operands everywhere?

    def __repr__(self):
        return f"{type(self).__name__}({', '.join(repr(s) for s in self.subexprs)})"

## Represent a list of conjuncts.
class And(LogicalExpr): pass

## Represent a list of disjuncts.
class Or(LogicalExpr):  pass

class Not(LogicalExpr):
    def __init__(self, negated_expr):
        self.negated_expr = negated_expr
        super().__init__(negated_expr)

## requirements that appear as witnesses (course-level predicates, not student attributes)
witness_types_ignore = (Major, Standing, Permission, UnsupportedRequirement)

## retrieve all witness predicates from an And-Or expression
def get_reqs(expr):
    if isinstance(expr, witness_types_ignore): return set()
    if isinstance(expr, Requirement):   return {expr}
    if isinstance(expr, LogicalExpr):   return set().union(*(get_reqs(op) for op in expr.operands))
    return set()

## retrieve all witness argument values (course IDs) from an And-Or expression
def get_courses(expr):
    return {arg for req in get_reqs(expr) for arg in req.arguments}

def transform_leaves(expr, fn):
    """Apply fn to every leaf (non-And/Or) node, preserving tree structure."""
    if isinstance(expr, (And, Or)):
        return type(expr)(*[transform_leaves(op, fn) for op in expr.operands])
    if isinstance(expr, (UnsupportedRequirement, Permission)):
        # Hardcode: these leaves are ignored by solvers and should never be wrapped.
        return expr
    return fn(expr)

def course_of(req):
    """Extract the course ID from a leaf requirement (e.g. Passed, Taken)."""
    return req.arguments[0]

# common constants

MAX_SEMS_ALLOWED = 40       # upper bound on future semesters
CREDIT_LIMIT = 15  # max credits per semester

SEM_NAMES = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}

def read_course_offered(csv_path='course_offered.csv'):
    base_dir = Path(__file__).resolve().parent
    path = Path(csv_path)
    if not path.is_absolute():
        path = base_dir / path

    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        return {
            row[0].strip(): {           # row[0] is course ID
                int(term.strip())
                for term in (row[1].strip() if len(row) > 1 else '').split(',')
                if term.strip().isdigit() and int(term.strip()) in {1, 2, 3, 4}
            }
            for row in reader
            if row and row[0].strip()
        }

COURSE_OFFERED_TERMS = read_course_offered('course_offered.csv')

# For the purpose of determining grade point average, grades are assigned
# point values as follows:
grade_points = {
  'A': 4.00, 'A-': 3.67,
  'B+': 3.33, 'B': 3.00, 'B-': 2.67,
  'C+': 2.33, 'C': 2.00, 'C-': 1.67,
  'D+': 1.33, 'D': 1.00,
  'F': 0.00, 'I/F': 0.00, 'Q': 0.00
}

def get_sem_distance(sem_before: tuple, sem_after: tuple): ## sem1, sem2 are (year, term) tuples
  return (sem_after[0] - sem_before[0]) * 4 + (sem_after[1] - sem_before[1])

def sem_to_int(sem: tuple, min_sem: tuple):
  return get_sem_distance(min_sem, sem) + 1

def int_to_sem(sem_int: int, min_sem: tuple):
  distance = sem_int - 1
  year = min_sem[0] + (min_sem[1] - 1 + distance) // 4
  term = (min_sem[1] - 1 + distance) % 4 + 1
  return (year, term)

def rel_sem_to_term(sem_int: int, min_sem: tuple) -> int:
  # sem_int is relative semester index (1..N)
  return ((min_sem[1] - 1) + (sem_int - 1)) % 4 + 1

if __name__ == "__main__":
    print(COURSE_OFFERED_TERMS)