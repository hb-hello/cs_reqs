#include "plan.lp".
#include "../kb_allreq.lp".

% req constraint expressed with allreq
:- plan(Cid, Sem), not allreq(Cid, Sem).