import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# consistent colours across all charts — index by backend name
COLORS = {
    'python':  '#4c72b0',   # muted blue
    'prolog':  '#dd8452',   # muted orange
    'ortools': '#55a868',   # muted green
    'clingo':  '#8172b2',   # muted purple
}
DEFAULT_COLOR = '#c44e52'   # muted red for unknown


def color(backend):
    return COLORS.get(backend, DEFAULT_COLOR)


def load(path):
    with open(path) as f:
        return json.load(f)


def _stat_summary(entry, key, skip_timeout=True):
    """Return (mean, err_lo, err_hi) or None if key missing or (timed out and skip_timeout)."""
    if not entry or key not in entry:
        return None
    if skip_timeout and entry.get('timed_out'):
        return None
    sub = entry[key]
    if isinstance(sub, dict):
        m = sub['mean']
        return m, m - sub['min'], sub['max'] - m
    # top-level scalar (e.g. mean_s) — look for companion min_s / max_s
    lo_key = key.replace('mean', 'min')
    hi_key = key.replace('mean', 'max')
    lo = entry.get(lo_key, sub)
    hi = entry.get(hi_key, sub)
    return sub, sub - lo, hi - sub


def _planner_cases(planning):
    def key(label):
        parts = label.split()
        if len(parts) >= 3 and parts[1] == 'input' and parts[2] == 'courses' and parts[0].isdigit():
            return int(parts[0])
        return float('inf')

    return sorted(planning.keys(), key=key)


def _course_count_label(case):
    return case.split()[0]


def _input_count(case):
    return int(_course_count_label(case))


def _planner_backends(planning, sizes):
    return sorted({b for s in sizes for b in planning[s]})


def _planner_series(planning, sizes, backend, key, skip_timeout=True):
    means, err_lo, err_hi = [], [], []
    for s in sizes:
        entry = planning[s].get(backend)
        r = _stat_summary(entry, key, skip_timeout=skip_timeout)
        if r:
            means.append(r[0]); err_lo.append(r[1]); err_hi.append(r[2])
        else:
            means.append(0); err_lo.append(0); err_hi.append(0)
    return means, err_lo, err_hi


def plot_checker_times(data, out_dir):
    checking = data['checking']
    cases    = list(checking.keys())
    backends = list(checking[cases[0]].keys())

    x, width = np.arange(len(cases)), 0.18
    fig, ax = plt.subplots(figsize=(8, 5))

    for i, b in enumerate(backends):
        cases.sort(key=lambda c : checking[c][b]['mean_s'])
        means = [checking[c][b]['mean_s'] for c in cases]
        errs  = [[checking[c][b]['mean_s'] - checking[c][b]['min_s'] for c in cases],
                 [checking[c][b]['max_s']  - checking[c][b]['mean_s'] for c in cases]]
        ax.bar(x + i * width, means, width, yerr=errs, label=b,
               color=color(b), capsize=3, alpha=0.85)

    ax.set_xticks(x + width * (len(backends) - 1) / 2)
    ax.set_xticklabels(cases)
    ax.set_ylabel('Time (s)')
    ax.set_title('Checker: time comparison (pass vs fail)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'checker_times.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_checker_times_pass_only(data, out_dir):
    checking = data['checking']
    if 'pass' not in checking:
        return

    pass_case = checking['pass']
    backends = sorted(pass_case.keys())
    x = np.arange(len(backends))

    means = [pass_case[b]['mean_s'] for b in backends]
    err_lo = [pass_case[b]['mean_s'] - pass_case[b]['min_s'] for b in backends]
    err_hi = [pass_case[b]['max_s'] - pass_case[b]['mean_s'] for b in backends]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x, means, yerr=[err_lo, err_hi], capsize=3, alpha=0.85,
           color=[color(b) for b in backends])

    ax.set_xticks(x)
    ax.set_xticklabels(backends)
    ax.set_ylabel('Time (s)')
    ax.set_title('Checker: pass case by implementation')
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'checker_times_pass_only.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_planner_times_bar(data, out_dir):
    planning = data['planning']
    sizes    = _planner_cases(planning)
    backends = _planner_backends(planning, sizes)

    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))

    all_x = []
    for i, b in enumerate(backends):
        means, err_lo, err_hi = _planner_series(planning, sizes, b, 'mean_s')
        x_vals = []
        for s in sizes:
            entry = planning[s].get(b)
            r = _stat_summary(entry, 'planned_new_courses', skip_timeout=False)
            x_vals.append(r[0] if r else _input_count(s))
        offset = (i - (len(backends) - 1) / 2) * width
        x_plot = np.array(x_vals, dtype=float) + offset
        all_x.extend(x_vals)
        ax.bar(x_plot, means, width, yerr=[err_lo, err_hi],
               label=b, color=color(b), capsize=3, alpha=0.85)

    ticks = sorted({int(round(v)) for v in all_x})
    ax.set_xticks(ticks)
    ax.set_xlabel('# new courses planned')
    ax.set_ylabel('Time (s)')
    ax.set_title('Planner: time comparison by output plan size')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_times_bar.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_planner_times_line(data, out_dir):
    planning = data['planning']
    sizes    = _planner_cases(planning)
    backends = _planner_backends(planning, sizes)

    fig, ax = plt.subplots(figsize=(9, 5))

    for b in backends:
        means, err_lo, err_hi = _planner_series(planning, sizes, b, 'mean_s')
        x_vals = []
        for s in sizes:
            entry = planning[s].get(b)
            r = _stat_summary(entry, 'planned_new_courses', skip_timeout=False)
            x_vals.append(r[0] if r else _input_count(s))
        points = sorted(zip(x_vals, means, err_lo, err_hi), key=lambda p: p[0])
        x_sorted  = [p[0] for p in points]
        y_sorted  = [p[1] for p in points]
        lo_sorted = [p[2] for p in points]
        hi_sorted = [p[3] for p in points]
        ax.errorbar(x_sorted, y_sorted, yerr=[lo_sorted, hi_sorted], marker='o', linewidth=2,
                    label=b, color=color(b), capsize=3)

    ax.set_xlabel('# new courses planned')
    ax.set_ylabel('Time (s)')
    ax.set_title('Planner: time comparison by output plan size (line)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_times_line.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_planner_output_size_bar(data, out_dir):
    planning = data['planning']
    sizes    = _planner_cases(planning)
    backends = _planner_backends(planning, sizes)

    x, width = np.arange(len(sizes)), 0.3
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, b in enumerate(backends):
        means, err_lo, err_hi = _planner_series(planning, sizes, b, 'planned_new_courses', skip_timeout=False)
        ax.bar(x + i * width, means, width, yerr=[err_lo, err_hi],
               label=b, color=color(b), capsize=3, alpha=0.85)

    ax.set_xticks(x + width * (len(backends) - 1) / 2)
    ax.set_xticklabels([_course_count_label(s) for s in sizes])
    ax.set_xlabel('# input courses')
    ax.set_ylabel('# new courses planned')
    ax.set_title('Planner: output size by number of input courses')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_output_size_bar.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_planner_output_size_line(data, out_dir):
    planning = data['planning']
    sizes    = _planner_cases(planning)
    backends = _planner_backends(planning, sizes)

    x = np.arange(len(sizes))
    fig, ax = plt.subplots(figsize=(9, 5))

    for b in backends:
        means, err_lo, err_hi = _planner_series(planning, sizes, b, 'planned_new_courses', skip_timeout=False)
        ax.errorbar(x, means, yerr=[err_lo, err_hi], marker='o', linewidth=2,
                    label=b, color=color(b), capsize=3)

    ax.set_xticks(x)
    ax.set_xticklabels([_course_count_label(s) for s in sizes])
    ax.set_xlabel('# input courses')
    ax.set_ylabel('# new courses planned')
    ax.set_title('Planner: output size by number of input courses (line)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_output_size_line.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_planner_booleans(data, out_dir):
    planning = data['planning']
    sizes    = _planner_cases(planning)
    backends = sorted({b for s in sizes for b in planning[s]})

    x, width = np.arange(len(sizes)), 0.3
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, b in enumerate(backends):
        means = []
        for s in sizes:
            entry = planning[s].get(b)
            r = _stat_summary(entry, 'booleans', skip_timeout=False)
            means.append(r[0] if r else 0)
        ax.bar(x + i * width, means, width, label=b, color=color(b), alpha=0.85)

    ax.set_xticks(x + width * (len(backends) - 1) / 2)
    ax.set_xticklabels([_course_count_label(s) for s in sizes])
    ax.set_ylabel('Booleans / Atoms (log scale)')
    ax.set_yscale('log')
    ax.set_title('Planner: variables (OR-Tools booleans vs Clingo atoms)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_booleans.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_planner_search_effort(data, out_dir):
    """Branches/choices and conflicts side by side for OR-Tools vs Clingo."""
    planning = data['planning']
    sizes    = _planner_cases(planning)

    # OR-Tools: branches + conflicts; Clingo: choices + conflicts
    series = [
        ('ortools', 'branches',  'OR-Tools branches'),
        ('ortools', 'conflicts', 'OR-Tools conflicts'),
        ('clingo',  'choices',   'Clingo choices'),
        ('clingo',  'conflicts', 'Clingo conflicts'),
    ]
    # only keep series that have at least one data point
    series = [(b, k, lbl) for b, k, lbl in series
              if any(_stat_summary(planning[s].get(b), k) for s in sizes)]

    if not series:
        return

    x, width = np.arange(len(sizes)), 0.2
    fig, ax = plt.subplots(figsize=(10, 5))

    # use lighter shade of each backend's colour for the second metric
    palette = {}
    for b, k, _ in series:
        base = COLORS.get(b, DEFAULT_COLOR)
        palette[(b, k)] = base if k in ('branches', 'choices') else base + '99'

    for i, (b, k, lbl) in enumerate(series):
        means = []
        for s in sizes:
            entry = planning[s].get(b)
            r = _stat_summary(entry, k, skip_timeout=False)
            means.append(r[0] if r else 0)
        ax.bar(x + i * width, means, width, label=lbl,
               color=palette[(b, k)], alpha=0.85)

    ax.set_xticks(x + width * (len(series) - 1) / 2)
    ax.set_xticklabels([_course_count_label(s) for s in sizes])
    ax.set_ylabel('Count (log scale)')
    ax.set_yscale('log')
    ax.set_title('Planner: search effort (branches/choices & conflicts)')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_search_effort.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def main():
    if len(sys.argv) < 2:
        here = Path(__file__).parent
        candidates = sorted(
            list(here.glob('benchmark-*/benchmark.json')) + list(here.glob('benchmark-*.json'))
        )
        if not candidates:
            print('Usage: plot_benchmarks.py <benchmark.json>')
            sys.exit(1)
        path = candidates[-1]
    else:
        path = Path(sys.argv[1])

    print(f'Reading {path}')
    data = load(path)
    out_dir = path.parent

    plot_checker_times(data, out_dir)
    plot_checker_times_pass_only(data, out_dir)
    plot_planner_times_bar(data, out_dir)
    plot_planner_times_line(data, out_dir)
    # plot_planner_output_size_bar(data, out_dir)
    # plot_planner_output_size_line(data, out_dir)
    plot_planner_booleans(data, out_dir)
    plot_planner_search_effort(data, out_dir)


if __name__ == '__main__':
    main()
