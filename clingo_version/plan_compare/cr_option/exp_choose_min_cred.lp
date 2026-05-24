#include "plan.lp".

% take the min credit option for each plan
plan_credits(Cid, Cr) :- plan(Cid, _), Cr = #min { C : credits(Cid, C) }.