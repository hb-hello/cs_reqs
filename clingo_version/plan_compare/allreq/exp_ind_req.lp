#include "plan.lp".
#include "../kb_indreq.lp".

% separate contraints for each requisite type
:- plan(Cid, Sem), has_prereq(Cid), not prereq(Cid, Sem).
:- plan(Cid, Sem), has_coreq(Cid), not coreq(Cid, Sem).
:- plan(Cid, Sem), has_pre_or_coreq(Cid), not pre_or_coreq(Cid, Sem).
:- plan(Cid, Sem), has_anti_req(Cid), not anti_req(Cid, Sem).