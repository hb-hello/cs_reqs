#include "plan.lp".
#include "../kb_allreq.lp".

% req constraint expressed with allreq
:- plan(Id, Sem), not allreq(Id, Sem).