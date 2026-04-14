from collections import defaultdict
import clingo
import argparse
import time
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

def _collect_clingo_stats(ctrl, timed_out, model_count, min_cost):
  """Collect clingo statistics into a plain dict (single source of metrics)."""
  lp       = ctrl.statistics.get('problem', {}).get('lp', {})
  solvers  = ctrl.statistics.get('solving', {}).get('solvers', {})
  times    = ctrl.statistics.get('summary', {}).get('times', {})
  total_t  = float(times.get('total', 0))
  solve_t  = float(times.get('solve', 0))
  return {
    'problem': {'lp': {'atoms': int(lp.get('atoms', 0)), 'rules': int(lp.get('rules', 0)),
                       'bodies': int(lp.get('bodies', 0)), 'eqs': int(lp.get('eqs', 0))}},
    'solving': {'solvers': {'choices':   int(solvers.get('choices', 0)),
                            'conflicts': int(solvers.get('conflicts', 0)),
                            'restarts':  int(solvers.get('restarts', 0))}},
    'summary': {'times': {'total': total_t, 'solve': solve_t}},
    'timed_out': timed_out,
    'model_count': model_count,
    'min_cost': list(min_cost) if min_cost is not None else None,
  }

def _generate_planning_input(inputs):
  taken_set = inputs.get('taken_set', set())
  must_include = inputs.get('must_include', set())
  must_exclude = inputs.get('must_exclude', set())
  min_sem = inputs.get('min_sem', MIN_SEM)
  max_sem = inputs.get('max_sem', MIN_SEM)
  num_sems = inputs.get('num_sems', NUM_SEMS)
  course_offered_terms = inputs.get('course_offered_terms', COURSE_OFFERED_TERMS)

  planning_facts = []
  planning_facts.extend(f'taken_id("{c.id}").' for c in taken_set)
  planning_facts.extend(f'include("{cid}").' for cid in must_include)
  planning_facts.extend(f'exclude("{cid}").' for cid in must_exclude)

  start_sem = sem_to_int(max_sem, min_sem) + 1
  finish_sem = start_sem + num_sems - 1

  planning_ctrl_args = [
    f"-c start_sem={start_sem}",
    f"-c finish_sem={finish_sem}",
    f"-c sem_max_credits={NUM_CREDITS_PER_SEM}",
  ]

  for cid, terms in course_offered_terms.items():
    # terms is a set like {2,3,4}; blank CSV entry is set()
    for sem in range(start_sem, finish_sem + 1):
      if rel_sem_to_term(sem, min_sem) in terms:
        planning_facts.append(f'offered("{cid}", {sem}).')

  return planning_facts, planning_ctrl_args

def run_clingo(
    mode,               ## one of 'check' or 'plan'
    main_lp=MAIN_LP,    ## relative path to main lp file
    kb_lp=KB_LP,        ## relative path to kb lp file
    timeout=10 * 60,    ## timeout in seconds
    ground_only=False,  ## skip solving
    **inputs            ## taken_set, must_include, must_exclude
    ):
  
  ## temp hacks, mode is the program name ("check", "plan", or other plan programs)
  to_ground = [("base", []), ("input", []), (mode, [])]
  
  assert mode.startswith(('check', 'plan')), f"mode must start with 'check' or 'plan', got {mode}"

  taken_set = inputs.get('taken_set', set())
  ctrl_args = ["0", "-Wno-atom-undefined"]

  items = (
    'intro', 'adv', 'elect', 'calc', 'alg', 'sta',
    'sci', 'ethics', 'writing', 'credits_at_SB', 'degree'
  )

  min_sem = min(c.when for c in taken_set) if taken_set else MIN_SEM

  input_facts = [
    f'taken("{c.id}", {c.credits}, "{c.grade}", {sem_to_int(c.when, min_sem)}, "{c.where}").'
    for c in taken_set
  ]

  if mode.startswith('plan'):
    planning_facts, planning_ctrl_args = _generate_planning_input(inputs)
    input_facts.extend(planning_facts)
    ctrl_args.extend(planning_ctrl_args)

  ctrl = clingo.Control(ctrl_args)
  ctrl.load(main_lp)
  ctrl.load(kb_lp)
  ctrl.add("input", [], "\n".join(input_facts))

  ground_start = time.perf_counter()
  ctrl.ground(to_ground, context=ClingoContext())
  ground_elapsed = time.perf_counter() - ground_start

  ## updated in on_model callback
  checked = {}
  schedule = {}
  min_cost = None
  model_count = 0
  
  def on_model(model):    ## invoked for every model found
    nonlocal checked, schedule, min_cost, model_count
    model_count += 1
    ## reset checked when there are multiple models (in planning mode)
    checked = {item: [False, []] for item in items}  ## initialize all items to not passed
    planned_courses = {}
    schedule = defaultdict(list)
    if model.cost is not None:
      cost = tuple(model.cost)
      if min_cost is None or cost < min_cost:
        min_cost = cost

    for sym in model.symbols(atoms=True):     ## collect check for each requirement
      if sym.name == "degree":
        checked['degree'][0] = True
      elif sym.name == "req":
        item = str(sym.arguments[0])
        checked[item][0] = True
      elif sym.name == "plan":             ## planning mode
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
          print(f'timeout {timeout} reached.')
          timed_out = True
          handle.cancel()
      except KeyboardInterrupt:
        print('interrupted by user')
        handle.cancel()
      finally:
        handle.wait()
 
  ## sort witness, same as test in python
  checked = {item: (check, sorted(wits)) for item, (check, wits) in checked.items()}

  ## sort courses in each semester
  for sem in schedule:
    schedule[sem].sort()

  stats = _collect_clingo_stats(ctrl, timed_out, model_count, min_cost)
  if ground_only:
    stats['summary']['times']['total'] = ground_elapsed
    stats['summary']['times']['solve'] = 0.0

  # if timed_out and checked:
  #   stats['partial_reqs_sat']   = [k for k, (ok, _) in checked.items() if ok]
  #   stats['partial_reqs_unsat'] = [k for k, (ok, _) in checked.items() if not ok]

  return checked, schedule, stats

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Run the Degree Checker and Planner.")
  parser.add_argument(
    '-m', '--mode',
    default='check',
    help="Run mode."
  )
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
          
  pprint(stats)