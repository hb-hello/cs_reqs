#include "plan.lp".
#include "../kb_indreq.lp".

% separate contraints for each requisite type
:- plan(Id, Sem), has_prereq(Id), not prereq(Id, Sem).
:- plan(Id, Sem), has_coreq(Id), not coreq(Id, Sem).
:- plan(Id, Sem), has_pre_or_coreq(Id), not pre_or_coreq(Id, Sem).
:- plan(Id, Sem), has_anti_req(Id), not anti_req(Id, Sem).