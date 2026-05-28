is_higher(Grade, Grade2) :- grade_toPoints(Grade, Points), grade_toPoints(Grade2, Points2), Points >= Points2.
c_or_higher(Grade) :- is_higher(Grade, 'C').

%% mapping letter grade to points for GPA calculation
grade_toPoints('A', 4.0). grade_toPoints('A-', 3.67).
grade_toPoints('B+', 3.33). grade_toPoints('B', 3.0). grade_toPoints('B-', 2.67).
grade_toPoints('C+', 2.33). grade_toPoints('C', 2.0). grade_toPoints('C-', 1.67).
grade_toPoints('D+', 1.33). grade_toPoints('D', 1.0). grade_toPoints('D-', 0.67).
grade_toPoints('F', 0.0).

passed(Id) :- taken(Id, _, Grade, _, _), c_or_higher(Grade).


% passed all courses with course Id in Subject
passed_all(Subject) :- forall(c(Id, Subject), passed(Id)).

% passed all courses with course Id in Subject
passed_all(Subject, ReqData) :- forall(c(Id, Subject), memberchk(f(Id, _, _), ReqData)).

:- discontiguous wit/2.
% course C is witness for passing all courses in a subject in requirement Item
wit(Item, Id) :- s(Item, Subj), passed_all(Subj), c(Id, Subj).


:- discontiguous c/2.
:- discontiguous s/2.
% 1. Required Introductory Courses
%%% CHANGED for 2025: restructured from prog/prog2/dmath/dmath2/sys
%%%   to focs/focs2/prog/prog2/focs_ii/focs_ii2/sys
c('CSE 113', focs).
c('CSE 150', focs2).
c('CSE 114', prog). c('CSE 214', prog).
c('CSE 160', prog2). c('CSE 161', prog2).
c('CSE 260', prog2). c('CSE 261', prog2).
c('CSE 213', focs_ii).
c('CSE 350', focs_ii2).
c('CSE 220', sys).
s(intro, focs). s(intro, focs2). s(intro, prog). s(intro, prog2). s(intro, focs_ii). s(intro, focs_ii2). s(intro, sys).

intro_courses(Id) :-
  c(Id, focs); c(Id, focs2); c(Id, prog); c(Id, prog2); c(Id, focs_ii); c(Id, focs_ii2); c(Id, sys).

intro_req() :-
  (passed_all(focs); passed_all(focs2)),
  (passed_all(prog); passed_all(prog2)),
  (passed_all(focs_ii); passed_all(focs_ii2)),
  passed_all(sys).

% 2. Required Advanced Courses
%%% CHANGED for 2025: restructured from theory/theory2/algs/algs2/other
c('CSE 307', ppl).
c('CSE 316', softdev).
c('CSE 320', sysfund).
c('CSE 373', algs).
c('CSE 385', algs2).
c('CSE 356', cloud).
c('CSE 416', se).
s(adv, ppl). s(adv, softdev). s(adv, sysfund). s(adv, algs). s(adv, algs2). s(adv, cloud). s(adv, se).

advanced_courses(Id) :-
  c(Id, ppl); c(Id, softdev); c(Id, sysfund); c(Id, algs); c(Id, algs2); c(Id, cloud); c(Id, se).

advanced_req() :-
  (passed_all(ppl); passed_all(prog2)),   %% CSE 307, or honors prog2 substitutes for it
  passed_all(softdev),
  passed_all(sysfund),
  (passed_all(algs); passed_all(algs2)),
  (passed_all(cloud); passed_all(se)).

% 3. Computer Science Electives
%%% CHANGED for 2025: threshold raised from 4 to 6, added elective cap
disallowed_elective('CSE475').
disallowed_elective('CSE495').
disallowed_elective('CSE301').

capped_elective('CSE 487').
capped_elective('CSE 496').
capped_elective('VIP 395').
capped_elective('VIP 396').
capped_elective('VIP 495').
capped_elective('VIP 496').

elective(Id) :- \+ advanced_courses(Id),
    taken(Id, Creds, _, _, _),
    Creds >= 3,
    \+ disallowed_elective(Id),
    \+ capped_elective(Id),
    upperdivCS(Id).

upperdivCS(Id) :- atom_concat('CSE', CourseNumstr, Id),
    atom_number(CourseNumstr, CourseNumInt),
    CourseNumInt >= 300.

capped_elective_count(Cap) :-
    findall(Id, (passed(Id), taken(Id, Creds, _, _, _), Creds >= 3, capped_elective(Id)), CappedList),
    length(CappedList, CappedLen),
    (CappedLen > 0 -> Cap = 1 ; Cap = 0).

elective_req() :-
    findall(Id, (passed(Id), elective(Id)), Electives),
    length(Electives, RegCount),
    capped_elective_count(Cap),
    Total is RegCount + Cap,
    Total >= 6.

wit(elective, Id) :- elective_req(), passed(Id), elective(Id).

% 4. Calculus
%%% NO CHANGE for 2025
c('AMS 151', calc). c('AMS 161', calc).
c('MAT 125', calc2). c('MAT 126', calc2). c('MAT 127', calc2).
c('MAT 131', calc3). c('MAT 132', calc3).

% 5. Linear Algebra
%%% NO CHANGE for 2025
c('MAT 211', linalg).
c('AMS 210', linalg2).

% 6. Statistics
%%% CHANGED for 2025: removed AMS 301 (finite) and AMS 311 (prob2)
c('AMS 310', prob).

s(math, calc). s(math, calc2). s(math, calc3).
s(math, linalg). s(math, linalg2).
s(math, prob).

math_req() :-
  (passed_all(calc); passed_all(calc2); passed_all(calc3)),
  (passed_all(linalg); passed_all(linalg2)),
  passed_all(prob).

% 7. At least one of the following natural science lecture/laboratory combinations:
%%% NO CHANGE for 2025 (same combos)
c('BIO 201', sci1). c('BIO 204', sci1).
c('BIO 202', sci2). c('BIO 204', sci2).
c('BIO 203', sci3). c('BIO 204', sci3).
c('CHE 131', sci4). c('CHE 133', sci4).
c('CHE 152', sci5). c('CHE 154', sci5).
c('PHY 126', sci6). c('PHY 133', sci6).
c('PHY 131', sci7). c('PHY 133', sci7).
c('PHY 141', sci8). c('PHY 133', sci8).

% 8. Additional natural science courses
%%% CHANGED for 2025: removed GEO courses, PHY 134, PHY 252; added BIO, CHE, PHY variants
c('AST 203', scimisc). c('AST 205', scimisc).
c('BIO 201', scimisc). c('BIO 202', scimisc). c('BIO 203', scimisc).
c('CHE 131', scimisc). c('CHE 132', scimisc). c('CHE 152', scimisc). c('CHE 321', scimisc). c('CHE 322', scimisc). c('CHE 331', scimisc). c('CHE 332', scimisc).
c('PHY 125', scimisc). c('PHY 126', scimisc). c('PHY 127', scimisc). c('PHY 131', scimisc). c('PHY 132', scimisc). c('PHY 142', scimisc). c('PHY 251', scimisc).

sci_courses(Id) :-
  c(Id, sci1); c(Id, sci2); c(Id, sci3); c(Id, sci4); c(Id, sci5); c(Id, sci6); c(Id, sci7); c(Id, sci8); c(Id, scimisc).

sci_subset_req():-
  findall(f(Id, Creds, Grade), (taken(Id, Creds, Grade, _, _), sci_courses(Id), grade_toPoints(Grade, _)), SciData),
  subset(SciData, SciReqData),
  lab_req(SciReqData),
  sci_req(SciReqData).

lab_req(ReqData) :-
  (passed_all(sci1, ReqData); passed_all(sci2, ReqData);
  passed_all(sci3, ReqData); passed_all(sci4, ReqData);
  passed_all(sci5, ReqData); passed_all(sci6, ReqData);
  passed_all(sci7, ReqData); passed_all(sci8, ReqData)).

sci_req(ReqData) :-
    sci_acc(ReqData, f(SciCreds, SciQP)),
    SciCreds >= 9,
    SciQP / SciCreds >= 2.0.

sci_acc([], f(0.0,0.0)).
sci_acc([f(_, Creds, Grade)|T], f(CSum, GSum)) :-
  sci_acc(T, f(SubCSum, SubGSum)),
  SubCSum + Creds == CSum,
  grade_toPoints(Grade, Points),
  SubGSum + (Points*Creds) == GSum.

subset([], []).
subset([_|T], Sub) :- subset(T, Sub).
subset([H|T], [H|Sub]) :- subset(T, Sub).

wit(science, Id) :- sci_subset_req(), sci_courses(Id), taken(Id, _, _, _, _).

course_in_cat123(Id) :- intro_courses(Id) ; advanced_courses(Id) ; upperdivCS(Id).
credits_at_sb_cat123(Total) :-
    aggregate_all(sum(Creds),
        (taken(Id, Creds, _, _, 'SBU'),
         passed(Id),
         course_in_cat123(Id)),
        Total).
satisfied_residency_123() :- credits_at_sb_cat123(Total), Total >= 24.
wit(res123, Id) :- satisfied_residency_123, taken(Id, Creds, _, _, 'SBU'), passed(Id), course_in_cat123(Id).

course_in_cat23(Id) :- advanced_courses(Id) ; upperdivCS(Id).
credits_at_sb_cat23(Total) :-
    aggregate_all(sum(Creds),
        (taken(Id, Creds, _, _, 'SBU'),
         passed(Id),
         course_in_cat23(Id)),
        Total).
satisfied_residency_23() :- credits_at_sb_cat23(Total), Total >= 18.
wit(res23, Id) :- satisfied_residency_23, taken(Id, Creds, _, _, 'SBU'), passed(Id), course_in_cat123(Id).

% 9. Required Non-Technical Courses
%%% CHANGED for 2025: renamed from ethics_comm to nontechnical
c('CSE 312', nontechnical). c('CSE 300', nontechnical).
s(nontechnical, nontechnical).

all_requirements() :-
    intro_req(),
    advanced_req(),
    elective_req(),
    satisfied_residency_123(),
    satisfied_residency_23(),
    math_req(),
    sci_subset_req(),
    passed_all(nontechnical).


%%% CHANGED for 2025: updated test courses
taken('CSE 113', 3, 'A', (2024,2), 'SBU').
taken('CSE 214', 3, 'A', (2024,2), 'SBU').
taken('CSE 114', 3, 'A', (2024,2), 'SBU').
taken('CSE 213', 3, 'A', (2024,2), 'SBU').
taken('CSE 220', 3, 'A', (2024,2), 'SBU').
taken('CSE 4', 3, 'A', (2024,2), 'SBU').
taken('CSE 0', 3, 'A', (2024,2), 'SBU').
taken('CSE 20', 3, 'A', (2024,2), 'SBU').
taken('CSE 2330', 3, 'A', (2024,2), 'SBU').