#include "plan.lp".
#include "../kb_indreq_wo_has.lp". %% the KB needs to satisfy absent requisites automatically.

% prereq and anti req in generation
{plan(Id, Sem) : offered(Id, Sem), prereq(Id, Sem), anti_req(Id, Sem)} == 1 :-
  offered_in_range(Id), include(Id).
{plan(Id, Sem) : offered(Id, Sem), prereq(Id, Sem), anti_req(Id, Sem)} <= 1 :-
  offered_in_range(Id), not taken_id(Id), not exclude(Id).

% coreq and pre_or_coreq in test
:- plan(Id, Sem), not coreq(Id, Sem).
:- plan(Id, Sem), not pre_or_coreq(Id, Sem).