import argparse
import csv
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import mean
from clingo_version.run_clingo import run_clingo_benchmark
from benchmarks.run_bm import plan_cases

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PLAN_COMPARE_DIR = ROOT / 'clingo_version' / 'plan_compare'
RESULTS_ROOT = ROOT / 'benchmarks' / 'clingo_bm_results'

METRICS = [
  ('total_time_s', 'Total time (s)'),
  ('solving_time_s', 'Solving time (s)'),
  ('grounding_time_s', 'Grounding time (s)'),
  ('variables', 'Variables (atoms)'),
  ('generated_rules', 'Generated rules'),
  ('branches', 'Branches (choices)'),
  ('conflicts', 'Conflicts'),
  ('model_count', 'Model count'),
]

EXPS = (
  'allreq',
  'cr_option',
  'opt_order',
  'req_in_test_vs_gen',
  # 'plan_anti' , # not needed anymore
)

def _git_short() -> str:
  try:
    result = subprocess.run(
      ['git', 'rev-parse', '--short=6', 'HEAD'],
      cwd=str(ROOT),
      capture_output=True,
      text=True,
      check=True,
    )
    return result.stdout.strip() or 'unknown'
  except Exception:
    return 'unknown'


def build_clingo_kwargs():
  return {}


def list_experiments():
  exp_lp_pattern = re.compile(r'^exp.*\.lp$')
  for path in sorted(PLAN_COMPARE_DIR.iterdir()):
    if not path.is_dir():
      continue
    if path.name.startswith('__'):
      continue
    lp_files = sorted(
      lp for lp in path.iterdir()
      if lp.is_file() and exp_lp_pattern.match(lp.name)
    )
    if lp_files:
      yield path, lp_files


def run_experiment(experiment_dir: Path, lp_files: list[Path], tests, repeats: int, timeout: float | None, out_dir: Path):
  rows = []
  for test_name, taken in tests:
    clingo_kwargs = build_clingo_kwargs()
    if timeout is not None:
      clingo_kwargs['timeout'] = timeout

    for program_path in lp_files:
      for run_idx in range(1, repeats + 1):
        _checked, _schedule, stats = run_clingo_benchmark(
          program_lp=str(program_path),
          taken_set=taken,
          **clingo_kwargs,
        )

        times = stats.get('summary', {}).get('times', {})
        total_time = float(times.get('total', 0.0))
        solve_time = float(times.get('solve', 0.0))
        grounding_time = total_time - solve_time
        min_cost = stats.get('min_cost')

        print(f"{program_path.stem} {test_name} {total_time} {min_cost}")

        lp = stats.get('problem', {}).get('lp', {})
        solvers = stats.get('solving', {}).get('solvers', {})

        rows.append({
          'experiment': experiment_dir.name,
          'program': program_path.stem,
          'test': test_name,
          'run': run_idx,
          'status': 'ok',
          'min_cost': min_cost,
          'total_time_s': round(total_time, 6),
          'solving_time_s': round(solve_time, 6),
          'grounding_time_s': round(grounding_time, 6),
          'variables': int(lp.get('atoms', 0)),
          'generated_rules': int(lp.get('rules', 0)),
          'branches': int(solvers.get('choices', 0)),
          'conflicts': int(solvers.get('conflicts', 0)),
          'timed_out': bool(stats.get('timed_out', False)),
          'model_count': int(stats.get('model_count', 0)),
          'error': '',
        })

  return rows


def write_csv(rows, out_csv: Path):
  out_csv.parent.mkdir(parents=True, exist_ok=True)
  fieldnames = [
    'experiment', 'program', 'test', 'run', 'status',
    'min_cost', 'total_time_s', 'solving_time_s', 'grounding_time_s',
    'variables', 'generated_rules', 'branches', 'conflicts',
    'timed_out', 'model_count', 'error',
  ]
  with out_csv.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def plot_metrics(rows, out_dir: Path):
  out_dir.mkdir(parents=True, exist_ok=True)
  ok_rows = [r for r in rows if r.get('status') == 'ok']
  if not ok_rows:
    return

  buckets = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
  tests = set()
  programs = set()
  for row in ok_rows:
    test = row['test']
    program = row['program']
    tests.add(test)
    programs.add(program)
    for metric, _ in METRICS:
      val = row.get(metric)
      if val is None:
        continue
      try:
        buckets[test][program][metric].append(float(val))
      except (TypeError, ValueError):
        continue

  tests = sorted(tests)
  programs = sorted(programs)
  width = 0.8 / max(1, len(programs))
  center = (len(programs) - 1) / 2

  for metric_key, metric_label in METRICS:
    x = np.arange(len(tests))
    fig, ax = plt.subplots(figsize=(max(10, len(tests) * 0.75), 5))
    for i, program in enumerate(programs):
      y_vals = [
        mean(buckets[test][program][metric_key])
        if buckets[test][program][metric_key] else 0.0
        for test in tests
      ]
      offset = (i - center) * width
      ax.bar(x + offset, y_vals, width, label=program, alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(tests, rotation=35, ha='right')
    ax.set_ylabel(metric_label)
    ax.set_title(metric_label)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / f'{metric_key}.png', dpi=150)
    plt.close(fig)


def main():
  parser = argparse.ArgumentParser(description='Benchmark plan_compare experiments and plot metrics.')
  parser.add_argument('--repeats', '-r', type=int, default=1, help='Number of runs per test/program')
  parser.add_argument('--timeout', '-t', type=float, default=None, help='Override clingo timeout (seconds)')
  parser.add_argument('--experiment', '-e', default=None, help='Run a single experiment folder by name')
  args = parser.parse_args()

  tests = sorted(plan_cases.items())
  order = ['full', 'sem_6', 'sem_5', 'sem_4', 'sem_3', 'sem_2', 'sem_1', 'empty']
  tests = sorted(tests, key=lambda item: order.index(item[0]) if item[0] in order else len(order))
  git_short = _git_short()

  for exp_dir, lp_files in list_experiments():
    if args.experiment and exp_dir.name != args.experiment:
      continue

    out_dir = RESULTS_ROOT / f"{exp_dir.name}-{git_short}"
    rows = run_experiment(exp_dir, lp_files, tests, repeats=args.repeats, timeout=args.timeout, out_dir=out_dir)

    write_csv(rows, out_dir / 'results.csv')
    plot_metrics(rows, out_dir)
    print(f"Wrote results for {exp_dir.name} to {out_dir}")


if __name__ == '__main__':
  main()
