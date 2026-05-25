import os
import re
import time

import pexpect
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_PL_FILE_SWI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024swi.pl')
_PL_FILE_XSB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs_reqs_2024xsb.pl')


def extract_cpu_time(text):
    for line in text.splitlines():
        if "CPU time:" in line:
            value = line.split("CPU time:")[1].split("s")[0].strip()
            return float(value)
    return None

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
        return run_swi(taken, return_timing=return_timing)

    child = pexpect.spawn('xsb', encoding='utf-8', timeout=20)
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

    for t in taken:
        fact = f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')"
        run_cmd(f"assertz({fact}).")

    u = run_cmd("measure_run_xsb(degree).")
    print(u)
    prolog_eval_s = extract_cpu_time(u)
    ok = query_truth('degree')

    # collect per-requirement witnesses
    req_predicates = {
        'intro':   'req(intro)',
        'adv':     'req(adv)',
        'elect':   'req(elect)',
        'sci':     'req(sci)',
        'ethics':  'req(ethics)',
        'writing': 'req(writing)',
        'calc':    'req(calc)',
        'alg':     'req(alg)',
        'sta':     'req(sta)',
    }
    checked = {}
    for key, pred in req_predicates.items():
        sat = query_truth(pred)
        wit_out = run_cmd(f"findall(Id, wit({key}, Id), Ids), writeq(Ids), fail.")
        courses = _parse_prolog_list(wit_out)
        checked[key] = (sat, courses)

    t123_out = run_cmd("items123_credits(T), write(credit_total(T)), fail.")
    t23_out  = run_cmd("items23_credits(T), write(credit_total(T)), fail.")
    t123_m = re.search(r'credit_total\(([\d.]+)\)', t123_out)
    t23_m  = re.search(r'credit_total\(([\d.]+)\)', t23_out)
    t123 = float(t123_m.group(1)) if t123_m else 0.0
    t23  = float(t23_m.group(1))  if t23_m  else 0.0
    checked['credits_at_SB'] = (t123 >= 24 and t23 >= 18,
                                 [f'items123 = {int(t123)}', f'items23 = {int(t23)}'])
    checked['degree'] = (ok, [])

    child.sendline('halt.')
    child.expect(pexpect.EOF)

    if return_timing:
        return {'ok': ok, 'prolog_eval_s': prolog_eval_s, 'engine': 'xsb', 'checked': checked}
    return checked


def run_swi(taken, return_timing=False):
    facts = (
        f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{t.where}')"
        for t in taken
    )

    import janus_swi as janus
    janus.query_once("style_check(-singleton)")
    janus.query_once("style_check(-discontiguous)")
    janus.consult(_PL_FILE_SWI)

    janus.query_once("retractall(taken(_,_,_,_,_))")

    for f in facts:
        janus.query_once(f"assertz({f})")

    reqs = {'intro':   'req(intro)',
             'adv':    'req(adv)',
             'elect':  'req(elect)',
             'sci':    'req(sci)',
             'ethics': 'req(ethics)',
             'writing':'req(writing)',
             'calc':   'req(calc)',
             'alg':    'req(alg)',
             'sta':    'req(sta)'}
    checked = {}
    for name, pred in reqs.items():
        sat = janus.query_once(pred).get('truth', False)
        courses = []
        with janus.query(f"wit({name}, Q)") as results:
            for d in results:
                if 'Q' in d:
                    courses.append(d['Q'])
        checked[name] = (sat, courses)
    checked['degree'] = (janus.query_once("degree()").get('truth', False), [])

    t123 = janus.query_once("items123_credits(T)")['T']
    t23  = janus.query_once("items23_credits(T)")['T']
    checked['credits_at_SB'] = (t123 >= 24 and t23 >= 18,
                                 [f'items123 = {int(t123)}', f'items23 = {int(t23)}'])

    # benchmark how long it takes to add in all taken data and check degree
    janus.query_once("retractall(taken(_,_,_,_,_))")

    # 1. Define a heavy Prolog goal
    prolog_eval_s = float(janus.query_once("measure_run_swi(degree, T).")['T'])
    goal = "degree()"

    # 2. Get Start Time
    start_stats = janus.query_once("statistics(cputime, T)")
    start_time = start_stats['T']

    # 3. Run the Goal

    for f in facts:
        janus.query_once(f"assertz({f})")
    
    janus.query_once(goal)

    # 4. Get End Time
    end_stats = janus.query_once("statistics(cputime, T)")
    end_time = end_stats['T']

    # 5. Calculate and print CPU time
    cpu_time = end_time - start_time

    if return_timing:
        return {
            'ok': checked.get('degree', (False, []))[0],
            'prolog_eval_s': prolog_eval_s,
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
    # taken = [
    #     Taken('CSE 114', 3, 'A', (2024,2), 'SB'),
    #     Taken('CSE 214', 3, 'A', (2024,2), 'SB'),
    #     Taken('CSE 216', 3, 'A', (2024,2), 'SB'),
    #     Taken('CSE 215', 3, 'A', (2024,2), 'SB'),
    #     Taken('CSE 220', 3, 'A', (2024,2), 'SB'),
    #     Taken('CSE 303', 3, 'A', (2024,2), 'SB'),
    #     # Taken('PHY 131', 3, 'A', (2024,2), 'SB'),
    #     Taken('PHY 132', 3, 'A', (2024,2), 'SB'),
    #     Taken('PHY 133', 3, 'A', (2024,2), 'SB'),
    # ]

    some = {
        'CSE 114', 'CSE 214', 'CSE 216', #'CSE 215', 'CSE 220',                  ## intro
        'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',       ## adv
        # 'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',       ## elect
        # 'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',                  ## calc, sta, alg
        # 'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                             ## sci
        # 'CSE 300', 'CSE 312',                                                   ## writing, ethics
    }

    taken = [Taken(cid, 3, 'A', (2024,2), 'SB') for cid in some]
    # engine = sys.argv[1] if len(sys.argv) > 1 else 'xsb'

    # taken = {Taken(id='CHE 133', credits=0, grade='A', when=(2022, 4), where='AP'), Taken(id='CSE 360', credits=3, grade='A', when=(2024, 4), where='SB'), Taken(id='CSE 216', credits=3, grade='A', when=(2023, 2), where='SB'), Taken(id='CSE 215', credits=3, grade='A', when=(2022, 4), where='SB'), Taken(id='CSE 316', credits=3, grade='A', when=(2023, 4), where='SB'), Taken(id='CSE 310', credits=3, grade=None, when=(2025, 4), where='SB'), Taken(id='CSE 361', credits=3, grade='A', when=(2025, 2), where='SB'), Taken(id='CSE 416', credits=3, grade=None, when=(2025, 4), where='SB'), Taken(id='AMS 161', credits=0, grade='A', when=(2022, 4), where='AP'), Taken(id='PHY 131', credits=3, grade='A', when=(2024, 4), where='SB'), Taken(id='CSE 373', credits=3, grade='A', when=(2024, 4), where='SB'), Taken(id='AMS 301', credits=3, grade='A', when=(2023, 2), where='SB'), Taken(id='CHE 132', credits=4, grade=None, when=(2025, 4), where='SB'), Taken(id='CSE 114', credits=3, grade='A', when=(2022, 4), where='AP'), Taken(id='CSE 214', credits=4, grade='A', when=(2022, 4), where='SB'), Taken(id='CSE 220', credits=4, grade='A', when=(2023, 4), where='SB'), Taken(id='CSE 303', credits=3, grade='A', when=(2023, 4), where='SB'), Taken(id='CSE 300', credits=3, grade='A', when=(2024, 2), where='SB'), Taken(id='AMS 310', credits=3, grade='A', when=(2022, 4), where='SB'), Taken(id='CHE 131', credits=4, grade='A', when=(2022, 4), where='AP'), Taken(id='CSE 312', credits=3, grade='A', when=(2024, 2), where='SB'), Taken(id='CSE 320', credits=3, grade='A', when=(2024, 2), where='SB'), Taken(id='CHE 132', credits=4, grade='D', when=(2025, 2), where='SB'), Taken(id='AMS 210', credits=3, grade='A', when=(2022, 4), where='SB')}

    try:
        # print(run_prolog(taken, 'xsb', swi_with_witness=True, return_timing=True))
        print(run_prolog(taken, 'swi', swi_with_witness=True, return_timing=True))
        # pprint(run_prolog(taken, 'swi', swi_with_witness=True, return_timing=True))
    except Exception as e:
        print(repr(e))
    # pprint(run_prolog(taken, 'xsb', return_timing=True))
    # run_swi(taken)

