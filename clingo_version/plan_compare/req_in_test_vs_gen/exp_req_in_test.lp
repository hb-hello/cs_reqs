#include "plan.lp".
#include "../kb_allreq.lp".

{plan(Cid, Sem) : offered(Cid, Sem)} == 1 :- offered_in_range(Cid), include(Cid).
{plan(Cid, Sem) : offered(Cid, Sem)} <= 1 :- offered_in_range(Cid), not taken_id(Cid), not exclude(Cid).

% requisites constraints only in tests
:- plan(Cid, Sem), not allreq(Cid, Sem).