from ortools.sat.python import cp_model
from collections.abc import Iterable, MutableMapping
from collections import UserDict


class Vars(UserDict):  # technically a var holder?
    def __init__(self, domain: Iterable = None, model: ORModel = None):
        self.domain = domain
        self.is_integer = True if domain and len(domain) > 2 else False
        self.model = model
        super().__init__()

    def __getitem__(self, key):
        if key not in self.data:
            self.__setitem__(key, self.model.new_var(self.domain, self.is_integer))
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key in self:
            raise "can't replace existing var"
        # call self.model.var instead.
        if not isinstance(value, cp_model.IntVar):
            # raise "can only store values of type cp_model.IntVar"
            v = self.model.var(value)
            if v:
                super().__setitem__(key, v)
        super().__setitem__(key, value)


class SpecialVars(Vars):
    def __init__(self, domain: Iterable = None, model: ORModel = None, op=None):
        self.op = op
        super().__init__(domain, model)


class ORModel:
    def __init__(self, ignore=(), plan=False):
        self.model = cp_model.CpModel()
        self.counter = 0  # monotonic id for vars
        self.indices = {}
        self.requirements = {}  # populated with a tree on each require call

    def vars(self, domain=None):
        return Vars(domain, self)

    def var(self, expr):
        if isinstance(expr, cp_model.BoundedLinearExpression):
            v = self.new_var()
            self.model.add(expr).only_enforce_if(v)
            return v
        return None

    def new_var(self, domain, is_integer=False):
        self.counter += 1
        name = f"var_{self.counter}"
        if is_integer and domain:
            d = cp_model.Domain.from_values(domain)
            return self.model.new_int_var_from_domain(d, name)
        else:
            return self.model.new_bool_var(name)


if __name__ == "__main__":
    m = ORModel()

    o = m.vars()
    ble = (o[1] * o[4]) + (o[2] * 9) > o[3]
    print(type(ble))
