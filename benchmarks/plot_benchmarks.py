import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

TIMEOUT = 300  # must match run_benchmarks.py


def load(path):
    with open(path) as f:
        return json.load(f)


def plot_checker_times(data, out_dir):
    checking = data['checking']
    cases = list(checking.keys())          # ['pass', 'fail']
    backends = list(checking[cases[0]].keys())  # ['python', 'prolog', 'ortools', 'clingo']

    x = np.arange(len(cases))
    width = 0.18
    fig, ax = plt.subplots(figsize=(8, 5))

    for i, backend in enumerate(backends):
        means = [checking[c][backend]['mean_s'] for c in cases]
        mins  = [checking[c][backend]['min_s'] for c in cases]
        maxs  = [checking[c][backend]['max_s'] for c in cases]
        errs  = [[m - lo for m, lo in zip(means, mins)],
                 [hi - m for m, hi in zip(means, maxs)]]
        ax.bar(x + i * width, means, width, yerr=errs, label=backend, capsize=3)

    ax.set_xticks(x + width * (len(backends) - 1) / 2)
    ax.set_xticklabels(cases)
    ax.set_ylabel('Time (s)')
    ax.set_title('Checker Time Comparison')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / 'checker_times.png', dpi=150)
    print(f'Wrote {out_dir / "checker_times.png"}')


def plot_planner_times(data, out_dir):
    planning = data['planning']
    sizes = [s for s in ['empty', 'small', 'medium', 'large'] if s in planning]
    backends = sorted({b for s in sizes for b in planning[s]})

    x = np.arange(len(sizes))
    width = 0.3
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, backend in enumerate(backends):
        means, mins, maxs, timed_out_labels = [], [], [], []
        for s in sizes:
            entry = planning[s].get(backend)
            if entry and not entry.get('timed_out'):
                means.append(entry['mean_s'])
                mins.append(entry['min_s'])
                maxs.append(entry['max_s'])
                timed_out_labels.append(False)
            else:
                means.append(0)
                mins.append(0)
                maxs.append(0)
                timed_out_labels.append(entry is None or entry.get('timed_out'))

        errs = [[m - lo for m, lo in zip(means, mins)],
                [hi - m for m, hi in zip(means, maxs)]]
        bars = ax.bar(x + i * width, means, width, yerr=errs, label=backend, capsize=3)

        # mark timeouts
        for j, (bar, is_timeout) in enumerate(zip(bars, timed_out_labels)):
            if is_timeout:
                ax.text(bar.get_x() + bar.get_width() / 2, ax.get_ylim()[1] * 0.02,
                        f'timeout\n(>{TIMEOUT}s)', ha='center', va='bottom',
                        fontsize=7, color='red', fontweight='bold')

    ax.set_xticks(x + width * (len(backends) - 1) / 2)
    ax.set_xticklabels(sizes)
    ax.set_ylabel('Time (s)')
    ax.set_title('Planner Time Comparison')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / 'planner_times.png', dpi=150)
    print(f'Wrote {out_dir / "planner_times.png"}')


def plot_planner_booleans(data, out_dir):
    planning = data['planning']
    sizes = [s for s in ['empty', 'small', 'medium', 'large'] if s in planning]
    backends = sorted({b for s in sizes for b in planning[s]})

    x = np.arange(len(sizes))
    width = 0.3
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, backend in enumerate(backends):
        means, timed_out_labels = [], []
        for s in sizes:
            entry = planning[s].get(backend)
            if entry and not entry.get('timed_out') and 'booleans' in entry:
                means.append(entry['booleans']['mean'])
                timed_out_labels.append(False)
            else:
                means.append(0)
                timed_out_labels.append(entry is None or (entry and entry.get('timed_out')))

        bars = ax.bar(x + i * width, means, width, label=backend)

        for j, (bar, is_timeout) in enumerate(zip(bars, timed_out_labels)):
            if is_timeout:
                ax.text(bar.get_x() + bar.get_width() / 2, ax.get_ylim()[1] * 0.02,
                        f'timeout\n(>{TIMEOUT}s)', ha='center', va='bottom',
                        fontsize=7, color='red', fontweight='bold')

    ax.set_xticks(x + width * (len(backends) - 1) / 2)
    ax.set_xticklabels(sizes)
    ax.set_ylabel('# Booleans / Atoms')
    ax.set_yscale('log')
    ax.set_title('Planner Variables Comparison (log scale)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / 'planner_booleans.png', dpi=150)
    print(f'Wrote {out_dir / "planner_booleans.png"}')


def main():
    if len(sys.argv) < 2:
        # find most recent benchmark json
        jsons = sorted(Path(__file__).parent.glob('benchmark-*.json'))
        if not jsons:
            print('Usage: plot_benchmarks.py <benchmark.json>')
            sys.exit(1)
        path = jsons[-1]
    else:
        path = Path(sys.argv[1])

    print(f'Reading {path}')
    data = load(path)
    out_dir = path.parent

    plot_checker_times(data, out_dir)
    plot_planner_times(data, out_dir)
    plot_planner_booleans(data, out_dir)


if __name__ == '__main__':
    main()
