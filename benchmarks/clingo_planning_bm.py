import argparse
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import mean
from clingo_version.run_clingo import run_planner_benchmark, run_planner_with_heuristics
from benchmarks.run_bm import plan_cases

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PLAN_COMPARE_DIR = ROOT / 'clingo_version' / 'plan_compare'
RESULTS_ROOT = ROOT / 'benchmarks' / 'clingo_bm_results'

ROW_FIELDS = [
  'experiment', 'program', 'test', 'run',
  'min_cost', 'total_time_s', 'solving_time_s', 'grounding_time_s',
  'variables', 'generated_rules', 'domain_choices', 'branches', 'conflicts',
  'timed_out', 'model_count',
]

def _git_short() -> str:
  try:
    result = subprocess.run(['git', 'rev-parse', '--short=6', 'HEAD'], cwd=str(ROOT), capture_output=True, text=True, check=True)
    return result.stdout.strip() or 'unknown'
  except Exception:
    return 'unknown'

def build_clingo_kwargs():
  return {}

def _normalize_for_json(value):
  if isinstance(value, dict):
    return {
      (k if isinstance(k, (str, int, float, bool)) or k is None else str(k)):
      _normalize_for_json(v)
      for k, v in value.items()
    }
  if isinstance(value, (list, tuple, set)):
    return [_normalize_for_json(v) for v in value]
  return value


def log_checked_schedule(out_dir: Path, payload: dict):
  out_dir.mkdir(parents=True, exist_ok=True)
  log_path = out_dir / 'checked_schedule.log'
  normalized = _normalize_for_json(payload)
  with log_path.open('a', encoding='utf-8') as f:
    f.write(json.dumps(normalized, sort_keys=True))
    f.write('\n')


def build_row(*, experiment, program, test, run, min_cost, total_time, solve_time, grounding_time, lp, solvers, stats):
  return {
    'experiment': experiment,
    'program': program,
    'test': test,
    'run': run,
    'min_cost': min_cost,
    'total_time_s': round(total_time, 6),
    'solving_time_s': round(solve_time, 6),
    'grounding_time_s': round(grounding_time, 6),
    'variables': int(lp.get('atoms', 0)),
    'generated_rules': int(lp.get('rules', 0)),
    'domain_choices': int(solvers.get('domain_choices', 0) or 0),
    'branches': int(solvers.get('choices', 0)),
    'conflicts': int(solvers.get('conflicts', 0)),
    'timed_out': bool(stats.get('timed_out', False)),
    'model_count': int(stats.get('model_count', 0)),
  }


def run_experiment(experiment_dir: Path, lp_files: list[Path], tests, repeats: int, timeout: float | None, out_dir: Path, with_heuristics=False):
  rows = []
  out_dir.mkdir(parents=True, exist_ok=True)
  for test_name, taken in tests:
    clingo_kwargs = build_clingo_kwargs()
    if timeout is not None:
      clingo_kwargs['timeout'] = timeout

    for program_path in lp_files:
      for run_idx in range(1, repeats + 1):
        print(f"Running {experiment_dir.name} | {program_path.stem} | {test_name} | run={run_idx}")
        planner_func = run_planner_with_heuristics if with_heuristics else run_planner_benchmark

        checked, schedule, stats = planner_func(
          program_lp=str(program_path),
          taken_set=taken,
          **clingo_kwargs,
        )

        log_checked_schedule(out_dir, {
          'experiment': experiment_dir.name,
          'program': program_path.stem,
          'test': test_name,
          'run': run_idx,
          'checked': checked,
          'schedule': schedule,
          'stats': stats,
        })

        times = stats.get('summary', {}).get('times', {})
        total_time = float(times.get('total', 0.0))
        solve_time = float(times.get('solve', 0.0))
        grounding_time = total_time - solve_time
        min_cost = stats.get('min_cost')

        print(f"{program_path.stem} {test_name} {total_time} {min_cost}")

        lp = stats.get('problem', {}).get('lp', {})
        solvers = stats.get('solving', {}).get('solvers', {})

        rows.append(build_row(
          experiment=experiment_dir.name,
          program=program_path.stem,
          test=test_name,
          run=run_idx,
          min_cost=min_cost,
          total_time=total_time,
          solve_time=solve_time,
          grounding_time=grounding_time,
          lp=lp,
          solvers=solvers,
          stats=stats,
        ))

  return rows


def write_csv(rows, out_csv: Path):
  out_csv.parent.mkdir(parents=True, exist_ok=True)
  fieldnames = ROW_FIELDS
  with out_csv.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def plot_metrics(rows, out_dir: Path):
  out_dir.mkdir(parents=True, exist_ok=True)
  if not rows:
    return

  metric_keys = [
    key for key in ROW_FIELDS
    if key not in {'experiment', 'program', 'test', 'run'}
  ]

  buckets = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
  tests = set()
  programs = set()
  for row in rows:
    test = row['test']
    program = row['program']
    tests.add(test)
    programs.add(program)
    for metric in metric_keys:
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

  for metric_key in metric_keys:
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
    ax.set_ylabel(metric_key)
    ax.set_title(metric_key)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / f'{metric_key}.png', dpi=150)
    plt.close(fig)


def main():
  parser = argparse.ArgumentParser(description='Benchmark plan_compare experiments and plot metrics.')
  parser.add_argument('--repeats', '-r', type=int, default=1, help='Number of runs per test/program')
  parser.add_argument('--timeout', '-t', type=float, default=None, help='Override clingo timeout (seconds)')
  parser.add_argument('--experiment', '-e', nargs='+', required=True, help='Program names to run, without .lp extension. (e.g., exp_plan exp_baseline).')
  parser.add_argument('--tests', '-ts', nargs='*', default=None, help='tests to run (e.g., sem_1 sem_2). If not specified, runs all tests.')
  parser.add_argument('--name', '-n', required=True, help='experiment name for the run.')
  parser.add_argument('--with-heuristics', '-heu', action='store_true', help='Run planner with heuristics, defined in run_clingo')
  args = parser.parse_args()

  test_cases = [(name, taken) for name, taken in plan_cases.items()]
  if args.tests:
    test_cases = [(name, taken) for name, taken in test_cases if name in set(args.tests)]
  order = ['complete', 'sem_7', 'sem_6', 'sem_5', 'sem_4', 'sem_3', 'sem_2', 'sem_1', 'empty']
  test_cases = sorted(test_cases, key=lambda item: order.index(item[0]) if item[0] in order else len(order))

  git_short = _git_short()

  test_programs = [
    lp for lp in PLAN_COMPARE_DIR.rglob('exp*.lp')
    if lp.is_file() and lp.stem in set(args.experiment)
  ]
    
  out_dir = RESULTS_ROOT / args.name
  if out_dir.exists():
    base_name = args.name
    counter = 1
    match = re.match(r"^(.*?)-(\d+)$", args.name)
    if match:
      base_name = match.group(1)
      counter = int(match.group(2)) + 1
    while True:
      candidate = RESULTS_ROOT / f"{base_name}-{counter}"
      if not candidate.exists():
        out_dir = candidate
        break
      counter += 1

  print("Selected programs:", ", ".join(sorted({lp.stem for lp in test_programs})))
  print("Results will be saved to:", out_dir)
  # if input("Proceed? [y/N]: ").strip().lower() not in {"y", "yes"}:
  #   print("Aborted.")
  #   return

  rows = run_experiment(out_dir, test_programs, test_cases, repeats=args.repeats, timeout=args.timeout, out_dir=out_dir, with_heuristics=args.with_heuristics)

  write_csv(rows, out_dir / 'results.csv')
  plot_metrics(rows, out_dir)
  print(f"Wrote results to {out_dir}")

if __name__ == '__main__':
  main()
