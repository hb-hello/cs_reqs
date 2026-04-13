{plan(Id, Sem) : offered(Id, Sem)} == 1 :- offered_in_range(Id), include(Id).
{plan(Id, Sem) : offered(Id, Sem)} <= 1 :- offered_in_range(Id),
											not taken_id(Id), not exclude(Id).

%% ! not correct in general, will generate multiple taken facts with the same Id.
taken(Id, Cr, "A", Sem, "SB") :- plan(Id, Sem), credits(Id, Cr).

:- item(X), not req(X).
:- plan(Id, Sem), has_prereq(Id), not prereq(Id, Sem).
:- plan(Id, Sem), has_coreq(Id), not coreq(Id, Sem).
:- plan(Id, Sem), has_pre_or_coreq(Id), not pre_or_coreq(Id, Sem).
:- plan(Id, Sem), has_anti_req(Id), not anti_req(Id, Sem).
:- plan(_, Sem),
	#sum { Cr, Id : plan(Id, Sem), credits(Id, Cr) } > sem_max_credits.

max_sem_plan(Sem) :- plan(_, Sem), Sem = #max { Sem1 : plan(_, Sem1) }.
#minimize { Sem@2 : max_sem_plan(Sem) }.
#minimize { 1@1, Id : plan(Id, _) }.
