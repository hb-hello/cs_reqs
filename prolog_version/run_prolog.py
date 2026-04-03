import subprocess, tempfile, os

_PL_FILE_SWI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024swi.pl')
_PL_FILE_XSB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024xsb.pl')

_ENGINES = {
    'xsb': {
        'bin':       'xsb',
        'flags':     ['--noprompt', '-q'],
        'preamble':  f":- ['{_PL_FILE_XSB}'].\n:- retractall(taken(_,_,_,_,_)).",
        # XSB needs the file loaded via -e, not as a positional arg
        'cmd_extra': lambda tmp: ['-e', f"['{tmp}'], halt."],
    }
}

_REQS       = ['intro', 'adv', 'elect', 'calc', 'alg', 'sta',
               'sci', 'ethics', 'writing', 'credits_at_SB']

# ── check infrastructure (appended to the extracted rules) ───────────────────

_REQS = ['intro', 'adv', 'elective', 'math', 'science', 'res123', 'res23', 'ethics']

# Prolog printed to stdout; _parse reads "name:true/false" and "wit:Id" lines
_CHECK_INFRA = """\
check_req(Name, Goal) :-
    ( call(Goal) ->
        write(Name), write(':true'), nl,
        forall(wit(Name, Id), (write('wit:'), write(Id), nl))
    ;
        write(Name), write(':false'), nl
    ).

:- catch((
        check_req(intro,    intro_req),
        check_req(adv,      advanced_req),
        check_req(elective, elective_req),
        check_req(math,     math_req),
        check_req(science,  sci_subset_req),
        check_req(res123,   satisfied_residency_123),
        check_req(res23,    satisfied_residency_23),
        check_req(ethics,   passed_all(ethics_comm))
    ), E, (write('error:'), writeln(E))).

:- halt.
"""

# ── public API ────────────────────────────────────────────────────────────────

def run_prolog(taken, engine='xsb'):
    if engine == 'swi':
        return run_swi(taken)

    cfg = _ENGINES[engine]
    facts = '\n'.join(
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')."
        for t in taken
    )
    content = cfg['preamble'] + '\n' + facts + '\n' + _CHECK_INFRA + '\n'

    with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as f:
        f.write(content)
        tmp = f.name

    try:
        r = subprocess.run(
            [cfg['bin']] + cfg['flags'],
            input=f"['{tmp}'], halt.\n",   # ← pipe load+halt via stdin
            capture_output=True, text=True, timeout=30
        )
        print(r.stdout)
        if r.stderr:
            print("STDERR:", r.stderr)
        return _parse(r.stdout)
    finally:
        os.unlink(tmp)

def _parse(output):
    checked, current, wits = {}, None, []
    for line in output.splitlines():
        line = line.strip()
        if line.endswith(':true'):
            if current:
                checked[current] = (True, sorted(wits))
            current, wits = line[:-5], []
        elif line.endswith(':false'):
            if current:
                checked[current] = (True, sorted(wits))
            current = None
            checked[line[:-6]] = (False, [])
        elif line.startswith('wit:'):
            wits.append(line[4:])   # ← was wits[4:] (bug)
    if current:
        checked[current] = (True, sorted(wits))
    checked['degree'] = (all(checked.get(r, (False,))[0] for r in _REQS), [])
    return checked


def run_swi(taken):
    facts = (
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')"
        for t in taken
    )

    import janus_swi as janus
    janus.consult(_PL_FILE_SWI)
    reqs = ('intro', 'adv', 'elect', 'sci', 'ethics_comm', 'math')
    queries = [('wit', req, 'Q') for req in reqs]
    queries.append(('all_requirements', None, None))
    checked = {}
    for f in facts:
        janus.query_once(f"assertz({f})")
    for pred, first, second in queries:
        arg = (first if first else '') + (f', {second}' if second else '')
        sat = False
        courses = []
        with janus.query(f"{pred}({arg})") as results:
            for d in results:
                sat = d.get('truth', False)
                if second and second in d:
                    courses.append(d[second])
            checked[first if second else pred] = (sat, courses)
    checked['degree'] = checked.pop('all_requirements')
    checked['ethics'] = checked.pop('ethics_comm')
    checked['writing'] = checked['ethics']
    checked['sta'] = checked.pop('math')
    checked['calc'] = checked['sta']
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
    # engine = sys.argv[1] if len(sys.argv) > 1 else 'xsb'
    pprint(run_prolog(taken, 'swi'))
    pprint(run_prolog(taken, 'xsb'))
    # run_swi(taken)

