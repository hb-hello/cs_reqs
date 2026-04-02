:- import memberchk/2 from lists.

c_or_higher(Grade) :- memberchk(Grade, ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']).

% upper_division() :- 

% GPA() :- 


% taken(Id, Credits, Grade, When, Where): taken course Id with Credits, etc.

passed(Id) :- taken(Id, _Credits, Grade, _When, _Where), c_or_higher(Grade).

% c(Id, Subject): course Id in Subject

% passed all courses with course Id in Subject
passed_all(Subject) :- forall(c(Id, Subject), passed(Id)).

% course C is witness for passing all courses in a subject in requirement Item
wit(Item, C) :- s(Item, Subj), passed_all(Subj), c(C, Subj).


% 1. Required Introductory Courses

c('CSE 114', prog). c('CSE 214', prog). c('CSE 216', prog). 
c('CSE 160', prog2). c('CSE 161', prog2). 
c('CSE 260', prog2). c('CSE 261', prog2).
c('CSE 215', dmath). 
c('CSE 150', dmath2).
c('CSE 220', sys). 

s(intro, prog). s(intro, prog2). s(intro, dmath). s(intro, dmath2).
s(intro, sys).

intro_req :-
  (passed_all(prog); passed_all(prog2)),
  (passed_all(dmath); passed_all(dmath2)),
  passed_all(sys).

% 2.


% test

taken_ids(['CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220', 
           'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',
           'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',
           'CSE 300', 'CSE 312',
           'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',
           'PHY 131', 'PHY 133', 'AST 203']).

%:- table taken_ids/2 as subsumptive,index(0). %abstract call to variable
%taken_id(Id) :- taken_ids(Ids), member(Id, Ids).

%:- table taken/5 as subsumptive,index(0).    
taken(Id, 4, 'A', (2024,2), 'SB') :- taken_ids(Ids), memberchk(Id,Ids).

test :- intro_req.


% could define forall using findall, avoid negation, but not as efficient
% fa_forall(P, Q) :- findall(Q, P, QList), all_true(QList).
% all_true([]).
% all_true([Q|Qs]) :- call(Q), all_true(Qs).
