#_ code/comments not used, to leave out
from pprint import pprint  ## for printing witness dictionary
from collections import namedtuple
#_ from typing import NamedTuple, Tuple
from itertools import chain, combinations  ## for pow

## power set of set s ## overriding python pow(base, exponents, modulus)
def pow(s): ## take set s, return set of subsets of s
  return set(frozenset(t) for t in chain.from_iterable( 
    combinations(s, r) for r in range(len(s) + 1) ))

#_ from enum import Enum
#_ Grade = Enum('Grade', 'A A- B+ B B- C+ C C- D+ D F I I/F NC NR P Q R S U W')

## https://www.stonybrook.edu/sb/bulletin/current-fall24/policiesandregulations/records_registration/grading_system.php

# Grading and the Grading System

def C_or_higher(grade): return grade in {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}

# The term "letter grade" refers to A through F and in certain
# circumstances to S grades.  ## what circumstance?
## def letter_grade(grade): return 'A' <= grade <= 'F'  ## not need to be used

# The following grades are not calculated into the g.p.a.: 
# P, NC, NR, R, S, U, W.  ## Also I.
# For the purpose of determining grade point average, grades are assigned
# point values as follows:
grade_points = {
  'A': 4.00, 'A-': 3.67,
  'B+': 3.33, 'B': 3.00, 'B-': 2.67,
  'C+': 2.33, 'C': 2.00, 'C-': 1.67,
  'D+': 1.33, 'D': 1.00,
  'F': 0.00, 'I/F': 0.00, 'Q': 0.00
}
# Calculate the Quality Points for each course by multiplying the Point value
# of the grade by the total number of Credits for the course:
def GPA(weighted_grades):  ## list of (credits, grade) pairs
  weighted_sum = sum(grade_points[g] * cr
                     for (cr,g) in weighted_grades if g in grade_points)
  sum_of_weights = sum(cr for (cr,g) in weighted_grades if g in grade_points)
  return weighted_sum / sum_of_weights if sum_of_weights != 0 else 0

## whether a course id is upper-division, i.e., 300-level or above
def upper_division(course_id): return int(course_id[4:]) >= 300


## a course taken, e.g., Taken('CSE 114', 4, 'A', (2024, 2), 'SB')
Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])
#_ class CourseTaken(NamedTuple):
#_   id: str  ## e.g., 'CSE 114'
#_   credits: int
#_   grade: str
#_   when: Tuple[int,int]  ## e.g., 2024,2  ## 1-4 for winter,spring,summer,fall
#_   where: str  ## e.g., 'SB'


## https://www.stonybrook.edu/sb/bulletin/current-fall24/academicprograms/cse/degreesandrequirements.php

# Requirements for the Major and Minor in Computer Science (CSE)
#
# Requirements for the Major

## check conditions and track desired witness for any condition that is true:
## for any requirement item 1-10 met, the witness is the set of courses used;
## otherwise, any helpful information could be give as the witness.

#_ ## for a witness object, with subject attribute for whether it is satisfied
#_ class Witness: pass
#_ w = Witness()

## witness dictionary, mapping each witness string name to it witness value
w = dict()
def wit(name, value):
  w[name] = value  ## record witness value for name; overwrite only in sci_req
  return True

## return whether set with string name s1name <= set s2, and 
## record withness for the string name as True if so
def ss_wit(s1name, s2):
  s1 = globals()[s1name]
  return s1 <= s2 and wit(s1name, True)

#_ ## add witness set for set with at least k elements
#_ def count_ge(s, k, sname):
#_   return len(s) >= k and wit(sname, s)

## return witness if requirement item is in withness dictionary, otherwise
## return witness of subjects for subjects in the item; only called on item
## so that the return value is a set supporting sorted on elements.
def get_wit(item): ## string name for the requirement item 
  return (w[item] if item in w else
    #_ [subj for subj in globals()[item] if subj in w] #@ only subj
    #_ [globals()[subj] for subj in globals()[item] if subj in w] ## crs by subj
    ### todo: globals()[item] on ethics/writing: set of crs, not subj, luck ok:(
    {c for subj in globals()[item] if subj in w for c in globals()[subj]}
  )

## return set of courses in string-name subjects in requirement item
def courses(item): return {c for subj in item for c in globals()[subj]}


## Each _req function below returns whether a requirement in 1-10 is satisfied.
## taken/taken_ids is the set of courses/ids taken (req 7-8);
## passed/passed_ids is those with of C or higher (requirements 1-6 and 9-10).

# 1. Required Introductory Courses
prog = {'CSE 114', 'CSE 214', 'CSE 216'}  ## todo: change to tuple?
prog2 = {'CSE 160', 'CSE 161', 'CSE 260', 'CSE 261'}  ## Honors
dmath = {'CSE 215'}
dmath2 = {'CSE 150'}  # Honors
sys = {'CSE 220'}
intro = {'prog', 'prog2', 'dmath', 'dmath2', 'sys'}

def intro_req(passed_ids):
  return ((ss_wit('prog', passed_ids) or ss_wit('prog2', passed_ids)) and 
          (ss_wit('dmath', passed_ids) or ss_wit('dmath2', passed_ids)) and
          ss_wit('sys', passed_ids))

# 2. Required Advanced Courses
theory = {'CSE 303'}
theory2 = {'CSE 350'}  # Honors
algo = {'CSE 373'}
algo2 = {'CSE 385'}  # Honors
other = {'CSE 310', 'CSE 316', 'CSE 320', 'CSE 416'}
adv = {'theory', 'theory2', 'algo', 'algo2', 'other'}

def adv_req(passed_ids):
  return ((ss_wit('theory', passed_ids) or ss_wit('theory2', passed_ids)) and
          (ss_wit('algo', passed_ids) or ss_wit('algo2', passed_ids)) and
          ss_wit('other', passed_ids))

# 3. Computer Science Electives  ## simpler than 2025
#
# Four upper-division technical CSE electives, each of which must carry at
# least three credits. Technical electives do not include teaching practica
# (CSE 475), the senior honors project (CSE 495, 496), and courses
# designated as non-technical in the course description (such as CSE 301).
elect_exclude = {'CSE 475', 'CSE 495', 'CSE 300', 'CSE 301', 'CSE 312'}

def elect_courses(passed):
  return {c.id for c in passed if c.id[:3] == 'CSE' and upper_division(c.id)
          and c.credits >= 3 and c.id not in courses(adv) | elect_exclude}

def elect_req(passed):
  s = elect_courses(passed)
  wit('elect', s if len(s) >= 4 else s|{'need 4 total'})
  return len(s) >= 4

# 4. AMS 151, AMS 161 Applied Calculus I, II
### todo: 
# Equivalency for MAT courses achieved through the Mathematics
# Placement Examination is accepted to meet MAT course requirements.
calc1 = {'AMS 151', 'AMS 161'}
calc2 = {'MAT 125', 'MAT 126', 'MAT 127'}
calc3 = {'MAT 131', 'MAT 132'}
calc = {'calc1', 'calc2', 'calc3'}

def calc_req(passed_ids):
  return (ss_wit('calc1', passed_ids) or ss_wit('calc2', passed_ids) or
          ss_wit('calc3', passed_ids))

# 5. One of the following
alg1 = {'MAT 211'}
alg2 = {'AMS 210'}
alg = {'alg1', 'alg2'}

def alg_req(passed_ids):
  return ss_wit('alg1', passed_ids) or ss_wit('alg2', passed_ids)

# 6. Both of the following
fmath =  {'AMS 301'}
sta1 = {'AMS 310'}
sta2 = {'AMS 311'}
sta = {'fmath', 'sta', 'sta2'}

def sta_req(passed_ids):
  return (ss_wit('fmath', passed_ids) and 
          (ss_wit('sta1', passed_ids) or ss_wit('sta2', passed_ids)))

# 7. At least one of the following natural science lecture/laboratory
# combinations:
bio = {'BIO 201', 'BIO 204'}; bio2 = {'BIO 202', 'BIO 204'}
bio3 = {'BIO 203', 'BIO 204'}
che = {'CHE 131', 'CHE 133'}; che2 ={'CHE 152', 'CHE 154'}
phy = {'PHY 126', 'PHY 133'}
phy2 = {'PHY 131', 'PHY 133'}; phy3 = {'PHY 141', 'PHY 133'}
sci_combs = [bio, bio2, bio3, che, che2, phy, phy2, phy3]  ## list/tuple/...

## subsumed by sci_req(taken) below
## def sci_comb_req(taken_ids):
##   ## some(comb in sci_combs, has= comb <= taken_ids)
##   return any(comb <= taken_ids for comb in sci_combs)

# 8. Additional natural science courses selected from above and following list:
#
# Note: The courses selected in 7 and 8 must carry at least 9 credits.
sci_more = {'AST 203', 'AST 205',
            'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332',
            'GEO 102', 'GEO 103', 'GEO 112', 'GEO 123', 'GEO 122',
            'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142', 
            'PHY 251', 'PHY 252'} 

def sci_courses(taken):
  return {c for c in taken if c.id in set().union(*sci_combs) | sci_more}

#_ not sufficient to be correct:
#_ def sci_cred_req(taken): return sum(c.credits for c in sci_courses(taken))>=9

def sci_req(taken): ### subsumes sci_comb_req
  taken_combs = [{c for c in taken if c.id in comb} 
                 for comb in sci_combs if comb <= {c.id for c in taken}]
  #_ some(t in taken_combs, s in pow({c for c in taken if c.id in sci_more}),
  #_      has= t|s <= taken and sum(c.credits for c in t|s) >= 9 and 
  #_      GPA([(cr, g) for (_, cr, g, _, _) in t|s]) >= 2.0)
  wit('sci', {'need a lec/lab combo and more, with >=9 credits and >=2.0 GPA'})
  return any(t|s <= taken and sum(c.credits for c in t|s) >= 9 and
             GPA([(cr, g) for (_, cr, g, _, _) in t|s]) >= 2.0
             and wit('sci', {c.id for c in t|s})
             for t in taken_combs for s in pow(sci_courses(taken)-t))

# 9. Professional Ethics
ethics = {'CSE 312'}

def ethics_req(passed_ids):
  return ethics <= passed_ids and wit('ethics', ethics)

# 10. Upper-Division Writing Requirement
writing = {'CSE 300'}

def writing_req(passed_ids):
  return writing <= passed_ids and wit('writing', writing)


### todo:
# Note: All students are encouraged to discuss their program with an
# undergraduate advisor.
# In Requirement 2 above, CSE/ESE double majors may substitute ESE
# 440, ESE 441 Electrical Engineering Design I, II for CSE 416 Software
# Engineering provided that the design project contains a significant
# software component. Approval of the Department of Computer Science is
# required.

## this is at the top of the section on the webpage:
# The major in Computer Science leads to the Bachelor of Science degree.
# Completion of the major requires approximately 80 credits.  ### todo: count
# At least 24 credits from items 1 to 3 below, and at least 18 credits from
# items 2 and 3, must be completed at Stony Brook.
### assume to be not about "The courses taken to satisfy Requirements ..."
def credits_at_SB_req(taken):
#_  item1_credits = ...
  items123_credits = sum(c.credits for c in taken if c.where == 'SB'
       if c.id in courses(intro) | courses(adv) | elect_courses(taken))
  items23_credits = sum(c.credits for c in taken if c.where == 'SB'
                        if c.id in courses(adv) | elect_courses(taken))
  wit('credits_at_SB', {'items123 = '+str(items123_credits),
                        'items23 = '+str(items23_credits)})
  return (items123_credits >= 24 and items23_credits >= 18)

# Grading
#
# All courses taken to satisfy Requirements 1 through 10 must be taken for
# a letter grade.  ### always true if the two below are true
# The courses in Requirements 1-6, 9, and 10 must be passed with a letter
# grade of C or higher.  ### assume to be: The courses *taken to satisfy* Req...
# The grade point average for the courses in Requirements 7 and 8 must be
# at least 2.00.  ### assume to be: The courses *taken to satisfy* Req...
## merged with 7 and 8; otherwise, not correct if as assumed.
#_ def sci_grade_req(taken):
#_   return GPA([(cr, g) for (_, cr, g, _, _) in sci_courses(taken)]) >= 2.0

## whether the taken courses satisfy all requirements for BS major in CSE
def degree_reqs(taken):
  taken_ids = {c.id for c in taken}
  passed = {c for c in taken if C_or_higher(c.grade)}
  passed_ids = {c.id for c in passed}
  checks = (intro_req(passed_ids), adv_req(passed_ids), elect_req(passed),
            calc_req(passed_ids), alg_req(passed_ids), sta_req(passed_ids),
            sci_req(taken), ethics_req(passed_ids), writing_req(passed_ids),
            credits_at_SB_req(taken))
  items = ('intro', 'adv', 'elect', 'calc', 'alg', 'sta', 
           'sci', 'ethics', 'writing', 'credits_at_SB')
  checked = {item : (check, sorted(get_wit(item)))
             for item, check in zip(items,checks)}
  checked['degree'] = all(checks), []
  print('---- checked, from running degree_reqs:')
  pprint(checked)
  print('----\n'+ '\n'.join(item + '\t ' + str(check) + ' ' + str(wit)
                  for item, (check, wit) in checked.items()))
  return checked

def test():
  taken_ids = {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220', 
               'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',
               'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',
               # electives
               'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',
               # science
               'PHY 131', 'PHY 133', 'AST 203',
               'CSE 300', 'CSE 312'
  }
  taken = {Taken(cid, 4, 'A', (2024,2), 'SB') for cid in taken_ids}
  degree_reqs(taken)
  print('---- witness:', w)

test()


import tests, inspect

def testing(test):
  taken, checked = test()
  print('---- taken_ids: ', sorted({c.id for c in taken}))
  # print('---- taken: ')
  # pprint(sorted(taken))
  print('---- checked: ')
  pprint(checked)
  assert(degree_reqs(taken)==checked)

def run_tests():
  global w
  for (name, func) in inspect.getmembers(tests, inspect.isfunction):
    if name.startswith('test_'):
      w = dict()
      print('--------', name, 'started:')
      testing(func)
    print('--------', name, 'passed !!!')

run_tests()