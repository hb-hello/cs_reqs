#include "plan.lp".
#include "../kb_indreq_wo_has.lp". %% the KB needs to satisfy absent requisites automatically.

% prereq and anti req in generation
{plan(Cid, Sem) : offered(Cid, Sem), prereq(Cid, Sem), anti_req(Cid, Sem)} == 1 :-
  offered_in_range(Cid), include(Cid).
{plan(Cid, Sem) : offered(Cid, Sem), prereq(Cid, Sem), anti_req(Cid, Sem)} <= 1 :-
  offered_in_range(Cid), not taken_id(Cid), not exclude(Cid).

% coreq and pre_or_coreq in test
:- plan(Cid, Sem), not coreq(Cid, Sem).
:- plan(Cid, Sem), not pre_or_coreq(Cid, Sem).