import subprocess, tempfile, os

_PL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024.pl')

_ENGINES = {
    'xsb': {
        'bin':      '/home/leto/opt/XSB/bin/xsb',
        'flags':    ['--noprompt', '--nobanner', '--quietload'],
        # XSB lacks aggregate_all/3 and memberchk/2 as builtins
        'preamble': ':- import sum_list/2 from lists.\n:- import memberchk/2 from basics.\naggregate_all(sum(X), Goal, Total) :- findall(X, Goal, Xs), sum_list(Xs, Total).\n',
    },
    'swi': {
        'bin':      'swipl',
        'flags':    ['-q'],
        'preamble': ':- use_module(library(aggregate)).\n',
    },
}
_REQS       = ['intro', 'adv', 'elect', 'calc', 'alg', 'sta',
               'sci', 'ethics', 'writing', 'credits_at_SB']

# ── rule extraction ───────────────────────────────────────────────────────────

def _rules():
    # extract everything from cs_reqs_2024.pl before the '% test' section,
    # stripping discontiguous directives (XSB doesn't support F/N notation)
    with open(_PL_FILE) as f:
        lines = []
        for line in f:
            if line.strip() == '% test':
                break
            if not line.strip().startswith(':- discontiguous'):
                lines.append(line)
    return ''.join(lines)

# ── check infrastructure (appended to the extracted rules) ───────────────────

_CHECK_INFRA = """
wit(intro, Q).
wit(intro, Q).
"""

# ── public API ────────────────────────────────────────────────────────────────

def run_prolog(taken, engine='swi'):
    cfg = _ENGINES[engine]
    facts = '\n'.join(
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')."
        for t in taken
    )
    query = cfg['preamble'] + '\n' + facts + '\n' + _CHECK_INFRA + '\n'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as f:
        f.write(query)
        tmp = f.name
    try:
        r = subprocess.run(
            [cfg['bin']] + cfg['flags'] + [tmp],
            capture_output=True, text=True, timeout=30
        )
        print(r.stdout)
        return _parse(r.stdout)
    finally:
        os.unlink(tmp)

def _parse(output):
    checked, current, wits = {}, None, []
    for line in output.splitlines():
        line = line.strip()
        if line.endswith(':true'):
            if current: checked[current] = (True, sorted(wits))
            current, wits = line[:-5], []
        elif line.endswith(':false'):
            if current: checked[current] = (True, sorted(wits))
            current = None
            checked[line[:-6]] = (False, [])
        elif line.startswith('wit:'):
            wits.append(line[4:])
        elif line.startswith('Q = '):
            wits.append(wits[4:])
    if current:
        checked[current] = (True, sorted(wits))
    checked['degree'] = (all(checked.get(r, (False,))[0] for r in _REQS), [])
    return checked


def run_swi(taken):
    facts = (
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')."
        for t in taken
    )

    import janus_swi as janus
    janus.consult(_PL_FILE)
    reqs = ('intro', 'adv', 'elect', 'sci')
    queries = [('wit', req, 'Q') for req in reqs]
    queries.append(('all_requirements', None, None))
    checked = {}
    for f in facts:
        janus.query_once(f)
    for pred, first, second in queries:
        arg = (first if first else '') + (f', {second}' if second else '')
        result = janus.query(f"{pred}({arg})")
        sat = False
        courses = []
        for d in result:
            sat = d['truth']
            courses.append(d[second])
        checked.setdefault(first if second else pred, []).append((sat, courses))
    checked['degree'] = checked['all_requirements'].pop()
    print(checked)
    return checked


# def collect_wit
    

if __name__ == '__main__':
    import sys
    from collections import namedtuple
    from pprint import pprint
    Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])
    taken = [
        Taken('CSE 114', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 214', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 216', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 215', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 220', 3, 'A', (2024,2), 'SBU'),
    ]
    engine = sys.argv[1] if len(sys.argv) > 1 else 'xsb'
    # pprint(run_prolog(taken, engine))
    run_swi(taken)

