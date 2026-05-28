import os
import re
import sys

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
    # spawn xsb from the prolog dir so the relative :- include('cs_reqs_2024swi.pl') resolves
    child = pexpect.spawn(XSB, encoding='utf-8', timeout=20,
                          cwd=os.path.dirname(os.path.abspath(__file__)))
    prompt_re = r'\|\s*\?-\s*'
    child.expect(prompt_re)

    def run_cmd(command):
        child.sendline(command)
        child.expect(prompt_re)
        return child.before.strip()

    def query_truth(goal):
        output = run_cmd(f"({goal} -> write(yes) ; write(no)).")
        return 'yes' in output

    xsb_load_path = os.path.splitext(_PL_FILE_XSB)[0].replace('\\', '/')
    run_cmd(f"['{xsb_load_path}'].")
    run_cmd("retractall(taken(_,_,_,_,_)).")

    for t in taken: run_cmd(f"assertz({_taken_fact(t)}).")
    u = run_cmd("measure_run_xsb(degree).")

    def extract_cpu_time(text):
      for line in text.splitlines():
          if "CPU time:" in line:
              value = line.split("CPU time:")[1].split("s")[0].strip()
              return float(value)
      return None

    ok, prolog_eval_s = query_truth('degree'), extract_cpu_time(u)

    def _parse_prolog_list(text):
        """Parse a Prolog list written via write/1, e.g. ['CSE 114','CSE 373'] → list of strings."""
        m = re.search(r'\[([^\]]*)\]', text)
        if not m: return []
        inner = m.group(1).strip()
        if not inner: return []
        items = re.findall(r"'([^']*)'|([^\s,]+)", inner)
        return [a or b for a, b in items if a or b]

    checked = {}
    for name in REQS:
        sat = query_truth(f'req({name})')
        wit_out = run_cmd(f"findall(Id, wit({name}, Id), Ids), writeq(Ids), fail.")
        checked[name] = (sat, _parse_prolog_list(wit_out))

    def parse_credits(query):
        m = re.search(r'credit_total\(([\d.]+)\)', run_cmd(query))
        return float(m.group(1)) if m else 0.0

    t123 = parse_credits("items123_credits(T), write(credit_total(T)), fail.")
    t23  = parse_credits("items23_credits(T), write(credit_total(T)), fail.")
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

