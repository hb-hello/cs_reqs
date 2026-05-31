subseq([], []).
subseq([H|T], [H|Sub]) :- subseq(T, Sub).
subseq([_|T], Sub) :- subseq(T, Sub).

:- discontiguous(wit/2).
:- discontiguous(c/2).
:- discontiguous(s/2).
is_higher(Grade, Grade2) :- grade_points(Grade, Points), grade_points(Grade2, Points2), Points >= Points2.
is_c_or_higher(Grade) :- is_higher(Grade, 'C').

%% mapping letter grade to points for GPA calculation
grade_points('A', 4.0). grade_points('A-', 3.67).
grade_points('B+', 3.33). grade_points('B', 3.0). grade_points('B-', 2.67).
grade_points('C+', 2.33). grade_points('C', 2.0). grade_points('C-', 1.67).
grade_points('D+', 1.33). grade_points('D', 1.0). grade_points('D-', 0.67).
grade_points('F', 0.0).

passed(Cid) :- taken(Cid, _, Grade, _, _), is_c_or_higher(Grade).

% passed all courses with course Cid in Subject
passed_all(Subject) :- forall(c(Subject, Cid), passed(Cid)).

% course C is witness for passing all courses in a subject in requirement Item
wit(I, Cid) :- item(I), s(I, Subj), passed_all(Subj), c(Subj, Cid).

courses(Cid, I) :- item(I), s(I, Subj), c(Subj, Cid).

% 1. Required Introductory Courses
%%% CHANGED for 2025: restructured from prog/prog2/dmath/dmath2/sys
%%%   to focs/focs2/prog/prog2/focs_ii/focs_ii2/sys
c(focs, 'CSE 113').
c(focs2, 'CSE 150').
c(prog, 'CSE 114'). c(prog, 'CSE 214').
c(prog2, 'CSE 160'). c(prog2, 'CSE 161').
c(prog2, 'CSE 260'). c(prog2, 'CSE 261').
c(focs_ii, 'CSE 213').
c(focs_ii2, 'CSE 350').
c(sys, 'CSE 220').
s(intro, focs). s(intro, focs2). s(intro, prog). s(intro, prog2). s(intro, focs_ii). s(intro, focs_ii2). s(intro, sys).

req(intro) :- (passed_all(focs); passed_all(focs2)), (passed_all(prog); passed_all(prog2)),
              (passed_all(focs_ii); passed_all(focs_ii2)), passed_all(sys).

% 2. Required Advanced Courses
%%% CHANGED for 2025: added CSE 307 (pl), CSE 356 (cloud); CSE 350 moved to focs_ii2
c(pl, 'CSE 307').
c(softdev, 'CSE 316').
c(sysfund, 'CSE 320').
c(algo, 'CSE 373').
c(algo2, 'CSE 385').
c(cloud, 'CSE 356').
c(se, 'CSE 416').
s(adv, pl). s(adv, softdev). s(adv, sysfund). s(adv, algo). s(adv, algo2). s(adv, cloud). s(adv, se).

req(adv) :- (passed_all(pl); passed_all(prog2)),    %% CSE 307, or honors prog2 substitutes for it
            passed_all(softdev), passed_all(sysfund), (passed_all(algo); passed_all(algo2)),
            (passed_all(cloud); passed_all(se)).

% 3. Computer Science Electives
%%% CHANGED for 2025: threshold raised from 4 to 6; added capped electives
c(elect_exclude, 'CSE 475'). c(elect_exclude, 'CSE 495'). c(elect_exclude, 'CSE 300'). c(elect_exclude, 'CSE 301'). c(elect_exclude, 'CSE 312').
c(elect_capped, 'CSE 487'). c(elect_capped, 'CSE 496'). c(elect_capped, 'VIP 395'). c(elect_capped, 'VIP 396'). c(elect_capped, 'VIP 495'). c(elect_capped, 'VIP 496').

cse_upper_division(Cid) :-
  atom_concat('CSE ', CourseNumstr, Cid),
  atom_number(CourseNumstr, CourseNumInt),
  CourseNumInt >= 300.

elect_passed(Cid) :-
  taken(Cid, Cr, G, _, _), is_c_or_higher(G),
  cse_upper_division(Cid),
  Cr >= 3, \+ courses(Cid, adv), \+ c(elect_exclude, Cid), \+ c(elect_capped, Cid).

%% if courses passed in elect_capped total credits >= 3, it counts as one elective
elect_capped_sat :-
  aggregate_all(sum(Cr), (c(elect_capped, Cid), passed(Cid), taken(Cid, Cr, _, _, _)), Sum),
  Sum >= 3.

req(elect) :- aggregate_all(count, distinct(Cid, elect_passed(Cid)), Count),
              (elect_capped_sat -> Total is Count + 1 ; Total = Count), Total >= 6.

wit(elect, Cid) :- elect_passed(Cid).
wit(elect, Cid) :- elect_capped_sat, c(elect_capped, Cid), passed(Cid).

% Req 4. Calculus
%%% NO CHANGE for 2025
c(calc, 'AMS 151'). c(calc, 'AMS 161').
c(calc2, 'MAT 125'). c(calc2, 'MAT 126'). c(calc2, 'MAT 127').
c(calc3, 'MAT 131'). c(calc3, 'MAT 132').
s(calc, calc). s(calc, calc2). s(calc, calc3).

req(calc) :- passed_all(calc); passed_all(calc2); passed_all(calc3).

% Req 5. Linear Algebra
%%% NO CHANGE for 2025
c(alg1, 'MAT 211').
c(alg2, 'AMS 210').
s(alg, alg1). s(alg, alg2).

req(alg) :- passed_all(alg1); passed_all(alg2).

% Req 6. Statistics
%%% CHANGED for 2025: simplified -- only AMS 310 required
c(sta1, 'AMS 310').
s(sta, sta1).

req(sta) :- passed_all(sta1).

% 7. At least one of the following natural science lecture/laboratory combinations:
%%% NO CHANGE for 2025 (same combos)
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
%%% CHANGED for 2025: removed GEO and PHY 134/252; added BIO 201-203, CHE 131/152, PHY 126/131
c(sci_more, 'AST 203'). c(sci_more, 'AST 205'). c(sci_more, 'BIO 201'). c(sci_more, 'BIO 202'). c(sci_more, 'BIO 203').
c(sci_more, 'CHE 131'). c(sci_more, 'CHE 132'). c(sci_more, 'CHE 152'). c(sci_more, 'CHE 321'). c(sci_more, 'CHE 322'). c(sci_more, 'CHE 331'). c(sci_more, 'CHE 332').
c(sci_more, 'PHY 125'). c(sci_more, 'PHY 126'). c(sci_more, 'PHY 127'). c(sci_more, 'PHY 131'). c(sci_more, 'PHY 132'). c(sci_more, 'PHY 142'). c(sci_more, 'PHY 251').

%% distinct/2 for deduplicating courses that appear multiple times (e.g. PHY 133)
sci_taken(Cid) :-
  distinct(Cid, (taken(Cid, _, _, _, _), ((s(sci_combs, Subj), c(Subj, Cid)); c(sci_more, Cid)))).

req_sci_combs(SciCrGrades) :- s(sci_combs, Subj), forall(c(Subj, Cid), memberchk([Cid, _, _], SciCrGrades)).

%%% CHANGED for 2025: dropped 9-credit requirement; keep GPA >= 2.0
req(sci) :-
  findall([Cid, Cr, Grade],
          (sci_taken(Cid),
           taken(Cid, Cr, Grade, _, _),
           grade_points(Grade, _)),
          SciCrGrades
         ),
  subseq(SciCrGrades, SubsetSciCrGrades),
  req_sci_combs(SubsetSciCrGrades),
  aggregate_all(sum(Cr), member([_, Cr, _], SubsetSciCrGrades), SciCrs),
  SciCrs > 0,
  aggregate_all(sum(Cr * Pts), (member([_, Cr, G], SubsetSciCrGrades), grade_points(G, Pts)), SciWtdGradeSum),
  SciWtdGradeSum / SciCrs >= 2.0.

wit(sci, Cid) :- sci_taken(Cid).

% 9. Required Non-Technical Courses
%%% CHANGED for 2025: merged ethics + writing into nontech
c(nontech, 'CSE 300'). c(nontech, 'CSE 312').
s(nontech, nontech).

req(nontech) :- passed_all(nontech).

items123_course(Cid) :- courses(Cid, intro) ; courses(Cid, adv) ; elect_passed(Cid).
items23_course(Cid) :- courses(Cid, adv) ; elect_passed(Cid).

items123_credits(Crs) :- aggregate_all(sum(Cr), (taken(Cid, Cr, _, _, 'SB'), items123_course(Cid)), Crs).
items23_credits(Crs) :- aggregate_all(sum(Cr), (taken(Cid, Cr, _, _, 'SB'), items23_course(Cid)), Crs).

req(credits_at_sb) :-
  items123_credits(Items123Crs), Items123Crs >= 24,
  items23_credits(Items23Crs), Items23Crs >= 18.

wit(credits_at_sb, Cid) :- items123_course(Cid), taken(Cid, _, _, _, 'SB').

item(intro). item(adv). item(elect). item(calc). item(alg). item(sta). item(sci). item(nontech). item(credits_at_sb).

degree :- forall(item(I), req(I)).

measure_run_swi(Goal, T) :-
  statistics(cputime, T0),
  (call(Goal) -> Outcome = yes ; Outcome = no),
  statistics(cputime, T1), T is T1 - T0,
  write('result('), write(Outcome), writeln(')'),
  write('CPU time: '), write(T), writeln(' s').
