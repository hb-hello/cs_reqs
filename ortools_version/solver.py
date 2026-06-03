from ortools.sat.python import cp_model
from course_kb.course_kb import Expr, Requirement, LogicalExpr, Or, Not
from collections.abc import Iterable
from bidict import bidict


class Condition(Expr):
    def __init__(self, *arguments):
        self.arguments = arguments

    def __repr__(self):
        return ", ".join(self.arguments)


# class Var(Expr):  # the "variable-representing" class represents a decision that the solver can take.
#     default_domain = None
#
#     def __init__(self, *args, domain: Iterable = None):
#         self._domain = domain
#         super().__init__(*args)
#
#     @property
#     def domain(self):
#         return self._domain if self._domain is not None else self.default_domain
#
#     def __setattr__(self, name, value):
#         if name == "domain" and isinstance(value, Iterable):
#             self._domain = value


def wit_expr(expr) -> str:
    if isinstance(expr, cp_model.BoundedLinearExpression):
        terms = [f"{c}*{v.name}" for c, v in zip(expr.coeffs, expr.vars)]
        return f"{' + '.join(terms)} + {expr.offset} in {expr.bounds}"
    if isinstance(expr, LogicalExpr):
        parts = []
        for child in expr.subexprs:
            child_str = wit_expr(child)  # ← no parent arg
            if (
                isinstance(child, LogicalExpr) and not isinstance(child, Not) and type(child) != type(expr)
            ):  # ← expr is already the parent
                child_str = f"({child_str})"
            parts.append(child_str)
        return f" {type(expr).__name__} ".join(parts)
    return repr(expr)


# stores, indexes and adds variables to the CP-SAT model
# get rid of the translation layer? Add a separate set_domain method as we can only do it once anyway
# figure out a representation of each variable to be queried from named requirements later
# logging/ enumerate solutions?


class ORModel:
    def __init__(self, ignore=(), plan=False):
        self.model = cp_model.CpModel()
        self._solver = None  # created on solve()
        self._vars = bidict({})  # Requirements/classes converted to BoolVars or lambdas
        self._domain_overrides = {}  # pred -> sorted values registered via with_domain
        self._pinned = {}  # pred -> pinned bool value (0 or 1), for selector mirroring
        self._pred_to_selectors = {}
        self._selectors_to_pred = {}  # Condition → Requirement
        self._condition_roots = {}  # root BoolVar → set[Condition] (leaves)
        self.ignore = tuple(ignore)
        self.requirements = {}
        self._req_counter = 0
        self.plan = (
            plan  # when false, consume require calls and store them to maximize later, ignore optimization objectives
        )
        # when true, set a == 1 constraint on require calls and activate optimization objectives

    def set_domain(self, pred, domain):
        values = sorted(set(domain))
        if not values:
            # raise ValueError(f"set_domain({pred}): domain must be non-empty")
            self[pred] = 0
            return pred
        if pred in self._vars:
            raise ValueError(f"set_domain({pred}): variable already created; call set_domain before first use")
        if pred in self._domain_overrides:
            raise ValueError(f"set_domain({pred}): called more than once")
        self._domain_overrides[pred] = values
        return pred

    def _declared_values(self, pred):
        if pred in self._domain_overrides:
            return self._domain_overrides[pred]
        domain = getattr(pred, "domain", None)
        if not isinstance(domain, Iterable) or isinstance(domain, (str, bytes)):
            return None
        return sorted(set(domain))

    def _effective_values(self, pred):
        values = self._declared_values(pred)
        if values is None:
            return None
        # For positive integer categorical vars, reserve 0 as the internal
        # "not assigned" sentinel used by iff(Taken, var).
        if values and all(isinstance(v, int) for v in values) and min(values) >= 1:
            return [0] + values
        return values

    # allows Python's default indexing -> solver[key]
    # automatically identifies the type of model variable needed from the domain
    def __getitem__(self, pred):
        if pred not in self._vars:
            cls = type(pred)
            if cls in self._vars and callable(self._vars[cls]):
                self._vars[pred] = self._vars[cls](*pred.arguments)
            else:
                values = self._effective_values(pred)
                if values is not None:
                    if values == [0, 1]:
                        self._vars[pred] = self.model.new_bool_var(str(pred))
                    elif len(values) == 1:
                        self._vars[pred] = self.model.new_constant(values[0])
                    else:
                        self._vars[pred] = self.model.new_int_var_from_domain(
                            cp_model.Domain.FromValues(values),
                            str(pred),
                        )
                elif getattr(pred, "domain", None) is None:
                    # if domain is None, we default to boolvar
                    self._vars[pred] = self.model.new_bool_var(str(pred))
                else:
                    return
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
            iv = self[pred] if isinstance(pred, Requirement) else pred
            self.model.add(iv == expr)
            if pred in self._pred_to_selectors:
                for sel in self._pred_to_selectors[pred]:
                    self.model.add(self[sel] == expr)
            if isinstance(pred, Requirement) and expr in (0, 1):
                self._pinned[pred] = expr

    def _var(self, expr):
        return self[expr] if isinstance(expr, Requirement) else expr

    def implies(self, a, b):
        c = self.resolve(b)
        if c is None:
            return
        if isinstance(c, int):  # 1 = trivially true, 0 = a must be false
            if c == 0:
                self.model.add(self._var(a) == 0)
            return
        bv = self._var(a)
        if self._is_bool_var(c):  # BoolVar: use native implication
            self.model.add_implication(bv, c)
        elif isinstance(c, cp_model.BoundedLinearExpression):  # e.g. grade >= C
            self.model.add(c).only_enforce_if(bv)
        else:  # multi-valued IntVar (e.g. Grade): implied ↔ non-zero
            self.model.add(c > 0).only_enforce_if(bv)

    # def negated(self, expr):
    #     if isinstance(expr, cp_model.IntVar) and list(expr.proto.domain) == [0, 1]:
    #         return expr.negated()
    #     if isinstance(expr, Requirement):
    #         v = self[expr]
    #         if list(v.proto.domain) == [0, 1]:
    #             return v.negated()
    #     return self.reify(expr)[0].negated()

    # # a → NOT b
    # def forbids(self, a, b):
    #     c = self.resolve(b)
    #     if c is None:
    #         return
    #     if isinstance(c, int):
    #         if c:
    #             self.model.add(self._var(a) == 0)  # b always true → a must be 0
    #     else:
    #         self.model.add_implication(self._var(a), c.negated())

    # bv is true ↔ iv > 0  (used to tie a bool predicate to a categorical one)
    def iff(self, bv, iv):
        bv, iv = self._var(bv), self[iv]
        self.model.add(iv > 0).only_enforce_if(bv)
        self.model.add(iv == 0).only_enforce_if(bv.negated())

    def eq(self, expr, n):
        expr = self[expr] if isinstance(expr, Requirement) else expr
        v = self.model.new_bool_var(f"eq_{n}_{id(expr)}")
        self.model.add(expr == n).only_enforce_if(v)
        self.model.add(expr != n).only_enforce_if(v.negated())
        return v

    # def ge(self, expr, n):
    #     expr = self[expr] if isinstance(expr, Requirement) else expr
    #     v = self.model.new_bool_var(f"geq_{n}_{id(expr)}")
    #     self.model.add(expr >= n).only_enforce_if(v)
    #     self.model.add(expr < n).only_enforce_if(v.negated())
    #     return v

    # def le(self, expr, n):
    #     expr = self[expr] if isinstance(expr, Requirement) else expr
    #     v = self.model.new_bool_var(f"leq_{n}_{id(expr)}")
    #     self.model.add(expr <= n).only_enforce_if(v)
    #     self.model.add(expr > n).only_enforce_if(v.negated())
    #     return v

    # def constrain_slots(self, slots, costs, capacity):
    #     pairs = list(zip(slots, costs))
    #     ivars = [self.model.new_fixed_size_interval_var(self[slot], 1, f"ci_{i}") for i, (slot, _) in enumerate(pairs)]
    #     self.model.add_cumulative(ivars, [cost for _, cost in pairs], capacity)

    def product(self, a, b):
        if isinstance(a, int):
            return a * b
        if isinstance(b, int):
            return b * a
        hi = self._upper_bound(a) * self._upper_bound(b)
        result = self.model.new_int_var(0, hi, f"prod_{id(a)}_{id(b)}")
        self.model.add_multiplication_equality(result, [a, b])
        return result

    def add(self, expr, name=None):
        if name is None:
            self._req_counter += 1
            name = f"_req_{self._req_counter}"
        conditions = set()
        v, _ = self.reify(expr, name=name, with_leaves=True, conditions=conditions)
        if v is None:
            return None
        self.requirements[name] = v
        if isinstance(v, cp_model.IntVar):
            self._condition_roots[v] = conditions
        if self.plan:
            if isinstance(v, cp_model.IntVar):  # covers BoolVar (bool is a domain-restricted IntVar)
                self.model.add(v > 0)
            else:  # BoundedLinearExpression (e.g. sum >= 4)
                self.model.add(v)
        return v

    # Recursively reify any expression into a single BoolVar while tracking each intermediate node as var
    # with_leaves=True:  create/index Condition variables; populate the leaves dict
    # with_leaves=False: directly build constraints and return a fresh BoolVar; no Condition caching
    def reify(self, expr, leaves=None, name=None, with_leaves=False, conditions=None):
        if leaves is None:
            leaves = {}

        if isinstance(expr, self.ignore):
            return None, leaves
        if isinstance(expr, cp_model.IntVar) and not isinstance(expr, Requirement):
            return expr, leaves
        if isinstance(expr, Requirement) and not with_leaves:
            return self[expr], leaves

        # All remaining paths need a BoolVar — cached under a Condition key (with_leaves) or fresh
        if with_leaves:
            node_key = Condition(f"{wit_expr(expr)} for {name or id(expr)}")
            if node_key not in self._vars:
                self._vars[node_key] = self.model.new_bool_var(repr(node_key))
            v = self._vars[node_key]
        else:
            v = self.model.new_bool_var(f"{wit_expr(expr)}")

        if isinstance(expr, Requirement):
            if expr not in leaves:
                leaves[expr] = v
                # self.implies(v, self[expr])
                self.model.add(self[expr] > 0).only_enforce_if(v)
                if expr in self._pinned:
                    self.model.add(v == self._pinned[expr])
                self._pred_to_selectors.setdefault(expr, []).append(node_key)
                self._selectors_to_pred[node_key] = expr
                if conditions is not None:
                    conditions.add(node_key)
            return v, leaves

        if isinstance(expr, cp_model.BoundedLinearExpression):
            if not with_leaves:
                self.model.add(expr).only_enforce_if(v)
            else:
                contrib_vars = []
                for var in expr.vars:
                    req = self._vars.inverse.get(var)  # reverse bidict lookup
                    if req is not None and isinstance(req, Requirement):
                        sel, leaves = self.reify(req, leaves, name, with_leaves, conditions)
                        contrib = self._make_contribution(req, sel)
                    else:
                        contrib = var  # raw IntVar/BoolVar — use directly
                    contrib_vars.append(contrib)
                new_lexpr = cp_model.LinearExpr.weighted_sum(contrib_vars, list(expr.coeffs))
                if expr.offset:
                    new_lexpr = new_lexpr + expr.offset
                self.model.add_linear_expression_in_domain(new_lexpr, expr.bounds).only_enforce_if(v)
            return v, leaves

        if isinstance(expr, LogicalExpr):
            ops = []
            for op in expr.operands:
                if isinstance(op, self.ignore):
                    continue
                child_v, leaves = self.reify(op, leaves, name, with_leaves, conditions)
                if child_v is not None:
                    ops.append(child_v)

            if not ops:
                return 1, leaves  # all ignored → trivially true
            if isinstance(expr, Not):
                negated = ops[0].negated()
                if with_leaves:
                    self._vars[node_key] = negated
                return negated, leaves
            if len(ops) == 1:
                return ops[0], leaves  # single child → collapse

            if isinstance(expr, Or):
                self.model.add_max_equality(v, ops)
            else:
                self.model.add_min_equality(v, ops)
            return v, leaves

        return expr, leaves

    def traverse(self, expr, path_classes=None, leaf_map=None, negated=()):
        if leaf_map is None:
            leaf_map = {}
        if path_classes is None:
            path_classes = frozenset()

        if isinstance(expr, self.ignore):
            return None, leaf_map
        if isinstance(expr, cp_model.IntVar) and not isinstance(expr, Requirement):
            return expr, leaf_map

        if isinstance(expr, negated):
            child_v, leaf_map = self.traverse(expr.arguments[0], path_classes | {type(expr)}, leaf_map, negated)
            return (child_v.negated() if child_v is not None else None), leaf_map

        if isinstance(expr, Requirement):
            new_classes = path_classes | {type(expr)}
            inner = expr.arguments[0] if expr.arguments else None
            if isinstance(inner, str):
                key = (inner, new_classes)
                if key not in leaf_map:
                    self._req_counter += 1
                    sel = self.model.new_bool_var(f"sel_{self._req_counter}")
                    self.model.add(self[expr] > 0).only_enforce_if(sel)
                    leaf_map[key] = sel
                return leaf_map[key], leaf_map
            return self.traverse(inner, new_classes, leaf_map, negated)

        if isinstance(expr, cp_model.BoundedLinearExpression):
            self._req_counter += 1
            v = self.model.new_bool_var(f"sel_{self._req_counter}")
            contrib_vars = []
            for var in expr.vars:
                req = self._vars.inverse.get(var)
                if req is not None and isinstance(req, Requirement):
                    sel, leaf_map = self.traverse(req, path_classes, leaf_map, negated)
                    contrib = self._make_contribution(req, sel) if sel is not None else var
                else:
                    contrib = var
                contrib_vars.append(contrib)
            new_lexpr = cp_model.LinearExpr.weighted_sum(contrib_vars, list(expr.coeffs))
            if expr.offset:
                new_lexpr = new_lexpr + expr.offset
            self.model.add_linear_expression_in_domain(new_lexpr, expr.bounds).only_enforce_if(v)
            return v, leaf_map

        if isinstance(expr, LogicalExpr):
            ops = []
            for op in expr.operands:
                if isinstance(op, self.ignore):
                    continue
                child_v, leaf_map = self.traverse(op, path_classes, leaf_map, negated)
                if child_v is not None:
                    ops.append(child_v)

            if not ops:
                return None, leaf_map
            if isinstance(expr, Not):
                return ops[0].negated(), leaf_map
            if len(ops) == 1:
                return ops[0], leaf_map

            v = self.model.new_bool_var(wit_expr(expr))
            if isinstance(expr, Or):
                self.model.add_max_equality(v, ops)
            else:
                self.model.add_min_equality(v, ops)
            return v, leaf_map

        return expr, leaf_map

    def _make_contribution(self, req, sel):
        fact_var = self[req]
        if self._is_bool_var(fact_var):
            return sel
        domain_values = self._effective_values(req)
        contrib_values = sorted(set([0] + domain_values))

        # IntVar — gate through selector, cache to avoid duplicates
        contrib_key = Condition(f"contrib_{wit_expr(req)}")
        if contrib_key not in self._vars:
            contrib = self.model.new_int_var_from_domain(cp_model.Domain.FromValues(contrib_values), repr(contrib_key))
            self._vars[contrib_key] = contrib
            self.model.add(contrib == fact_var).only_enforce_if(sel)
            self.model.add(contrib == 0).only_enforce_if(sel.Not())
        return self._vars[contrib_key]

    # recursively walk an And-Or expression and set up boolvars in the model
    def resolve(self, expr):
        # if isinstance(expr, self.ignore):
        #     return None
        # if isinstance(expr, cp_model.BoundedLinearExpression):
        #     v = self.model.new_bool_var(wit_expr(expr))
        #     self.model.add(expr).only_enforce_if(v)
        #     return v
        # if not isinstance(expr, Expr):
        #     return expr  # raw BoolVar or linear expression
        # if isinstance(expr, Requirement):
        #     return self[expr]

        # # recursively add constraints for operands
        # ops = [self.resolve(op) for op in expr.operands]

        # # check if operands are to be ignored
        # ops = [o for o in ops if o is not None]
        # if not ops: return 1        # all operands ignored makes it true
        # if len(ops) == 1: return ops[0]

        # # create model variable to store the Or/And relation if there are multiple operands
        # v = self.model.new_bool_var(f"{'or' if isinstance(expr, Or) else 'and'}_{id(expr)}")
        # if isinstance(expr, Or): self.model.add_max_equality(v, ops)
        # else:                    self.model.add_min_equality(v, ops)
        # return v
        return self.reify(expr)[0]

    # returns an IntVar equal to the max of the given vars
    # hi: explicit upper bound — required when vars are linear expressions
    def max_of(self, vars, hi=None):
        vars = list(vars)
        if not vars:
            return 0
        if hi is None:
            hi = max(self._upper_bound(v) for v in vars)
        result = self.model.new_int_var(0, hi, "max")
        self.model.add_max_equality(result, vars)
        return result

    def _upper_bound(self, var):
        if not isinstance(var, cp_model.IntVar):
            return 1
        domain = list(var.proto.domain)
        if not domain:
            return 1
        return max(domain[1::2])

    def _is_bool_var(self, var):
        return isinstance(var, cp_model.IntVar) and list(var.proto.domain) == [0, 1]

    # minimize objectives in priority order — each level must dominate the sum of all lower levels
    def minimize(self, objectives):
        if not self.plan:
            return
        scale, expr = 1, 0
        for obj in reversed(objectives):
            expr += obj * scale
            scale *= 100_000
        self.model.minimize(expr)

    # def maximize(self, objectives):
    #     if not self.plan:
    #         return
    #     scale, expr = 1, 0
    #     for obj in reversed(objectives):
    #         expr += obj * scale
    #         scale *= 100_000
    #     self.model.maximize(expr)

    def _expr_bounds(self, expr):
        if isinstance(expr, int):
            return expr, expr
        if isinstance(expr, cp_model.IntVar):
            d = list(expr.proto.domain)
            return d[0], d[-1]
        # IntAffine: coeff * var + offset
        d = list(expr.expression.proto.domain)
        lo = d[0] * expr.coefficient + expr.offset
        hi = d[-1] * expr.coefficient + expr.offset
        return (lo, hi) if expr.coefficient >= 0 else (hi, lo)

    # map a domain predicate through func via element lookup; iff= holds only when bv is true
    def select(self, func, pred, iff=None):
        if isinstance(func, dict):
            func = func.__getitem__
        declared_values = self._declared_values(pred)
        domain_values = self._effective_values(pred)
        declared_set = set(declared_values)
        mapped_values = [func(v) if v in declared_set else 0 for v in domain_values]
        bounds = [self._expr_bounds(v) for v in mapped_values]
        lo, hi = min(b[0] for b in bounds), max(b[1] for b in bounds)
        mapped = self.model.new_int_var(lo, hi, f"apply_{pred}_mapped")
        for v, out in zip(domain_values, mapped_values):
            self.model.add(mapped == out).only_enforce_if(self.eq(pred, v))
        if iff is not None:
            bv = self._var(iff)
            result = self.model.new_int_var(min(0, lo), max(0, hi), f"apply_{pred}")
            self.model.add(result == mapped).only_enforce_if(bv)
            self.model.add(result == 0).only_enforce_if(bv.negated())
            return result
        return mapped

    def solve(self):
        if not self.plan:
            self.model.maximize(sum(self.requirements.values()))
        return ORSolver(self)


class ORSolver:
    def __init__(self, model):
        self._model = model
        self._cp = cp_model.CpSolver()
        status = self._cp.solve(model.model)
        self.status = self._cp.status_name(status)
        self.obj = int(self._cp.objective_value) if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None

    # helper to read solution variable values; auto-decodes categorical domains
    def value(self, v):
        var = self._model[v] if isinstance(v, Requirement) else v
        return self._cp.value(var)

    def metrics(self):
        s = self._cp
        out = {}
        if hasattr(s, "NumConflicts"):
            out["conflicts"] = s.NumConflicts()
        if hasattr(s, "NumBranches"):
            out["branches"] = s.NumBranches()
        if hasattr(s, "NumBooleans"):
            out["booleans"] = s.NumBooleans()
        if hasattr(s, "WallTime"):
            out["wall_time_s"] = round(s.WallTime(), 3)
        if hasattr(s, "UserTime"):
            out["user_time_s"] = round(s.UserTime(), 3)
        if hasattr(s, "ResponseProto"):
            out["det_time"] = s.ResponseProto().deterministic_time
        return out

    def print_metrics(self):
        m = self.metrics()
        parts = [f"{k}={v}" for k, v in m.items()]
        print("Solver metrics: " + (", ".join(parts) if parts else "n/a"))

    def chosen(self, boolvar):
        conditions = self._model._condition_roots.get(boolvar, set())
        return {self._model._selectors_to_pred[c] for c in conditions if self._cp.value(self._model._vars[c])}


class ReqWithDomain(Requirement):
    default_domain = None

    def __init__(self, cid, domain=None):
        self._domain = domain
        super().__init__(cid)

    @property
    def domain(self):
        return self._domain if self._domain is not None else self.default_domain


if __name__ == "__main__":
    m = ORModel()

    class Color(ReqWithDomain):
        pass

    Color.default_domain = ["red", "green", "blue", "yellow"]
    countries = {"Belgium", "France", "Germany", "Netherlands", "Luxembourg", "Denmark"}

    for c in countries:
        m.require(m[Color(c)] > 0)
    w = []
    m.require(m[Color("Belgium")] != m[Color("France")])
    m.require(m[Color("Belgium")] != m[Color("Germany")])
    m.require(m[Color("Belgium")] != m[Color("Netherlands")])
    m.require(m[Color("Belgium")] != m[Color("Luxembourg")])
    m.require(m[Color("Denmark")] != m[Color("Germany")])
    m.require(m[Color("France")] != m[Color("Germany")])
    m.require(m[Color("France")] != m[Color("Luxembourg")])
    m.require(m[Color("Germany")] != m[Color("Luxembourg")])
    m.require(m[Color("Germany")] != m[Color("Netherlands")])

    sol = m.solve()
    sol.print_metrics()

    for c in countries:
        print(f"{c}: {sol.value(Color(c))}")
