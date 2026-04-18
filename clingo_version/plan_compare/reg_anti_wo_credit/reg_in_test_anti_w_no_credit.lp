{plan(Id, Sem) : offered(Id, Sem)} == 1 :- offered_in_range(Id), include(Id).
{plan(Id, Sem) : offered(Id, Sem)} <= 1 :- offered_in_range(Id),
											not taken_id(Id), not exclude(Id).

%% if anti not sat, take with 0 credits.
plan_credits(Id, 0) :- 
  plan(Id, Sem), 
  has_anti_req(Id), 
  not anti_req(Id, Sem).

%% either no anti, or anti sat, take with actual credits.
{plan_credits(Id, Cr) : credits(Id, Cr)} == 1 :- plan(Id, _), not has_anti_req(Id).
{plan_credits(Id, Cr) : credits(Id, Cr)} == 1 :- plan(Id, Sem), has_anti_req(Id), anti_req(Id, Sem).

taken(Id, Cr, "A", Sem, "SB") :- plan(Id, Sem), plan_credits(Id, Cr).

:- item(X), not req(X).
:- plan(Id, Sem), has_prereq(Id), not prereq(Id, Sem).
:- plan(Id, Sem), has_coreq(Id), not coreq(Id, Sem).
:- plan(Id, Sem), has_pre_or_coreq(Id), not pre_or_coreq(Id, Sem).
:- plan(_, Sem),
	#sum { Cr, Id : plan(Id, Sem), plan_credits(Id, Cr) } > sem_max_credits.

max_sem_plan(Sem) :- plan(_, Sem), Sem = #max { Sem1 : plan(_, Sem1) }.
#minimize { Sem@2 : max_sem_plan(Sem) }.
#minimize { 1@1, Id : plan(Id, _) }.