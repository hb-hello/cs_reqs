#include "../base.lp".

{plan(Id, Sem) : offered(Id, Sem)} == 1 :- offered_in_range(Id), include(Id).
{plan(Id, Sem) : offered(Id, Sem)} <= 1 :- offered_in_range(Id), 
                                           not taken_id(Id), not exclude(Id).
{plan_credits(Id, Cr) : credits(Id, Cr)} == 1 :- plan(Id, _).

taken(Id, Cr, "None", Sem, "SB") :- plan(Id, Sem), plan_credits(Id, Cr).

:- item(I), not req(I).
:- plan(_, Sem),
   #sum {Cr, Id: plan(Id, Sem), plan_credits(Id, Cr)} > sem_max_credits.

max_sem_plan(Sem) :- plan(_, Sem), Sem = #max {Sem1 : plan(_, Sem1)}.
#minimize {Sem@2: max_sem_plan(Sem)}.
#minimize {1@1, Cid: plan(Cid, _)}.