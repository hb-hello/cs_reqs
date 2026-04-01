import inspect
from pprint import pprint
from run_clingo import DEFAULT_KB_LP, DEFAULT_MAIN_LP, print_clingo_stats, run_clingo
import tests                ## tests.py in cs_reqs

def run_case(test_func, mode='check', checks_witness=False):
  taken, expected_checked = test_func()
  print('---- taken_ids: ', sorted({c.id for c in taken}))
  clingo_checked, schedule, stats = run_clingo(
    taken_set=taken,
    mode=mode, 
    main_lp=DEFAULT_MAIN_LP, 
    kb_lp=DEFAULT_KB_LP
  )

  if checks_witness:
    for req, (expected_check, expected_wits) in expected_checked.items():
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

  print_clingo_stats(stats)

  return clingo_checked, schedule, stats

def testing(test_func):
  return run_case(test_func, mode='check', checks_witness=True)

def test_clingo_planning(test_func):
  return run_case(test_func, mode='plan', checks_witness=False)

def run_tests():
  for (name, func) in inspect.getmembers(tests, inspect.isfunction):
    if name.startswith('test_'):
      print('--------', name, 'started:')
      testing(func)
      print('--------', name, 'passed !!!')

def test_plan_01():
  ## test planning. remove one mandatory course, and the planner should add it back.
  taken, checked = tests.test_04()                      ## degree req is True in test04.
  
  taken -= {c for c in taken if c.id in {'CSE 214'}}    ## remove one mandatory course

  return taken, checked

def test_plan_02():   ## remove more courses from prev
  taken, _ = test_plan_01()

  taken -= {c for c in taken if c.id in {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220'}}

  return taken, None

def test_plan_03():   ## remove more courses from prev
  taken, _ = test_plan_02()

  taken -= {c for c in taken if c.id in {'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',}}

  return taken, None

def test_plan_04():   ## remove math courses
  taken, _ = test_plan_03()

  taken -= {c for c in taken if c.id in {'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310'}}

  return taken, None

def test_plan_05():   ## remove science courses
  taken, _ = test_plan_04()

  taken -= {c for c in taken if c.id in {'PHY 131', 'PHY 133', 'AST 203'}}

  return taken, None

def test_plan_06():   ## remove all courses, should plan everything
  taken, _ = test_plan_05()

  taken.clear()

  return taken, None

if __name__ == "__main__":
  # run_tests()
  
  # # print("\n\n======== testing planning mode ========")
  test_clingo_planning(test_plan_01)  ## expected: planned CSE 214 in semester 1
  test_clingo_planning(test_plan_03)
  # test_clingo_planning(test_plan_02)
  # test_clingo_planning(test_plan_04)
  # test_clingo_planning(test_plan_05)
  # test_clingo_planning(test_plan_06) 