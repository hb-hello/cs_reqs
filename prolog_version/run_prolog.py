import os
import re
import time

import pexpect
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_PL_FILE_SWI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024swi.pl')
_PL_FILE_XSB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024xsb.pl')


def _normalize_where(where):
    key = str(where).strip().upper()
    if key == 'SB':
        return 'SBU'
    return key

# ── public API ────────────────────────────────────────────────────────────────

def _parse_prolog_list(text):
    """Parse a Prolog list written via write/1, e.g. ['CSE 114','CSE 373'] → list of strings."""
    m = re.search(r'\[([^\]]*)\]', text)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []
    items = re.findall(r"'([^']*)'|([^\s,]+)", inner)
    return [a or b for a, b in items if a or b]


def run_prolog(taken, engine='xsb', swi_with_witness=False, return_timing=False):
    if engine == 'swi':
        return run_swi(taken, with_witness=swi_with_witness, return_timing=return_timing)

    child = pexpect.spawn('xsb', encoding='utf-8', timeout=20)
    child.expect(r'\| \?-')

    def run_cmd(command):
        child.sendline(command)
        child.expect(r'\| \?-')
        return child.before.strip()

    run_cmd(f"['{_PL_FILE_XSB}'].")
    run_cmd("retractall(taken(_,_,_,_,_)).")

    for t in taken:
        where = _normalize_where(t.where)
        fact = f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{where}')"
        run_cmd(f"assertz({fact}).")

    query_output = run_cmd("measure_wall(all_requirements).")
    ok = 'result(yes)' in query_output.lower()
    time_match = re.search(r"wall\s*time:\s*([-+0-9.eE]+)\s*(ms|s)", query_output.lower())
    if time_match:
        raw = float(time_match.group(1))
        unit = time_match.group(2)
        prolog_eval_s = raw / 1000.0 if unit == 'ms' else raw
    else:
        prolog_eval_s = None

    # collect per-requirement witnesses
    req_predicates = {
        'intro':   'intro_req',
        'adv':     'advanced_req',
        'elect':   'elective_req',
        'sci':     'sci_subseq_req',
        'ethics':  "passed('CSE 312')",
        'writing': "passed('CSE 300')",
        'calc':    'calc_req',
        'alg':     'alg_req',
        'sta':     'sta_req',
    }
    checked = {}
    for key, pred in req_predicates.items():
        sat_out = run_cmd(f"({pred} -> write(yes) ; write(no)).")
        sat = 'yes' in sat_out
        wit_out = run_cmd(f"findall(Id, wit({key}, Id), Ids), write(Ids).")
        courses = _parse_prolog_list(wit_out)
        checked[key] = (sat, courses)

    t123_out = run_cmd("credits_at_sb_cat123(T), write(T).")
    t23_out  = run_cmd("credits_at_sb_cat23(T), write(T).")
    t123_m = re.search(r'[\d.]+', t123_out)
    t23_m  = re.search(r'[\d.]+', t23_out)
    t123 = float(t123_m.group()) if t123_m else 0.0
    t23  = float(t23_m.group())  if t23_m  else 0.0
    checked['credits_at_SB'] = (t123 >= 24 and t23 >= 18,
                                 [f'items123 = {int(t123)}', f'items23 = {int(t23)}'])
    checked['degree'] = (ok, [])

    child.sendline('halt.')
    child.expect(pexpect.EOF)

    if return_timing:
        return {'ok': ok, 'prolog_eval_s': prolog_eval_s, 'engine': 'xsb', 'checked': checked}
    return checked


def run_swi(taken, with_witness=True, return_timing=False):
    facts = (
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{_normalize_where(t.where)}')"
        for t in taken
    )

    import janus_swi as janus
    print(_PL_FILE_SWI)
    janus.consult(_PL_FILE_SWI)

    t0 = time.perf_counter()
    janus.query_once("retractall(taken(_,_,_,_,_))")

    for f in facts:
        janus.query_once(f"assertz({f})")

    if not with_witness:
        ok = janus.query_once("all_requirements()").get('truth', False)
        elapsed = time.perf_counter() - t0
        if return_timing:
            return {'ok': ok, 'prolog_eval_s': elapsed, 'engine': 'swi'}
        return ok

    req_predicates = {
        'intro':   'intro_req()',
        'adv':     'advanced_req()',
        'elect':   'elective_req()',
        'sci':     'sci_subseq_req()',
        'ethics':  "passed('CSE 312')",
        'writing': "passed('CSE 300')",
        'calc':    'calc_req()',
        'alg':     'alg_req()',
        'sta':     'sta_req()',
    }
    checked = {}
    for req, pred in req_predicates.items():
        sat = janus.query_once(pred).get('truth', False)
        courses = []
        with janus.query(f"wit({req}, Q)") as results:
            for d in results:
                if 'Q' in d:
                    courses.append(d['Q'])
        checked[req] = (sat, courses)
    checked['degree'] = (janus.query_once("all_requirements()").get('truth', False), [])

    t123 = janus.query_once("credits_at_sb_cat123(T)")['T']
    t23  = janus.query_once("credits_at_sb_cat23(T)")['T']
    checked['credits_at_SB'] = (t123 >= 24 and t23 >= 18,
                                 [f'items123 = {int(t123)}', f'items23 = {int(t23)}'])
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
    FULL = {
        'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',                  ## intro
        'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',       ## adv
        'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',       ## elect
        'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',                  ## calc, sta, alg
        'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                             ## sci
        'CSE 300', 'CSE 312',                                                   ## writing, ethics
    }
    Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])
    taken = [
        Taken('CSE 114', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 214', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 216', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 215', 3, 'A', (2024,2), 'SBU'),
        Taken('CSE 220', 3, 'A', (2024,2), 'SBU'),
    ]

    taken = [Taken(cid, 3, 'A', (2024,2), 'SB') for cid in FULL]
    # engine = sys.argv[1] if len(sys.argv) > 1 else 'xsb'
    try:
        pprint(run_prolog(taken, 'swi', return_timing=True))
    except Exception as e:
        print(repr(e))
    # pprint(run_prolog(taken, 'xsb', return_timing=True))
    # run_swi(taken)

