import time
import statistics
import json
import os
import re
import io
from contextlib import redirect_stdout

from ortools_version.course_catalog import CATALOG, Taken, Major, Standing

try:
    from ortools_version.planner import plan_courses as planner_plan
except Exception:
    planner_plan = None

try:
    from ortools_version.plannerv2 import plan_courses as plannerv2_plan
except Exception:
    plannerv2_plan = None


def plot_from_json(json_path, out_dir='benchmarks'):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib not available; install it to generate plots')
        return

    if not os.path.exists(json_path):
        print(f'Benchmark JSON not found: {json_path}')
        return

    with open(json_path) as f:
        results = json.load(f)

    os.makedirs(out_dir, exist_ok=True)

    # prefer ordered scenarios: empty, small, medium, large
    desired = ['empty', 'small', 'medium', 'large']
    scen_names = [s for s in desired if s in results] + [s for s in results.keys() if s not in desired and s != 'checker']
    x = list(range(len(scen_names)))

    backends = set()
    for sc in scen_names:
        if isinstance(results.get(sc), dict):
            backends.update(results[sc].keys())
    backends = sorted(backends)

    # basic plots
    plt.figure(figsize=(8, 4))
    for b in backends:
        y = [results.get(sc, {}).get(b, {}).get('mean_s', 0) for sc in scen_names]
        plt.plot(x, y, marker='o', label=b)
    plt.xticks(x, scen_names)
    plt.xlabel('Scenario')
    plt.ylabel('mean time (s)')
    plt.title('Planner mean time by scenario')
    plt.grid(True)
    if backends:
        plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'time_comparison.png'))

    plt.figure(figsize=(8, 4))
    for b in backends:
        y = []
        for sc in scen_names:
            r = results.get(sc, {}).get(b)
            if not r:
                y.append(0)
                continue
            vals = [m.get('booleans') for m in r.get('metrics', []) if m.get('booleans') is not None]
            y.append(statistics.mean(vals) if vals else 0)
        plt.plot(x, y, marker='o', label=b)
    plt.xticks(x, scen_names)
    plt.xlabel('Scenario')
    plt.ylabel('mean booleans (variables)')
    plt.title('Planner boolean variables by scenario')
    plt.grid(True)
    if backends:
        plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'vars_comparison.png'))

    plt.figure(figsize=(8, 4))
    for b in backends:
        y = []
        for sc in scen_names:
            r = results.get(sc, {}).get(b)
            if not r:
                y.append(0)
                continue
            vals = [m.get('branches') for m in r.get('metrics', []) if m.get('branches') is not None]
            y.append(statistics.mean(vals) if vals else 0)
        plt.plot(x, y, marker='o', label=b)
    plt.xticks(x, scen_names)
    plt.xlabel('Scenario')
    plt.ylabel('mean branches')
    plt.title('Solver branches by scenario')
    plt.grid(True)
    if backends:
        plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'branches_comparison.png'))

    # combined
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        ax_time, ax_vars, ax_branches, ax_checker = axes.flat

        for b in backends:
            y = [results.get(sc, {}).get(b, {}).get('mean_s', 0) for sc in scen_names]
            ax_time.plot(x, y, marker='o', label=b)
            for xi, sc in enumerate(scen_names):
                r = results.get(sc, {}).get(b)
                if not r:
                    continue
                ys = [m.get('elapsed_s') for m in r.get('metrics', []) if m.get('elapsed_s') is not None]
                if ys:
                    ax_time.scatter([xi] * len(ys), ys, s=20, alpha=0.6)
        ax_time.set_xticks(x)
        ax_time.set_xticklabels(scen_names)
        ax_time.set_title('Mean time (s)')
        ax_time.grid(True)

        for b in backends:
            y = []
            for sc in scen_names:
                r = results.get(sc, {}).get(b)
                if not r:
                    y.append(0)
                    continue
                vals = [m.get('booleans') for m in r.get('metrics', []) if m.get('booleans') is not None]
                y.append(statistics.mean(vals) if vals else 0)
            ax_vars.plot(x, y, marker='o', label=b)
            for xi, sc in enumerate(scen_names):
                r = results.get(sc, {}).get(b)
                if not r:
                    continue
                vals = [m.get('booleans') for m in r.get('metrics', []) if m.get('booleans') is not None]
                if vals:
                    ax_vars.scatter([xi] * len(vals), vals, s=20, alpha=0.6)
        ax_vars.set_xticks(x)
        ax_vars.set_xticklabels(scen_names)
        ax_vars.set_title('Boolean variables (mean)')
        ax_vars.grid(True)

        for b in backends:
            y = []
            for sc in scen_names:
                r = results.get(sc, {}).get(b)
                if not r:
                    y.append(0)
                    continue
                vals = [m.get('branches') for m in r.get('metrics', []) if m.get('branches') is not None]
                y.append(statistics.mean(vals) if vals else 0)
            ax_branches.plot(x, y, marker='o', label=b)
            for xi, sc in enumerate(scen_names):
                r = results.get(sc, {}).get(b)
                if not r:
                    continue
                vals = [m.get('branches') for m in r.get('metrics', []) if m.get('branches') is not None]
                if vals:
                    ax_branches.scatter([xi] * len(vals), vals, s=20, alpha=0.6)
        ax_branches.set_xticks(x)
        ax_branches.set_xticklabels(scen_names)
        ax_branches.set_title('Solver branches (mean)')
        ax_branches.grid(True)

        if 'checker' in results:
            checker = results['checker']
            x2 = [0, 1]
            # plot per-backend lines (includes baseline and any backends)
            for cb in sorted(checker.keys()):
                if not isinstance(checker.get(cb), dict):
                    continue
                pass_m = checker.get(cb, {}).get('pass', {}).get('mean_s') if checker.get(cb, {}).get('pass') else None
                fail_m = checker.get(cb, {}).get('fail', {}).get('mean_s') if checker.get(cb, {}).get('fail') else None
                if pass_m is None and fail_m is None:
                    continue
                y = [pass_m or 0, fail_m or 0]
                style = '--' if cb == 'baseline' else '-'
                ax_checker.plot(x2, y, marker='o', linestyle=style, label=cb)
            ax_checker.set_xticks(x2)
            ax_checker.set_xticklabels(['checker-pass', 'checker-fail'])
            ax_checker.set_title('Checker: pass vs fail (per backend)')
            ax_checker.grid(True)
            ax_checker.legend()
        else:
            ax_checker.axis('off')

        plt.tight_layout()
        combined_path = os.path.join(out_dir, 'combined_benchmarks.png')
        fig.savefig(combined_path)
        print(f'Wrote combined plot: {combined_path}')
    except Exception:
        print('Could not create combined plot (matplotlib)')


def make_history(taken_ids, when=(1, 1), grade='C', where='SB'):
    return [Taken(cid, CATALOG[cid].credits, grade, when, where) for cid in sorted(taken_ids) if cid in CATALOG]


def choose_histories():
    ids = list(CATALOG.keys())
    small = ids[:8]
    medium = ids[:30]
    large = ids[:80] if len(ids) >= 80 else ids
    return {
        'empty': [],
        'small': make_history(small),
        'medium': make_history(medium),
        'large': make_history(large),
    }


def parse_metrics_from_stdout(text):
    # find key=value pairs; values may be ints or floats
    out = {}
    for k, v in re.findall(r"(\w+)=([0-9.]+)", text):
        if '.' in v:
            out[k] = float(v)
        else:
            out[k] = int(v)
    return out


def run_benchmark(func, history, runs=3, **kwargs):
    import inspect
    sig = inspect.signature(func)
    accepts = set(sig.parameters.keys())
    common_kwargs = {}
    if 'starting_semester' in accepts:
        common_kwargs['starting_semester'] = min((h.when for h in history), default=(1, 1))

    times = []
    metrics = []
    for _ in range(runs):
        t0 = time.perf_counter()
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                if planner_plan is func or plannerv2_plan is func:
                    # try student-style call
                    res = func(history, Major('CSE'), Standing('U4'), **{**common_kwargs, **kwargs})
                else:
                    res = func(history, **{**common_kwargs, **kwargs})
            except TypeError:
                res = func(history, **kwargs)
        t1 = time.perf_counter()
        elapsed = t1 - t0
        out = parse_metrics_from_stdout(buf.getvalue())
        out['elapsed_s'] = elapsed
        times.append(elapsed)
        metrics.append(out)

    return {
        'runs': runs,
        'mean_s': statistics.mean(times),
        'median_s': statistics.median(times),
        'min_s': min(times),
        'max_s': max(times),
        'metrics': metrics,
    }


def main():
    histories = choose_histories()
    results = {}
    backends = []
    if planner_plan:
        backends.append(('planner', planner_plan))
    if plannerv2_plan:
        backends.append(('plannerv2', plannerv2_plan))

    for name, hist in histories.items():
        results.setdefault(name, {})
        for bname, func in backends:
            print(f'Running {bname} on {name}...')
            try:
                r = run_benchmark(func, hist, runs=3)
                results[name][bname] = r
            except Exception as e:
                print(f'Error running {bname} on {name}: {e}')

    # try checker if available
    try:
        from tests.checking import checker_test_cases_a as checker_tests

        def run_checker_case(test_func, pre_backend_func=None):
            times = []
            for _ in range(3):
                t0 = time.perf_counter()
                # if a backend plan function is provided, run it once before the checker
                if pre_backend_func:
                    try:
                        pre_backend_func(histories.get('small', []))
                    except Exception:
                        pass
                test_func()
                t1 = time.perf_counter()
                times.append(t1 - t0)
            return {'runs': 3, 'mean_s': statistics.mean(times), 'metrics': [{'elapsed_s': t} for t in times]}

        # run baseline checker (no planner)
        results.setdefault('checker', {})['baseline'] = {
            'pass': run_checker_case(checker_tests.test_0),
            'fail': run_checker_case(checker_tests.test_01),
        }

        # run checker including each backend's planning step (small history used as pre-step)
        for bname, func in backends:
            results['checker'].setdefault(bname, {})
            results['checker'][bname]['pass'] = run_checker_case(checker_tests.test_0, pre_backend_func=func if func else None)
            results['checker'][bname]['fail'] = run_checker_case(checker_tests.test_01, pre_backend_func=func if func else None)
    except Exception:
        print('Checker tests not available; skipping checker benchmarks')

    os.makedirs('benchmarks', exist_ok=True)
    out_path = os.path.join('benchmarks', 'benchmarks.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'Wrote benchmark results to {out_path}')

    # generate plots
    plot_from_json(out_path)


if __name__ == '__main__':
    main()
