% base program for benchmarking

% include encoding
#include "../cse_req_clingo.lp".

% common predicate definitions for planning
before(Sem1, Sem2) :- Sem1 = 1..finish_sem, Sem2 = 1..finish_sem, Sem1 < Sem2.
passed_before_grade(Cid, Grade, Sem) :-
  taken(Cid, _, _, Sem1, _), before(Sem1, Sem), passed_with_grade(Cid, Grade).

%% "C or higher" in prereq
passed_before(Cid, Sem):- taken(Cid, _, _, Sem1, _), before(Sem1, Sem), passed(Cid).

%% course Id is taken at semester Sem.                            %% coreq
taken_together(Id, Sem) :- taken(Id, _, _, Sem, _).

%% could be taken before or at the same semester.                 %% pre_or_coreq
passed_before_or_together_grade(Id, Grade, Sem) :- 
  grade_points(Grade, _), passed_before_grade(Id, Grade, Sem).
passed_before_or_together_grade(Id, Grade, Sem) :- 
  grade_points(Grade, _), taken_together(Id, Sem).

offered_in_range(Id) :- offered(Id, Sem), before(start_sem, Sem), before(Sem, finish_sem).