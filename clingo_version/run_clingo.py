from collections import defaultdict
import clingo
import argparse
from pprint import pprint
from course_kb.course_kb import *
from clingo_version.configs import MAIN_LP, KB_LP

MIN_SEM = (2024, 2)
NUM_SEMS = 16
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

def run_clingo(
    mode,               ## one of 'check' or 'plan'
    main_lp=MAIN_LP,    ## relative path to main lp file
    kb_lp=KB_LP,        ## relative path to kb lp file
    timeout=10 * 60,    ## timeout in seconds
    ground_only=False,  ## skip solving
    **inputs            ## taken_set, must_include, must_exclude
    ):
  
  taken_set = inputs.get('taken_set', set())
  must_include = inputs.get('must_include', set())
  must_exclude = inputs.get('must_exclude', set())

  ctrl_args = ["0", "-Wno-atom-undefined"]  ## find optimal solution and suppress warnings about undefined atoms
  
  items = ('intro', 'adv', 'elect', 'calc', 'alg', 'sta', 
          'sci', 'ethics', 'writing', 'credits_at_SB',
          'degree')   ## include degree as an item

  min_sem = min(c.when for c in taken_set) if taken_set else MIN_SEM
  max_sem = max(c.when for c in taken_set) if taken_set else MIN_SEM

  test_facts = []
  
  test_facts.extend([f'taken("{c.id}", {c.credits}, "{c.grade}", {sem_to_int(c.when, min_sem)}, "{c.where}").' for c in taken_set])

  if mode == 'plan':  ## needed only for planning
    test_facts.extend([f'taken_id("{c.id}").' for c in taken_set])
    test_facts.extend([f'must_include("{cid}").' for cid in must_include])
    test_facts.extend([f'must_exclude("{cid}").' for cid in must_exclude])

    start_sem = sem_to_int(max_sem, min_sem) + 1
    finish_sem = start_sem + NUM_SEMS - 1
    ctrl_args.append(f"-c start_sem={start_sem}")
    ctrl_args.append(f"-c finish_sem={finish_sem}")
    ctrl_args.append(f"-c max_credits_per_semester={NUM_CREDITS_PER_SEM}")  
  
    for cid, terms in COURSE_OFFERED.items():
      # terms is a set like {2,3,4}; blank CSV entry is set()
      for sem in range(start_sem, finish_sem + 1):
        if rel_sem_to_term(sem, min_sem) in terms:
          test_facts.append(f'offered("{cid}", {sem}).')

  ctrl = clingo.Control(ctrl_args)
  
  ctrl.load(main_lp)
  ctrl.load(kb_lp)

  ctrl.add("input", [], "\n".join(test_facts))

  to_ground = [("base", []), ("input", []), ("check", [])]
  if mode == 'plan': to_ground.append(("plan", []))

  ctrl.ground(to_ground, context=ClingoContext())
  
  checked = {}  ## initialize all items to not passed
  schedule = {}
  
  def on_model(model):    ## invoked for every model found
    nonlocal checked, schedule

    ## reset checked when there are multiple models (in planning mode)
    checked = {item: [False, []] for item in items}  ## initialize all items to not passed
    planned_courses = {}
    schedule = defaultdict(list)
    cost = model.cost if model.cost is not None else None
    # print(f"Model found with cost: {cost}")
    
    for sym in model.symbols(atoms=True):     ## collect check for each requirement
      if sym.name == "degree":
        checked['degree'][0] = True
      elif sym.name == "sat":
        item = str(sym.arguments[0])
        checked[item][0] = True
      elif sym.name == "planned":             ## planning mode
        cid_sym, semester_sym = sym.arguments
        cid = str(cid_sym).strip('"')
        sem = int_to_sem(semester_sym.number, min_sem)
        planned_courses[cid] = sem            ## record planned semester
        schedule[sem].append(cid)             ## add course to schedule

    for sym in model.symbols(atoms=True):     ## collect witness
      if sym.name == "wit":
        item, val = str(sym.arguments[0]), sym.arguments[1]
        if item == "credits_at_SB" and val.type == clingo.SymbolType.Function and val.name in {"items123", "items23"}:
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
  timed_out = False
  if not ground_only:
    with ctrl.solve(on_model=on_model, async_=True) as handle:
      try:
        finished = handle.wait(timeout)
        if not finished:
          print(f'timeout {timeout} reached.'); timed_out = True
          handle.cancel()
      except KeyboardInterrupt:
        print('interrupted by user')
        handle.cancel()
      finally:
        handle.wait()  ## wait for solver to finish after canceling
        result = handle.get()
 
  ## sort witness, same as test in python
  checked = {item: (check, sorted(wits)) for item, (check, wits) in checked.items()}

  for sem in schedule:
    schedule[sem].sort()

  ## build a plain dict from clingo statistics for easy access and JSON serialisation
  lp       = ctrl.statistics.get('problem', {}).get('lp', {})
  solvers  = ctrl.statistics.get('solving', {}).get('solvers', {})
  times    = ctrl.statistics.get('summary', {}).get('times', {})
  total_t  = float(times.get('total', 0))
  solve_t  = float(times.get('solve', 0))
  stats = {
    'problem': {'lp': {'atoms': int(lp.get('atoms', 0)), 'rules': int(lp.get('rules', 0)),
                       'bodies': int(lp.get('bodies', 0)), 'eqs': int(lp.get('eqs', 0))}},
    'solving': {'solvers': {'choices':   int(solvers.get('choices', 0)),
                            'conflicts': int(solvers.get('conflicts', 0)),
                            'restarts':  int(solvers.get('restarts', 0))}},
    'summary': {'times': {'total': total_t, 'solve': solve_t}},
    'timed_out': timed_out
  }
  if timed_out and checked:
    stats['partial_reqs_sat']   = [k for k, (ok, _) in checked.items() if ok]
    stats['partial_reqs_unsat'] = [k for k, (ok, _) in checked.items() if not ok]

  return checked, schedule, stats

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Run the Degree Checker and Planner.")
  parser.add_argument('-m', '--mode', choices=['check', 'plan'], default='check', help="Run mode.")
  parser.add_argument('-f', '--file', default=MAIN_LP, help="Path to the main .lp file that encodes the logic.")
  parser.add_argument('-k', '--kb', default=KB_LP, help="Path to the KB .lp file.")
  
  ctrl_args = parser.parse_args()
  
  print(f"--- Running in {ctrl_args.mode.upper()} mode ---")
  checked, schedule, stats = run_clingo(mode=ctrl_args.mode, main_lp=ctrl_args.file, kb_lp=ctrl_args.kb)
  
  if ctrl_args.mode == 'check':
    pprint(checked)
  elif ctrl_args.mode == 'plan':
    print(f"Degree Passed: {checked['degree'][0]}")
    print("\n---- planned schedule:")
    for sem in sorted(schedule):
      print(f"  Semester {sem}: {schedule[sem]}")
          
  print_clingo_stats(stats)