#include "../base.lp".
#include "../kb_allreq.lp".

% baseline, same as in cse_req_clingo.lp
{plan(Id, Sem) : offered(Id, Sem)} == 1 :- offered_in_range(Id), include(Id).
{plan(Id, Sem) : offered(Id, Sem)} <= 1 :- offered_in_range(Id),
											not taken_id(Id), not exclude(Id).
{plan_credits(Id, Cr) : credits(Id, Cr)} == 1 :- plan(Id, _).

taken(Id, Cr, "None", Sem, "SB") :- plan(Id, Sem), plan_credits(Id, Cr).

:- item(I), not req(I).
:- plan(Cid, Sem), not allreq(Cid, Sem).
:- plan(_, Sem),
	#sum { Cr, Id : plan(Id, Sem), plan_credits(Id, Cr) } > sem_max_credits.

max_sem_plan(Sem) :- plan(_, Sem), Sem = #max { Sem1 : plan(_, Sem1) }.

#minimize { 1@1, Id : plan(Id, _); 
            Sem@2   : max_sem_plan(Sem)}.