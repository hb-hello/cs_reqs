import os
import re
import sys
import tempfile

import pexpect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_PL_FILE_SWI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024swi.pl')
_PL_FILE_XSB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024xsb.pl')
XSB = 'xsb'
SWI = 'swi'

# requirement names shared between engines; each maps to req(Name) and wit(Name, _)
REQS = ['intro', 'adv', 'elect', 'sci', 'ethics', 'writing', 'calc', 'alg', 'sta']

def _taken_fact(t):
    return f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')"

def _credits_at_sb(t123, t23):
    return (t123 >= 24 and t23 >= 18,
            [f'items123 = {int(t123)}', f'items23 = {int(t23)}'])

def run_prolog(taken, engine=XSB, return_timing=False):
    assert engine in {XSB, SWI}, f"Unknown Prolog engine: {engine}"
    if engine == SWI:
        return run_swi(taken, return_timing=return_timing)
    return run_xsb(taken, return_timing=return_timing)

def run_xsb(taken, return_timing=False):
    pl_dir = os.path.dirname(os.path.abspath(__file__))
    prompt = r'\|\s*\?-\s*'
    child = pexpect.spawn(XSB, encoding='utf-8', timeout=20, cwd=pl_dir)
    child.expect(prompt)

    def run(cmd):
        child.sendline(cmd)
        child.expect(prompt)
        return child.before.strip()

    def truth(goal):
        # XSB writes "yes" or "no" as the last word based on whether the goal
        # succeeded. once/1 forces a single solution so there's no "More?" prompt.
        return run(f"once({goal}).").endswith('yes')

    def parse_list(out):
        # extract the first [...] in the output as a list of atoms.
        m = re.search(r'\[([^\]]*)\]', out)
        if not m or not m.group(1).strip(): return []
        return [a or b for a, b in re.findall(r"'([^']*)'|([^\s,]+)", m.group(1))]

    # load encoding, clear old taken/5, assert new facts via a temp file
    # (long inline assertz lines are too slow via pty echo).
    run(f"['{os.path.splitext(_PL_FILE_XSB)[0]}'].")
    run("retractall(taken(_,_,_,_,_)).")
    if taken:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.P') as f:
            for t in taken: f.write(f":- assert({_taken_fact(t)}).\n")
            f.flush()
            run(f"['{os.path.splitext(f.name)[0]}'].")

    # measure_run_xsb prints `result(yes|no)` and `CPU time: <s> s`; parse both.
    degree_out = run("measure_run_xsb(degree).")
    ok = 'result(yes)' in degree_out
    cpu = re.search(r'CPU time:\s*([\d.eE+-]+)', degree_out)
    prolog_eval_s = float(cpu.group(1)) if cpu else None

    # per-req: truth + witness list
    checked = {}
    for name in REQS:
        sat = truth(f'req({name})')
        wits = parse_list(run(f"findall(Id, wit({name}, Id), Ids), writeq(Ids), fail."))
        checked[name] = (sat, wits)

    # credits totals -> witness for credits_at_SB
    def credits(query):
        m = re.search(r'credit_total\(([\d.]+)\)', run(query))
        return float(m.group(1)) if m else 0.0
    t123 = credits("items123_credits(T), write(credit_total(T)), fail.")
    t23  = credits("items23_credits(T), write(credit_total(T)), fail.")
    checked['credits_at_SB'] = _credits_at_sb(t123, t23)
    checked['degree'] = (ok, [])

    child.sendline('halt.')
    child.expect(pexpect.EOF)

    if return_timing:
        return {'ok': ok, 'prolog_eval_s': prolog_eval_s, 'engine': XSB, 'checked': checked}
    return checked


def run_swi(taken, return_timing=False):
    facts = [_taken_fact(t) for t in taken]

    import janus_swi as janus
    janus.query_once("style_check(-singleton)")
    janus.query_once("style_check(-discontiguous)")
    janus.consult(_PL_FILE_SWI)

    janus.query_once("retractall(taken(_,_,_,_,_))")

    for f in facts:
        janus.query_once(f"assertz({f})")

    checked = {}
    for name in REQS:
        sat = janus.query_once(f'req({name})').get('truth', False)
        courses = []
        with janus.query(f"wit({name}, Q)") as results:
            for d in results:
                if 'Q' in d:
                    courses.append(d['Q'])
        checked[name] = (sat, courses)
    checked['degree'] = (janus.query_once("degree()").get('truth', False), [])

    t123 = janus.query_once("items123_credits(T)")['T']
    t23  = janus.query_once("items23_credits(T)")['T']
    checked['credits_at_SB'] = _credits_at_sb(t123, t23)

    prolog_eval_s = float(janus.query_once("measure_run_swi(degree, T).")['T'])

    if return_timing:
        return {'ok': checked['degree'][0], 'prolog_eval_s': prolog_eval_s, 'engine': SWI, 'checked': checked}
    return checked


if __name__ == '__main__':
    from collections import namedtuple
    Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])

    some = {
        'CSE 114', 'CSE 214', 'CSE 216',                                        ## intro (missing CSE 215, CSE 220)
        'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',       ## adv
        'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',       ## elect
        'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                             ## sci
    }
    taken = [Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in some]

    engine = sys.argv[1] if len(sys.argv) > 1 else XSB
    print(run_prolog(taken, engine, return_timing=True))

