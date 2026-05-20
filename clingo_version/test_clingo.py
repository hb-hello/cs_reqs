import inspect
from pprint import pprint
from run_clingo import run_clingo
import python_version.tests as tests                ## tests.py in cs_reqs

PLANNING_MODE = 'plan'
CHECKING_MODE = 'check'

def run_testcase(test_func, mode, checks_witness=False):
  case = test_func()
  if len(case) == 2:
    taken, expected_checked = case
    extra_inputs = {}
  elif len(case) == 3:
    taken, expected_checked, extra_inputs = case
  else:
    raise ValueError('test case must return (taken, expected_checked) or (taken, expected_checked, extra_inputs)')

  print('---- taken_ids: ', sorted({c.id for c in taken}))
  print('---- other inputs: ', extra_inputs)

  clingo_checked, schedule, stats = run_clingo(
    mode=mode, 
    taken_set=taken,
    **extra_inputs,
  )

  if checks_witness:
    for req, (expected_check, expected_wits) in expected_checked.items():
      if req == 'credits_at_SB': continue
      if req not in clingo_checked:
        assert False, f"Clingo is missing requirement: {req}"
      clingo_check = clingo_checked[req][0]
      clingo_wits = clingo_checked[req][1]
      assert expected_check == clingo_check, f"Expected {expected_check} for {req}, but got {clingo_check}"
      assert set(expected_wits) <= set(clingo_wits), f"Expected witness {expected_wits} for {req}, but got {clingo_wits}"

  pprint(clingo_checked)

  if mode == 'plan':
    print('---- planned schedule:')
    for sem in sorted(schedule):
      print(f"Semester {sem}: {schedule[sem]}")

  pprint(stats)

  return clingo_checked, schedule, stats

def test_checking(test_func):
  return run_testcase(test_func, mode=CHECKING_MODE, checks_witness=True)

def test_planning(test_func):
  return run_testcase(test_func, mode=PLANNING_MODE, checks_witness=False)

def run_python_checking_tests():
  for (name, func) in inspect.getmembers(tests, inspect.isfunction):
    if name.startswith('test_'):
      print('--------', name, 'started:')
      test_checking(func)
      print('--------', name, 'passed !!!')

def test_plan_empty():   ## remove all courses, should plan everything
  return set(), None

def test_plan_must_take_phy():
  taken = set()  ## no courses taken
  must_include = {'PHY 251', 'PHY 252', 'PHY 126', 'PHY 133'}
  return taken, None, {'must_include': must_include}

if __name__ == "__main__":
  run_python_checking_tests()
  # test_planning(test_plan_must_take_phy)