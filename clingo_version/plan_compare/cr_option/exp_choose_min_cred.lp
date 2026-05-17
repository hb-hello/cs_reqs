#include "plan.lp".

% take the min credit option for each plan
plan_credits(Id, Cr) :- plan(Id, _), Cr = #min { C : credits(Id, C) }.