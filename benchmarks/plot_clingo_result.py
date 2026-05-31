import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np


ROW_FIELDS = [
  'experiment', 'program', 'test', 'run',
  'min_cost', 'total_time_s', 'solving_time_s', 'grounding_time_s',
  'variables', 'generated_rules', 'domain_choices', 'branches', 'conflicts',
  'timed_out', 'model_count',
]


def read_csv_rows(csv_path: Path):
  rows = []
  with csv_path.open('r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
      rows.append(row)
  return rows


def _resolve_metric_keys(rows, metrics=None):
  if metrics:
    return metrics
  if not rows:
    return []
  keys = list(rows[0].keys())
  return [k for k in keys if k not in {'experiment', 'program', 'test', 'run'}]


def plot_metrics(rows, out_dir: Path, metrics=None):
  out_dir.mkdir(parents=True, exist_ok=True)
  if not rows:
    return

  metric_keys = _resolve_metric_keys(rows, metrics)
  if not metric_keys:
    return

  buckets = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
  tests = set()
  programs = set()
  for row in rows:
    test = row.get('test')
    program = row.get('program')
    if test is None or program is None:
      continue
    tests.add(test)
    programs.add(program)
    for metric in metric_keys:
      val = row.get(metric)
      if val is None or val == '':
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
  parser = argparse.ArgumentParser(description='Plot benchmark metrics from a CSV file.')
  parser.add_argument('-csv', '--csv', dest='csv_path', required=True, help='Path to results CSV')
  parser.add_argument('-m', '--metrics', nargs='*', default=None, help='Metrics to plot (defaults to all)')
  args = parser.parse_args()

  csv_path = Path(args.csv_path)
  rows = read_csv_rows(csv_path)
  plot_metrics(rows, csv_path.parent, metrics=args.metrics)


if __name__ == '__main__':
  main()
