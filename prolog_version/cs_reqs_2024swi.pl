subseq([], []).
subseq([H|T], [H|Sub]) :- subseq(T, Sub).
subseq([_|T], Sub) :- subseq(T, Sub).

is_higher(Grade, Grade2) :- grade_points(Grade, Points), grade_points(Grade2, Points2), Points >= Points2.
c_or_higher(Grade) :- is_higher(Grade, 'C').

%% mapping letter grade to points for GPA calculation
grade_points('A', 4.0). grade_points('A-', 3.67).
grade_points('B+', 3.33). grade_points('B', 3.0). grade_points('B-', 2.67).
grade_points('C+', 2.33). grade_points('C', 2.0). grade_points('C-', 1.67).
grade_points('D+', 1.33). grade_points('D', 1.0). grade_points('D-', 0.67).
grade_points('F', 0.0).

passed(Id) :- taken(Id, _, Grade, _, _), c_or_higher(Grade).

% passed all courses with course Id in Subject
passed_all(Subject) :- forall(c(Subject, Id), passed(Id)).

% passed all courses with course Id in Subject
passed_all(Subject, ReqData) :- forall(c(Subject, Id), memberchk([Id, _, _], ReqData)).

:- dynamic(wit/2).
% course C is witness for passing all courses in a subject in requirement Item
wit(Item, Id) :- s(Item, Subj), passed_all(Subj), c(Subj, Id).

:- dynamic(c/2).
:- dynamic(s/2).

% 1. Required Introductory Courses
c(prog, 'CSE 114'). c(prog, 'CSE 214'). c(prog, 'CSE 216').
c(prog2, 'CSE 160'). c(prog2, 'CSE 161').
c(prog2, 'CSE 260'). c(prog2, 'CSE 261').
c(dmath, 'CSE 215').
c(dmath2, 'CSE 150').
c(sys, 'CSE 220').
s(intro, prog). s(intro, prog2). s(intro, dmath). s(intro, dmath2). s(intro, sys).

intro_courses(Id) :-
  c(prog, Id); c(prog2, Id); c(dmath, Id); c(dmath2, Id); c(sys, Id).

intro_req :-
  (passed_all(prog); passed_all(prog2)),
  (passed_all(dmath); passed_all(dmath2)),
  passed_all(sys).

% 2. Required Advanced Courses
c(other, 'CSE 310'). c(other, 'CSE 316'). c(other, 'CSE 320'). c(other, 'CSE 416').
c(algo, 'CSE 373').
c(algo2, 'CSE 385').
c(theory, 'CSE 303').
c(theory2, 'CSE 350').
s(adv, theory). s(adv, theory2). s(adv, algo). s(adv, algo2). s(adv, other).

advanced_courses(Id) :-
  c(other, Id); c(algo, Id); c(algo2, Id); c(theory, Id); c(theory2, Id).

advanced_req :-
  (passed_all(algs); passed_all(algs2)),
  (passed_all(theory); passed_all(theory2)),
  passed_all(other).

% 3. Computer Science Electives  %% simpler than 2025
elective_exclude('CSE 475').
elective_exclude('CSE 495').
elective_exclude('CSE 496').
elective_exclude('CSE 301').
elective_exclude('CSE 300').
elective_exclude('CSE 312').

elective_req :- findall(Id, (passed(Id), elective(Id)), Electives),
  length(Electives, Count),
    Count > 3.

elective(Id) :- \+ advanced_courses(Id),
    taken(Id, Creds, _, _, _),
    Creds >= 3,
    \+ elective_exclude(Id),
    upperdivCS(Id).

upperdivCS(Id) :- 
  atom_concat('CSE ', CourseNumstr, Id),
  atom_number(CourseNumstr, CourseNumInt),
  CourseNumInt >= 300.

wit(elect, Id) :- passed(Id), elective(Id).

% Req 4. Calculus
c(calc, 'AMS 151'). c(calc, 'AMS 161').
c(calc2, 'MAT 125'). c(calc2, 'MAT 126'). c(calc2, 'MAT 127').
c(calc3, 'MAT 131'). c(calc3, 'MAT 132').
s(calc, calc). s(calc, calc2). s(calc, calc3).
calc_req :-
  (passed_all(calc); passed_all(calc2); passed_all(calc3)).

% Req 5. Linear Algebra
c(alg1, 'MAT 211').
c(alg2, 'AMS 210').
s(alg, alg1). s(alg, alg2).
alg_req :-
  (passed_all(alg1); passed_all(alg2)).

% Req 6. Statistics / Finite Math
c(fmath, 'AMS 301').
c(sta1, 'AMS 310').
c(sta2, 'AMS 311').
s(sta, fmath). s(sta, sta1). s(sta, sta2).
sta_req :-
  passed_all(fmath),
  (passed_all(sta1); passed_all(sta2)).

% 7. At least one of the following natural science lecture/laboratory combinations:
% BIO 201/204 or BIO 202/204 or BIO 203/204 or CHE 131/133 or CHE 152/154 or PHY 126/133 or
% PHY 131/133 or PHY 141/133
c(sci1, 'BIO 201'). c(sci1, 'BIO 204').
c(sci2, 'BIO 202'). c(sci2, 'BIO 204').
c(sci3, 'BIO 203'). c(sci3, 'BIO 204').
c(sci4, 'CHE 131'). c(sci4, 'CHE 133').
c(sci5, 'CHE 152'). c(sci5, 'CHE 154').
c(sci6, 'PHY 126'). c(sci6, 'PHY 133').
c(sci7, 'PHY 131'). c(sci7, 'PHY 133').
c(sci8, 'PHY 141'). c(sci8, 'PHY 133').
c(scimisc, 'AST 203'). c(scimisc, 'AST 205').
c(scimisc, 'CHE 132'). c(scimisc, 'CHE 321'). c(scimisc, 'CHE 322'). c(scimisc, 'CHE 331'). c(scimisc, 'CHE 332').
c(scimisc, 'GEO 113'). c(scimisc, 'GEO 122'). c(scimisc, 'GEO 102'). c(scimisc, 'GEO 103'). c(scimisc, 'GEO 112').
c(scimisc, 'PHY 125'). c(scimisc, 'PHY 127'). c(scimisc, 'PHY 132'). c(scimisc, 'PHY 134'). c(scimisc, 'PHY 142'). c(scimisc, 'PHY 251'). c(scimisc, 'PHY 252').

sci_courses(Id) :-
  c(sci1, Id); c(sci2, Id); c(sci3, Id); c(sci4, Id); c(sci5, Id); c(sci6, Id); c(sci7, Id); c(sci8, Id); c(scimisc, Id).

sci_subseq_req :-
  findall([Id, Creds, Grade], (taken(Id, Creds, Grade, _, _), sci_courses(Id), grade_points(Grade, _)), SciData),
  subseq(SciData, SciReqData),
  lab_req(SciReqData),
  sci_req(SciReqData).

lab_req(ReqData) :-
  (passed_all(sci1, ReqData); passed_all(sci2, ReqData);
  passed_all(sci3, ReqData); passed_all(sci4, ReqData);
  passed_all(sci5, ReqData); passed_all(sci6, ReqData);
  passed_all(sci7, ReqData); passed_all(sci8, ReqData)).

sci_req(ReqData) :-
    sci_acc(ReqData, SciCreds, SciQP),
    SciCreds >= 9,
    SciQP / SciCreds >= 2.0.

sci_acc([], 0.0, 0.0).
sci_acc([[_, Creds, Grade]|T], CSum, GSum) :-
  sci_acc(T, SubCSum, SubGSum),
  CSum is SubCSum + Creds,
  grade_points(Grade, Points),
  GSum is SubGSum + (Points*Creds).

wit(sci, Id) :- sci_courses(Id), taken(Id, _, _, _, _).

course_in_cat123(Id) :- intro_courses(Id) ; advanced_courses(Id) ; elective(Id).
credits_at_sb_cat123(Total) :-
    aggregate_all(sum(Creds),
        (taken(Cid, Creds, _, _, 'SBU'),
         passed(Cid),
         course_in_cat123(Cid)),
        Total).
satisfied_residency_123 :- credits_at_sb_cat123(Total), Total >= 24.
wit(res123, Id) :- taken(Id, Creds, _, _, 'SBU'), passed(Id), course_in_cat123(Id).

course_in_cat23(Id) :- advanced_courses(Id) ; elective(Id).

credits_at_sb_cat23(Total) :-
    aggregate_all(sum(Creds),
        (taken(Cid, Creds, _, _, 'SBU'),
         passed(Cid),
         course_in_cat23(Cid)),
        Total).
satisfied_residency_23 :- credits_at_sb_cat23(Total), Total >= 18.
wit(res23, Id) :- taken(Id, Creds, _, _, 'SBU'), passed(Id), course_in_cat123(Id).

% ethics and communication courses
c(ethics, 'CSE 312'). c(writing, 'CSE 300').
s(ethics, ethics). s(writing, writing).
writing_req :- passed_all(writing).
ethics_req :- passed_all(ethics).
all_requirements :-
    intro_req,
    advanced_req,
    elective_req,
    satisfied_residency_123,
    satisfied_residency_23,
    calc_req,
    alg_req,
    sta_req,
    sci_subseq_req,
    writing_req,
    ethics_req.

measure_run_swi(Goal, T) :-
  statistics(cputime, T0),
  (call(Goal) -> Outcome = yes ; Outcome = no),
  statistics(cputime, T1),
  T is T1 - T0,
  write('result('), write(Outcome), writeln(')'),
  write('CPU time: '), write(T), writeln(' s').
