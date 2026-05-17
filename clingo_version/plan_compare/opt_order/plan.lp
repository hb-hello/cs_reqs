#include "../base.lp".
#include "kb.lp".

{plan(Id, Sem) : offered(Id, Sem)} == 1 :- offered_in_range(Id), include(Id).
{plan(Id, Sem) : offered(Id, Sem)} <= 1 :- offered_in_range(Id),
											not taken_id(Id), not exclude(Id).
{plan_credits(Id, Cr) : credits(Id, Cr)} == 1 :- plan(Id, _).

taken(Id, Cr, "None", Sem, "SB") :- plan(Id, Sem), plan_credits(Id, Cr).

:- item(I), not req(I).
:- plan(Cid, Sem), not allreq(Cid, Sem).
:- plan(_, Sem),
	#sum { Cr, Id : plan(Id, Sem), plan_credits(Id, Cr) } > sem_max_credits.

