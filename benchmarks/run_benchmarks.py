import io
import json
import os
import random
import select
import signal
import statistics
import time
import sys
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent
if str(_THIS_DIR) in sys.path:
    sys.path.remove(str(_THIS_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

TIMEOUT = 300  # seconds per run
PLANNING_CASE_SIZES = (13, 17, 21, 24)

from clingo_version.configs import KB_LP, MAIN_LP
import python_version.cs_reqs_2024 as py_checker
from clingo_version.run_clingo import run_clingo
from ortools_version.course_catalog import Taken, Major, Standing, COURSE_OFFERED_TERMS, CATALOG, get_courses
from ortools_version.planner import best_attempts, plan_courses
from prolog_version.run_prolog import run_prolog
from python_version.cs_reqs_2024 import Taken, degree_reqs
from tests.checking.checker_test_cases_a import test_0, test_01
from tests.planning.planner_test_cases import FULL

import python_version.cs_reqs_2024 as reqs

INTRO = set().union(*(getattr(reqs, name) for name in reqs.intro))
ADV = set().union(*(getattr(reqs, name) for name in reqs.adv))
CALC = set().union(*(getattr(reqs, name) for name in reqs.calc))
STA = set().union(*(getattr(reqs, name) for name in reqs.sta))
ALG = set().union(*(getattr(reqs, name) for name in reqs.alg))
SCI_COMB = set().union(*reqs.sci_combs)
SCI_MORE = reqs.sci_more
ELECT = {'CSE 337', 'CSE 327', 'CSE 307', 'CSE 371', 'CSE 333', 'CSE 392', 'CSE 381', 
         'CSE 304', 'CSE 487', 'CSE 352', 'CSE 328', 'CSE 377', 'CSE 334', 'CSE 357', 
         'CSE 380', 'CSE 356', 'CSE 370', 'CSE 355', 'CSE 391', 'CSE 353', 'CSE 362', 
         'CSE 363', 'CSE 305', 'CSE 332', 'CSE 390', 'CSE 488', 'CSE 351', 'CSE 354', 
         'CSE 336', 'CSE 364', 'CSE 376', 'CSE 393', 'CSE 360', 'CSE 366', 'CSE 311', 
         'CSE 496', 'CSE 306', 'CSE 378', 'CSE 323', 'CSE 394', 'CSE 331', 'CSE 361', 'CSE 325'}

## replace previous cases (empty, small, large)
def planning_cases_inc_taken():
    return {
        'only_intro_done': FULL & INTRO,  # only intro req satisfied
        'only_sci_done': FULL & (SCI_COMB | SCI_MORE),
        'only_electives_done': FULL & ELECT,
        'all_done_except_sci_ethics': FULL & (INTRO | ADV | ELECT | CALC | STA | ALG),  # planning for sci courses
        'all_done_except_ethics': FULL & (INTRO | ADV | ELECT | CALC | STA | ALG | SCI_COMB | SCI_MORE),
    }

## planning with different categories of taken input.
##   different categories may have different impacts on pruning the search space
##   e.g. planning for sci courses might be harder than planning for cs courses.
def planning_cases_category():      ### todo: move to planner_tests.py?
    return {
        'intro_only': FULL & INTRO,
        'advanced_only': FULL & ADV,
        'math_only': FULL & (CALC | STA | ALG),
        'elect_only': FULL & ELECT,
        'science_only': FULL & (SCI_COMB | SCI_MORE),
    }

# def planning_cases_prereq_impact():
#     return {
#         'with_cse_373': FULL,
#         'without_cse_373': FULL - {'CSE 373'},
#         'without_cse_352': FULL - {'CSE 352'},
#         'without_cse_355': FULL - {'CSE 355'},
#         'without_cse_310': FULL - {'CSE 310'},
#     }

COURSE_WISE_PREREQS_ANALYSIS = ('', 'CSE 373', 'CSE 352', 'CSE 355', 'CSE 310')

def run_once(func, extract_metrics=None):
    # fork so SIGKILL can terminate blocking C extensions (SIGALRM can't)
    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        os.close(r_fd)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                t0 = time.perf_counter()
                result = func()
                elapsed = time.perf_counter() - t0
            metrics = extract_metrics(buf.getvalue(), result) if extract_metrics else {}
            data = json.dumps({'elapsed': elapsed, 'metrics': metrics}).encode()
            os.write(w_fd, data)
        except Exception:
            import traceback
            err = json.dumps({'error': traceback.format_exc()}).encode()
            os.write(w_fd, err)
        finally:
            os.close(w_fd)
            os._exit(0)
    else:  # parent
        os.close(w_fd)
        ready, _, _ = select.select([r_fd], [], [], TIMEOUT)
        if not ready:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            os.close(r_fd)
            return None
        data = b''
        while chunk := os.read(r_fd, 4096):
            data += chunk
        os.close(r_fd)
        os.waitpid(pid, 0)
        try:
            return json.loads(data)
        except Exception:
            return None


def run_once_direct(func, extract_metrics=None):
    # no fork — used when the callee manages its own timeout (clingo async solve)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            t0 = time.perf_counter()
            result = func()
            elapsed = time.perf_counter() - t0
        metrics = extract_metrics(buf.getvalue(), result) if extract_metrics else {}
        return {'elapsed': elapsed, 'metrics': metrics}
    except Exception:
        import traceback
        return {'error': traceback.format_exc()}


def timed_runs(func, n, extract_metrics=None, label='', direct=False, timing_metric_key=None):
    if label:
        print(f'  {label} ', end='', flush=True)
    times = []
    numeric = {}   # key -> [values]  aggregated as min/max/mean
    lists   = {}   # key -> last seen list  (e.g. partial_reqs_sat)
    scalars = {}   # key -> last seen scalar metadata (e.g. test_case_name)
    any_timed_out = False

    for _ in range(n):
        run = run_once_direct(func, extract_metrics) if direct else run_once(func, extract_metrics)
        if run is None:
            print('T', end='', flush=True)
            continue
        if 'error' in run:
            print(f'\n  ERROR: {run["error"]}', flush=True)
            continue
        metrics = run.get('metrics', {})
        run_time = run['elapsed']
        if timing_metric_key and isinstance(metrics.get(timing_metric_key), (int, float)):
            run_time = float(metrics[timing_metric_key])
        times.append(run_time)

        for k, v in metrics.items():
            if isinstance(v, bool):
                if v: any_timed_out = True
            elif isinstance(v, list):
                lists[k] = v
            elif isinstance(v, (int, float)):
                numeric.setdefault(k, []).append(v)
            elif v is not None:
                scalars[k] = v
        print('.', end='', flush=True)

    if not times:
        print('  all runs killed (SIGKILL)')
        return {'runs': 0, 'timed_out': True}
    out = {'runs': len(times), 'min_s': min(times), 'max_s': max(times), 'mean_s': statistics.mean(times)}
    for k, vals in numeric.items():
        out[k] = {'min': min(vals), 'max': max(vals), 'mean': statistics.mean(vals)}
    out['timed_out'] = any_timed_out
    out.update(lists)
    out.update(scalars)
    print(f'  mean={out["mean_s"]:.3f}s' + (' [TIMEOUT]' if any_timed_out else ''))
    return out


def extract_course_ids(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if hasattr(value, 'id') and isinstance(value.id, str):
        return [value.id]
    if isinstance(value, dict):
        out = []
        for k in value.keys():
            out.extend(extract_course_ids(k))
        for v in value.values():
            out.extend(extract_course_ids(v))
        return out
    if isinstance(value, (list, tuple, set)):
        out = []
        for v in value:
            out.extend(extract_course_ids(v))
        return out
    return []


def ortools_metrics(_stdout, result, input_course_ids=None, input_count=None, case_name=None):
    checked, planned, m = result
    input_ids = set(input_course_ids or ())
    planned_all = sorted(set(extract_course_ids(planned)))
    planned_new = sorted(set(planned_all) - input_ids)
    out = {k: m.get(k) for k in ('booleans', 'branches', 'conflicts', 'wall_time_s', 'user_time_s', 'det_time')}
    out['planned_new_courses'] = len(planned)
    out['planned_witness'] = checked
    out['planned_all_ids'] = planned_all
    out['planned_new_ids'] = planned_new
    if input_ids:
        out['input_ids'] = sorted(input_ids)
    if input_count is not None:
        out['input_courses'] = input_count
    if case_name is not None:
        out['test_case_name'] = case_name
    return out


def clingo_metrics(_stdout, result, input_course_ids=None, input_count=None, case_name=None):
    checked, schedule, stats = result
    lp      = stats.get('problem', {}).get('lp', {})
    solvers = stats.get('solving', {}).get('solvers', {})
    times   = stats.get('summary', {}).get('times', {})
    total_t = float(times.get('total', 0))
    solve_t = float(times.get('solve', 0))
    planned = {cid for courses in schedule.values() for cid in courses}
    input_ids = set(input_course_ids or ())
    planned_all = sorted(planned)
    planned_new = sorted(planned - input_ids)
    m = {
        'booleans':    int(lp.get('atoms', 0)) or None,
        'choices':     int(solvers.get('choices', 0)),
        'conflicts':   int(solvers.get('conflicts', 0)),
        'total_s':     round(total_t, 4),
        'grounding_s': round(total_t - solve_t, 4),
        'solving_s':   round(solve_t, 4),
        'planned_new_courses': len(planned - input_ids),
        'planned_witness': checked,
        'planned_all_ids': planned_all,
        'planned_new_ids': planned_new,
        'timed_out':   bool(stats.get('timed_out', False)),
    }
    if input_ids:
        m['input_ids'] = sorted(input_ids)
    if input_count is not None:
        m['input_courses'] = input_count
    if case_name is not None:
        m['test_case_name'] = case_name
    if stats.get('timed_out'):
        m['partial_reqs_sat']   = stats.get('partial_reqs_sat', [])
        m['partial_reqs_unsat'] = stats.get('partial_reqs_unsat', [])
    return m


def ortools_check_metrics(_stdout, result, input_count=None, case_name=None):
    checked, _planned, _m = result
    out = ortools_metrics(_stdout, result, input_count=input_count, case_name=case_name)
    out['reqs_sat'] = sum(1 for ok, _ in checked.values() if ok)
    out['reqs_unsat'] = sum(1 for ok, _ in checked.values() if not ok)
    out['check_passed'] = 1 if checked.get('degree', (False, []))[0] else 0
    return out


def clingo_check_metrics(_stdout, result, input_count=None, case_name=None):
    checked, _schedule, stats = result
    out = clingo_metrics(_stdout, result, input_count=input_count, case_name=case_name)
    out['reqs_sat'] = sum(1 for ok, _ in checked.values() if ok)
    out['reqs_unsat'] = sum(1 for ok, _ in checked.values() if not ok)
    out['check_passed'] = 1 if checked.get('degree', (False, []))[0] else 0
    if stats.get('timed_out'):
        out['partial_reqs_sat'] = stats.get('partial_reqs_sat', [])
        out['partial_reqs_unsat'] = stats.get('partial_reqs_unsat', [])
    return out


def prolog_metrics(_stdout, result):
    if not isinstance(result, dict):
        return {}
    out = {}
    if isinstance(result.get('prolog_eval_s'), (int, float)):
        out['prolog_eval_s'] = float(result['prolog_eval_s'])
    if 'ok' in result:
        out['check_passed'] = 1 if result['ok'] else 0
    if result.get('engine'):
        out['engine'] = result['engine']
    return out


def python_check(taken):
    py_checker.w = {}
    return degree_reqs(taken)


def to_history(ids):
    return [Taken(cid, CATALOG[cid].credits, 'A', (2024, 2), 'SB') for cid in sorted(ids)]


def to_taken(history):
    return {Taken(h.id, h.credits, h.grade, h.when, h.where) for h in history}


def planning_inputs():
    return {f'input_{n}_courses': to_history(sorted(FULL)[:n]) for n in PLANNING_CASE_SIZES}
    # return {name: to_history(taken_set) for name, taken_set in planning_cases_category().items()}


def load_latest_prereq_options():
    stats_dir = Path(__file__).resolve().parent / 'prereq_stats'
    candidates = sorted(stats_dir.glob('prereq_stats_*.json'))
    if not candidates:
        return {}

    latest = candidates[-1]
    with open(latest) as f:
        data = json.load(f)
    return {row['course_id']: row.get('options') for row in data.get('rows', [])}


def run_checking_benchmarks():
    passing_taken, _ = test_0()
    failing_taken, _ = test_01()

    results = {}
    for case, taken in [('pass', passing_taken), ('fail', failing_taken)]:
        print(f'\n  checking [{case}]')
        hist = best_attempts([Taken(t.id, t.credits, t.grade, t.when, t.where) for t in taken])
        input_count = len(taken)
        results[case] = {
            'python':  timed_runs(lambda t=taken: python_check(t), 5, label='python'),
            'prolog_swi':  timed_runs(
                lambda t=taken: run_prolog(t, 'swi', swi_with_witness=False, return_timing=True),
                5,
                extract_metrics=prolog_metrics,
                timing_metric_key='prolog_eval_s',
                label='prolog_swi'),
            'prolog_xsb':  timed_runs(
                lambda t=taken: run_prolog(t, 'xsb', return_timing=True),
                5,
                extract_metrics=prolog_metrics,
                timing_metric_key='prolog_eval_s',
                label='prolog_xsb'),
            'ortools': timed_runs(
                lambda h=hist: plan_courses(h, Major('CSE'), Standing('U4'), check=True),
                5,
                extract_metrics=lambda o, r, n=input_count, c=case: ortools_check_metrics(o, r, n, c),
                timing_metric_key='wall_time_s',
                label='ortools'),
            'clingo':  timed_runs(
                lambda t=taken: run_clingo(taken_set=t, mode='check', main_lp=MAIN_LP, kb_lp=KB_LP),
                5,
                extract_metrics=lambda o, r, n=input_count, c=case: clingo_check_metrics(o, r, n, c),
                timing_metric_key='total_s',
                label='clingo'),
        }
    return results


def run_planning_benchmarks():
    inputs = planning_inputs()
    results = {}
    for case_name, hist in inputs.items():
        print(f'\n  planning [{case_name}]')
        taken = to_taken(hist)
        input_count = len(hist)
        input_ids = {h.id for h in hist}
        start = min((h.when for h in hist), default=(2024, 3))
        results[case_name] = {
            'ortools': timed_runs(
                lambda h=hist, s=start: plan_courses(h, Major('CSE'), Standing('U4'), starting_semester=s),
                1,
                extract_metrics=lambda o, r, ids=input_ids, n=input_count, c=case_name: ortools_metrics(o, r, ids, n, c),
                timing_metric_key='wall_time_s',
                label='ortools'),
        }
        results[case_name]['clingo'] = timed_runs(
            lambda t=taken: run_clingo(taken_set=t, mode='plan', main_lp=MAIN_LP, kb_lp=KB_LP, timeout=TIMEOUT),
            1,
            extract_metrics=lambda o, r, ids=input_ids, n=input_count, c=case_name: clingo_metrics(o, r, ids, n, c),
            timing_metric_key='total_s',
            label='clingo',
            direct=True)
    return results


def run_course_wise_prereqs_analysis():
    prereq_options = load_latest_prereq_options()
    base_full = set(FULL)
    times = {'ortools': {}, 'clingo': {}}
    prereqs = {}
    normalized_offerings = dict(COURSE_OFFERED_TERMS)
    for target in COURSE_WISE_PREREQS_ANALYSIS:
        if target:
            normalized_offerings[target] = {2, 3, 4}

    for cid in COURSE_WISE_PREREQS_ANALYSIS:
        if cid == '':
            taken_ids = base_full - {'CSE 114'}
        else:
            prereq_courses = set(get_courses(CATALOG[cid].prereq)) if CATALOG.get(cid) and CATALOG[cid].prereq else set()
            taken_ids = base_full - (prereq_courses | {'CSE 114'})
        hist = to_history(taken_ids)
        taken = to_taken(hist)
        start = min((h.when for h in hist), default=(2024, 3))
        label = 'FULL' if cid == '' else f'FULL-{cid}'
        ort_timing = timed_runs(
            lambda h=hist, s=start, offerings=normalized_offerings: plan_courses(
                h, Major('CSE'), Standing('U4'), starting_semester=s, course_offered_terms=offerings),
            10, extract_metrics=ortools_metrics, timing_metric_key='wall_time_s', label=f'ortools {label}')
        clingo_timing = timed_runs(
            lambda t=taken: run_clingo(taken_set=t, mode='plan', main_lp=MAIN_LP, kb_lp=KB_LP, timeout=TIMEOUT),
            10, extract_metrics=clingo_metrics, timing_metric_key='total_s', label=f'clingo {label}', direct=True)
        times['ortools'][cid] = ort_timing.get('mean_s')
        times['clingo'][cid] = clingo_timing.get('mean_s')
        prereqs[cid] = 0 if cid == '' else prereq_options.get(cid)

    return {'prereqs': prereqs, 'time': times}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode not in {'check', 'plan', 'all'}:
        print("Usage: python benchmarks/run_benchmarks.py [check|plan|all]")
        return

    checking = None
    planning = None
    course_prereq_impact = None

    if mode in {'check', 'all'}:
        print('=== checking benchmarks ===')
        checking = run_checking_benchmarks()

    if mode in {'plan', 'all'}:
        print('\n=== planning benchmarks ===')
        planning = run_planning_benchmarks()
        print('\n=== course prereq impact ===')
        course_prereq_impact = run_course_wise_prereqs_analysis()

    results = {
        'timestamp': datetime.now().isoformat(),
        'checking': checking,
        'planning': planning,
        'course_prereq_impact': course_prereq_impact,
    }

    stamp   = datetime.now().strftime('%Y%m%d-%H%M%S')
    out_dir = Path(__file__).resolve().parent / f'benchmark-{stamp}'
    out_dir.mkdir(exist_ok=True)
    path = out_dir / 'benchmark.json'
    with open(path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'Wrote {path}')


if __name__ == '__main__':
    main()
