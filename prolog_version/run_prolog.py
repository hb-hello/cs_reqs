import os
import re
import time

import pexpect

_PL_FILE_SWI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024swi.pl')
_PL_FILE_XSB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024xsb.pl')

# ── public API ────────────────────────────────────────────────────────────────

def run_prolog(taken, engine='xsb', swi_with_witness=False, return_timing=False):
    if engine == 'swi':
        return run_swi(taken, with_witness=swi_with_witness, return_timing=return_timing)

    child = pexpect.spawn('xsb', encoding='utf-8', timeout=20)
    child.expect(r'\| \?-')

    def run_cmd(command):
        child.sendline(command)
        child.expect(r'\| \?-')
        return child.before.strip()

    run_cmd(f"['{_PL_FILE_XSB}']" + ".")

    run_cmd("retractall(taken(_,_,_,_,_)).")

    for t in taken:
        fact = f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')"
        run_cmd(f"assertz({fact}).")

    query_output = run_cmd("measure_wall(all_requirements).")

    child.sendline('halt.')
    child.expect(pexpect.EOF)

    ok = 'result(yes)' in query_output.lower()
    time_match = re.search(r"wall\s*time:\s*([-+0-9.eE]+)\s*(ms|s)", query_output.lower())
    if time_match:
        raw = float(time_match.group(1))
        unit = time_match.group(2)
        prolog_eval_s = raw / 1000.0 if unit == 'ms' else raw
    else:
        prolog_eval_s = None
    if return_timing:
        return {'ok': ok, 'prolog_eval_s': prolog_eval_s, 'engine': 'xsb'}
    return ok


def run_swi(taken, with_witness=True, return_timing=False):
    facts = (
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')"
        for t in taken
    )

    import janus_swi as janus
    janus.consult(_PL_FILE_SWI)

    t0 = time.perf_counter()
    janus.query_once("retractall(taken(_,_,_,_,_))")

    for f in facts:
        janus.query_once(f"assertz({f})")

    if not with_witness:
        ok = janus.query_once("all_requirements").get('truth', False)
        elapsed = time.perf_counter() - t0
        if return_timing:
            return {'ok': ok, 'prolog_eval_s': elapsed, 'engine': 'swi'}
        return ok

    reqs = ('intro', 'adv', 'elect', 'sci', 'ethics_comm', 'math')
    queries = [('wit', req, 'Q') for req in reqs]
    queries.append(('all_requirements', None, None))
    checked = {}
    for pred, first, second in queries:
        arg = (first if first else '') + (f', {second}' if second else '')
        goal = pred if not arg else f"{pred}({arg})"
        sat = False
        courses = []
        with janus.query(goal) as results:
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
    elapsed = time.perf_counter() - t0
    if return_timing:
        return {
            'ok': checked.get('degree', (False, []))[0],
            'prolog_eval_s': elapsed,
            'engine': 'swi',
            'checked': checked,
        }
    return checked


# def collect_wit
    

if __name__ == '__main__':
    import sys
    from collections import namedtuple
    from pprint import pprint
    from tests.planning.planner_test_cases import FULL
    Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])
    taken = [
        Taken('CSE 114', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 214', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 216', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 215', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 220', 3, 'A', (2024,2), 'SBU'),
    ]

    taken = [Taken(cid, 3, 'A', (2024,2), 'SBU') for cid in FULL]
    # engine = sys.argv[1] if len(sys.argv) > 1 else 'xsb'
    # pprint(run_prolog(taken, 'swi'))
    pprint(run_prolog(taken, 'xsb', return_timing=True))
    # run_swi(taken)

