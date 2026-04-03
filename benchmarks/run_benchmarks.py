import io
import json
import os
import random
import select
import signal
import statistics
import time
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path

TIMEOUT = 300  # seconds per run

from configs import KB_LP, MAIN_LP
import python_version.cs_reqs_2024 as py_checker
from clingo_version.run_clingo import run_clingo
from ortools_version.course_catalog import History, Major, Standing, catalog
from ortools_version.planner import best_attempts, plan_courses
from prolog_version.run_prolog import run_prolog
from python_version.cs_reqs_2024 import Taken, degree_reqs
from tests.checking.checker_test_cases_a import test_0, test_01
from tests.planning.planner_test_cases import FULL


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


def timed_runs(func, n, extract_metrics=None, label='', direct=False):
    if label:
        print(f'  {label} ', end='', flush=True)
    times = []
    numeric = {}   # key -> [values]  aggregated as min/max/mean
    lists   = {}   # key -> last seen list  (e.g. partial_reqs_sat)
    any_timed_out = False

    for _ in range(n):
        run = run_once_direct(func, extract_metrics) if direct else run_once(func, extract_metrics)
        if run is None:
            print('T', end='', flush=True)
            continue
        if 'error' in run:
            print(f'\n  ERROR: {run["error"]}', flush=True)
            continue
        times.append(run['elapsed'])
        for k, v in run.get('metrics', {}).items():
            if isinstance(v, bool):
                if v: any_timed_out = True
            elif isinstance(v, list):
                lists[k] = v
            elif v is not None:
                numeric.setdefault(k, []).append(v)
        print('.', end='', flush=True)

    if not times:
        print('  all runs killed (SIGKILL)')
        return {'runs': 0, 'timed_out': True}

    out = {'runs': len(times), 'min_s': min(times), 'max_s': max(times), 'mean_s': statistics.mean(times)}
    for k, vals in numeric.items():
        out[k] = {'min': min(vals), 'max': max(vals), 'mean': statistics.mean(vals)}
    out['timed_out'] = any_timed_out
    out.update(lists)
    print(f'  mean={out["mean_s"]:.3f}s' + (' [TIMEOUT]' if any_timed_out else ''))
    return out


def ortools_metrics(_stdout, result):
    _, _, m = result
    return {k: m.get(k) for k in ('booleans', 'branches', 'conflicts')}


def clingo_metrics(_stdout, result):
    _, _, stats = result
    lp      = stats.get('problem', {}).get('lp', {})
    solvers = stats.get('solving', {}).get('solvers', {})
    times   = stats.get('summary', {}).get('times', {})
    total_t = float(times.get('total', 0))
    solve_t = float(times.get('solve', 0))
    m = {
        'booleans':    int(lp.get('atoms', 0)) or None,
        'choices':     int(solvers.get('choices', 0)),
        'conflicts':   int(solvers.get('conflicts', 0)),
        'grounding_s': round(total_t - solve_t, 4),
        'solving_s':   round(solve_t, 4),
        'timed_out':   bool(stats.get('timed_out', False)),
    }
    if stats.get('timed_out'):
        m['partial_reqs_sat']   = stats.get('partial_reqs_sat', [])
        m['partial_reqs_unsat'] = stats.get('partial_reqs_unsat', [])
    return m


def python_check(taken):
    py_checker.w = {}
    return degree_reqs(taken)


def to_history(ids):
    return [History(cid, catalog[cid].credits, 'A', (2024, 2), 'SB') for cid in sorted(ids)]


def to_taken(history):
    return {Taken(h.id, h.credits, h.grade, h.when, h.where) for h in history}


def planning_inputs():
    full = sorted(FULL)
    random.seed(42)
    random.shuffle(full)
    n = len(full)  # 28
    return {
        'empty':  [],
        'small':  to_history(full[:n // 4]),
        'medium': to_history(full[:n // 2]),
        'large':  to_history(full[:3 * n // 4]),
    }


def run_checking_benchmarks():
    passing_taken, _ = test_0()
    failing_taken, _ = test_01()

    results = {}
    for case, taken in [('pass', passing_taken), ('fail', failing_taken)]:
        print(f'\n  checking [{case}]')
        hist = best_attempts([History(t.id, t.credits, t.grade, t.when, t.where) for t in taken])
        results[case] = {
            'python':  timed_runs(lambda t=taken: python_check(t), 5, label='python'),
            'prolog':  timed_runs(lambda t=taken: run_prolog(t), 5, label='prolog'),
            'ortools': timed_runs(lambda h=hist: plan_courses(h, Major('CSE'), Standing('U4'), check=True), 5, label='ortools'),
            'clingo':  timed_runs(lambda t=taken: run_clingo(taken_set=t, mode='check', main_lp=MAIN_LP, kb_lp=KB_LP), 5, label='clingo'),
        }
    return results


def run_planning_benchmarks():
    inputs = planning_inputs()
    results = {}
    for size, hist in inputs.items():
        print(f'\n  planning [{size}]')
        taken = to_taken(hist)
        start = min((h.when for h in hist), default=(2024, 3))
        results[size] = {
            'ortools': timed_runs(
                lambda h=hist, s=start: plan_courses(h, Major('CSE'), Standing('U4'), starting_semester=s),
                2, extract_metrics=ortools_metrics, label='ortools'),
        }
        if size in {'empty', 'small'}:
            results[size]['clingo'] = timed_runs(
                lambda t=taken: run_clingo(taken_set=t, mode='plan', main_lp=MAIN_LP, kb_lp=KB_LP, ground_only=True),
                1, extract_metrics=clingo_metrics, label='clingo (ground only)', direct=True)
        else:
            results[size]['clingo'] = timed_runs(
                lambda t=taken: run_clingo(taken_set=t, mode='plan', main_lp=MAIN_LP, kb_lp=KB_LP, timeout=TIMEOUT),
                2, extract_metrics=clingo_metrics, label='clingo', direct=True)
    return results


def main():
    print('=== checking benchmarks ===')
    checking = run_checking_benchmarks()
    print('\n=== planning benchmarks ===')
    planning = run_planning_benchmarks()

    results = {
        'timestamp': datetime.now().isoformat(),
        'checking': checking,
        'planning': planning,
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
