% example to test writing prereq in generation
% clingo --text [thisfile.lp] to see the generated program
%   generated program has #delay, what does it mean?
%   https://github.com/potassco/clingo/issues/331
courses(c1;c2;c3).
sem(1..3).
before(Sem1, Sem2) :- sem(Sem1), sem(Sem2), Sem1 < Sem2.
offered(Id, Sem) :- courses(Id), sem(Sem).

prereq(c1, Sem) :- passed_before(c2, Sem).
prereq(c2, Sem) :- passed_before(c3, Sem).
prereq(c3, Sem) :- offered(c3, Sem).

{plan(Id, Sem) : offered(Id, Sem), prereq(Id, Sem)} <= 1 :- offered(Id, _).

taken(Id, "A", Sem) :- plan(Id, Sem).

passed_before(Id, Sem) :- taken(Id, "A", Sem1), before(Sem1, Sem).

planned(c1) :- plan(c1, _).
:- not planned(c1).

#show plan/2.
#show passed_before/2.