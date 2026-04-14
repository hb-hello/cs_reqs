## Clingo combo builder — adapted from clingo_version/run_clingo.py.
## Builds and solves clingo plan1 models with selective reqs and features.
## enable_reqs: set of requirement names to include (None = all).
## enable_features: set of planning feature names to include (None = all).
##   'offering'      -- course offered-terms constraints
##   'prereqs'       -- prerequisite/corequisite/antireq constraints
##   'credit_limits' -- per-semester credit cap

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import clingo
from clingo_version.configs import MAIN_LP, KB_LP
from clingo_version.run_clingo import ClingoContext, MIN_SEM, NUM_SEMS, NUM_CREDITS_PER_SEM
from course_kb.course_kb import COURSE_OFFERED_TERMS, rel_sem_to_term

ALL_REQS = {'intro', 'adv', 'elect', 'calc', 'alg', 'sta', 'sci', 'ethics', 'writing', 'credits_at_SB'}
ALL_FEATURES = {'offering', 'prereqs', 'credit_limits'}


def solve_combo(enable_reqs=None, enable_features=None, num_sems=NUM_SEMS, timeout=600):
    reqs_on = ALL_REQS if enable_reqs is None else enable_reqs
    features_on = ALL_FEATURES if enable_features is None else enable_features

    min_sem = MIN_SEM
    start_sem = 1
    finish_sem = start_sem + num_sems - 1
    credits_per_sem = NUM_CREDITS_PER_SEM if 'credit_limits' in features_on else 999

    ctrl_args = ["0", "-Wno-atom-undefined",
                 f"-c start_sem={start_sem}", f"-c finish_sem={finish_sem}",
                 f"-c sem_max_credits={credits_per_sem}"]

    # build facts to inject
    facts = []

    # auto-satisfy disabled reqs
    for r in ALL_REQS - reqs_on:
        facts.append(f'req({r}).')

    # trivially satisfy prereq/coreq/pre_or_coreq when disabled
    if 'prereqs' not in features_on:
        facts.extend([
            'prereq(Id, Sem) :- offered(Id, Sem).',
            'coreq(Id, Sem) :- offered(Id, Sem).',
            'pre_or_coreq(Id, Sem) :- offered(Id, Sem).',
        ])

    # offered facts: all terms when offering disabled, else respect course_offered_terms
    offering_terms = COURSE_OFFERED_TERMS if 'offering' in features_on else {cid: {1, 2, 3, 4} for cid in COURSE_OFFERED_TERMS}
    for cid, terms in offering_terms.items():
        for sem in range(start_sem, finish_sem + 1):
            if rel_sem_to_term(sem, min_sem) in terms:
                facts.append(f'offered("{cid}", {sem}).')

    ctrl = clingo.Control(ctrl_args)
    ctrl.load(MAIN_LP)
    ctrl.load(KB_LP)
    ctrl.add("input", [], "\n".join(facts))
    ctrl.ground([("base", []), ("input", []), ("plan1", [])], context=ClingoContext())

    # solve
    min_cost = None
    model_count = 0
    def on_model(model):
        nonlocal min_cost, model_count
        model_count += 1
        if model.cost is not None:
            cost = tuple(model.cost)
            if min_cost is None or cost < min_cost:
                min_cost = cost

    timed_out = False
    with ctrl.solve(on_model=on_model, async_=True) as handle:
        finished = handle.wait(timeout)
        if not finished:
            timed_out = True
            handle.cancel()
        handle.wait()

    # collect stats
    lp = ctrl.statistics.get('problem', {}).get('lp', {})
    solvers = ctrl.statistics.get('solving', {}).get('solvers', {})
    times = ctrl.statistics.get('summary', {}).get('times', {})
    total_t = float(times.get('total', 0))
    solve_t = float(times.get('solve', 0))
    return {
        'atoms': int(lp.get('atoms', 0)), 'rules': int(lp.get('rules', 0)),
        'choices': int(solvers.get('choices', 0)), 'conflicts': int(solvers.get('conflicts', 0)),
        'total_s': round(total_t, 4), 'solve_s': round(solve_t, 4),
        'ground_s': round(total_t - solve_t, 4),
        'timed_out': timed_out, 'min_cost': list(min_cost) if min_cost else None,
    }


def run_combos(reqs_to_test=None, features_to_test=None, timeout=600):
    reqs_to_test = sorted(reqs_to_test or ALL_REQS)
    features_to_test = sorted(features_to_test or ALL_FEATURES)

    results = {}
    for req_name in reqs_to_test:
        results[f"{req_name}+none"] = {'req': req_name, 'feature': 'none',
            **solve_combo(enable_reqs={req_name}, enable_features=set(), timeout=timeout)}
        for feat_name in features_to_test:
            results[f"{req_name}+{feat_name}"] = {'req': req_name, 'feature': feat_name,
                **solve_combo(enable_reqs={req_name}, enable_features={feat_name}, timeout=timeout)}
        results[f"{req_name}+all"] = {'req': req_name, 'feature': 'all',
            **solve_combo(enable_reqs={req_name}, enable_features=ALL_FEATURES, timeout=timeout)}

    # aggregate column: all tested reqs active together
    all_reqs = set(reqs_to_test)
    results['all+none'] = {'req': 'all', 'feature': 'none',
        **solve_combo(enable_reqs=all_reqs, enable_features=set(), timeout=timeout)}
    for feat_name in features_to_test:
        results[f"all+{feat_name}"] = {'req': 'all', 'feature': feat_name,
            **solve_combo(enable_reqs=all_reqs, enable_features={feat_name}, timeout=timeout)}
    results['all+all'] = {'req': 'all', 'feature': 'all',
        **solve_combo(enable_reqs=all_reqs, enable_features=ALL_FEATURES, timeout=timeout)}
    return results


def print_combo_table(results):
    metrics = ['atoms', 'rules', 'choices', 'conflicts', 'total_s']
    header = f"{'combo':<30}" + ''.join(f'{m:>14}' for m in metrics)
    print(header)
    print('-' * len(header))
    for label in sorted(results):
        row = results[label]
        vals = ''.join(f'{_fmt(row.get(m, "n/a")):>14}' for m in metrics)
        print(f"{label:<30}{vals}")


def _fmt(val):
    if isinstance(val, float): return f'{val:.4f}'
    return str(val)