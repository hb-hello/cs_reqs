import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# consistent colours across all charts — index by backend name
COLORS = {
    'python':  '#4c72b0',   # muted blue
    'prolog_swi':  '#dd8452',   # muted orange
    'prolog_xsb': '#c44e52',    # muted red
    'ortools': '#55a868',   # muted green
    'clingo':  '#8172b2',   # muted purple
}
DEFAULT_COLOR = '#c44e52'   # muted red for unknown
PLANNER_TIME_CAP_S = 10


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
    def key(case_name):
        n = _input_count(planning, case_name)
        return (n is None, n if n is not None else float('inf'), case_name)

    return sorted(planning.keys(), key=key)


def _input_count(planning, case_name):
    for entry in planning.get(case_name, {}).values():
        r = _stat_summary(entry, 'input_courses', skip_timeout=False)
        if r:
            return int(round(r[0]))
    return None


def _case_label_with_count(planning, case_name):
    n = _input_count(planning, case_name)
    return f'{n}' if n is not None else case_name


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


def _planner_time_series_capped(planning, sizes, backend):
    means, err_lo, err_hi, timed_out = [], [], [], []
    for s in sizes:
        entry = planning[s].get(backend)
        if not entry:
            means.append(0); err_lo.append(0); err_hi.append(0); timed_out.append(False)
            continue

        mean = float(entry.get('mean_s', 0) or 0)
        min_s = float(entry.get('min_s', mean) or mean)
        max_s = float(entry.get('max_s', mean) or mean)
        hit_cap = bool(entry.get('timed_out')) or max_s > PLANNER_TIME_CAP_S

        mean_c = min(mean, PLANNER_TIME_CAP_S)
        min_c = min(min_s, mean_c)
        max_c = min(max_s, PLANNER_TIME_CAP_S)
        means.append(mean_c)
        err_lo.append(mean_c - min_c)
        err_hi.append(max(0, max_c - mean_c))
        timed_out.append(hit_cap)

    return means, err_lo, err_hi, timed_out


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
        means, err_lo, err_hi, timed_out = _planner_time_series_capped(planning, sizes, b)
        x_vals = []
        for s in sizes:
            entry = planning[s].get(b)
            r = _stat_summary(entry, 'planned_new_courses', skip_timeout=False)
            fallback = _input_count(planning, s)
            x_vals.append(r[0] if r else (fallback if fallback is not None else 0))
        offset = (i - (len(backends) - 1) / 2) * width
        x_plot = np.array(x_vals, dtype=float) + offset
        all_x.extend(x_vals)
        bars = ax.bar(x_plot, means, width, yerr=[err_lo, err_hi],
                      label=b, color=color(b), capsize=3, alpha=0.85)
        for j, bar in enumerate(bars):
            if timed_out[j]:
                ax.text(bar.get_x() + bar.get_width() / 2, PLANNER_TIME_CAP_S,
                        'timeout', ha='center', va='bottom', fontsize=7, color='#666')

    ticks = sorted({int(round(v)) for v in all_x})
    ax.set_xticks(ticks)
    ax.set_xlabel('# new courses planned')
    ax.set_ylabel('Time (s)')
    ax.set_title('Planner: time comparison by output plan size')
    ax.set_ylim(0, PLANNER_TIME_CAP_S)
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
        means, err_lo, err_hi, timed_out = _planner_time_series_capped(planning, sizes, b)
        x_vals = []
        for s in sizes:
            entry = planning[s].get(b)
            r = _stat_summary(entry, 'planned_new_courses', skip_timeout=False)
            fallback = _input_count(planning, s)
            x_vals.append(r[0] if r else (fallback if fallback is not None else 0))
        points = sorted(zip(x_vals, means, err_lo, err_hi, timed_out), key=lambda p: p[0])
        x_sorted  = [p[0] for p in points]
        y_sorted  = [p[1] for p in points]
        lo_sorted = [p[2] for p in points]
        hi_sorted = [p[3] for p in points]
        t_sorted = [p[4] for p in points]
        ax.errorbar(x_sorted, y_sorted, yerr=[lo_sorted, hi_sorted], marker='o', linewidth=2,
                    label=b, color=color(b), capsize=3)
        for x, t in zip(x_sorted, t_sorted):
            if t:
                ax.text(x, PLANNER_TIME_CAP_S, 'timeout', ha='center', va='bottom', fontsize=7, color='#666')

    ax.set_xlabel('# new courses planned')
    ax.set_ylabel('Time (s)')
    ax.set_title('Planner: time comparison by output plan size (line)')
    ax.set_ylim(0, PLANNER_TIME_CAP_S)
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
    ax.set_xticklabels([_case_label_with_count(planning, s) for s in sizes])
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
    ax.set_xticklabels([_case_label_with_count(planning, s) for s in sizes])
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
    ax.set_xticklabels([_case_label_with_count(planning, s) for s in sizes])
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
    ax.set_xticklabels([_case_label_with_count(planning, s) for s in sizes])
    ax.set_ylabel('Count (log scale)')
    ax.set_yscale('log')
    ax.set_title('Planner: search effort (branches/choices & conflicts)')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_search_effort.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_planner_times_bar_reqs(data, out_dir):
    planning = data['planning']
    sizes    = _planner_cases(planning)
    backends = _planner_backends(planning, sizes)

    x, width = np.arange(len(sizes)), 0.3
    fig, ax = plt.subplots(figsize=(10, 5))

    for i, b in enumerate(backends):
        means, err_lo, err_hi, timed_out = _planner_time_series_capped(planning, sizes, b)
        bars = ax.bar(x + i * width, means, width, yerr=[err_lo, err_hi],
                      label=b, color=color(b), capsize=3, alpha=0.85)
        for j, bar in enumerate(bars):
            if timed_out[j]:
                ax.text(bar.get_x() + bar.get_width() / 2, PLANNER_TIME_CAP_S,
                        'timeout', ha='center', va='bottom', fontsize=7, color='#666')

    ax.set_xticks(x + width * (len(backends) - 1) / 2)
    ax.set_xticklabels(sizes, rotation=20, ha='right')
    ax.set_xlabel('Planning test case')
    ax.set_ylabel('Time (s)')
    ax.set_title('Planner: time comparison by planning test case')
    ax.set_ylim(0, PLANNER_TIME_CAP_S)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    out = out_dir / 'planner_times_bar_reqs.png'
    fig.savefig(out, dpi=150)
    print(f'Wrote {out}')


def plot_checker_planner_wall_time_combo(data, out_dir):
    checking = data.get('checking')
    planning = data.get('planning')
    if not checking or not planning:
        return

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(14, 5))

    # Left panel: checker times by case/backend (grouped bars)
    cases = list(checking.keys())
    # backends = sorted(checking[cases[0]].keys())
    backends = ['python', 'prolog_swi', 'prolog_xsb', 'clingo', 'ortools']
    x = np.arange(len(cases))
    width = 0.75 / max(1, len(backends))

    for i, b in enumerate(backends):
        means = [checking[c][b]['mean_s'] for c in cases]
        err_lo = [checking[c][b]['mean_s'] - checking[c][b]['min_s'] for c in cases]
        err_hi = [checking[c][b]['max_s'] - checking[c][b]['mean_s'] for c in cases]
        offset = (i - (len(backends) - 1) / 2) * width
        ax_l.bar(x + offset, means, width, yerr=[err_lo, err_hi],
                 label=b, color=color(b), capsize=3, alpha=0.85)

    ax_l.set_xticks(x)
    ax_l.set_xticklabels(cases)
    ax_l.set_ylabel('Wall time (s)')
    ax_l.set_title('Checker Wall Time')
    ax_l.grid(axis='y', alpha=0.3)
    ax_l.legend(fontsize=10)

    # Right panel: planner times as lines vs # new courses planned
    sizes = _planner_cases(planning)
    backends_r = _planner_backends(planning, sizes)
    for b in backends_r:
        means, err_lo, err_hi, timed_out = _planner_time_series_capped(planning, sizes, b)
        x_vals = []
        for s in sizes:
            entry = planning[s].get(b)
            r = _stat_summary(entry, 'planned_new_courses', skip_timeout=False)
            fallback = _input_count(planning, s)
            x_vals.append(r[0] if r else (fallback if fallback is not None else 0))
        points = sorted(zip(x_vals, means, err_lo, err_hi, timed_out), key=lambda p: p[0])
        x_sorted  = [p[0] for p in points]
        y_sorted  = [p[1] for p in points]
        lo_sorted = [p[2] for p in points]
        hi_sorted = [p[3] for p in points]
        t_sorted  = [p[4] for p in points]
        ax_r.errorbar(x_sorted, y_sorted, yerr=[lo_sorted, hi_sorted], marker='o', linewidth=2,
                      label=b, color=color(b), capsize=3)
        for xv, tv in zip(x_sorted, t_sorted):
            if tv:
                ax_r.text(xv, PLANNER_TIME_CAP_S, 'timeout', ha='center', va='bottom', fontsize=15, color='#666')

    ax_r.set_xlabel('# new courses planned')
    ax_r.set_ylabel('Wall time (s)')
    ax_r.set_title('Planner Wall Time')
    ax_r.set_ylim(0, PLANNER_TIME_CAP_S)
    ax_r.grid(axis='y', alpha=0.3)
    ax_r.legend(fontsize=10)

    fig.tight_layout()
    fig.subplots_adjust(wspace=0.35)
    out = out_dir / 'checker_planner_wall_time_combo.png'
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
    plot_planner_times_bar_reqs(data, out_dir)
    plot_planner_times_bar(data, out_dir)
    plot_planner_times_line(data, out_dir)
    plot_checker_planner_wall_time_combo(data, out_dir)
    # plot_planner_output_size_bar(data, out_dir)
    # plot_planner_output_size_line(data, out_dir)
    plot_planner_booleans(data, out_dir)
    plot_planner_search_effort(data, out_dir)


if __name__ == '__main__':
    main()
