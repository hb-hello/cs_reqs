%% Guide: 3.1.10 Pooling
%% the following is equivalent to is_c_or_higher("A"). is_c_or_higher("A-"). ...
%% clingo encoding for BS degree requirements in CSE at Stony Brook University (Fall 2025).
% https://catalog.stonybrook.edu/preview_program.php?catoid=7&poid=318

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

%% gpa calculation, takes a subset (marked by the tag) and calculates the GPA = floor(weighted sum / sum of weights).
%%   only consider letter grades in grade_points.
%%   if a course is taken multiple times, only one would be counted. we assume no repeated courses
%%   to allow repeats, simply add 'When' in the aggregate, but grounding takes longer.
gpa(Tag, GPA) :-
  subset_taken(_, Tag),
  WeightedSum = #sum { Cr * Pts, Id: subset_taken(Id, Tag), taken(Id, Cr, G, _, _), grade_points(G, Pts) },
  SumOfWeights = #sum { Cr, Id : subset_taken(Id, Tag), taken(Id, Cr, G, _, _), grade_points(G, _) },
  SumOfWeights > 0, GPA = WeightedSum / SumOfWeights. %%% integer floor division. 

%% gpa is 0 when sum of weights is 0, as in python.
gpa(Tag, 0) :-
  subset_taken(_, Tag),
  #sum { Cr, Id: subset_taken(Id, Tag), taken(Id, Cr, G, _, _), grade_points(G, _) } = 0.

% taken(Id, Credits, Grade, When, Where): taken course Id with Credits, etc.

c_or_higher(Cid) :- taken(Cid, _, Grade, _, _), is_c_or_higher(Grade).
passed(Cid) :- c_or_higher(Cid).
passed_with_grade(Cid, Grade) :- taken(Cid, _, Grade1, _, _), is_or_higher(Grade1, Grade).

% c(Subject, Id): course Id in Subject

% passed all courses in Subject
passed_all(Subject) :-
  c(Subject, _),                 %% ground Subject
  passed(Id) : c(Subject, Id).   %% passed for each course in subject

%% course C is witness for passing all courses in a subject in requirement Item
wit(Item, Id) :- s(Item, Subj), passed_all(Subj), c(Subj, Id).

% return set of courses in subjects in requirement item.
courses(Id, Item) :- s(Item, Subj), c(Subj, Id).

% 1. Required Introductory Courses
%%% CHANGED for 2025: restructured from prog/prog2/dmath/dmath2/sys
%%%   to focs/focs2/prog/prog2/focs_ii/focs_ii2/sys
%%%   - added CSE 113 (focs) and CSE 150 as its honors substitute (focs2)
%%%   - prog is now {CSE 114, CSE 214} (removed CSE 216)
%%%   - prog2 stays {CSE 160, CSE 161, CSE 260, CSE 261}
%%%     but now substitutes for {CSE 114, CSE 214, CSE 307} (307 is in req 2)
%%%   - added CSE 213 (focs_ii) and CSE 350 as its honors substitute (focs_ii2)
%%%   - removed CSE 215 (dmath) and CSE 150 as dmath2 (CSE 150 is now focs2)
c(focs, "CSE 113").
c(focs2, "CSE 150").
c(prog, ("CSE 114"; "CSE 214")).
c(prog2, ("CSE 160"; "CSE 161"; "CSE 260"; "CSE 261")).
c(focs_ii, "CSE 213").
c(focs_ii2, "CSE 350").
c(sys, "CSE 220"). 
s(intro, (focs; focs2; prog; prog2; focs_ii; focs_ii2; sys)).

req(intro) :- 
  passed_all(focs; focs2),
  passed_all(prog; prog2),
  passed_all(focs_ii; focs_ii2),
  passed_all(sys).

% 2. Required Advanced Courses
%%% CHANGED for 2025: restructured from theory/theory2/algo/algo2/common
%%%   - removed CSE 303 (theory) and CSE 350 (theory2) — CSE 350 moved to req 1 focs_ii2
%%%   - removed CSE 310 from required (was in common)
%%%   - added CSE 307 as required (pl); prog2 also satisfies it (cross-req substitution)
%%%   - CSE 316 and CSE 320 remain required (now individual sets)
%%%   - added CSE 356 OR CSE 416 choice (was: CSE 416 in common with no alternative)
c(pl, "CSE 307").
c(softdev, "CSE 316"). 
c(sysfund, "CSE 320").
c(algo, "CSE 373").
c(algo2, "CSE 385").
c(cloud, "CSE 356").
c(se, "CSE 416").
s(adv, (pl; softdev; sysfund; algo; algo2; cloud; se)).

req(adv) :- 
  passed_all(pl; prog2),     %% CSE 307, or honors prog2 substitutes for it
  passed_all(softdev),
  passed_all(sysfund),
  passed_all(algo; algo2),
  passed_all(cloud; se).

% 3. Computer Science Electives
%%% CHANGED for 2025:
%%%   - threshold raised from 4 to 6
%%%   - removed CSE 300 and CSE 312 from elect_exclude (but still excluded as non-technical)
%%%   - added following:
% Students may only use 3 credits from the following courses to satisfy one upper-division technical elective for the CSE major requirements: CSE 487, CSE 496, VIP 395, VIP 396, VIP 495, VIP 496. 
%%% todo: could 3 credits satisfy more than one? interpret as at most 3 credits from the following
c(elect_capped, ("CSE 487"; "CSE 496"; "VIP 395"; "VIP 396"; "VIP 495"; "VIP 496")).

c(elect_exclude, ("CSE 475"; "CSE 495"; "CSE 300"; "CSE 301"; "CSE 312")).

subset_taken(Id, elect_passed) :-
  taken(Id, Crs, G, _, _), is_c_or_higher(G),
  @course_prog(Id) = "CSE",
  @upper_division(Id) = 1,    %% is upper division
  Crs >= 3, not courses(Id, adv), not c((elect_exclude;elect_capped), Id).

% 1. if all courses in elect_capped are 3 credits or higher:
% choose up to 1 course from elect_capped 
{ subset_taken(Id, elect_passed) : c(elect_capped, Id), passed(Id) } 1.

% 2. if the courses in elect_capped can have different credits, we need to check the total credits from elect_capped is at most 3 if more than 1 course from elect_capped is chosen.
% use the following two rules:
% { subset_taken(Id, elect_passed) : c(elect_capped, Id), passed(Id) }.
% :- #sum { Crs, Id : subset_taken(Id, elect_passed), c(elect_capped, Id), taken(Id, Crs, _, _, _) } > 3,
%    #count { Id: subset_taken(Id, elect_passed), c(elect_capped, Id) } > 1.

req(elect) :- 
  #count { Id: subset_taken(Id, elect_passed) } >= 6.

%% for elect, witness is the subset elect_passed used in elect.
wit(elect, Id) :- subset_taken(Id, elect_passed).

% 4. AMS 151, AMS 161 Applied Calculus I, II
%%% (copied from python) todo:
% Equivalency for MAT courses achieved through the Mathematics
% Placement Examination is accepted to meet MAT course requirements.
%%% NO CHANGE for 2025
c(calc, ("AMS 151"; "AMS 161")).
c(calc2, ("MAT 125"; "MAT 126"; "MAT 127")).
c(calc3, ("MAT 131"; "MAT 132")).
s(calc, (calc; calc2; calc3)).

req(calc) :- 
  passed_all(calc;calc2;calc3).

% 5. One of the following:
%%% NO CHANGE for 2025
c(alg, "MAT 211").
c(alg2, "AMS 210").
s(alg, (alg; alg2)).

req(alg) :- 
  passed_all(alg; alg2).

% 6. Required Upper-Division Statistics Course
%%% CHANGED for 2025: simplified
%%%   - removed AMS 301 (fmath) — no longer required
%%%   - removed AMS 311 (sta2) — no longer an alternative
%%%   - just AMS 310 required
c(sta, "AMS 310").
s(sta, sta).

sta_req :-
  passed_all(sta).

% 7. At least one of the following natural science lecture/laboratory combinations...
% All courses taken to satisfy Requirements 1 through 9 must be taken for a letter grade.
%%% NO CHANGE for 2025 (same combos)
c(bio, ("BIO 201"; "BIO 204")).
c(bio2, ("BIO 202"; "BIO 204")).
c(bio3, ("BIO 203"; "BIO 204")).
c(che, ("CHE 131"; "CHE 133")).
c(che2, ("CHE 152"; "CHE 154")).
c(phy, ("PHY 126"; "PHY 133")).
c(phy2, ("PHY 131"; "PHY 133")).
c(phy3, ("PHY 141"; "PHY 133")).
sci_combs(bio; bio2; bio3; che; che2; phy; phy2; phy3).
% 8. One additional natural science course selected from above and the following list...
% All courses taken to satisfy Requirements 1 through 9 must be taken for a letter grade.
%%% CHANGED for 2025:
%%%   - removed: GEO 102, GEO 103, GEO 112, GEO 123, GEO 122 (5 GEO courses)
%%%   - removed: PHY 134, PHY 252
%%%   - added: BIO 201, BIO 202, BIO 203
%%%   - added: CHE 131, CHE 152
%%%   - added: PHY 126, PHY 131

%%% no sci_cred_req
c(sci_more, ("AST 203"; "AST 205"; "BIO 201"; "BIO 202"; "BIO 203"; 
            "CHE 131"; "CHE 132"; "CHE 152"; "CHE 321"; "CHE 322"; "CHE 331"; "CHE 332"; 
            "PHY 125"; "PHY 126"; "PHY 127"; "PHY 131"; "PHY 132"; "PHY 142"; "PHY 251")).

%% sci_courses(taken) in python: set of all sci courses taken
sci_taken(Id) :- sci_combs(Subj), c(Subj, Id), taken(Id, _, _, _, _).
sci_taken(Id) :- c(sci_more, Id), taken(Id, _, _, _, _).

%% generate a subset of sci_courses taken: use the same subset to satisfy sci_req, sci_cred_req and sci_grade_req.
{ subset_taken(Id, sci) } :- sci_taken(Id).

%%% separeted out because clingo treats all conditions after a colon (:) as part of the condition
sci_combs_req :- sci_combs(Subj), subset_taken(Id, sci) : c(Subj, Id).

req(sci) :- 
  sci_combs_req,
  gpa(sci, Gpa), Gpa >= 2*100.

%%% CHANGED FOR 2025:
% Note: One may not take science courses that are deemed equivalent to satisfy 7 and 8 (e.g., PHY 125 and PHY 131). Please review course descriptions for more information. 

% equiv(C1, C2): courses C1 and C2 are deemed equivalent for satisfying the sci requirement. to be taken from KB.

:- subset_taken(C1, sci), subset_taken(C2, sci), equiv(C1, C2).

%% witness for sci is the subset used to satisfy all sci requirements, as in python.
wit(sci, Id) :- subset_taken(Id, sci).

% 9. Required Non-Technical Courses
%%% CHANGED for 2025: req 9 and 10 in 2024 merged.
%%%   - was: ethics_req (CSE 312) and writing_req (CSE 300) as separate requirements
%%%   - now: nontechnical_req requiring both CSE 300 and CSE 312
c(nontech, ("CSE 300"; "CSE 312")).
s(nontech, nontech).

req(nontech) :- passed_all(nontech).

%%% (copied from python) todo:
% Note: All students are encouraged to discuss their program with an
% undergraduate advisor.
% In Requirement 2 above, CSE/ESE double majors may substitute ESE
% 440, ESE 441 Electrical Engineering Design I, II for CSE 356 - Cloud
% Computing or CSE 416 - Software Engineering provided that the design
% project contains a significant software component. Approval of the
% Department of Computer Science is required.
%%% Note for 2025: CSE 356 or CSE 416 must be completed at Stony Brook University.
%% at the top of webpage:
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

req(credits_at_SB) :-
  #sum { Cr, Id : taken(Id, Cr, _, _, "SB"), items123_course(Id) } >= 24,
  #sum { Cr, Id : taken(Id, Cr, _, _, "SB"), items23_course(Id) } >= 18.

wit(credits_at_SB, Id) :- items123_course(Id), taken(Id, _, _, _, "SB").
wit(credits_at_SB, Id) :- items23_course(Id), taken(Id, _, _, _, "SB").

%% requirements items
%%% CHANGED for 2025: replaced ethics and writing with nontech
item(intro; adv; elect; calc; alg; sta; sci; nontech; credits_at_SB).

%% degree requirement sat if all requirements are satisfied
degree :- req(Item) : item(Item).

% checking. program tag omitted
#maximize { 1, Item : req(Item) }.    %% soft constraint: maximize the number of requirements satisfied. 
                                      %%   so we have a model even when not all requirements are satisfied.

% plan, input: same as in cse_req_clingo.lp