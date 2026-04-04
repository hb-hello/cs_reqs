from ortools.sat.python import cp_model
from course_kb.course_kb import Expr, Requirement, Or


# use operator overloads to make expressions prettier? 
# lets us evaluate Pred(A) < Pred(B) to or_model[Pred(A)] < or_model[Pred(B)]

# stores, indexes and adds variables to the CP-SAT model
class ORModel:
    def __init__(self, ignore=()):
        self.model   = cp_model.CpModel()
        self._solver = None         # created on solve()
        self._vars   = {}           # Requirements/classes converted to BoolVars or lambdas
        self._domains = {}          # var id -> domain size (upper bound; avoids Proto() calls)
        self._encoders = {}         # pred_class -> encode_dict (cached from class domain)
        self.ignore  = tuple(ignore)

    # lazily build and cache the encode dict from a Requirement class's domain
    def _encoder(self, cls):
        if cls not in self._encoders and isinstance(cls.domain, list):
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

    # return the BoolVar for a predicate, caching so each predicate maps to exactly one var
    def val(self, pred):
        return self[pred]

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
        if c is not None:
            self.model.add(c == 1)

    # recursively walk an And-Or expression and set up boolvars in the model
    def resolve(self, expr):
        if isinstance(expr, self.ignore):
            return None
        if not isinstance(expr, Expr):
            return expr  # raw BoolVar or linear expression
        if isinstance(expr, Requirement):
            return self.val(expr)

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

    # run the solver and return an ORSolver with the results
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
