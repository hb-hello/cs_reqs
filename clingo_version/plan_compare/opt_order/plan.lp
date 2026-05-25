#include "../base.lp".
#include "kb.lp".

{plan(Cid, Sem) : offered(Cid, Sem)} == 1 :- offered_in_range(Cid), include(Cid).
{plan(Cid, Sem) : offered(Cid, Sem)} <= 1 :- offered_in_range(Cid),
											not taken_id(Cid), not exclude(Cid).
{plan_credits(Cid, Cr) : credits(Cid, Cr)} == 1 :- plan(Cid, _).

taken(Cid, Cr, "None", Sem, "SB") :- plan(Cid, Sem), plan_credits(Cid, Cr).

:- item(I), not req(I).
:- plan(Cid, Sem), not allreq(Cid, Sem).
:- plan(_, Sem),
	#sum { Cr, Cid : plan(Cid, Sem), plan_credits(Cid, Cr) } > sem_max_credits.

