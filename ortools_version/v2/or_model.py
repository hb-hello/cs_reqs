from ortools.sat.python import cp_model, Domain
from collections.abc import Iterable

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


