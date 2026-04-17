from ortools.sat.python import cp_model
from course_kb.course_kb import Expr, Requirement, LogicalExpr, Or
from collections.abc import Iterable

class Condition(Expr):
    def __init__(self, *arguments): self.arguments = arguments

def wit_expr(expr:cp_model.BoundedLinearExpression):
    if isinstance(expr, cp_model.BoundedLinearExpression):
        terms = [f"{c}*{v.name}" for c, v in zip(expr.coeffs, expr.vars)]
        return f"{' + '.join(terms)} + {expr.offset} in {expr.bounds}"
    if isinstance(expr, LogicalExpr):
        # Inorder traversal: recursively format each child, then join with operator
        parts = []
        for child in expr.subexprs:
            child_str = wit_expr(child, parent=expr)
            if (isinstance(child, LogicalExpr) and
                    not isinstance(child, Not) and
                    type(child) != type(expr)):
                child_str = f"({child_str})"
            parts.append(child_str)
        return f" {expr.op} ".join(parts)
    else: return repr(expr)

class Var(Requirement): # the "variable-representing" class represents a decision that the solver can take.
    default_domain = None
    # default_encoded = None
    def __init__(self, *args, domain:Iterable=None):
        self._domain = domain
        # self._encoded = self._encode(domain) if isinstance(domain, Iterable) else {}
        super().__init__(*args)
    # @property
    # def encoded(self):
    #     if self._encoded is None:
    #         if self.domain is None: 
    #             if self.default_encoded is None: self.default_encoded = self._encode(self.default_domain)
    #             return self.default_encoded
    #         self._encoded = self._encode(self.domain)
    #     return self._encoded

    @property
    def domain(self):
        return self._domain if self._domain is not None else self.default_domain
    
    def __setattr__(self, name, value):
        if name == "domain" and isinstance(value, Iterable): 
            self._domain = value
    #         self._encoded = self._encode(value)
    # def _encode(domain:Iterable=None):
    #     return {val: i + 1 for i, val in enumerate(domain)} if domain else {}
    

# stores, indexes and adds variables to the CP-SAT model
class ORModel:
    def __init__(self, ignore=()):
        self.model   = cp_model.CpModel()
        self._solver = None         # created on solve()
        self._vars   = {}           # Requirements/classes converted to BoolVars or lambdas
        self._domains = {}          # var id -> domain size (upper bound; avoids Proto() calls)
        self._encoders = {}         # pred_class -> encode_dict (cached from class domain)
        self._pinned = {}           # pred -> pinned bool value (0 or 1), for selector mirroring
        self.ignore  = tuple(ignore)

    # lazily build and cache the encode dict from a Requirement class's domain
    def _encoder(self, cls):
        if hasattr(cls, "domain") and cls not in self._encoders and isinstance(cls.domain, list):
            self._encoders[cls] = {v: i + 1 for i, v in enumerate(cls.domain)} | {None: 0}
        return self._encoders.get(cls)

    # allows Python's default indexing -> solver[key]
    # automatically identifies the type of model variable needed from the domain
    def __getitem__(self, pred):
        if pred not in self._vars:
            cls = type(pred)
            if cls in self._vars and callable(self._vars[cls]):
                self._vars[pred] = self._vars[cls](*pred.arguments)
            else:
                domain = getattr(pred, 'domain', None)
                if isinstance(domain, list):
                    n = len(domain) - 1   # max index
                    # if domain has 1 or 2 values we default to boolvar
                    if n <= 1:
                        self._vars[pred] = self.model.new_bool_var(str(pred))
                        if n == 0: self.model.add(self._vars[pred] == 0)
                        self._domains[id(self._vars[pred])] = 1
                    else:
                        # if domain has more than 2 values we create an int var
                        self._vars[pred] = self.model.new_int_var(0, len(domain), str(pred))
                        self._domains[id(self._vars[pred])] = len(domain)
                elif domain is None:
                    # if domain is None, we default to boolvar
                    self._vars[pred] = self.model.new_bool_var(str(pred))
                    self._domains[id(self._vars[pred])] = 1
                else: return
        return self._vars[pred]

    # allows the in operator to work naturally
    def __contains__(self, pred):
        return pred in self._vars

    # solver[PredClass] = lambda  → register query
    # solver[pred] = model_var    → store computed result
    # solver[pred] = Expr         → store resolved constraint
    # solver[pred] = scalar       → pin value (replaces ensure)
    def __setitem__(self, pred, expr):
        if isinstance(pred, type) and callable(expr):
            self._vars[pred] = expr
        elif isinstance(expr, Expr):
            self._vars[pred] = self.resolve(expr)
        elif isinstance(expr, cp_model.IntVar):
            self._vars[pred] = expr
        else:
            iv, n = self._encode(pred, expr)  # scalar → pin
            self.model.add(iv == n)
            if isinstance(pred, Requirement) and n in (0, 1):
                self._pinned[pred] = n

    def _var(self, expr):
        return self[expr] if isinstance(expr, Requirement) else expr

    def implies(self, a, b):
        c = self.resolve(b)
        if c is None: return
        if isinstance(c, int):  # 1 = trivially true, 0 = a must be false
            if c == 0: self.model.add(self._var(a) == 0)
            return
        bv = self._var(a)
        if hasattr(c, 'negated'):   # BoolVar: use native implication
            self.model.add_implication(bv, c)
        else:                        # BoundedLinearExpression (e.g. a > b)
            self.model.add(c).only_enforce_if(bv)

    # a → NOT b
    def forbids(self, a, b):
        c = self.resolve(b)
        if c is None: return
        if isinstance(c, int):
            if c: self.model.add(self._var(a) == 0)  # b always true → a must be 0
        else:
            self.model.add_implication(self._var(a), c.negated())

    # bv is true ↔ iv > 0  (used to tie a bool predicate to a categorical one)
    def iff(self, bv, iv):
        bv, iv = self._var(bv), self[iv]
        self.model.add(iv > 0).only_enforce_if(bv)
        self.model.add(iv == 0).only_enforce_if(bv.negated())

    # auto-resolves Requirements and encodes domain values for n
    def _encode(self, expr, n):
        if isinstance(expr, Requirement):
            cls = type(expr)
            enc = self._encoder(cls)
            if enc and n in enc: n = enc[n]
            return self[expr], n
        return expr, n  # already a model variable or linear expression

    def exactly(self, expr, n):
        expr, n = self._encode(expr, n)
        v = self.model.new_bool_var(f"eq_{n}_{id(expr)}")
        self.model.add(expr == n).only_enforce_if(v)
        self.model.add(expr != n).only_enforce_if(v.negated())
        return v

    def at_least(self, expr, n):
        expr, n = self._encode(expr, n)
        v = self.model.new_bool_var(f"geq_{n}_{id(expr)}")
        self.model.add(expr >= n).only_enforce_if(v)
        self.model.add(expr <  n).only_enforce_if(v.negated())
        return v

    def at_most(self, expr, n):
        expr, n = self._encode(expr, n)
        v = self.model.new_bool_var(f"leq_{n}_{id(expr)}")
        self.model.add(expr <= n).only_enforce_if(v)
        self.model.add(expr >  n).only_enforce_if(v.negated())
        return v

    # make a constraint unconditionally mandatory
    def require(self, expr):
        c = self.resolve(expr)
        if c is None or isinstance(c, int): return
        if isinstance(c, cp_model.IntVar):  # covers BoolVar (bool is a domain-restricted IntVar)
            self.model.add(c > 0)
        else:                               # BoundedLinearExpression (e.g. sum >= 4)
            self.model.add(c)
    
    def require_with_wit(self, expr):
        v, leaves = self._reify(expr)
        if v is None or isinstance(v, int): return
        if isinstance(v, cp_model.IntVar):  # covers BoolVar (bool is a domain-restricted IntVar)
            self.model.add(v > 0)
        else:                               # BoundedLinearExpression (e.g. sum >= 4)
            self.model.add(v)
        return leaves
    
    def _reify(self, expr, leaves=None, name=None):
        leaves = leaves if leaves is not None else {}   # to keep track of "leaf variables" as and when encountered
        # if isinstance(expr, self.ignore):
        #     return None
        cond = Condition(f"{wit_expr(expr)} for {name if name else "unnamed"}")
        if cond not in self._vars:
            self._vars[cond] = self.model.new_bool_var(f"{type(cond)}_{id(cond)}")
        
        v = self._vars[cond]

        if isinstance(expr, Requirement):
            if expr not in leaves:           # dedup: same req in multiple branches → one selector
                leaves[expr] = cond
                self.implies(v, self[expr])
                if expr in self._pinned:     # mirror pin: history (1) or excluded (0)
                    self.model.add(v == self._pinned[expr])        

        elif isinstance(expr, cp_model.BoundedLinearExpression):
            # retreive all vars from BLE
            # reify them and construct a new LE in domain on the selector/chosen vars
            # maintain a var to req lookup and retreive the req from that (to make key of leaves) maybe a bidict for this?
            self.model.add(expr).only_enforce_if(v)
            for var in expr.vars:
                _, leaves = self._reify(var, leaves, name)
        
        elif isinstance(expr, LogicalExpr):
            ops = [self._reify(op, leaves, name)[0] for op in expr.operands if not isinstance(op, self.ignore)] # recurse
            if not ops: return 1 # all operands ignored makes it true
            if len(ops) == 1: return ops[0]
            if isinstance(expr, Or): self.model.add_max_equality(v, ops)
            else: self.model.add_min_equality(v, ops)

        return v, leaves

    # recursively walk an And-Or expression and set up boolvars in the model
    def resolve(self, expr):
        if isinstance(expr, self.ignore):
            return None
        if not isinstance(expr, Expr):
            return expr  # raw BoolVar or linear expression
        if isinstance(expr, Requirement):
            return self[expr]

        # recursively add constraints for operands
        ops = [self.resolve(op) for op in expr.operands]

        # check if operands are to be ignored
        ops = [o for o in ops if o is not None]
        if not ops: return 1        # all operands ignored makes it true
        if len(ops) == 1: return ops[0]

        # create model variable to store the Or/And relation if there are multiple operands
        v = self.model.new_bool_var(f"{'or' if isinstance(expr, Or) else 'and'}_{id(expr)}")
        if isinstance(expr, Or): self.model.add_max_equality(v, ops)
        else:                    self.model.add_min_equality(v, ops)
        return v

    def leaves(self, expr):
        if isinstance(expr, self.ignore): return set()
        if isinstance(expr, Requirement):   return {expr}
        else: return set().union(*(self.leaves(op) for op in expr.operands))

    def resolve_with_wit(self, expr, chosen=None):
        chosen = chosen if chosen is not None else {}

        if isinstance(expr, self.ignore):
            return None, chosen
        if not isinstance(expr, Expr):
            return expr, chosen  # raw BoolVar or linear expression
        if isinstance(expr, Requirement):
            if expr not in chosen:           # dedup: same req in multiple branches → one selector
                chosen[expr] = self.model.new_bool_var(f"chosen_{id(expr)}")
                self.implies(chosen[expr], self[expr])
                if expr in self._pinned:     # mirror pin: history (1) or excluded (0)
                    self.model.add(chosen[expr] == self._pinned[expr])
            return chosen[expr], chosen

        # recursively add constraints for operands
        ops = [self.resolve_with_wit(op, chosen) for op in expr.operands]

        # check if operands are to be ignored
        ops = [o for o, _ in ops if o is not None]
        if not ops: return 1, chosen        # all operands ignored makes it true
        if len(ops) == 1: return ops[0], chosen

        # create model variable to store the Or/And relation if there are multiple operands
        v = self.model.new_bool_var(f"{'or' if isinstance(expr, Or) else 'and'}_{id(expr)}")
        if isinstance(expr, Or): self.model.add_max_equality(v, ops)
        else:                    self.model.add_min_equality(v, ops)
        return v, chosen

    # returns an IntVar equal to the max of the given vars
    # hi: explicit upper bound — required when vars are linear expressions
    def max_of(self, vars, hi=None):
        vars = list(vars)
        if not vars: return 0
        if hi is None:
            hi = max(self._domains.get(id(v), 1) for v in vars)
        result = self.model.new_int_var(0, hi, "max")
        self.model.add_max_equality(result, vars)
        return result

    # minimize objectives in priority order — each level must dominate the sum of all lower levels
    def minimize(self, objectives):
        scale, expr = 1, 0
        for obj in reversed(objectives):
            expr += obj * scale
            scale *= 100_000
        self.model.minimize(expr)

    def maximize(self, expr):
        self.model.maximize(expr)

    # map a domain predicate through func via element lookup; iff= holds only when bv is true
    def apply(self, pred, func, iff=None):
        values = [0] + [func(v) for v in type(pred).domain]
        result = self.model.new_int_var(0, max(values), f"apply_{pred}")
        ct = self.model.add_element(self[pred], values, result)
        if iff is not None:
            bv = self._var(iff)
            ct.only_enforce_if(bv)
            self.model.add(result == 0).only_enforce_if(bv.negated())
        return result

    def solve(self):
        return ORSolver(self)


class ORSolver:
    def __init__(self, model):
        self._model = model
        self._cp    = cp_model.CpSolver()
        status      = self._cp.solve(model.model)
        self.status = self._cp.status_name(status)
        self.obj    = (int(self._cp.objective_value)
                       if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None)

    # helper to read solution variable values; auto-decodes categorical domains
    def value(self, v):
        var = self._model[v] if isinstance(v, Requirement) else v
        raw = self._cp.value(var)
        domain = getattr(v, 'domain', None)
        if isinstance(domain, list):
            return None if raw == 0 else domain[raw - 1]
        return raw

    def metrics(self):
        s = self._cp
        out = {}
        if hasattr(s, 'NumConflicts'): out['conflicts']   = s.NumConflicts()
        if hasattr(s, 'NumBranches'):  out['branches']    = s.NumBranches()
        if hasattr(s, 'NumBooleans'):  out['booleans']    = s.NumBooleans()
        if hasattr(s, 'WallTime'):     out['wall_time_s'] = round(s.WallTime(), 3)
        if hasattr(s, 'UserTime'):     out['user_time_s'] = round(s.UserTime(), 3)
        if hasattr(s, 'ResponseProto'):
            out['det_time'] = s.ResponseProto().deterministic_time
        return out

    def print_metrics(self):
        m = self.metrics()
        parts = [f"{k}={v}" for k, v in m.items()]
        print('Solver metrics: ' + (', '.join(parts) if parts else 'n/a'))

class ReqWithDomain(Requirement):
    default_domain = None
    def __init__(self, cid, domain=None):
        self._domain = domain
        super().__init__(cid)
    @property
    def domain(self):
        return self._domain if self._domain is not None else self.default_domain

if __name__=='__main__':
    m = ORModel()

    class Color(ReqWithDomain): pass
    Color.default_domain = ['red', 'green', 'blue', 'yellow']
    countries = {'Belgium', 'France', 'Germany', 'Netherlands', 'Luxembourg', 'Denmark'}

    for c in countries:
        m.require(m[Color(c)] > 0)
    w = []
    m.require(m[Color('Belgium')] != m[Color('France')])
    m.require(m[Color('Belgium')] != m[Color('Germany')])
    m.require(m[Color('Belgium')] != m[Color('Netherlands')])
    m.require(m[Color('Belgium')] != m[Color('Luxembourg')])
    m.require(m[Color('Denmark')] != m[Color('Germany')])
    m.require(m[Color('France')] != m[Color('Germany')])
    m.require(m[Color('France')] != m[Color('Luxembourg')])
    m.require(m[Color('Germany')] != m[Color('Luxembourg')])
    m.require(m[Color('Germany')] != m[Color('Netherlands')])

    sol = m.solve()
    sol.print_metrics()

    for c in countries:
        print(f"{c}: {sol.value(Color(c))}")
