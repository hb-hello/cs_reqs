## Unified plot script for combo analysis (OR-Tools + Clingo).
## Usage (from repo root):
##   python -m benchmarks.plot_analysis [analysis-dir]
##
## If no dir given, uses the latest benchmarks/analysis-* directory.

import sys, json
from pathlib import Path

from benchmarks.ortools.plot_analysis import (
    _plot_combo_heatmap, _plot_combo_heatmap_pct,
)


def _latest_analysis_dir():
    base = Path(__file__).resolve().parent
    dirs = sorted(base.glob('analysis-*'), reverse=True)
    return dirs[0] if dirs else None


def plot_solver_combos(combos, solver, metrics, out_dir):
    for metric, label in metrics:
        _plot_combo_heatmap(
            combos, metric,
            f'{label} — {solver} combos (one req × one feature)\nred = more · blue = fewer',
            label,
            out_dir / f'{solver}_combo_{metric}.png')
        _plot_combo_heatmap_pct(
            combos, metric,
            f'{label} as % of all-features — {solver}\n100% = feature alone captures full complexity',
            out_dir / f'{solver}_combo_{metric}_pct.png')


def main():
    if len(sys.argv) >= 2:
        analysis_dir = Path(sys.argv[1])
    else:
        analysis_dir = _latest_analysis_dir()
        if analysis_dir is None:
            print('No analysis-* dirs found. Run benchmarks.run_analysis first.')
            sys.exit(1)
        print(f'Using latest: {analysis_dir.name}')

    json_path = analysis_dir / 'analysis.json'
    if not json_path.exists():
        print(f'No analysis.json in {analysis_dir}')
        sys.exit(1)

    with open(json_path) as f:
        data = json.load(f)

    out_dir = analysis_dir
    print('Writing plots...')

    if 'ortools' in data:
        print('  OR-Tools:')
        plot_solver_combos(data['ortools'], 'ortools',
            [('branches', 'Branches'), ('conflicts', 'Conflicts'), ('booleans', 'Booleans')],
            out_dir)

    if 'clingo' in data:
        print('  Clingo:')
        plot_solver_combos(data['clingo'], 'clingo',
            [('choices', 'Choices'), ('conflicts', 'Conflicts'), ('atoms', 'Atoms')],
            out_dir)

    print('Done.')


if __name__ == '__main__':
    main()