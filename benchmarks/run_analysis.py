## Unified combo analysis for OR-Tools and Clingo.
## Usage (from repo root):
##   python -m benchmarks.run_analysis                    # both solvers
##   python -m benchmarks.run_analysis --ortools-only     # OR-Tools only
##   python -m benchmarks.run_analysis --clingo-only      # Clingo only

import sys, os, json, argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from benchmarks.ortools.model_builder import (
    run_combos as ortools_combos, print_combo_table as ortools_table,
    ALL_REQS as ORTOOLS_ALL_REQS, ALL_FEATURES as ORTOOLS_ALL_FEATURES,
)
from benchmarks.clingo.model_builder import (
    run_combos as clingo_combos, print_combo_table as clingo_table,
    ALL_REQS as CLINGO_ALL_REQS, ALL_FEATURES as CLINGO_ALL_FEATURES,
)

# ── configurable enable sets ─────────────────────────────────────────────────
ENABLED_REQS = {'intro', 'adv', 'elect', 'sci'}
ENABLED_FEATURES = {'offering', 'prereqs', 'credit_limits'}


def main():
    parser = argparse.ArgumentParser(description='Combo analysis: OR-Tools + Clingo')
    parser.add_argument('--ortools-only', action='store_true')
    parser.add_argument('--clingo-only', action='store_true')
    args = parser.parse_args()

    run_ortools = not args.clingo_only
    run_clingo = not args.ortools_only

    results = {}

    if run_ortools:
        print('\n=== OR-Tools combos (empty history) ===')
        results['ortools'] = ortools_combos(ENABLED_REQS, ENABLED_FEATURES)
        ortools_table(results['ortools'])

    if run_clingo:
        print('\n=== Clingo combos (empty history, plan1) ===')
        results['clingo'] = clingo_combos(ENABLED_REQS, ENABLED_FEATURES)
        clingo_table(results['clingo'])

    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    out_dir = Path(__file__).resolve().parent / f'analysis-{stamp}'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'analysis.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f'\nWrote {out_path}')


if __name__ == '__main__':
    main()