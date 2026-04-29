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
    prompt_re = r'\|\s*\?-\s*'
    child.expect(prompt_re)

    def run_cmd(command):
        child.sendline(command)
        child.expect(prompt_re)
        return child.before.strip()

    def query_truth(goal):
        output = run_cmd(f"({goal} -> write(yes) ; write(no)).")
        return 'yes' in output
    
    def get_xsb_runtime():
        # XSB returns [TimeSinceStart, TimeSinceLastStatCall]
        # Use a failing probe query so XSB does not pause for top-level bindings.
        output = run_cmd("statistics(runtime, [T|_]), writeln(time_marker(T)), fail.")
        match = re.search(r"time_marker\(([-+0-9.eE]+)\)", output)
        return float(match.group(1)) if match else 0.0

    xsb_load_path = os.path.splitext(_PL_FILE_XSB)[0].replace('\\', '/')
    run_cmd(f"['{xsb_load_path}'].")
    run_cmd("retractall(taken(_,_,_,_,_)).")

    t0 = get_xsb_runtime()
    for t in taken:
        where = _normalize_where(t.where)
        fact = f"taken('{t.id}', {t.credits}, '{t.grade}', ({t.when[0]},{t.when[1]}), '{where}')"
        run_cmd(f"assertz({fact}).")

    ok = query_truth('all_requirements')
    t1 = get_xsb_runtime()
    # time_match = re.search(r"wall\s*time:\s*([-+0-9.eE]+)\s*(ms|s)", query_output.lower())
    # if time_match:
    #     raw = float(time_match.group(1))
    #     unit = time_match.group(2)
    #     prolog_eval_s = raw / 1000.0 if unit == 'ms' else raw
    # else:
    #     prolog_eval_s = None
    # XSB runtime statistics are CPU time in this environment.
    prolog_eval_s = t1 - t0

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
        sat = query_truth(pred)
        wit_out = run_cmd(f"findall(Id, wit({key}, Id), Ids), writeq(Ids), fail.")
        courses = _parse_prolog_list(wit_out)
        checked[key] = (sat, courses)

    t123_out = run_cmd("credits_at_sb_cat123(T), write(credit_total(T)), fail.")
    t23_out  = run_cmd("credits_at_sb_cat23(T), write(credit_total(T)), fail.")
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

    reqs = {'intro':   'intro_req()',
             'adv':    'advanced_req()',
             'elect':  'elective_req()',
             'sci':    'sci_subseq_req()',
             'ethics': "passed('CSE 312')",
             'writing':"passed('CSE 300')",
             'calc':   'calc_req()',
             'alg':    'alg_req()',
             'sta':    'sta_req()'}
    checked = {}
    for name, pred in reqs.items():
        sat = janus.query_once(pred).get('truth', False)
        courses = []
        with janus.query(f"wit({name}, Q)") as results:
            for d in results:
                if 'Q' in d:
                    courses.append(d['Q'])
        checked[name] = (sat, courses)
    checked['degree'] = (janus.query_once("all_requirements()").get('truth', False), [])

    t123 = janus.query_once("credits_at_sb_cat123(T)")['T']
    t23  = janus.query_once("credits_at_sb_cat23(T)")['T']
    checked['credits_at_SB'] = (t123 >= 24 and t23 >= 18,
                                 [f'items123 = {int(t123)}', f'items23 = {int(t23)}'])
    elapsed = time.perf_counter() - t0

    # benchmark how long it takes to add in all taken data and check all_requirements
    janus.query_once("retractall(taken(_,_,_,_,_))")

    # 1. Define a heavy Prolog goal
    goal = "all_requirements()"

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
    print(f"Prolog CPU time: {cpu_time:.6f} seconds")

    # data = janus.query('course_in_cat123(Q)')
    # for d in data:
    #     print(f"{d['Q']}: {[t.credits for t in taken if t.id == d['Q']]}")

    # print("23")
    # data = janus.query('course_in_cat23(Q)')
    # for d in data:
    #     print(f"{d['Q']}: {[t.credits for t in taken if t.id == d['Q']]}")

    # print("temp")
    # data1 = janus.query_once('tempNone(Q)')
    # print(data1)
    # for d in data1:
    #     print(f"{d['Q']}, {d['truth']}, {d}")


    if return_timing:
        return {
            'ok': checked.get('degree', (False, []))[0],
            'prolog_eval_s': cpu_time if cpu_time else elapsed,
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
    #     Taken('CSE 114', 3, 'A', (2024,2), 'SBU'),
    #     Taken('CSE 214', 3, 'A', (2024,2), 'SBU'),
    #     Taken('CSE 216', 3, 'A', (2024,2), 'SBU'),
    #     Taken('CSE 215', 3, 'A', (2024,2), 'SBU'),
    #     Taken('CSE 220', 3, 'A', (2024,2), 'SBU'),
    #     Taken('CSE 303', 3, 'A', (2024,2), 'SBU'),
    #     # Taken('PHY 131', 3, 'A', (2024,2), 'SBU'),
    #     Taken('PHY 132', 3, 'A', (2024,2), 'SBU'),
    #     Taken('PHY 133', 3, 'A', (2024,2), 'SBU'),
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
        pprint(run_prolog(taken, 'xsb', swi_with_witness=True, return_timing=True))
        # pprint(run_prolog(taken, 'swi', swi_with_witness=True, return_timing=True))
    except Exception as e:
        print(repr(e))
    # pprint(run_prolog(taken, 'xsb', return_timing=True))
    # run_swi(taken)

