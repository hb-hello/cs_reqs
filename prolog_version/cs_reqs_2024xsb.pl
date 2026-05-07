:- import memberchk/2 from basics.
:- import length/2 from lists.
:- import concat_atom/2 from string.
:- dynamic taken/5.

:- op(1150,fx,(discontiguous)).
discontiguous(_).

atom_number(Atom, Num) :-
    atom_codes(Atom, Codes),
    number_codes(Num, Codes).

aggregate_all(sum(Exp),Goal,Agg) :-
    findall(Exp,Goal,ExpList),
    sum_exp_list(ExpList,0,Agg).

sum_exp_list([],S,S).
sum_exp_list([E|Es],S0,S) :-
    S1 is E+S0,
    sum_exp_list(Es,S1,S).

upperdivCS(Id) :- 
  concat_atom(['CSE ', CourseNumstr], Id),
  atom_number(CourseNumstr, CourseNumInt),
  CourseNumInt >= 300.

%atom_concat(Prefix, Postfix, Full) :-
%  concat_atom([Prefix, Postfix], Full).

measure_run_xsb(Goal, T) :-
  statistics(runtime, T0),
  (call(Goal) -> Outcome = yes ; Outcome = no),
  statistics(runtime, T1),
  T is T1 - T0,
  write('result('), write(Outcome), writeln(')'),
  write('CPU time: '), write(T), writeln(' s').

:- include('cs_reqs_2024swi.pl').

