from collections import defaultdict

import clingo
import argparse
from pprint import pprint

DEFAULT_MAIN_LP = './cse_req_clingo.lp'
DEFAULT_KB_LP = '../course_kb/kb_complete.lp'
MIN_SEM = (2024, 2)
NUM_SEMS = 8
NUM_CREDITS_PER_SEM = 18

class ClingoContext:
  ## can't have python code in the clingo file if using python api.
  ## the #script (python) in the clingo file is commented out, and we move the functions here.
  def upper_division(self, course_id):
    return clingo.Number(int(course_id.string[4:]) >= 300)

  def course_prog(self, course_id):
    return clingo.String(course_id.string[:3])

def print_clingo_stats(stats):
  times = stats.get('summary', {}).get('times', {})
  total_time = times.get('total', 0)
  solve_time = times.get('solve', 0)
  ground_time = total_time - solve_time
  print("======================")
  print(f"Total time:     {total_time:.4f} seconds")
  print(f"Grounding time: {ground_time:.4f} seconds")
  print(f"Solving time:   {solve_time:.4f} seconds")
  lp_stats = stats.get('problem', {}).get('lp', {})
  if lp_stats:
    print(f"Atoms (Variables): {int(lp_stats.get('atoms', 0)):,}")
    print(f"Generated Rules:   {int(lp_stats.get('rules', 0)):,}")
    print(f"Rule Bodies:       {int(lp_stats.get('bodies', 0)):,}")
    print(f"Equivalences:      {int(lp_stats.get('eqs', 0)):,}")
  solving_stats = stats.get('solving', {}).get('solvers', {})
  if solving_stats:
    choices = int(solving_stats.get('choices', 0))
    conflicts = int(solving_stats.get('conflicts', 0))
    restarts = int(solving_stats.get('restarts', 0))
    
    print(f"Choices:   {choices:,}")
    print(f"Conflicts: {conflicts:,}")
    print(f"Restarts:  {restarts:,}")
  print("======================")

def run_clingo(mode, main_lp, kb_lp, taken_set = set()):
  ## runs Clingo, injects the taken courses, and returns the checked dict and schedule.
  
  ## find optimal solution and supress warnings about undefined atoms
  ctrl = clingo.Control(["0", "-Wno-atom-undefined"])
  
  ctrl.load(main_lp)
  ctrl.load(kb_lp)
  
  items = ('intro', 'adv', 'elect', 'calc', 'alg', 'sta', 
          'sci', 'ethics', 'writing', 'credits_at_SB',
          'degree')   ## include degree as an item

  min_sem = min(c.when for c in taken_set) if taken_set else MIN_SEM
  max_sem = max(c.when for c in taken_set) if taken_set else MIN_SEM

  def get_sem_distance(sem1: tuple, sem2: tuple): ## sem1, sem2 are (year, term) tuples
    return (sem1[0] - sem2[0]) * 4 + (sem1[1] - sem2[1])

  def sem_to_int(sem: tuple):
    nonlocal min_sem
    return get_sem_distance(sem, min_sem) + 1

  def int_to_sem(sem_int: int):
    nonlocal min_sem
    distance = sem_int - 1
    year = min_sem[0] + (min_sem[1] - 1 + distance) // 4
    term = (min_sem[1] - 1 + distance) % 4 + 1
    return (year, term)

  test_facts = ""
  for c in taken_set:
    ## get taken facts from test.
    test_facts += f'taken("{c.id}", {c.credits}, "{c.grade}", {sem_to_int(c.when)}, "{c.where}").\n'
    if mode == 'plan':
      test_facts += f'taken_id("{c.id}").\n'  ## taken_id is only for planning, not needed in checking
  
  ctrl.add("input", [], test_facts)
  
  to_ground = [("base", []), ("input", []), ("check", [])]
  if mode == 'plan': 
    start_sem = sem_to_int(max_sem) + 1
    finish_sem = start_sem + NUM_SEMS
    to_ground.append(("plan", [clingo.Number(start_sem), clingo.Number(finish_sem), clingo.Number(NUM_CREDITS_PER_SEM)]))

  ctrl.ground(to_ground, context=ClingoContext())
  
  checked = {}  ## initialize all items to not passed
  schedule = {}
  
  def on_model(model):    ## invoked for every model found
    nonlocal checked, schedule

    ## reset checked when there are multiple models (in planning mode)
    checked = {item: [False, []] for item in items}  ## initialize all items to not passed
    planned_courses = {}
    schedule = defaultdict(list)
    
    for sym in model.symbols(atoms=True):     ## collect check for each requirement
      if sym.name == "degree":
        checked['degree'][0] = True
      elif sym.name == "sat":
        item = str(sym.arguments[0])
        checked[item][0] = True
      elif sym.name == "planned":             ## planning mode
        cid_sym, semester_sym = sym.arguments
        cid = str(cid_sym).strip('"')
        sem = int_to_sem(semester_sym.number)
        planned_courses[cid] = sem            ## record planned semester
        schedule[sem].append(cid)             ## add course to schedule

    for sym in model.symbols(atoms=True):     ## collect witness
      if sym.name == "wit":
        item, val = str(sym.arguments[0]), sym.arguments[1]
        if item == "credits_at_SB":  ## val.name is items123 or items23. matches python witness for credits_at_SB
          checked[item][1].append(f"{val.name} = {val.arguments[0].number}")
          continue
        course = str(val).strip('"')
        if course in planned_courses:         ## for planned courses, indicate the semester
          course += f' (sem {planned_courses[course]})'
        checked[item][1].append(course)
    
    ## add extra strings if check for item is false
    if not checked['elect'][0]:
      checked['elect'][1].append('need 4 total')
    if not checked['sci'][0]:
      checked['sci'][1].append('need a lec/lab combo and more, with >=9 credits and >=2.0 GPA')

  ctrl.solve(on_model=on_model)

  ## sort witness, same as test in python
  checked = {item: (check, sorted(wits)) for item, (check, wits) in checked.items()}

  for sem in schedule:
    schedule[sem].sort()
      
  return checked, schedule, ctrl.statistics

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Run the Degree Checker and Planner.")
  parser.add_argument('-m', '--mode', choices=['check', 'plan'], default='check', help="Run mode.")
  parser.add_argument('-f', '--file', default=DEFAULT_MAIN_LP, help="Path to the main .lp file that encodes the logic.")
  parser.add_argument('-k', '--kb', default=DEFAULT_KB_LP, help="Path to the KB .lp file.")
  
  args = parser.parse_args()
  
  print(f"--- Running in {args.mode.upper()} mode ---")
  checked, schedule, stats = run_clingo(mode=args.mode, main_lp=args.file, kb_lp=args.kb)
  
  if args.mode == 'check':
    pprint(checked)
  elif args.mode == 'plan':
    print(f"Degree Passed: {checked['degree'][0]}")
    print("\n---- planned schedule:")
    for sem in sorted(schedule):
      print(f"  Semester {sem}: {schedule[sem]}")
          
  print_clingo_stats(stats)