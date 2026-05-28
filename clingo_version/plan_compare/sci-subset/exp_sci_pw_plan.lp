#include "base-sci-subset.lp".

% plan_course(Cid)
{plan_course(Cid)} :- offered_in_range(Cid), not taken_id(Cid), not exclude(Cid).
plan_course(Cid) :- offered_in_range(Cid), include(Cid).

{plan(Cid, Sem) : offered(Cid, Sem)} == 1 :- plan_course(Cid).
{plan_credits(Cid, Cr) : credits(Cid, Cr)} == 1 :- plan_course(Cid).

taken(Cid, Cr, "None", Sem, "SB") :- plan(Cid, Sem), plan_credits(Cid, Cr).

:- item(I), not req(I).
:- plan(Cid, Sem), not allreq(Cid, Sem).
:- plan(_, Sem),
	#sum { Cr, Cid : plan(Cid, Sem), plan_credits(Cid, Cr) } > sem_max_credits.

max_sem(Sem) :- plan(_, Sem), Sem = #max { Sem1 : plan(_, Sem1) }.

#minimize { 1@1, Cid : plan(Cid, _); 
            Sem@2   : max_sem(Sem)}.