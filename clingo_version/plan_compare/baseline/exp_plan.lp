#include "../base.lp".
#include "../kb_allreq.lp".

% decouple course selection from planning. 
% {plan(Cid, Sem) : offered(Cid, Sem)} == 1 :- offered_in_range(Cid), include(Cid).
% {plan(Cid, Sem) : offered(Cid, Sem)} <= 1 :- offered_in_range(Cid),
% 											not taken_id(Cid), not exclude(Cid).
{ plan_course(Cid) } :- offered_in_range(Cid), not taken_id(Cid), not exclude(Cid).
plan_course(Cid) :- offered_in_range(Cid), include(Cid).

{plan(Cid, Sem) : offered(Cid, Sem)} == 1 :- plan_course(Cid).
{plan_credits(Cid, Cr) : credits(Cid, Cr)} == 1 :- plan_course(Cid).

taken(Cid, Cr, "None", Sem, "SB") :- plan(Cid, Sem), plan_credits(Cid, Cr).

:- item(I), not req(I).
:- plan(Cid, Sem), not allreq(Cid, Sem).
:- plan(_, Sem),
	#sum { Cr, Cid : plan(Cid, Sem), plan_credits(Cid, Cr) } > sem_max_credits.

max_sem_plan(Sem) :- plan(_, Sem), Sem = #max { Sem1 : plan(_, Sem1) }.

#minimize { 1@1, Cid : plan(Cid, _); 
            Sem@2   : max_sem_plan(Sem)}.

%* compare with baseline, faster in all cases except sem_4 and sem_1 (similar in sem_1).
python benchmarks/clingo_planning_bm.py -e baseline -t 300 -r 2

exp_baseline full 7.347477912902832 [0.0, 0.0]
exp_baseline full 7.355194807052612 [0.0, 0.0]
exp_plan full 2.3569791316986084 [0.0, 0.0]
exp_plan full 2.397716999053955 [0.0, 0.0]
exp_baseline sem_6 3.4163708686828613 [3.0, 6.0]
exp_baseline sem_6 3.536824941635132 [3.0, 6.0]
exp_plan sem_6 2.459725856781006 [3.0, 6.0]
exp_plan sem_6 2.4398460388183594 [3.0, 6.0]
exp_baseline sem_5 3.9668309688568115 [3.0, 11.0]
exp_baseline sem_5 3.894209861755371 [3.0, 11.0]
exp_plan sem_5 3.055614948272705 [3.0, 11.0]
exp_plan sem_5 3.061102867126465 [3.0, 11.0]
exp_baseline sem_4 3.865345001220703 [4.0, 14.0]
exp_baseline sem_4 3.8635551929473877 [4.0, 14.0]
exp_plan sem_4 5.592282056808472 [4.0, 14.0]
exp_plan sem_4 5.378902196884155 [4.0, 14.0]
exp_baseline sem_3 5.900598049163818 [5.0, 18.0]
exp_baseline sem_3 5.886441946029663 [5.0, 18.0]
exp_plan sem_3 4.881992816925049 [5.0, 18.0]
exp_plan sem_3 4.756530046463013 [5.0, 18.0]
exp_baseline sem_2 8.709395170211792 [6.0, 22.0]
exp_baseline sem_2 9.070487976074219 [6.0, 22.0]
exp_plan sem_2 6.135547876358032 [6.0, 22.0]
exp_plan sem_2 6.120253801345825 [6.0, 22.0]
exp_baseline sem_1 198.6294538974762 [9.0, 27.0]
exp_baseline sem_1 192.79991507530212 [9.0, 27.0]
exp_plan sem_1 202.3181290626526 [9.0, 27.0]
exp_plan sem_1 199.93642497062683 [9.0, 27.0]
*%