#include "plan.lp".

% take the max credit option for each plan
plan_credits(Cid, Cr) :- plan(Cid, _), Cr = #max { C : credits(Cid, C) }.