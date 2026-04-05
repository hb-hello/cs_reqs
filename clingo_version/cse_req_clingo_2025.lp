%%%%% TO RUN: copy the this file and the KB file (kb_complete.lp) into the following:
%%%%%         https://potassco.org/clingo/run/ (it works for clingo v5.7.2)
%%%%%         click the toggle for "lua" and it should be blue and says "python"
%%%%%         paste the code and click "Run"

%%%%% Guide: https://github.com/potassco/guide/releases/tag/v2.2.0
%%%%%   "introduction to the Answer Set Programming (ASP) tools gringo, clasp, and clingo"

%%% ISSUE: better ways to do the same?
%%%   Clingo does not seem to have native support for string manipulation,
%%%   therefore we use external python functions to extract course number and program from course Id.
#script (python)
import clingo

def upper_division(id):
  return clingo.Number(int(id.string[4:]) >= 300)

def course_prog(id):
  return clingo.String(id.string[:3])

#end.

%% Guide: 3.1.10 Pooling
%% the following is equivalent to c_or_higher("A"). c_or_higher("A-"). ...
c_or_higher("A";"A-";"B+";"B";"B-";"C+";"C").

grade_to_points("A", 400).
grade_to_points("A-", 367).
grade_to_points("B+", 333).
grade_to_points("B", 300).
grade_to_points("B-", 267).
grade_to_points("C+", 233).
grade_to_points("C", 200).
grade_to_points("C-", 167).
grade_to_points("D+", 133).
grade_to_points("D", 100).
grade_to_points("F", 0).
grade_to_points("I/F", 0).
grade_to_points("Q", 0).

gpa_mul_100(TakenSubset, Gpa) :-
  courses_taken(Id, _, _, TakenSubset),
  WeightedSum = #sum { Credit*Points : courses_taken(Id_, Credit, Grade, TakenSubset), grade_to_points(Grade, Points) }, %% only consider letter grades
  SumOfWeights = #sum { Credit : courses_taken(Id_, Credit, Grade, TakenSubset), grade_to_points(Grade, _) },
  SumOfWeights > 0,   %%% fails when it's 0, not returning 0 as in python.
  Gpa = WeightedSum / SumOfWeights.

%% taken(Id, Credits, Grade, When, Where), defined later
passed(Id) :- taken(Id, Credits_, Grade, When_, Where_), c_or_higher(Grade).

%% define passed_all using distalgo semantics for "each"
passed_all(Subject) :-
  c(_, Subject),                                % c(Id, Subject): course Id in Subject
  X = #count { C : c(C, Subject), passed(C) },
  Y = #count { C : c(C, Subject) },
  X = Y.

%% it could also be defined as follows:
%% passed_all(Subject) :-
%%   c(_, Subject),
%%   0 = #count { C : c(C, Subject), not passed(C) }.

%% alternatively, we could first define the negation of passed_all
%% 	then define passed_all:
%% -passed_all(Subject) :- c(Id, Subject), not passed(Id).
%% passed_all(Subject) :- c(_, Subject), not -passed_all(Subject).

% 1. Required Introductory Courses
%%% CHANGED for 2025: restructured from prog/prog2/dmath/dmath2/sys
%%%   to focs/focs2/prog/prog2/focs_ii/focs_ii2/sys
%%%   - added CSE 113 (focs) and CSE 150 as its honors substitute (focs2)
%%%   - prog is now {CSE 114, CSE 214} (removed CSE 216)
%%%   - prog2 stays {CSE 160, CSE 161, CSE 260, CSE 261}
%%%     but now substitutes for {CSE 114, CSE 214, CSE 307} (307 is in req 2)
%%%   - added CSE 213 (focs_ii) and CSE 350 as its honors substitute (focs_ii2)
%%%   - removed CSE 215 (dmath) and CSE 150 as dmath2 (CSE 150 is now focs2)
c("CSE 113", focs).
c("CSE 150", focs2).
c("CSE 114", prog). c("CSE 214", prog).
c("CSE 160", prog2). c("CSE 161", prog2). 
c("CSE 260", prog2). c("CSE 261", prog2).
c("CSE 213", focs_ii).
c("CSE 350", focs_ii2).
c("CSE 220", sys). 
intro_courses(Id) :- c(Id, (focs; focs2; prog; prog2; focs_ii; focs_ii2; sys)).

intro_req :- 
  passed_all(focs; focs2),
  passed_all(prog; prog2),
  passed_all(focs_ii; focs_ii2),
  passed_all(sys).

% 2. Required Advanced Courses
%%% CHANGED for 2025: restructured from theory/theory2/algo/algo2/common
%%%   - removed CSE 303 (theory) and CSE 350 (theory2) — CSE 350 moved to req 1 focs_ii2
%%%   - removed CSE 310 from required (was in common)
%%%   - added CSE 307 as required (ppl); prog2 also satisfies it (cross-req substitution)
%%%   - CSE 316 and CSE 320 remain required (now individual sets)
%%%   - added CSE 356 OR CSE 416 choice (was: CSE 416 in common with no alternative)
c("CSE 307", ppl).
c("CSE 316", softdev). 
c("CSE 320", sysfund).
c("CSE 373", algo). c("CSE 385", algo2).
c("CSE 356", cloud). c("CSE 416", se).
adv_courses(Id) :- c(Id, (ppl; softdev; sysfund; algo; algo2; cloud; se)).

adv_req :- 
  passed_all(ppl; prog2),     %% CSE 307, or honors prog2 substitutes for it
  passed_all(softdev),
  passed_all(sysfund),
  passed_all(algo; algo2),
  passed_all(cloud; se).

% 3. Computer Science Electives
%%% CHANGED for 2025:
%%%   - threshold raised from 4 to 6
%%%   - removed CSE 300 and CSE 312 from elect_exclude (but still excluded as non-technical)
%%%   - added elect_cap_one set: at most 1 of these counts toward the 6 electives
%%%     (CSE 487, CSE 496, VIP 395, VIP 396, VIP 495, VIP 496)
c(("CSE 475"; "CSE 495"; "CSE 300"; "CSE 301"; "CSE 312"), elect_exclude).
c(("CSE 487"; "CSE 496"; "VIP 395"; "VIP 396"; "VIP 495"; "VIP 496"), elect_cap_one).

%% define courses_taken(Id, Credits, Grade, Subset) to represent a subset of taken courses 
%%   as in Annie's python, where Subset is a term used to identify the subset.
%% regular electives (not capped)
courses_taken(Id, Credits, Grade, elect_passed) :- 
  taken(Id, Credits, Grade, _, _), 
  Prog = @course_prog(Id), 
  Prog = "CSE", 
  @upper_division(Id) = 1,    %% is upper division
  Credits >= 3, not adv_courses(Id), not c(Id, elect_exclude), not c(Id, elect_cap_one).

%% capped electives (at most 1 counts toward the 6)
courses_taken(Id, Credits, Grade, elect_cap_passed) :-
  taken(Id, Credits, Grade, _, _),
  c(Id, elect_cap_one), Credits >= 3.

%% helper: 1 if any capped elective was passed, 0 otherwise
has_elect_cap :- courses_taken(_, _, _, elect_cap_passed).
elect_cap_count(1) :- has_elect_cap.
elect_cap_count(0) :- not has_elect_cap.

elect_req :- 
  N1 = #count { Id: courses_taken(Id, _, _, elect_passed) },
  elect_cap_count(N2),
  N1 + N2 >= 6.

% 4. AMS 151, AMS 161 Applied Calculus I, II
%%% (copied from python) todo:
% Equivalency for MAT courses achieved through the Mathematics
% Placement Examination is accepted to meet MAT course requirements.
%%% NO CHANGE for 2025
c("AMS 151", calc). c("AMS 161", calc).
c("MAT 125", calc2). c("MAT 126", calc2). c("MAT 127", calc2).
c("MAT 131", calc3). c("MAT 132", calc3).

calc_req :- 
  passed_all(calc;calc2;calc3).

% 5. One of the following:
%%% NO CHANGE for 2025
c("MAT 211", alg).
c("AMS 210", alg2).

alg_req :- 
  passed_all(alg;alg2).

% 6. Required Upper-Division Statistics Course
%%% CHANGED for 2025: simplified
%%%   - removed AMS 301 (fmath) — no longer required
%%%   - removed AMS 311 (sta2) — no longer an alternative
%%%   - just AMS 310 required
c("AMS 310", sta).

sta_req :-
  passed_all(sta).

% 7. At least one of the following natural science lecture/laboratory combinations...
% All courses taken to satisfy Requirements 1 through 9 must be taken for a letter grade.
%%% NO CHANGE for 2025 (same combos)
c("BIO 201", bio). c("BIO 204", bio).
c("BIO 202", bio2). c("BIO 204", bio2).
c("BIO 203", bio3). c("BIO 204", bio3).
c("CHE 131", che). c("CHE 133", che).
c("CHE 152", che2). c("CHE 154", che2).
c("PHY 126", phy). c("PHY 133", phy).
c("PHY 131", phy2). c("PHY 133", phy2).
c("PHY 141", phy3). c("PHY 133", phy3).

sci_combs(L) :- L = (bio;bio2;bio3;che;che2;phy;phy2;phy3).

% 8. One additional natural science course selected from above and the following list...
% All courses taken to satisfy Requirements 1 through 9 must be taken for a letter grade.
%%% CHANGED for 2025:
%%%   - removed: GEO 102, GEO 103, GEO 112, GEO 123, GEO 122 (5 GEO courses)
%%%   - removed: PHY 134, PHY 252
%%%   - added: BIO 201, BIO 202, BIO 203
%%%   - added: CHE 131, CHE 152
%%%   - added: PHY 126, PHY 131
c(("AST 203"; "AST 205"; "BIO 201"; "BIO 202"; "BIO 203"; "CHE 131"; "CHE 132"; "CHE 152"; "CHE 321"; "CHE 322"; "CHE 331"; "CHE 332"; "PHY 125"; "PHY 126"; "PHY 127"; "PHY 131"; "PHY 132"; "PHY 142"; "PHY 251"), sci_more).

%% set of all sci courses taken
courses_taken(Id, Credit, Grade, sci_courses) :- taken(Id, Credit, Grade, _, _), c(Id, sci_more).
courses_taken(Id, Credit, Grade, sci_courses) :- taken(Id, Credit, Grade, _, _), c(Id, L), sci_combs(L).

%% a subset of sci courses taken: to satisfy sci_req, sci_cred_req and sci_grade_req.
{ courses_taken(Id, Credit, Grade, sci_subset) : courses_taken(Id, Credit, Grade, sci_courses) }.

%% use the same subset to check both credit and grade requirements:
%% the subset must contain one sci_combo, use in requirement 7. %%% assume each combo has only two courses.
sci_req :- sci_combs(L),
           c(Id1, L),
           c(Id2, L),
           Id1 != Id2,
           courses_taken(Id1, _, _, sci_subset), courses_taken(Id2, _, _, sci_subset).

% The courses selected in 7 and 8 must carry at least 9 credits.
%% Id is needed otherwise credit will only be counted once for courses that have the same credits.
sci_cred_req :-  #sum { Credit, Id : courses_taken(Id, Credit, _, sci_subset) } >= 9.

% The grade point average for the courses in Requirements 7 and 8 must be at least 2.00.
sci_grade_req :- gpa_mul_100(sci_subset, Gpa), Gpa >= 200.  %% scaled by 100.

% 9. Required Non-Technical Courses
%%% CHANGED for 2025: merged old req 9 (ethics) and req 10 (writing) into one
%%%   - was: ethics_req (CSE 312) and writing_req (CSE 300) as separate requirements
%%%   - now: nontechnical_req requiring both CSE 300 and CSE 312
c("CSE 300", nontechnical). c("CSE 312", nontechnical).

nontechnical_req :- passed_all(nontechnical).

%%% (copied from python) todo:
% Note: All students are encouraged to discuss their program with an
% undergraduate advisor.
% In Requirement 2 above, CSE/ESE double majors may substitute ESE
% 440, ESE 441 Electrical Engineering Design I, II for CSE 356 - Cloud
% Computing or CSE 416 - Software Engineering provided that the design
% project contains a significant software component. Approval of the
% Department of Computer Science is required.
%%% Note for 2025: CSE 356 or CSE 416 must be completed at Stony Brook University.
%% this is at the top of the section on the webpage:
% The major in Computer Science leads to the Bachelor of Science degree.
% Completion of the major requires approximately 80 credits.  %%% todo: count
% At least 24 credits from items 1 to 3 below, and at least 18 credits from
% items 2 and 3, must be completed at Stony Brook.
%%% assume to be not about "The courses taken to satisfy Requirements ..."

item123_course(Id) :- intro_courses(Id).
item123_course(Id) :- adv_courses(Id).
item123_course(Id) :- courses_taken(Id, _, _, elect_passed).

item23_course(Id) :- adv_courses(Id).
item23_course(Id) :- courses_taken(Id, _, _, elect_passed).

credits_at_sb_req :- %% similar to sci_cred_req
  #sum { Credit, Id : taken(Id, Credit, _, _, "SB"), item123_course(Id) } >= 24,
  #sum { Credit, Id : taken(Id, Credit, _, _, "SB"), item23_course(Id) } >= 18.

%%%%% planning

%%%% constants
#const min_semester = 1.            %% min semester number, assume 1
#const max_semester = 8.            %% max number of semesters, assume 8
#const max_courses_per_semester = 4.

%% define semester to be from 1 to 8
semester(min_semester..max_semester).

%%%% KB rules

%% for prereq and antireq
taken_before(Id, Sem) :- semester(Sem), taken(Id, _, _, Sem1, _), Sem1 < Sem.
%% for prereq
passed_before(Id, Sem) :- semester(Sem), taken(Id, _, Grade, Sem1, _), Sem1 < Sem, c_or_higher(Grade).
%% for coreq
taken_same(Id, Sem) :- semester(Sem), taken(Id, _, _, Sem, _).

%%%% generate
%% if a course is not taken, we consider it for planning.
%%   requisites (prereq, coreq, antireq) will be checked in constraints.
%%   can't use taken/5 because planning needs to add new taken facts.
can_take(Id) :- course(Id, _), not taken_id(Id).

%% choose up to max_course_planned courses to plan for
%% assume each planned course will be taken with credit, grade ...
%% for each course, only take it in one semester.
{ taken(Id, 4, "A", Sem, "SB") : Sem = min_semester..max_semester } 1 :- can_take(Id). %% #const can't be used in the head

%% planned if not in the input (taken_id) and chosen in the generate rule above.
planned(Id, Sem) :- taken(Id, _, _, Sem, _), not taken_id(Id).

%%%% constraints

%% all requirements must be satisfied.
:- req_name(X), not req_passed(X).

%% prereq
:-  planned(Id, Sem),
    has_prereq(Id),
    not prereq(Id, Sem).

% coreq
:-  planned(Id, Sem),
    has_coreq(Id),
    not coreq(Id, Sem).

%% antireq                     %% TODO: for antireq we can not simply assume unsupported is true or false
% :-  plan_to_take(Id, Sem),   %%        need to work on the KB on each one (there is only 3 courses with anti-req)
%     has_anti_req(Id), 
%     anti_req(Id, Sem).      %% anti-req can not be satisfied

%% do not exceed max courses per semester
:- semester(Sem), #count { Id : planned(Id, Sem) } > max_courses_per_semester.

%%%% optimization
%% minimize the number of courses to take to satisfy all requirements.
% #minimize { 1, Id : taken(Id, _, _, _, _) }.

%% minimize the number of semesters
max_sem(X) :- semester(X), X = #max { Sem : planned(_, Sem) }.
#minimize { X: max_sem(X) }.

#show planned/2.       %% courses planned

%%%%% test
%% to play around:
%%   you can comment out more of the taken_id facts.
%%   change the generate rule (in the planning part below) to set upper_bound to max number of courses to plan for, e.g. 5.
%%   upper_bound can also be removed, which means there is no limit.
%%   { plan_to_take(Id) : can_take(Id) } upper_bound
%%% CHANGED for 2025: updated test courses
%%%   - removed: CSE 216 (no longer in req 1)
%%%   - removed: CSE 303 (no longer in req 2)
%%%   - removed: AMS 301 (no longer required)
%%%   - added: CSE 113 (new in req 1)
%%%   - added: CSE 213 (new in req 1)
%%%   - added: CSE 307 (new in req 2)
%% first line commented out to test planning
taken_id("CSE 113"). taken_id("CSE 114"). taken_id("CSE 213"). taken_id("CSE 214").
% taken_id("CSE 220").
% taken_id("CSE 307"). taken_id("CSE 316").
% taken_id("CSE 320"). taken_id("CSE 373"). taken_id("CSE 416").
% taken_id("MAT 131"). taken_id("MAT 132"). taken_id("AMS 210").
% taken_id("AMS 310").
% taken_id("CSE 300"). taken_id("CSE 312").
% taken_id("CSE 360"). taken_id("CSE 361"). taken_id("CSE 351").
% taken_id("CSE 352"). taken_id("CSE 353"). taken_id("CSE 355").
% taken_id("PHY 131"). taken_id("PHY 133"). taken_id("AST 203").

%% generate input, assume all courses are taken in semester 0 (before planning semesters)
taken(Id, Credit, "A", 0, "SB") :- course(Id, Credit), taken_id(Id).

%% student facts
standing("U1"). standing("U2"). standing("U3"). standing("U4").
major("CSE").

%% requirements:
%% req_name: used in the constraint to check if all requirements are satisfied.
%% req_passed: used in the constraint, also in the output.
%%% CHANGED for 2025: removed ethics_req and writing_req, added nontechnical_req
req_name(intro_req; adv_req; elect_req; calc_req; alg_req; sta_req; sci_req; sci_cred_req; sci_grade_req; nontechnical_req; credits_at_sb_req).

%% req 1-6
req_passed(intro_req)         :- intro_req.
req_passed(adv_req)           :- adv_req.
req_passed(elect_req)         :- elect_req.
req_passed(calc_req)          :- calc_req.
req_passed(alg_req)           :- alg_req.
req_passed(sta_req)           :- sta_req.

%% req 7, 8
req_passed(sci_req)           :- sci_req.
req_passed(sci_cred_req)      :- sci_cred_req.
req_passed(sci_grade_req)     :- sci_grade_req.

%% req 9 (merged from old req 9 + 10)
req_passed(nontechnical_req)  :- nontechnical_req.

req_passed(credits_at_sb_req) :- credits_at_sb_req.
