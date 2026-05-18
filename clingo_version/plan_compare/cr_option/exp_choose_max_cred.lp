#include "plan.lp".

% take the max credit option for each plan
plan_credits(Id, Cr) :- plan(Id, _), Cr = #max { C : credits(Id, C) }.