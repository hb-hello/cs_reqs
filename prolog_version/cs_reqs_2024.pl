is_higher(Grade, Grade2) :- grade_points(Grade, Points), grade_points(Grade2, Points2), Points >= Points2.
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

% course C is witness for passing all courses in a subject in requirement Item
wit(Item, Id) :- s(Item, Subj), passed_all(Subj), c(Id, Subj).


:- discontiguous c/1.
:- discontiguous s/2.
% 1. Required Introductory Courses
c('CSE 114', prog). c('CSE 214', prog). c('CSE 216', prog). 
c('CSE 160', prog2). c('CSE 161', prog2). 
c('CSE 260', prog2). c('CSE 261', prog2).
c('CSE 215', dmath). 
c('CSE 150', dmath2).
c('CSE 220', sys). 
s(intro, prog). s(intro, prog2). s(intro, dmath). s(intro, dmath2). s(intro, sys).

intro_courses(Id) :-
  c(Id, prog); c(Id, prog2); c(Id, dmath); c(Id, dmath2); c(Id, sys).

intro_req() :-
  (passed_all(prog); passed_all(prog2)),
  (passed_all(dmath); passed_all(dmath2)),
  passed_all(sys).

% 2. Required Advanced Courses
c('CSE 310', other). c('CSE 316', other). c('CSE 320', other). c('CSE 416', other). 
c('CSE 373', algs). 
c('CSE 385', algs2).
c('CSE 303', theory). 
c('CSE 350', theory2).
s(adv, theory). s(adv, theory2). s(adv, algo). s(adv, algo2). s(adv, other).

advanced_courses(Id) :-
  c(Id, other); c(Id, algs); c(Id, algs2); c(Id, theory); c(Id, theory2).

advanced_req() :-
  (passed_all(algs); passed_all(algs2)),
  (passed_all(theory); passed_all(theory2)),
  passed_all(other).

% 3. Computer Science Electives  %% simpler than 2025
disallowed_elective('CSE475').
disallowed_elective('CSE495').
disallowed_elective('CSE496').
disallowed_elective('CSE301').

elective_req() :- findall(Id, (passed(Id), elective(Id)), Electives), 
    length(Electives, Count), 
    Count > 3.

elective(Id) :- \+ advanced_courses(Id), 
    taken(Id, Creds, _, _, _), 
    Creds >= 3, 
    \+ disallowed_elective(Id), 
    upperdivCS(Id).

upperdivCS(Id) :- atom_concat('CSE', CourseNumstr, Id), 
    atom_number(CourseNumstr, CourseNumInt), 
    CourseNumInt >= 300.




% 4. AMS 151, AMS 161 Applied Calculus I, II
% Note: The following alternate calculus course sequences may be substituted for AMS 151, AMS 161 in major 
% requirements or prerequisites: MAT 125, MAT 126, MAT 127, or MAT 131, MAT 132. Equivalency for MAT courses achieved through the Mathematics Placement Examination is accepted to meet MAT course requirements.
% 5. One of the following:
% MAT 211 Introduction to Linear Algebra
% AMS 210 Applied Linear Algebra
% 6. Both of the following:
% AMS 301 Finite Mathematical Structures
% AMS 310 Survey of Probability and Statistics or AMS 311 Probability Theory 
c('AMS 151', calc). c('AMS 161', calc). 
c('MAT 125', calc2). c('MAT 126', calc2). c('MAT 127', calc2). 
c('MAT 131', calc3). c('MAT 132', calc3). 
c('MAT 211', linalg). 
c('AMS 210', linalg2).
c('AMS 301', finite).
c('AMS 310', prob). 
c('AMS 311', prob2).

math_req() :-
  (passed_all(calc); passed_all(calc2); passed_all(calc3)),
  (passed_all(linalg); passed_all(linalg2)),
  passed_all(finite),
  (passed_all(prob); passed_all(prob2)).

% 7. At least one of the following natural science lecture/laboratory combinations:
% BIO 201/204 or BIO 202/204 or BIO 203/204 or CHE 131/133 or CHE 152/154 or PHY 126/133 or 
% PHY 131/133 or PHY 141/133
c('BIO 201', sci1). c('BIO 204', sci1).
c('BIO 202', sci2). c('BIO 204', sci2).
c('BIO 203', sci3). c('BIO 204', sci3).
c('CHE 131', sci4). c('CHE 133', sci4).
c('CHE 152', sci5). c('CHE 154', sci5).
c('PHY 126', sci6). c('PHY 133', sci6).
c('PHY 131', sci7). c('PHY 133', sci7).
c('PHY 141', sci8). c('PHY 133', sci8).
c('AST 203', scimisc). c('AST 205', scimisc). 
c('CHE 132', scimisc). c('CHE 321', scimisc). c('CHE 322', scimisc). c('CHE 331', scimisc). c('CHE 332', scimisc). 
c('GEO 113', scimisc). c('GEO 122', scimisc). c('GEO 102', scimisc). c('GEO 103', scimisc). c('GEO 112', scimisc). 
c('PHY 125', scimisc). c('PHY 127', scimisc). c('PHY 132', scimisc). c('PHY 134', scimisc). c('PHY 142', scimisc). c('PHY 251', scimisc). c('PHY 252', scimisc). 

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



course_in_cat123(Id) :- intro_courses(Id) ; advanced_courses(Id) ; upperdivCS(Id).
credits_at_sb_cat123(Total) :-
    aggregate_all(sum(Creds),
        (taken(Id, Creds, _, _, 'SBU'),
         passed(Id),
         course_in_cat123(Id)),
        Total).
satisfied_residency_123() :- credits_at_sb_cat123(Total), Total >= 24.

course_in_cat23(Id) :- advanced_courses(Id) ; upperdivCS(Id).
credits_at_sb_cat23(Total) :-
    aggregate_all(sum(Creds),
        (taken(Id, Creds, _, _, 'SBU'),
         passed(Id),
         course_in_cat23(Id)),
        Total).
satisfied_residency_23() :- credits_at_sb_cat23(Total), Total >= 18.

% ethics and communication courses
c('CSE 312', ethics_comm). c('CSE 300', ethics_comm).

all_requirements() :-
    intro_req(),
    advanced_req(),
    elective_req(),
    satisfied_residency_123(),
    satisfied_residency_23(),
    math_req(),
    sci_subset_req(),
    passed_all(ethics_comm).

all_requirements(w(W1,W2,W3,W4,W5,W6,W7,W8)) :-
    intro_req(W1),
    advanced_req(W2),
    elective_req(W3),
    satisfied_residency_123(W4),
    satisfied_residency_23(W5),
    math_req(W6),
    sci_subset_req(W7),
    passed_all_witness(ethics_comm, W8).

intro_req(Witness) :-
    (passed_all_witness(prog, W1) ; passed_all_witness(prog2, W1)),
    (passed_all_witness(dmath, W2) ; passed_all_witness(dmath2, W2)),
    passed_all_witness(sys, W3),
    append([W1, W2, W3], Witness).

advanced_req(Witness) :-
    (passed_all_witness(algs, W1) ; passed_all_witness(algs2, W1)),
    (passed_all_witness(theory, W2) ; passed_all_witness(theory2, W2)),
    passed_all_witness(other, W3),
    append([W1, W2, W3], Witness).

elective_req(Witness) :-
    findall(Id, (passed(Id), elective(Id)), Witness),
    length(Witness, Count),
    Count > 3.

satisfied_residency_123(Witness) :-
    credits_at_sb_cat123(Total), Total >= 24,
    findall(Id, (taken(Id, _, _, _, 'SBU'), passed(Id), course_in_cat123(Id)), Witness).

satisfied_residency_23(Witness) :-
    credits_at_sb_cat23(Total), Total >= 18,
    findall(Id, (taken(Id, _, _, _, 'SBU'), passed(Id), course_in_cat23(Id)), Witness).

math_req(Witness) :-
    (passed_all_witness(calc, W1) ; passed_all_witness(calc2, W1) ; passed_all_witness(calc3, W1)),
    (passed_all_witness(linalg, W2) ; passed_all_witness(linalg2, W2)),
    passed_all_witness(finite, W3),
    (passed_all_witness(prob, W4) ; passed_all_witness(prob2, W4)),
    append([W1, W2, W3, W4], Witness).

sci_subset_req(Witness) :-
    findall(f(Id, Creds, Grade), (taken(Id, Creds, Grade, _, _), sci_courses(Id), grade_toPoints(Grade, _)), SciData),
    subset(SciData, Witness),
    lab_req(Witness),
    sci_req(Witness).



taken('CSE 215', 3, 'A', (2024,2), 'SBU').
taken('CSE 214', 3, 'A', (2024,2), 'SBU').
taken('CSE 114', 3, 'A', (2024,2), 'SBU').
taken('CSE 216', 3, 'A', (2024,2), 'SBU').
taken('CSE 220', 3, 'A', (2024,2), 'SBU').
taken('CSE 4', 3, 'A', (2024,2), 'SBU').
taken('CSE 0', 3, 'A', (2024,2), 'SBU').
taken('CSE 20', 3, 'A', (2024,2), 'SBU').
taken('CSE 2330', 3, 'A', (2024,2), 'SBU').