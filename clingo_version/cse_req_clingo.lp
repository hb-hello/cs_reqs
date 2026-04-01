%% comments in this file:
%%    %: english text from the degree requirements, comments in python, or commented out code
%%   %%: my own comments explaining the logic
%%  %%%: issues, some are copied from python

%% clingo version for checking and planning for BS degree requirements in CSE at Stony Brook University (Fall 2024).
%% python version: https://github.com/unicomputing/cs_reqs/blob/main/cs_reqs_2024.da (checking only)

is_higher(Grade, Grade2) :- grade_points(Grade, Points), grade_points(Grade2, Points2), Points >= Points2.
c_or_higher(Grade) :- is_higher(Grade, "C").

%% mapping letter grade to points for GPA calculation
%% scaled by 100 to make each integer
grade_points("A", 400). grade_points("A-", 367).
grade_points("B+", 333). grade_points("B", 300). grade_points("B-", 267).
grade_points("C+", 233). grade_points("C", 200). grade_points("C-", 167).
grade_points("D+", 133). grade_points("D", 100). grade_points("F", 0).
grade_points("I/F", 0). grade_points("Q", 0).

%% gpa calculation, takes a subset (marked by the tag) and calculates the GPA = floor(weighted sum / sum of weights).
%%   only consider letter grades in grade_points.
%%   if a course is taken multiple times, all of them will be counted, as in python.
gpa_x100(Tag, GPA) :-
  subset_taken(_, Tag),
  WeightedSum = #sum { Credit*Points, Id, When : subset_taken(Id, Tag), taken(Id, Credit, Grade, When, _), grade_points(Grade, Points) },
  SumOfWeights = #sum { Credit, Id, When : subset_taken(Id, Tag), taken(Id, Credit, Grade, When, _), grade_points(Grade, _) },
  SumOfWeights > 0,
  GPA = WeightedSum / SumOfWeights. %%% integer floor division. 

%% gpa is 0 when sum of weights is 0, as in python.
gpa_x100(Tag, 0) :-
  subset_taken(_, Tag),
  #sum { Credit, Id, When : subset_taken(Id, Tag), taken(Id, Credit, Grade, When, _), grade_points(Grade, _) } = 0.

% taken(Id, Credits, Grade, When, Where): taken course Id with Credits, etc.

passed(Id) :- taken(Id, Credits_, Grade, When_, Where_), c_or_higher(Grade).

% passed all courses with course Id in Subject
passed_all(Subject) :-
  c(_, Subject),                 % c(Id, Subject): course Id in Subject
  passed(Id) : c(Id, Subject).   %% for each course Id in Subject, passed(Id) is true

% course C is witness for passing all courses in a subject in requirement Item
wit(Item, Id) :- s(Item, Subj), passed_all(Subj), c(Id, Subj).

% return set of courses in subjects in requirement item.
courses(Id, Item) :- s(Item, Subj), c(Id, Subj).
subset_taken(Id, Item) :- s(Item, Subj), c(Id, Subj), taken(Id, _, _, _, _).

% 1. Required Introductory Courses
c(("CSE 114"; "CSE 214"; "CSE 216"), prog).
c(("CSE 160"; "CSE 161"; "CSE 260"; "CSE 261"), prog2).
c("CSE 215", dmath). 
c("CSE 150", dmath2).
c("CSE 220", sys). 
s(intro, (prog; prog2; dmath; dmath2; sys)).

sat(intro) :-
  passed_all(prog; prog2),
  passed_all(dmath; dmath2),
  passed_all(sys).

% 2. Required Advanced Courses
c("CSE 303", theory). c("CSE 350", theory2).
c("CSE 373", algo). c("CSE 385", algo2).
c(("CSE 310"; "CSE 316"; "CSE 320"; "CSE 416"), other).
s(adv, (theory; theory2; algo; algo2; other)).

sat(adv) :- 
  passed_all(theory; theory2),
  passed_all(algo; algo2),
  passed_all(other).

% 3. Computer Science Electives  %% simpler than 2025
c(("CSE 475"; "CSE 495"; "CSE 300"; "CSE 301"; "CSE 312"), elect_exclude).

subset_taken(Id, elect_passed) :-
  taken(Id, Credits, Grade, _, _), c_or_higher(Grade),
  @course_prog(Id) = "CSE",
  @upper_division(Id) = 1,    %% is upper division
  Credits >= 3, not courses(Id, adv), not c(Id, elect_exclude).

sat(elect) :- 
  #count { Id: subset_taken(Id, elect_passed) } >= 4.

%% for elect, witness is the subset elect_passed used in elect.
wit(elect, Id) :- subset_taken(Id, elect_passed).

% 4. AMS 151, AMS 161 Applied Calculus I, II
%%% (copied from python) todo:
% Equivalency for MAT courses achieved through the Mathematics
% Placement Examination is accepted to meet MAT course requirements.
c(("AMS 151"; "AMS 161"), calc).
c(("MAT 125"; "MAT 126"; "MAT 127"), calc2).
c(("MAT 131"; "MAT 132"), calc3).
s(calc, (calc; calc2; calc3)).

sat(calc) :- 
  passed_all(calc; calc2; calc3).

% 5. One of the following:
c("MAT 211", alg).
c("AMS 210", alg2).
s(alg, (alg; alg2)).

sat(alg) :- 
  passed_all(alg; alg2).

% 6. Both of the following:
c("AMS 301", fmath).
c("AMS 310", sta).
c("AMS 311", sta2).
s(sta, (fmath; sta; sta2)).

sat(sta) :-
  passed_all(fmath),
  passed_all(sta; sta2).

% 7. At least one of the following natural science lecture/laboratory combinations...
% combinations:
c(("BIO 201"; "BIO 204"), bio).
c(("BIO 202"; "BIO 204"), bio2).
c(("BIO 203"; "BIO 204"), bio3).
c(("CHE 131"; "CHE 133"), che).
c(("CHE 152"; "CHE 154"), che2).
c(("PHY 126"; "PHY 133"), phy).
c(("PHY 131"; "PHY 133"), phy2).
c(("PHY 141"; "PHY 133"), phy3).
sci_combs(bio; bio2; bio3; che; che2; phy; phy2; phy3).

% 8. Additional natural science courses selected from above and following list:
% Note: The courses selected in 7 and 8 must carry at least 9 credits.
c(("AST 203"; "AST 205"; "CHE 132"; "CHE 321"; "CHE 322"; "CHE 331"; "CHE 332";
   "GEO 102"; "GEO 103"; "GEO 112"; "GEO 123"; "GEO 122";
   "PHY 125"; "PHY 127"; "PHY 132"; "PHY 134"; "PHY 142"; "PHY 251"; "PHY 252"), sci_more).

%% sci_courses(taken) in python: set of all sci courses taken
sci_taken(Id) :- sci_combs(Subj), c(Id, Subj), taken(Id, _, _, _, _).
sci_taken(Id) :- c(Id, sci_more), taken(Id, _, _, _, _).

%% generate a subset of sci_courses taken: use the same subset to satisfy sci_req, sci_cred_req and sci_grade_req.
{ subset_taken(Id, sci) } :- sci_taken(Id).

%% the subset must contain one sci_combo, use in requirement 7.
sci_combs_req :- sci_combs(Subj), subset_taken(Id, sci) : c(Id, Subj).

% The courses selected in 7 and 8 must carry at least 9 credits.
%% Id is needed otherwise credit will only be counted once for courses that have the same credits.
sci_cred_req :- #sum { Credit, Id, When : subset_taken(Id, sci), taken(Id, Credit, _, When, _) } >= 9.

% The grade point average for the courses in Requirements 7 and 8 must be at least 2.00.
sci_grade_req :- gpa_x100(sci, GPA), GPA >= 2*100.

sat(sci) :- sci_combs_req, sci_cred_req, sci_grade_req.

%% witness for sci is the subset used to satisfy all sci requirements, as in python.
wit(sci, Id) :- subset_taken(Id, sci).

% 9. Professional Ethics
c("CSE 312", ethics).
s(ethics, ethics).

sat(ethics) :- passed_all(ethics).

% 10. Upper-Division Writing Requirement
c("CSE 300", writing).
s(writing, writing).

sat(writing) :- passed_all(writing).

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
items123_course(Id) :- courses(Id, intro).
items123_course(Id) :- courses(Id, adv).
items123_course(Id) :- subset_taken(Id, elect_passed).

%% courses in items 2,3
items23_course(Id) :- courses(Id, adv).
items23_course(Id) :- subset_taken(Id, elect_passed).

items123_credits(Credits) :- Credits = #sum { Credit, Id : taken(Id, Credit, _, _, "SB"), items123_course(Id) }.
items23_credits(Credits) :- Credits = #sum { Credit, Id : taken(Id, Credit, _, _, "SB"), items23_course(Id) }.

sat(credits_at_SB) :-
  items123_credits(Credits1), Credits1 >= 24,
  items23_credits(Credits2), Credits2 >= 18.

wit(credits_at_SB, items123(Total)) :- items123_credits(Total).
wit(credits_at_SB, items23(Total)) :- items23_credits(Total).

% Grading (%%% comments are copied from python)
%
% All courses taken to satisfy Requirements 1 through 10 must be taken for
% a letter grade.  %%% always true if the two below are true
% The courses in Requirements 1-6, 9, and 10 must be passed with a letter
% grade of C or higher.  %%% assume to be: The courses *taken to satisfy* Req...
% The grade point average for the courses in Requirements 7 and 8 must be
% at least 2.00.  %%% assume to be: The courses *taken to satisfy* Req...
%% merged with 7 and 8; otherwise, not correct if as assumed.

#program check.

%% requirements items
item(intro; adv; elect; calc; alg; sta; sci; ethics; writing; credits_at_SB).

degree :- sat(Item) : item(Item).     %% degree requirement sat if all requirements are satisfied

#maximize { 1@3, Item : sat(Item) }.  %% soft constraint: maximize the number of requirements satisfied. 
                                      %%   so we have a model even when not all requirements are satisfied.

#program plan(start_sem, finish_sem, max_credits_per_semester).
% getting from python
% #const start_sem = 1.
% #const finish_sem = 8.
% #const max_credits_per_semester = 18. %% max courses to take in one semester

semester(start_sem..finish_sem).
%% The KB uses temporal relations (*_before, *_same) to evaluate requisites.
%% e.g. prereq("CSE 214", Sem) :- semester(Sem), passed_before("CSE 114", Sem).
%% e.g. coreq("CSE 161", Sem) :- semester(Sem), taken_same("CSE 160", Sem).

%% course Id is taken before semester Sem. %% for prereq and antireq
taken_before(Id, Sem) :- semester(Sem), taken(Id, _, _, Sem1, _), Sem1 < Sem.

%% passed course Id before Sem with grade higher than Grade %% prereq only
passed_before((Id, Grade), Sem) :- semester(Sem), taken(Id, _, Grade1, Sem1, _), Sem1 < Sem, is_higher(Grade1, Grade).

%% course Id is taken at semester Sem. %% coreq only   %%% todo: rename to taken_at?
taken_same(Id, Sem) :- semester(Sem), taken(Id, _, _, Sem, _).

%% for prereq_or_coreq: could be taken before or at the same semester.
taken_before_or_same(Id, Sem) :- taken_before(Id, Sem).
taken_before_or_same(Id, Sem) :- taken_same(Id, Sem).

%%% TODO: assume courses are offered in all semesters, need to change it later.
offered(Id, Sem) :- course(Id, _), semester(Sem).

%%%% generate
%% any untaken course can be planned for at most one semester.
{ planned(Id, Sem) : semester(Sem), offered(Id, Sem) } 1 :- course(Id, _), not taken_id(Id).

%% select exactly one credit option for each planned course (there could be many)
1 { planned_credit(Id, Credit) : course(Id, Credit) } 1 :- planned(Id, _).

%% assume course planned has grade A and taken in SB
taken(Id, Credit, "A", Sem, "SB") :- planned(Id, Sem), planned_credit(Id, Credit).

%%%% constraints
%% all requirements must be satisfied.
:- item(X), not sat(X).

%% prereq: if a course is planned, then the prereq must be satisfied at the same semester.
:- planned(Id, Sem),
   has_prereq(Id),
   not prereq(Id, Sem).

% coreq: if a course is planned, then the coreq must be satisfied at the same semester.
:- planned(Id, Sem),
   has_coreq(Id),
   not coreq(Id, Sem).

% antireq: can not be satisfied at the same semester.
:- planned(Id, Sem),
   has_anti_req(Id), 
   anti_req(Id, Sem).      %% anti-req can not be satisfied

% must avoid: must-avoid can not be planned for (ignore history).
:- planned(Id, _),
   must_avoid(Id).

% must take: for must-take, either in history or in the plan.
:- must_take(Id),
   not taken_id(Id),
   not planned(Id, _).

%% do not exceed max credits per semester
:- semester(Sem), #sum { Credit, Id : planned(Id, Sem), planned_credit(Id, Credit) } > max_credits_per_semester.

%%%% optimization

%% first, minimize the number of courses to take to satisfy all requirements.
#minimize { 1@2, Id : planned(Id, _) }.

%% next, minimize the number of semesters
max_sem(Sem) :- semester(Sem), Sem = #max { Sem1 : planned(_, Sem1) }. %% get the max semester in the plan
#minimize { Sem@1 : max_sem(Sem) }.

#program input.

%% student facts
standing("U1"). standing("U2"). standing("U3"). standing("U4").
major("CSE"). permission.
% must_avoid("CHE 322").
% must_take("CHE 322").
%%%%% test (commented out to get input from python)
%% to play around:
%%   you can comment out more of the taken_id facts.
%%   change the generate rule (in the planning part below) to set upper_bound to max number of courses to plan for, e.g. 5.
%%   upper_bound can also be removed, which means there is no limit.
%%   { plan_to_take(Id) : can_take(Id) } upper_bound
%% first line commented out to test planning
% taken_id("CSE 114"). taken_id("CSE 214"). taken_id("CSE 216").
% taken_id("CSE 160"). taken_id("CSE 161"). taken_id("CSE 260"). taken_id("CSE 261").
% taken_id("CSE 215"). taken_id("CSE 220").
% taken_id("CSE 303"). taken_id("CSE 310"). taken_id("CSE 316").
% taken_id("CSE 320"). taken_id("CSE 373"). taken_id("CSE 416").
% taken_id("MAT 131"). taken_id("MAT 132"). taken_id("AMS 210").
% taken_id("AMS 301"). taken_id("AMS 310").
% taken_id("CSE 300"). taken_id("CSE 312").
% taken_id("CSE 360"). taken_id("CSE 361"). taken_id("CSE 351").
% taken_id("CSE 352"). taken_id("CSE 353"). taken_id("CSE 355").
% taken_id("PHY 131"). taken_id("PHY 133"). taken_id("AST 203").

%% generate input, assume all courses are taken in semester 0
% taken(Id, Credit, "A", (0, 0), "SB") :- course(Id, Credit), taken_id(Id).