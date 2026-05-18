#include "plan.lp".

max_sem_plan(Sem) :- plan(_, Sem), Sem = #max { Sem1 : plan(_, Sem1) }.

#minimize { 1@1, Id : plan(Id, _); 
            Sem@2   : max_sem_plan(Sem)}.