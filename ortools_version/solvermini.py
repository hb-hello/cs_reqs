from ortools.sat.python import cp_model
from course_kb.course_kb import Expr,Requirement,Or
class ORModel:
    def __init__(self,ignore=()):
        self.model=cp_model.CpModel()
        self._solver=None
        self._vars={}
        self._domains={}
        self._encoders={}
        self.ignore=tuple(ignore)
    def _encoder(self,cls):
        if cls not in self._encoders and isinstance(cls.domain,list): self._encoders[cls]={v:i+1 for i,v in enumerate(cls.domain)}|{None:0}
        return self._encoders.get(cls)
    def __getitem__(self,pred):
        if pred not in self._vars:
            cls=type(pred)
            if cls in self._vars and callable(self._vars[cls]): self._vars[pred]=self._vars[cls](*pred.arguments)
            else:
                domain=getattr(pred,'domain',None)
                if isinstance(domain,list):
                    n=len(domain)-1
                    if n<=1:
                        self._vars[pred]=self.model.new_bool_var(str(pred))
                        if n==0: self.model.add(self._vars[pred]==0)
                        self._domains[id(self._vars[pred])]=1
                    else:
                        self._vars[pred]=self.model.new_int_var(0,len(domain),str(pred))
                        self._domains[id(self._vars[pred])]=len(domain)
                elif domain is None:
                    self._vars[pred]=self.model.new_bool_var(str(pred))
                    self._domains[id(self._vars[pred])]=1
                else: return
        return self._vars[pred]
    def __contains__(self,pred): return pred in self._vars
    def val(self,pred): return self[pred]
    def __setitem__(self,pred,expr):
        if isinstance(pred,type) and callable(expr): self._vars[pred]=expr
        elif isinstance(expr,Expr): self._vars[pred]=self.resolve(expr)
        elif isinstance(expr,cp_model.IntVar): self._vars[pred]=expr
        else:
            iv,n=self._encode(pred,expr)
            self.model.add(iv==n)
    def _var(self,expr): return self[expr] if isinstance(expr,Requirement) else expr
    def implies(self,a,b):
        c=self.resolve(b)
        if c is None: return
        if isinstance(c,int):
            if c==0: self.model.add(self._var(a)==0)
            return
        bv=self._var(a)
        if hasattr(c,'negated'): self.model.add_implication(bv,c)
        else: self.model.add(c).only_enforce_if(bv)
    def forbids(self,a,b):
        c=self.resolve(b)
        if c is None: return
        if isinstance(c,int):
            if c: self.model.add(self._var(a)==0)
        else: self.model.add_implication(self._var(a),c.negated())
    def iff(self,bv,iv):
        bv,iv=self._var(bv),self[iv]
        self.model.add(iv>0).only_enforce_if(bv)
        self.model.add(iv==0).only_enforce_if(bv.negated())
    def _encode(self,expr,n):
        if isinstance(expr,Requirement):
            cls=type(expr)
            enc=self._encoder(cls)
            if enc and n in enc: n=enc[n]
            return self[expr],n
        return expr,n
    def exactly(self,expr,n):
        expr,n=self._encode(expr,n)
        v=self.model.new_bool_var(f"eq_{n}_{id(expr)}")
        self.model.add(expr==n).only_enforce_if(v)
        self.model.add(expr!=n).only_enforce_if(v.negated())
        return v
    def at_least(self,expr,n):
        expr,n=self._encode(expr,n)
        v=self.model.new_bool_var(f"geq_{n}_{id(expr)}")
        self.model.add(expr>=n).only_enforce_if(v)
        self.model.add(expr<n).only_enforce_if(v.negated())
        return v
    def at_most(self,expr,n):
        expr,n=self._encode(expr,n)
        v=self.model.new_bool_var(f"leq_{n}_{id(expr)}")
        self.model.add(expr<=n).only_enforce_if(v)
        self.model.add(expr>n).only_enforce_if(v.negated())
        return v
    def require(self,expr):
        c=self.resolve(expr)
        if c is not None: self.model.add(c==1)
    def resolve(self,expr):
        if isinstance(expr,self.ignore): return None
        if not isinstance(expr,Expr): return expr
        if isinstance(expr,Requirement): return self.val(expr)
        ops=[self.resolve(op) for op in expr.operands]
        ops=[o for o in ops if o is not None]
        if not ops: return 1
        if len(ops)==1: return ops[0]
        v=self.model.new_bool_var(f"{'or' if isinstance(expr,Or) else 'and'}_{id(expr)}")
        if isinstance(expr,Or): self.model.add_max_equality(v,ops)
        else: self.model.add_min_equality(v,ops)
        return v
    def max_of(self,vars,hi=None):
        vars=list(vars)
        if not vars: return 0
        if hi is None: hi=max(self._domains.get(id(v),1) for v in vars)
        result=self.model.new_int_var(0,hi,"max")
        self.model.add_max_equality(result,vars)
        return result
    def minimize(self,objectives):
        scale,expr=1,0
        for obj in reversed(objectives):
            expr+=obj*scale
            scale*=100_000
        self.model.minimize(expr)
    def maximize(self,expr): self.model.maximize(expr)
    def apply(self,pred,func,iff=None):
        values=[0]+[func(v) for v in type(pred).domain]
        result=self.model.new_int_var(0,max(values),f"apply_{pred}")
        ct=self.model.add_element(self[pred],values,result)
        if iff is not None:
            bv=self._var(iff)
            ct.only_enforce_if(bv)
            self.model.add(result==0).only_enforce_if(bv.negated())
        return result
    def solve(self): return ORSolver(self)
class ORSolver:
    def __init__(self,model):
        self._model=model
        self._cp=cp_model.CpSolver()
        status=self._cp.solve(model.model)
        self.status=self._cp.status_name(status)
        self.obj=int(self._cp.objective_value) if status in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None
    def value(self,v):
        var=self._model[v] if isinstance(v,Requirement) else v
        raw=self._cp.value(var)
        domain=getattr(v,'domain',None)
        if isinstance(domain,list): return None if raw==0 else domain[raw-1]
        return raw
    def metrics(self):
        s=self._cp
        out={}
        if hasattr(s,'NumConflicts'): out['conflicts']=s.NumConflicts()
        if hasattr(s,'NumBranches'): out['branches']=s.NumBranches()
        if hasattr(s,'NumBooleans'): out['booleans']=s.NumBooleans()
        if hasattr(s,'WallTime'): out['wall_time_s']=round(s.WallTime(),3)
        if hasattr(s,'UserTime'): out['user_time_s']=round(s.UserTime(),3)
        if hasattr(s,'ResponseProto'): out['det_time']=s.ResponseProto().deterministic_time
        return out
    def print_metrics(self):
        m=self.metrics()
        parts=[f"{k}={v}" for k,v in m.items()]
        print('Solver metrics: '+(', '.join(parts) if parts else 'n/a'))