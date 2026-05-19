from collections import defaultdict
from dataclasses import dataclass, field
import clingo
import argparse
from pprint import pprint
from course_kb.course_kb import *
from clingo_version.configs import MAIN_LP, KB_LP

## Constants for planning
MIN_SEM = (2024, 2)           ## default minimum semester (that gets mapped to 1 in clingo)
NUM_SEMS = 16                 ## default total sems
NUM_CREDITS_PER_SEM = 18      ## default max credits per sem for planning
STUDENT_FACTS = """standing("U1"). standing("U2"). standing("U3"). standing("U4"). major("CSE"). permission."""

class ClingoContext:
  ## can't have python code in the clingo file if using python api.
  ## the #script (python) in the clingo file is commented out, and we move the functions here.
  def upper_division(self, course_id):
    return clingo.Number(int(course_id.string[4:]) >= 300)

  def course_prog(self, course_id):
    return clingo.String(course_id.string[:3])
  
  def course_level(self, course_id):
    ## for heuristic. 1 for 100-level, 2 for 200-level, etc.
    return clingo.Number(int(course_id.string[4]))

@dataclass
class ClingoResult:
  ## output that includes witness and clingo stats
  checked: dict[str, tuple]                  ## item -> (bool, witness list)
  schedule: dict[int, list[str]]             ## semester -> list of course ids
  stats: dict = field(default_factory=dict)  ## collected statistics from clingo
  plan_credits: dict = field(default_factory=dict)

  ## backwards compatibility, allow unpacking: checked, schedule, stats = run_clingo(...)
  def __iter__(self):
    yield self.checked
    yield self.schedule
    yield self.stats


## building inputs
def _generate_planning_input(inputs: dict) -> tuple[list[str], list[str]]:
  input_dict = {  # defining defaults
      'taken_set': set(),
      'must_include': set(),
      'must_exclude': set(),
      'min_sem': MIN_SEM,
      'max_sem': MIN_SEM,
      'num_sems': NUM_SEMS,
      'course_offered_terms': COURSE_OFFERED_TERMS,
      'student_facts': STUDENT_FACTS,
  }
  input_dict.update(inputs)

  start_sem = sem_to_int(input_dict['max_sem'], input_dict['min_sem']) + 1
  finish_sem = start_sem + input_dict['num_sems'] - 1

  planning_facts = (
    [f'taken_id("{c.id}").' for c in input_dict['taken_set']] +
    [f'include("{cid}").' for cid in input_dict['must_include']] +
    [f'exclude("{cid}").' for cid in input_dict['must_exclude']] +
    [f'offered("{cid}", {sem}).'
     for cid, terms in input_dict['course_offered_terms'].items()
     for sem in range(start_sem, finish_sem + 1)
     if rel_sem_to_term(sem, input_dict['min_sem']) in terms] +
    [input_dict['student_facts']]
  )

  planning_ctrl_args = [
    f"-c start_sem={start_sem}",
    f"-c finish_sem={finish_sem}",
    f"-c sem_max_credits={NUM_CREDITS_PER_SEM}",
  ]

  return planning_facts, planning_ctrl_args

def build_inputs(mode: str, heuristics=None, **inputs):
  assert mode in {'check', 'plan'}, f"Invalid mode: {mode}"

  taken_set = inputs.get('taken_set', set())
  min_sem = min(c.when for c in taken_set) if taken_set else MIN_SEM
  inputs['min_sem'] = min_sem  # Ensure planning generator uses the correct min_sem
  
  input_facts = [
    f'taken("{c.id}", {c.credits}, "{c.grade}", {sem_to_int(c.when, min_sem)}, "{c.where}").'
    for c in taken_set
  ]
  
  ctrl_args = ["0", "-Wno-atom-undefined", "--stats=2"]
  if heuristics:
    ctrl_args.append("--heuristic=Domain")
  
  if mode == 'plan':
    planning_facts, planning_ctrl_args = _generate_planning_input(inputs)
    input_facts.extend(planning_facts)
    ctrl_args.extend(planning_ctrl_args)
  
  return "\n".join(input_facts), ctrl_args
class ModelParser:
  ## parses clingo model to extract witness
  ITEMS = (
    'intro', 'adv', 'elect', 'calc', 'alg', 'sta',
    'sci', 'ethics', 'writing', 'credits_at_SB', 'degree'
  )

  def __init__(self, **input):
    self.min_sem = input.get('min_sem', MIN_SEM)
    self.checked = {item: [False, []] for item in self.ITEMS}
    self.schedule = defaultdict(list)
    self.plan_credits = {}

  def on_model(self, model):
    self.checked = {item: [False, []] for item in self.ITEMS}
    self.schedule.clear()
    self.plan_credits.clear()
    planned_courses = {}
    
    for sym in model.symbols(atoms=True):     ## collect check for each requirement
      if sym.name == "degree":
        self.checked['degree'][0] = True
      elif sym.name == "req":
        item = str(sym.arguments[0])
        self.checked[item][0] = True
      elif sym.name == "plan":             ## planning mode
        cid_sym, semester_sym = sym.arguments
        cid = str(cid_sym).strip('"')
        sem = int_to_sem(semester_sym.number, self.min_sem)
        planned_courses[cid] = sem            ## record planned semester
        self.schedule[sem].append(cid)             ## add course to schedule
      elif sym.name == "plan_credits":
        cid_sym, credits_sym = sym.arguments
        cid = str(cid_sym).strip('"')
        credits = credits_sym.number
        self.plan_credits[cid] = credits

    for sym in model.symbols(atoms=True):     ## collect witness
      if sym.name == "wit":
        item, val = str(sym.arguments[0]), sym.arguments[1]
        if item == "credits_at_SB" and val.type == clingo.SymbolType.Function and val.name in {"items123", "items23"}:
          self.checked[item][1].append(f"{val.name} = {val.arguments[0].number}")
          continue
        course = str(val).strip('"')
        self.checked[item][1].append(course)
    
    ## add extra strings if check for item is false
    if not self.checked['elect'][0]:
      self.checked['elect'][1].append('need 4 total')
    if not self.checked['sci'][0]:
      self.checked['sci'][1].append('need a lec/lab combo and more, with >=9 credits and >=2.0 GPA')
  
  def finalize(self, stats: dict) -> ClingoResult:
    checked = {item: (check, sorted(wits)) for item, (check, wits) in self.checked.items()}
    schedule = {sem: sorted(cids) for sem, cids in self.schedule.items()}
    return ClingoResult(
      checked=checked,
      schedule=schedule,
      stats=stats,
      plan_credits=self.plan_credits,
    )

## main interface to run clingo
def run(
    lp_files: list[str],    ## paths to lp files
    program_str: str,       ## additional program string to add
    ground_targets,         ## e.g. [('base', []), ('check', [])] or [('base', []), ('plan', [])]
    ctrl_args: list[str] = None,  ## extra control arguments, including constants (start_sem, finish_sem, max_credits).
    on_model = None,        ## callback for model found
    timeout: int = 10 * 60,
):
  ctrl = clingo.Control(ctrl_args)

  for f in lp_files:
    ctrl.load(f)
  
  ctrl.add("base", [], program_str)

  ctrl.ground(ground_targets, context=ClingoContext())

  timed_out = False
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

    ## collect stats
    lp       = ctrl.statistics.get('problem', {}).get('lp', {})
    solvers  = ctrl.statistics.get('solving', {}).get('solvers', {})
    times    = ctrl.statistics.get('summary', {}).get('times', {})
    models   = ctrl.statistics.get('summary', {}).get('models', {})
    min_cost = ctrl.statistics.get('summary', {}).get('costs', None)
    total_t  = float(times.get('total', 0))
    solve_t  = float(times.get('solve', 0))
    model_count = int(models.get('enumerated', 0))
    return {
      'problem': {'lp': {'atoms': int(lp.get('atoms', 0)), 'rules': int(lp.get('rules', 0)),
                        'bodies': int(lp.get('bodies', 0)), 'eqs': int(lp.get('eqs', 0))}},
      'solving': {'solvers': {
                  'choices':        int(solvers.get('choices', 0)),
                  'domain_choices': int(solvers.get('extra', {}).get('domain_choices', None)),
                  'conflicts':      int(solvers.get('conflicts', 0)),
                  'restarts':       int(solvers.get('restarts', 0))}},
      'summary': {'times': {'total': total_t, 'solve': solve_t}},
      'timed_out': timed_out,
      'model_count': model_count,
      'min_cost': min_cost,
    }

def run_clingo(
    mode,               ## one of 'check' or 'plan'
    main_lp=MAIN_LP,    ## path to main lp file
    kb_lp=KB_LP,        ## path to kb lp file
    timeout=10 * 60,    ## timeout in seconds
    heuristics:str = None,
    **inputs            ## taken_set, must_include, must_exclude, etc.
    ) -> ClingoResult:
  input_facts, ctrl_args = build_inputs(mode, heuristics, **inputs)
  
  assert mode in {'check', 'plan'}, f"Invalid mode: {mode}"
  lp_files = [kb_lp, main_lp] if mode == 'plan' else [kb_lp, main_lp]

  ground_targets = [('base', []), (mode, [])]
  model_parser = ModelParser(**inputs)
  
  clingo_stats = run(
    lp_files=lp_files,
    program_str=input_facts+heuristics if heuristics else input_facts,
    ground_targets=ground_targets,
    ctrl_args=ctrl_args,
    on_model=model_parser.on_model,
    timeout=timeout,
  )

  return model_parser.finalize(clingo_stats)

def run_planner_benchmark(
    program_lp,
    timeout=10 * 60,
    heuristics:str = None,
    **inputs
    ) -> ClingoResult:
  input_facts, ctrl_args = build_inputs('plan', heuristics, **inputs)
  
  model_parser = ModelParser(**inputs)
  
  clingo_stats = run(
    lp_files=[program_lp],
    program_str=input_facts+heuristics if heuristics else input_facts,
    ground_targets=[('base', [])],
    ctrl_args=ctrl_args,
    on_model=model_parser.on_model,
    timeout=timeout,
  )

  return model_parser.finalize(clingo_stats)

HEU_SCI = """
default_sci("CHE 131"; "CHE 133").
#heuristic plan_course(Id) : default_sci(Id), offered_in_range(Id). [100@1, true]
"""

HEU_ELECT = """
default_elect("CSE 307"; "CSE 311"; "CSE 351"; "CSE 488").
#heuristic plan_course(Id) : default_elect(Id), offered_in_range(Id). [100@1, true]
"""

def build_heuristics_from_witness(checked: dict, taken_set=None) -> str:
  heuristics = []

  if not checked.get('sci', [True])[0]:
    heuristics.append(HEU_SCI)

  if not checked.get('elect', [True])[0]:
    heuristics.append(HEU_ELECT)

  return "\n".join(heuristics)

def run_planner_with_heuristics(
    program_lp,
    timeout=10*60,
    **inputs
    ) -> ClingoResult:
  # first run checker to get witness for heuristics
  checked, _schedule, _stats = run_clingo(mode='check', **inputs)
  heuristics = build_heuristics_from_witness(checked, taken_set=inputs.get('taken_set'))
  
  print(f"Built heuristics from witness:\n{heuristics}\n")
  return run_planner_benchmark(
    program_lp=program_lp,
    timeout=timeout,
    heuristics=heuristics if heuristics else None,
    **inputs,
  )

def run_planner_incremental(mode='plan', main_lp=MAIN_LP, kb_lp=KB_LP, timeout=10 * 60, **inputs):
  max_allowed_sems = inputs.get('num_sems', NUM_SEMS)

  ## limit the number of sems in the plan by iteratively increasing it until we find a solution.
  for t in range(1, max_allowed_sems + 1):
    iter_inputs = dict(inputs)
    iter_inputs['num_sems'] = t
    checked, schedule, stats = run_clingo(
      mode=mode, main_lp=main_lp, kb_lp=kb_lp, timeout=timeout, **iter_inputs,
    )
    if stats.get('model_count', 0) > 0:
      return checked, schedule, stats

  return None, None, None

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