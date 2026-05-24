%% comments in this file:
%%    %: english text from the degree requirements, comments in python, or commented out code
%%   %%: my own comments explaining the logic
%%  %%%: issues, some are copied from python

%% clingo version for checking and planning for BS degree requirements in CSE at Stony Brook University (Fall 2024).
%% python version: https://github.com/unicomputing/cs_reqs/blob/main/cs_reqs_2024.da (checking only)

is_or_higher(Grade, Grade2) :- 
  grade_points(Grade, Points), grade_points(Grade2, Points2), Points >= Points2.
is_c_or_higher(Grade) :- is_or_higher(Grade, "C").

%% mapping letter grade to points for GPA calculation
%% scaled by 100 to make each integer
grade_points("A", 400). grade_points("A-", 367).
grade_points("B+", 333). grade_points("B", 300). grade_points("B-", 267).
grade_points("C+", 233). grade_points("C", 200). grade_points("C-", 167).
grade_points("D+", 133). grade_points("D", 100). grade_points("F", 0).
grade_points("I/F", 0). grade_points("Q", 0).
%% for planned courses, treat as C - minimum needed to satisfy most requirements.
grade_points("None", 200). 

%% gpa calculation, takes a subset (marked by the tag) and calculates the GPA = floor(weighted sum / sum of weights).
%%   only consider letter grades in grade_points.
%%   if a course is taken multiple times, only one would be counted. we assume no repeated courses
%%   to allow repeats, simply add 'When' in the aggregate, but grounding takes longer.
gpa(GPA) :-
  subset_sci_taken(_),
  WeightedSum = #sum { Cr * Pts, Cid: subset_sci_taken(Cid), taken(Cid, Cr, G, _, _), grade_points(G, Pts) },
  SumOfWeights = #sum { Cr, Cid : subset_sci_taken(Cid), taken(Cid, Cr, G, _, _), grade_points(G, _) },
  SumOfWeights > 0, GPA = WeightedSum / SumOfWeights. %%% integer floor division. 

%% gpa is 0 when sum of weights is 0, as in python.
gpa(0) :- #sum { Cr, Cid: subset_sci_taken(Cid), taken(Cid, Cr, G, _, _), grade_points(G, _) } = 0.

% taken(Cid, Credits, Grade, When, Where): taken course Cid with Credits, etc.

c_or_higher(Cid) :- taken(Cid, _, Grade, _, _), is_c_or_higher(Grade).
passed(Cid) :- c_or_higher(Cid).
passed_with_grade(Cid, Grade) :- taken(Cid, _, Grade1, _, _), is_or_higher(Grade1, Grade).

% c(Subject, Cid): course Cid in Subject

% passed all courses in Subject
passed_all(Subject) :-
  c(Subject, _),                 %% ground Subject
  passed(Cid) : c(Subject, Cid).   %% passed for each course in subject

%% course C is witness for passing all courses in a subject in requirement Item
wit(Item, Cid) :- s(Item, Subj), passed_all(Subj), c(Subj, Cid).

% set of courses in subjects of requirement item
courses(Cid, Item) :- s(Item, Subj), c(Subj, Cid).

% 1. Required Introductory Courses
c(prog, ("CSE 114"; "CSE 214"; "CSE 216")).
c(prog2, ("CSE 160"; "CSE 161"; "CSE 260"; "CSE 261")).
c(dmath, "CSE 215"). 
c(dmath2, "CSE 150").
c(sys, "CSE 220"). 
s(intro, (prog; prog2; dmath; dmath2; sys)).

req(intro) :-
  passed_all(prog; prog2),
  passed_all(dmath; dmath2),
  passed_all(sys).

% 2. Required Advanced Courses
c(theory, "CSE 303"). c(theory2, "CSE 350").
c(algo, "CSE 373"). c(algo2, "CSE 385").
c(other, ("CSE 310"; "CSE 316"; "CSE 320"; "CSE 416")).
s(adv, (theory; theory2; algo; algo2; other)).

req(adv) :- 
  passed_all(theory; theory2),
  passed_all(algo; algo2),
  passed_all(other).

% 3. Computer Science Electives  %% simpler than 2025
c(elect_exclude, ("CSE 475"; "CSE 495"; "CSE 300"; "CSE 301"; "CSE 312")).

elect_passed(Cid) :-
  taken(Cid, Crs, G, _, _), is_c_or_higher(G),
  @course_prog(Cid) = "CSE",
  @upper_division(Cid) = 1,    %% is upper division
  Crs >= 3, not courses(Cid, adv), not c(elect_exclude, Cid).

req(elect) :- 
  #count { Cid: elect_passed(Cid) } >= 4.

%% witness for elect is the subset elect_passed used in elect.
wit(elect, Cid) :- elect_passed(Cid).

% 4. AMS 151, AMS 161 Applied Calculus I, II
%%% (copied from python) todo:
% Equivalency for MAT courses achieved through the Mathematics
% Placement Examination is accepted to meet MAT course requirements.
c(calc, ("AMS 151"; "AMS 161")).
c(calc2, ("MAT 125"; "MAT 126"; "MAT 127")).
c(calc3, ("MAT 131"; "MAT 132")).
s(calc, (calc; calc2; calc3)).

req(calc) :- 
  passed_all(calc; calc2; calc3).

% 5. One of the following:
c(alg, "MAT 211").
c(alg2, "AMS 210").
s(alg, (alg; alg2)).

req(alg) :- 
  passed_all(alg; alg2).

% 6. Both of the following:
c(fmath, "AMS 301").
c(sta, "AMS 310").
c(sta2, "AMS 311").
s(sta, (fmath; sta; sta2)).

req(sta) :-
  passed_all(fmath),
  passed_all(sta; sta2).

% 7. At least one of the following natural science lecture/laboratory combinations...
% combinations:
c(bio, ("BIO 201"; "BIO 204")).
c(bio2, ("BIO 202"; "BIO 204")).
c(bio3, ("BIO 203"; "BIO 204")).
c(che, ("CHE 131"; "CHE 133")).
c(che2, ("CHE 152"; "CHE 154")).
c(phy, ("PHY 126"; "PHY 133")).
c(phy2, ("PHY 131"; "PHY 133")).
c(phy3, ("PHY 141"; "PHY 133")).
sci_combs(bio; bio2; bio3; che; che2; phy; phy2; phy3).

% 8. Additional natural science courses selected from above and following list:
% Note: The courses selected in 7 and 8 must carry at least 9 credits.
c(sci_more, ("AST 203"; "AST 205"; "CHE 132"; "CHE 321"; "CHE 322"; "CHE 331"; "CHE 332";
             "GEO 102"; "GEO 103"; "GEO 112"; "GEO 123"; "GEO 122";
             "PHY 125"; "PHY 127"; "PHY 132"; "PHY 134"; "PHY 142"; "PHY 251"; "PHY 252")).

%% sci_courses(taken) in python: set of all sci courses taken
sci_taken(Cid) :- sci_combs(Subj), c(Subj, Cid), taken(Cid, _, _, _, _).
sci_taken(Cid) :- c(sci_more, Cid), taken(Cid, _, _, _, _).

%% generate a subset of sci_courses taken: use the same subset to satisfy sci_req, sci_cred_req and sci_grade_req.
{ subset_sci_taken(Cid) } :- sci_taken(Cid).

%%% separeted out because clingo treats all conditions after a colon (:) as part of the condition
sci_combs_req :- sci_combs(Subj), subset_sci_taken(Cid) : c(Subj, Cid).

req(sci) :- 
  sci_combs_req,
  % The courses selected in 7 and 8 must carry at least 9 credits.
  #sum { Cr, Cid : subset_sci_taken(Cid), taken(Cid, Cr, _, When_, _) } >= 9,
  % The grade point average for the courses in Requirements 7 and 8 must be at least 2.00.
  gpa(GPA), GPA >= 2*100.

%% witness for sci is the subset used to satisfy all sci requirements, as in python.
wit(sci, Cid) :- subset_sci_taken(Cid).

% 9. Professional Ethics
c(ethics, "CSE 312").
s(ethics, ethics).

req(ethics) :- passed_all(ethics).

% 10. Upper-Division Writing Requirement
c(writing, "CSE 300").
s(writing, writing).

req(writing) :- passed_all(writing).

%%% (copied from python) todo:
% Note: All students are encouraged to discuss their program with an
% undergraduate advisor.
% In Requirement 2 above, CSE/ESE double majors may substitute ESE
% 440, ESE 441 Electrical Engineering Design I, II for CSE 416 Software
% Engineering provided that the design project contains a significant
% software component. Approval of the Department of Computer Science is
% required.
%% this is at the top of the section on the webpage:
% The major in Computer Science leads to the Bachelor of Science degree.
% Completion of the major requires approximately 80 credits.  %%% todo: count
% At least 24 credits from items 1 to 3 below, and at least 18 credits from
% items 2 and 3, must be completed at Stony Brook.
%%% assume to be not about "The courses taken to satisfy Requirements ..."

%% courses in items 1,2,3
items123_course(Cid) :- courses(Cid, intro).
items123_course(Cid) :- courses(Cid, adv).
items123_course(Cid) :- elect_passed(Cid).

%% courses in items 2,3
items23_course(Cid) :- courses(Cid, adv).
items23_course(Cid) :- elect_passed(Cid).

req(credits_at_SB) :-
  #sum { Cr, Cid : taken(Cid, Cr, _, _, "SB"), items123_course(Cid) } >= 24,
  #sum { Cr, Cid : taken(Cid, Cr, _, _, "SB"), items23_course(Cid) } >= 18.

wit(credits_at_SB, Cid) :- items123_course(Cid), taken(Cid, _, _, _, "SB").
wit(credits_at_SB, Cid) :- items23_course(Cid), taken(Cid, _, _, _, "SB").

% Grading (%%% comments are copied from python)
%
% All courses taken to satisfy Requirements 1 through 10 must be taken for
% a letter grade.  %%% always true if the two below are true
% The courses in Requirements 1-6, 9, and 10 must be passed with a letter
% grade of C or higher.  %%% assume to be: The courses *taken to satisfy* Req...
% The grade point average for the courses in Requirements 7 and 8 must be
% at least 2.00.  %%% assume to be: The courses *taken to satisfy* Req...
%% merged with 7 and 8; otherwise, not correct if as assumed.

%% requirements items
item(intro; adv; elect; calc; alg; sta; sci; ethics; writing; credits_at_SB).

%% degree requirement sat if all requirements are satisfied
degree :- req(Item) : item(Item).

#program check.

#maximize { 1, Item : req(Item) }.    %% soft constraint: maximize the number of requirements satisfied. 
                                      %%   so we have a model even when not all requirements are satisfied.

%% Default planning constants (can be overridden by python).
%%  for semesters we only use small integers, instead of a (year, semester) tuple.
%%  python maintains the mapping between integers and (year, term) tuples.
#const start_sem = 1.         %% earliest semester to plan for
#const end_sem = 4*4.      %% latest semester ...
#const sem_max_credits = 18.  %% max credits allowed per semester planned

#program plan.    %% with requisites in the test

%% Temporal relations used by the KB to evaluate requisites (e.g., passed_before, taken_together). 

%% helper predicate for comparing semesters.
%%   O(N^2) grounding for semester pairs, but since the domain is small,
%%   this is efficient.
before(Sem1, Sem2) :- Sem1 = 1..end_sem, Sem2 = 1..end_sem, Sem1 < Sem2.

% %% course is taken before semester Sem.                           %% for prereq and antireq
% taken_before(Cid, Sem) :- taken(Cid, _, _, Sem1, _), before(Sem1, Sem).

%% course taken before semester with at least grade.
passed_before_grade(Cid, Grade, Sem) :-
  taken(Cid, _, _, Sem1, _), before(Sem1, Sem), passed_with_grade(Cid, Grade).

%% "C or higher" in prereq
passed_before(Cid, Sem):- taken(Cid, _, _, Sem1, _), before(Sem1, Sem), passed(Cid).

%% course Cid is taken at semester Sem.                            %% coreq
taken_together(Cid, Sem) :- taken(Cid, _, _, Sem, _).

%% could be taken before or at the same semester.                 %% pre_or_coreq
passed_before_or_together_grade(Cid, Grade, Sem) :- 
  grade_points(Grade, _), passed_before_grade(Cid, Grade, Sem).
passed_before_or_together_grade(Cid, Grade, Sem) :- 
  grade_points(Grade, _), taken_together(Cid, Sem).

%%%% generate 

%% offered(Cid, Sem): course Cid is offered at semester Sem. input taken from python.

%% define history from taken?
% grade("A"; "A-"; "B+"; "B"; "B-"; "C+"; "C"; "C-"; "D+"; "D"; "F"; "I/F"; "Q").
% history(Cid) :- taken(Cid, _, G, _, _), grade(G).

%% if used before(Sem), Sem would need to be grounded. this is more straightforward.
offered_in_range(Cid) :- offered(Cid, Sem), start_sem <= Sem, Sem <= end_sem.
{plan(Cid, Sem) : offered(Cid, Sem)} == 1 :- offered_in_range(Cid), include(Cid).
{plan(Cid, Sem) : offered(Cid, Sem)} <= 1 :- offered_in_range(Cid), 
                                           not taken_id(Cid),
                                           not exclude(Cid).

{plan_credits(Cid, Cr) : credits(Cid, Cr)} == 1 :- plan(Cid, _).

%% planned course has grade "None", which is treated as C in GPA calculation.
%% we could also make grade a variable and optimize for minimum grade needed.
taken(Cid, Cr, "None", Sem, "SB") :- plan(Cid, Sem), plan_credits(Cid, Cr).

%%%% constraints
%% all requirements must be satisfied
:- item(I), not req(I).
%% all requisites must be satisfied
:- plan(Cid, Sem), not allreq(Cid, Sem).
%% do not exceed max credits per semester
:- plan(_, Sem),
   #sum {Cr, Cid: plan(Cid, Sem), plan_credits(Cid, Cr)} > sem_max_credits.

%%%% optimization

%% minimize the number of semesters
max_sem_plan(Sem) :- plan(_, Sem), Sem = #max {Sem1 : plan(_, Sem1)}. %% get the max semester in the plan
#minimize {Sem@2: max_sem_plan(Sem)}.

%% next, minimize the number of courses to take to satisfy all requirements.
#minimize {1@1, Cid: plan(Cid, _)}.
% could write in one statement (better?) as:
% #minimize { 
%     Sem@2, Cid : plan(Cid, Sem) ; 
%     1@1, Cid : plan(Cid, _) 
% }.

% plan as early as possible, but causes a lot of conflicts (possibly because of prereqs)
% #heuristic plan(Cid, Sem). [20 - Sem@2, true]

% plan fixed electives to reduce search. do the same for sci?
% fast_track_elect("CSE 334"; "CSE 331"; "CSE 328"; "CSE 360").
% #heuristic plan(Cid, Sem) : not req(elect),
%                            fast_track_elect(Cid), 
%                            not taken_id(Cid),
%                            offered(Cid, Sem). [100-Sem@1, true]

% input to planning:
% standing("U1"). standing("U2"). standing("U3"). standing("U4").
% major("CSE"). permission.
%% from python:
  %% must exclude and must include: 
  %% exclude("CHE 322").
  %% include("CHE 322").

  %% taken_id(Cid).
  %% taken(Cid, ...)