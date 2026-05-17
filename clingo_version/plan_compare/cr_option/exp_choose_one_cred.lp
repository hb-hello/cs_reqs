#include "plan.lp".

{plan_credits(Id, Cr) : credits(Id, Cr)} == 1 :- plan(Id, _).