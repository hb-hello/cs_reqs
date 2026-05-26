subseq([], []).
subseq([H|T], [H|Sub]) :- subseq(T, Sub).
subseq([_|T], Sub) :- subseq(T, Sub).

is_higher(Grade, Grade2) :- grade_points(Grade, Points), grade_points(Grade2, Points2), Points >= Points2.
is_c_or_higher(Grade) :- is_higher(Grade, 'C').

%% mapping letter grade to points for GPA calculation
grade_points('A', 4.0). grade_points('A-', 3.67).
grade_points('B+', 3.33). grade_points('B', 3.0). grade_points('B-', 2.67).
grade_points('C+', 2.33). grade_points('C', 2.0). grade_points('C-', 1.67).
grade_points('D+', 1.33). grade_points('D', 1.0). grade_points('D-', 0.67).
grade_points('F', 0.0).

passed(Id) :- taken(Id, _, Grade, _, _), is_c_or_higher(Grade).

% passed all courses with course Id in Subject
passed_all(Subject) :- forall(c(Subject, Id), passed(Id)).

% passed all courses with course Id in Subject
passed_all(Subject, ReqData) :- forall(c(Subject, Id), memberchk([Id, _, _], ReqData)).

:- dynamic(wit/2).
% course C is witness for passing all courses in a subject in requirement Item
wit(I, Cid) :- item(I), s(I, Subj), passed_all(Subj), c(Subj, Cid).

courses(Cid, I) :- item(I), s(I, Subj), c(Subj, Cid).

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

req(intro) :-
  (passed_all(prog); passed_all(prog2)),
  (passed_all(dmath); passed_all(dmath2)),
  passed_all(sys).

% 2. Required Advanced Courses
c(theory, 'CSE 303'). c(theory2, 'CSE 350').
c(algo, 'CSE 373'). c(algo2, 'CSE 385').
c(other, 'CSE 310'). c(other, 'CSE 316'). c(other, 'CSE 320'). c(other, 'CSE 416').
s(adv, theory). s(adv, theory2). s(adv, algo). s(adv, algo2). s(adv, other).

req(adv) :-
  (passed_all(algo); passed_all(algo2)),
  (passed_all(theory); passed_all(theory2)),
  passed_all(other).

% 3. Computer Science Electives  %% simpler than 2025
c(elect_exclude, 'CSE 475'). c(elect_exclude, 'CSE 495'). c(elect_exclude, 'CSE 496'). c(elect_exclude, 'CSE 301'). c(elect_exclude, 'CSE 300'). c(elect_exclude, 'CSE 312').

cse_upper_division(Id) :- 
  atom_concat('CSE ', CourseNumstr, Id),
  atom_number(CourseNumstr, CourseNumInt),
  CourseNumInt >= 300.

elect_passed(Id) :- 
  taken(Id, Cr, G, _, _), cse_upper_division(Id), 
  is_c_or_higher(G), Cr >= 3,
  \+ courses(Id, adv), \+ c(elect_exclude, Id).

req(elect) :-
  aggregate_all(count, distinct(Id, elect_passed(Id)), Count), Count >= 4.

wit(elect, Id) :- elect_passed(Id).

% Req 4. Calculus
c(calc, 'AMS 151'). c(calc, 'AMS 161').
c(calc2, 'MAT 125'). c(calc2, 'MAT 126'). c(calc2, 'MAT 127').
c(calc3, 'MAT 131'). c(calc3, 'MAT 132').
s(calc, calc). s(calc, calc2). s(calc, calc3).

req(calc) :- passed_all(calc); passed_all(calc2); passed_all(calc3).

% Req 5. Linear Algebra
c(alg1, 'MAT 211').
c(alg2, 'AMS 210').
s(alg, alg1). s(alg, alg2).

req(alg) :- passed_all(alg1); passed_all(alg2).

% Req 6. Statistics / Finite Math
c(fmath, 'AMS 301').
c(sta1, 'AMS 310').
c(sta2, 'AMS 311').
s(sta, fmath). s(sta, sta1). s(sta, sta2).

req(sta) :-
  passed_all(fmath),
  (passed_all(sta1); passed_all(sta2)).

% 7. At least one of the following natural science lecture/laboratory combinations:
% BIO 201/204 or BIO 202/204 or BIO 203/204 or CHE 131/133 or CHE 152/154 or PHY 126/133 or
% PHY 131/133 or PHY 141/133
c(bio, 'BIO 201'). c(bio, 'BIO 204').
c(bio2, 'BIO 202'). c(bio2, 'BIO 204').
c(bio3, 'BIO 203'). c(bio3, 'BIO 204').
c(che, 'CHE 131'). c(che, 'CHE 133').
c(che2, 'CHE 152'). c(che2, 'CHE 154').
c(phy, 'PHY 126'). c(phy, 'PHY 133').
c(phy2, 'PHY 131'). c(phy2, 'PHY 133').
c(phy3, 'PHY 141'). c(phy3, 'PHY 133').
s(sci_combs, bio). s(sci_combs, bio2). s(sci_combs, bio3). s(sci_combs, che). s(sci_combs, che2). s(sci_combs, phy). s(sci_combs, phy2). s(sci_combs, phy3).

% 8. Additional natural science courses selected from above and following list:
% Note: The courses selected in 7 and 8 must carry at least 9 credits.
c(sci_more, 'AST 203'). c(sci_more, 'AST 205').
c(sci_more, 'CHE 132'). c(sci_more, 'CHE 321'). c(sci_more, 'CHE 322'). c(sci_more, 'CHE 331'). c(sci_more, 'CHE 332').
c(sci_more, 'GEO 102'). c(sci_more, 'GEO 103'). c(sci_more, 'GEO 112'). c(sci_more, 'GEO 123'). c(sci_more, 'GEO 122').
c(sci_more, 'PHY 125'). c(sci_more, 'PHY 127'). c(sci_more, 'PHY 132'). c(sci_more, 'PHY 134'). c(sci_more, 'PHY 142'). c(sci_more, 'PHY 251'). c(sci_more, 'PHY 252').

%% distinct/2 for deduplicating courses that appears multiple times (e.g. PHY 133)
sci_taken(Id) :- distinct(Id,
  (taken(Id, _, _, _, _), 
  ((s(sci_combs, Subj), c(Subj, Id)); c(sci_more, Id)))).

req_sci_combs(ReqData) :- s(sci_combs, Subj), passed_all(Subj, ReqData).

%% TODO: this is more general than sci requirement, might want to move it to the top and use it other requirements as well.
best_taken(Id, Cr, Grade, When, Where) :- 
    taken(Id, Cr, Grade, When, Where), 
    grade_points(Grade, GPts),
    \+ (taken(Id, _, BetterGrade, _, _), grade_points(BetterGrade, BGPts), BGPts > GPts).

req(sci) :-
  findall([Id, Cr, Grade], 
          (sci_taken(Id), once(best_taken(Id, Cr, Grade, _, _)), % once/1 break ties if repeats have same grade
                          grade_points(Grade, _)), 
          SciData),
  once((subseq(SciData, SciReqData),
        req_sci_combs(SciReqData),
        aggregate_all(sum(Cr), member([_, Cr, _], SciReqData), SciCreds),
        SciCreds >= 9,
        aggregate_all(sum(Cr * Pts), (member([_, Cr, G], SciReqData), grade_points(G, Pts)), SciWtdGradeSum),
        SciWtdGradeSum / SciCreds >= 2.0)).

wit(sci, Id) :- sci_taken(Id).

% ethics and communication courses
c(ethics, 'CSE 312'). 
s(ethics, ethics).

req(ethics) :- passed_all(ethics).

c(writing, 'CSE 300').
s(writing, writing).

req(writing) :- passed_all(writing).

items123_course(Cid) :- courses(Cid, intro) ; courses(Cid, adv) ; elect_passed(Cid).
items23_course(Cid) :- courses(Cid, adv) ; elect_passed(Cid).

items123_credits(Crs) :-
  aggregate_all(sum(Cr),
                (taken(Cid, Cr, _, _, 'SB'), passed(Cid), items123_course(Cid)),
                Crs).

items23_credits(Crs) :-
  aggregate_all(sum(Cr),
                (taken(Cid, Cr, _, _, 'SB'), passed(Cid), items23_course(Cid)),
                Crs).

req(credits_at_sb) :-
  items123_credits(Items123_credit), Items123_credit >= 24,
  items23_credits(Items23_credit), Items23_credit >= 18.

%% TODO: items123 includes items23. only need to include items123.
wit(credits_at_sb, Id) :- (items123_course(Id); items23_course(Id)), taken(Id, _, _, _, 'SB'), passed(Id).

item(intro). item(adv). item(elect). 
item(calc). item(alg). item(sta). item(sci).
item(ethics). item(writing). item(credits_at_sb).

degree :- forall(item(I), req(I)).

measure_run_swi(Goal, T) :-
  statistics(cputime, T0),
  (call(Goal) -> Outcome = yes ; Outcome = no),
  statistics(cputime, T1),
  T is T1 - T0,
  write('result('), write(Outcome), writeln(')'),
  write('CPU time: '), write(T), writeln(' s').
