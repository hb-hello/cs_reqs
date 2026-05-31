:- import memberchk/2, member/2, length/2 from basics.
:- dynamic taken/5.

:- op(1150,fx,(discontiguous)).
discontiguous(_).

atom_number(Atom, Num) :-
    atom_codes(Atom, Codes),
    number_codes(Num, Codes).

distinct(X,Goal) :-
    findall(X,Goal,List),
    sort(List,SList),
    member(X,SList).

aggregate_all(count, Goal, Counts) :-
    findall(_, Goal, Results),
    length(Results, Counts).

aggregate_all(sum(Exp), Goal, Sum) :-
    findall(Exp, Goal, Vs),
    sum_acc(Vs, 0, Sum).

sum_acc([], S, S).
sum_acc([V|Vs], A, S) :- A1 is A + V, sum_acc(Vs, A1, S).

measure_run_xsb(Goal) :-
  statistics(runtime, [_,_]),
  (call(Goal) -> Outcome = yes ; Outcome = no),
  statistics(runtime, [_,T]),
  write('result('), write(Outcome), writeln(')'),
  write('CPU time: '), write(T), writeln(' s').

:- include('cs_reqs_2024swi.pl').