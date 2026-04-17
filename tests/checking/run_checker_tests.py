import inspect
import io
import importlib
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from pprint import pformat
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# ── adapters ─────────────────────────────────────────────────────────────────

def check_python(taken):
    import python_version.cs_reqs_2024 as checker
    from python_version.cs_reqs_2024 import degree_reqs
    checker.w = {}  # reset module-level witness state between calls
    return degree_reqs(taken)

def check_ortools(taken):
    from ortools_version.planner import plan_courses, best_attempts
    from ortools_version.course_catalog import Major, Standing, Taken
    history = best_attempts([Taken(t.id, t.credits, t.grade, t.when, t.where) for t in taken])
    checked, _, _ = plan_courses(history, Major("CSE"), Standing("U4"), check=True)
    return checked

def check_prolog(taken):
    from prolog_version.run_prolog import run_swi
    return run_swi(taken)

def check_clingo(taken):
    from clingo_version.run_clingo import run_clingo
    checked, _, _ = run_clingo(
        taken_set=taken,
        mode='check',
        main_lp='clingo_version/cse_req_clingo.lp',
        kb_lp='course_kb/kb_complete.lp',
    )
    return checked

# ── runner ───────────────────────────────────────────────────────────────────

def collect_tests():
    modules = []
    for path in sorted(Path(__file__).parent.glob('checker_test_cases_*.py')):
        module_name = f"tests.checking.{path.stem}"
        print(module_name)
        modules.append(importlib.import_module(module_name))

    tests = []
    for module in modules:
        module_tests = [
            (f"{module.__name__.split('.')[-1]}.{name}", func)
            for name, func in inspect.getmembers(module, inspect.isfunction)
            if name.startswith('test_')
        ]
        tests.extend(sorted(module_tests))
    return tests


ALL_TESTS = collect_tests()

APPROACHES = [
    ('python_version',  check_python),
    # ('ortools_version', check_ortools),
    # ('clingo_version',  check_clingo),
    ('prolog_version',  check_prolog),
]

def run_one(label, check_fn):
    passed, failed = [], []
    errors = []

    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        for name, test_fn in ALL_TESTS:
            try:
                taken, expected = test_fn()
                result = check_fn(taken)
            except Exception as e:
                errors.append((name, e))
                failed.append((name, {}))
                continue

            diff = {
                req: {'expected': (exp_bool, exp_wits), 'got': result.get(req)}
                for req, (exp_bool, exp_wits) in expected.items()
                if req not in result
                or result[req][0] != exp_bool
                or (exp_bool and exp_wits and not (set(result[req][1]) <= set(exp_wits)))
            }
            if diff:
                failed.append((name, diff))
            else:
                passed.append(name)

    print(f"\n-> {label} : passed {len(passed)} test cases, failed {len(failed)} test cases")
    for name, diff in failed:
        err = next((e for n, e in errors if n == name), None)
        print(f"   FAIL: {name}" + (f" ({err})" if err else ""))
        if diff:
            print(pformat(diff, indent=6, sort_dicts=True))

def run_all():
    for label, check_fn in APPROACHES:
        run_one(label, check_fn)

if __name__ == '__main__':
    run_all()
    # run_one('ortools_version', check_ortools)
