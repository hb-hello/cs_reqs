#include "plan.lp".

{plan_credits(Cid, Cr) : credits(Cid, Cr)} == 1 :- plan(Cid, _).