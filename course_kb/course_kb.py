from collections import namedtuple

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
    domain = None      ## None for boolean, list of ordered domain

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

class Passed(Requirement):    ## e.g. passed("CSE 101"), passed("AMS 210", "B")
    ## by default, we assume passing means C or higher because that's the only case in cse courses.
    ## other programs may have 'passed with B or higher'.
    def __init__(self, *arguments):
        if len(arguments) == 1:
            arguments = (arguments[0], 'C')
        super().__init__(*arguments)

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
class Not(LogicalExpr): pass

## requirements that appear as witnesses (course-level predicates, not student attributes)
witness_types = (Taken, Passed, Coregister)

## retrieve all witness predicates from an And-Or expression
def get_reqs(expr):
    if isinstance(expr, witness_types): return {expr}
    if isinstance(expr, Requirement):   return set()
    if isinstance(expr, LogicalExpr):   return set().union(*(get_reqs(op) for op in expr.operands))
    return set()

## retrieve all witness argument values (course IDs) from an And-Or expression
def get_courses(expr):
    return {arg for req in get_reqs(expr) for arg in req.arguments}

# common constants

MAX_SEMS_ALLOWED = 40       # upper bound on future semesters
CREDIT_LIMIT = 15  # max credits per semester

SEM_NAMES = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}

# For the purpose of determining grade point average, grades are assigned
# point values as follows:
grade_points = {
  'A': 4.00, 'A-': 3.67,
  'B+': 3.33, 'B': 3.00, 'B-': 2.67,
  'C+': 2.33, 'C': 2.00, 'C-': 1.67,
  'D+': 1.33, 'D': 1.00,
  'F': 0.00, 'I/F': 0.00, 'Q': 0.00
}