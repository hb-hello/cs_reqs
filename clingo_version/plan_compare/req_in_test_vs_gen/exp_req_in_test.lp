#include "plan.lp".
#include "../kb_allreq.lp".

{plan(Id, Sem) : offered(Id, Sem)} == 1 :- offered_in_range(Id), include(Id).
{plan(Id, Sem) : offered(Id, Sem)} <= 1 :- offered_in_range(Id), not taken_id(Id), not exclude(Id).

% requisites constraints only in tests
:- plan(Id, Sem), not allreq(Id, Sem).