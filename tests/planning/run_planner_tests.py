import inspect
import io
import importlib
import re
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]


def collect_tests():
    modules = []
    for path in sorted(Path(__file__).parent.glob('planner_test_cases*.py')):
        module_name = f"tests.planning.{path.stem}"
        modules.append(importlib.import_module(module_name))

    tests = []
    for module in modules:
        module_tests = [
            (f"{module.__name__.split('.')[-1]}.{name}", func)
            for name, func in inspect.getmembers(module, inspect.isfunction)
            if name.startswith('test_plan_')
        ]
        tests.extend(sorted(module_tests))
    return tests


ALL_TESTS = collect_tests()


def normalize_witness(value):
    return re.sub(r" \(sem \d+\)$", "", value)


def normalize_checked(checked):
    out = {}
    for req, (ok, witness) in checked.items():
        out[req] = (ok, sorted({normalize_witness(w) for w in witness}))
    return out

def to_checker_taken(history, planned_courses, planned_credits=None):
    from ortools_version.planner import catalog
    from python_version.cs_reqs_2024 import Taken

    planned_credits = planned_credits or {}

    taken = set()
    for h in history:
        taken.add(Taken(h.id, h.credits, h.grade, h.when, h.where))
    for cid, when in planned_courses.items():
        credits = planned_credits.get(cid, catalog[cid].credits)
        taken.add(Taken(cid, credits, 'C', when, 'SB'))
    return taken

def validate_with_checker(history, planned_courses, planned_credits=None):
    import python_version.cs_reqs_2024 as checker
    from python_version.cs_reqs_2024 import degree_reqs

    checker.w = {}
    with redirect_stdout(io.StringIO()):
        result = degree_reqs(to_checker_taken(history, planned_courses, planned_credits=planned_credits))
    return result, result['degree'][0]


def must_include_missing(schedule_courses, must_include):
    return sorted(set(must_include) - set(schedule_courses))


def must_exclude_added(schedule_courses, must_exclude):
    return sorted(set(must_exclude) & set(schedule_courses))


def run_ortools(history, attrs=None):
    from ortools_version.course_catalog import Major, Standing
    from ortools_version.planner import plan_courses

    attrs = attrs or {}
    must_include = set(attrs.get('must_include', set()))
    must_exclude = set(attrs.get('must_exclude', set()))
    start_sem = min((h.when for h in history), default=(1, 1))
    # with redirect_stdout(io.StringIO()):
    checked, schedule, _ = plan_courses(
        history,
        Major('CSE'),
        Standing('U4'),
        starting_semester=start_sem,
        must_include=must_include,
        must_exclude=must_exclude,
    )
    if checked is None:
        return {'degree': (False, [])}, set(), {}, {}, False, ['INFEASIBLE']

    # OR-Tools credits are the catalog credits for planned courses.
    from ortools_version.planner import catalog
    plan_credits = {cid: catalog[cid].credits for cid in schedule}

    checker_result, checker_ok = validate_with_checker(history, schedule, planned_credits=plan_credits)
    failed = [k for k, v in checker_result.items() if not v[0]]
    return normalize_checked(checked), set(schedule), schedule, plan_credits, checker_ok, failed


def run_clingo_backend(history, attrs=None):
    from clingo_version.run_clingo import run_clingo
    from python_version.cs_reqs_2024 import Taken

    attrs = attrs or {}
    must_include = set(attrs.get('must_include', set()))
    must_exclude = set(attrs.get('must_exclude', set()))
    ## TODO: there's more

    taken = {
        Taken(h.id, h.credits, h.grade, h.when, h.where)
        for h in history
    }
    with redirect_stdout(io.StringIO()):
        result = run_clingo(
            taken_set=taken,
            mode='plan',
            main_lp=str(ROOT / 'clingo_version' / 'cse_req_clingo.lp'),
            kb_lp=str(ROOT / 'course_kb' / 'kb_complete.lp'),
            must_include=must_include,
            must_exclude=must_exclude,
        )

    checked, schedule, _ = result
    plan_credits = dict(result.plan_credits or {})

    planned_courses = {}
    for sem, courses in schedule.items():
        for cid in courses:
            planned_courses[cid] = sem

    missing_credits = sorted(set(planned_courses) - set(plan_credits))
    if missing_credits:
        raise ValueError(
            f"clingo backend did not return plan_credits for planned courses: {missing_credits}"
        )

    checker_result, checker_ok = validate_with_checker(history, planned_courses, planned_credits=plan_credits)
    failed = [k for k, v in checker_result.items() if not v[0]]
    schedule_courses = {cid for courses in schedule.values() for cid in courses}
    return normalize_checked(checked), schedule_courses, planned_courses, plan_credits, checker_ok, failed


def run_one(system, backend):
    passed = []
    failed = []
    skipped = []

    print(f"\nRunning tests in {system}...")
    # with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
    for name, func in ALL_TESTS:
        try:
            case = func()
            if len(case) == 2:
                history, validate = case
                attrs = {}
            elif len(case) == 3:
                history, validate, attrs = case
            else:
                raise ValueError('test case must return (history, validate) or (history, validate, attrs)')

            approaches = set(attrs.get('approaches', []))
            if approaches and system not in approaches:
                skipped.append(name)
                continue

            backend_out = backend(history, attrs)
            if len(backend_out) == 5:
                checked, schedule_courses, schedule_by_course, checker_ok, checker_failed = backend_out
                plan_credits = {}
            elif len(backend_out) == 6:
                checked, schedule_courses, schedule_by_course, plan_credits, checker_ok, checker_failed = backend_out
            else:
                raise ValueError(f"backend must return 5 or 6 values, got {len(backend_out)}")

            print(name)
            if not checker_ok and not attrs.get('skip_checker_validation', False):
                failed.append((name, f"python checker rejected combined plan on: {checker_failed}"))
                continue

            missing = must_include_missing(schedule_courses, attrs.get('must_include', set()))
            if missing:
                failed.append((name, f"missing must_include in planned schedule: {missing}"))
                continue

            added_excludes = must_exclude_added(schedule_courses, attrs.get('must_exclude', set()))
            if added_excludes:
                failed.append((name, f"found must_exclude in planned schedule: {added_excludes}"))
                continue

            sig = inspect.signature(validate)
            positional = [
                p for p in sig.parameters.values()
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values())

            if has_varargs or len(positional) >= 4:
                validate(checked, schedule_courses, schedule_by_course, plan_credits)
            else:
                validate(checked, schedule_courses, schedule_by_course)

            passed.append(name)
        except Exception as e:
            failed.append((name, str(e)))

    print(
        f"\n-> {system}: passed {len(passed)} test cases, "
        f"failed {len(failed)} test cases, skipped {len(skipped)} test cases: {skipped}"
    )
    if failed:
        for name, error in failed:
            print(f"   FAIL: {name}")
            print(f"      - {error}")
        print(schedule_courses)


def run_all():
    run_one('ortools_version', run_ortools)
    run_one('clingo_version', run_clingo_backend)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        system = sys.argv[1]
        if system == 'ortools': run_one('ortools_version', run_ortools)
        elif system == 'clingo': run_one('clingo_version', run_clingo_backend)
        else: print(f'unknown system: {system}, expected "ortools" or "clingo"')
    else:
        run_all()
