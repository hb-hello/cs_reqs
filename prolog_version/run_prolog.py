import subprocess, tempfile, os

_XSB        = '/home/leto/opt/XSB/bin/xsb'
_PL_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024.pl')
_REQS       = ['intro', 'adv', 'elect', 'calc', 'alg', 'sta',
               'sci', 'ethics', 'writing', 'credits_at_SB']

# ── rule extraction ───────────────────────────────────────────────────────────

def _rules():
    # extract everything from cs_reqs_2024.pl before the '% test' section
    with open(_PL_FILE) as f:
        lines = []
        for line in f:
            if line.strip() == '% test':
                break
            lines.append(line)
    return ''.join(lines)

# ── check infrastructure (appended to the extracted rules) ───────────────────

_CHECK_INFRA = """
check_req(Item, Pred) :-
    (catch(call(Pred), _, fail) ->
        write(Item), write(':true'), nl,
        findall(C, wit(Item, C), Cs),
        print_wits(Cs)
    ;
        write(Item), write(':false'), nl
    ).

print_wits([]).
print_wits([H|T]) :- write('wit:'), write(H), nl, print_wits(T).

check_all :-
    check_req(intro, intro_req).
"""

# ── public API ────────────────────────────────────────────────────────────────

def run_prolog(taken):
    facts = '\n'.join(
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')."
        for t in taken
    )
    query = _rules() + '\n' + facts + '\n' + _CHECK_INFRA + '\n:- check_all, halt.\n'

    with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as f:
        f.write(query)
        tmp = f.name
    try:
        r = subprocess.run(
            [_XSB, '--noprompt', '--nobanner', '--quietload', tmp],
            capture_output=True, text=True, timeout=30
        )
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
    if current:
        checked[current] = (True, sorted(wits))
    checked['degree'] = (all(checked.get(r, (False,))[0] for r in _REQS), [])
    return checked
