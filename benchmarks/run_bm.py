import time
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path
from python_version.cs_reqs_2024 import Taken, degree_reqs
from prolog_version.run_prolog import run_prolog
from ortools_version.planner import plan_courses
from clingo_version.configs import KB_LP, MAIN_LP
from clingo_version.run_clingo import run_clingo
from datetime import datetime

FULL = {
    'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',                  ## intro
    'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',       ## adv
    'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',       ## elect
    'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',                  ## calc, sta, alg
    'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                             ## sci
    'CSE 300', 'CSE 312',                                                   ## writing, ethics
}
intro = {'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220'}
adv = {'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416'}
elect = {'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355'}
sci = {'PHY 131', 'PHY 132', 'PHY 133', 'AST 203'}
mat = {'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310'}
writing = {'CSE 300'}
ethics = {'CSE 312'}
extra_sci = {'CHE 132', 'CHE 321', 'CHE 322', 'CHE 331', 'CHE 332', 'PHY 125', 'PHY 127', 'PHY 132', 'PHY 134', 'PHY 142'}
extra_elect = {'CSE 380', 'CSE 356', 'CSE 370', 'CSE 355', 'CSE 391', 'CSE 353', 'CSE 362', 
         'CSE 363', 'CSE 305', 'CSE 332', 'CSE 390', 'CSE 488', 'CSE 351', 'CSE 354'}

cases = {
    'passing': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL},
    'no_intro': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL - intro},
    'no_adv': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL - adv},
    'no_elect': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL - elect},
    'no_mat': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL - mat},
    'no_sci': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL - sci},
    'no_wrt': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL - writing},
    'no_eth': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL - ethics},
    'extra_sci': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL | extra_sci},
    'extra_elect': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in FULL | extra_elect}
}

def bm_check(version, taken, runs = 1):
    if version not in {'python', 'swi', 'xsb', 'clingo', 'ortools'}: return 0
    times = []
    
    for i in range(runs):
        match version:
            case 'python':
                t0 = time.perf_counter()
                degree_reqs(taken)
                times.append(time.perf_counter() - t0)
            case 'swi': times.append(run_prolog(taken, 'swi', return_timing=True)['prolog_eval_s'])
            case 'xsb': times.append(run_prolog(taken, 'xsb', return_timing=True)['prolog_eval_s'])
            case 'ortools': 
                checked, _, metrics = plan_courses(taken, check=True)
                times.append(metrics['user_time_s'])
            case 'clingo':
                checked, _, metrics = run_clingo(taken_set=taken, mode='check', main_lp=MAIN_LP, kb_lp=KB_LP)
                t = metrics.get('summary', {}).get('times', {})
                times.append(float(t.get('total', 0)))
    print(version, times)
    return sum(times)/runs

#   year:2024 semester:3 (11 cr): CHE 131 (A), CSE 114 (C), WRT 101 (C)
#   year:2024 semester:4 (14 cr): CHE 152 (D), CHE 154 (Q), CSE 214 (C), MAT 125 (C), MAT 130 (F)
#   year:2025 semester:1 (3 cr): WRT 102 (D)
#   year:2025 semester:2 (13 cr): AMS 210 (C), CSE 215 (C), CSE 300 (C), MAT 126 (C)
#   year:2025 semester:3 (14 cr): CSE 216 (C), CSE 220 (C), CSE 310 (C), MAT 127 (C)
#   year:2025 semester:4 (15 cr): CSE 303 (C), CSE 312 (C), CSE 316 (C), CSE 320 (C), CSE 373 (C)
#   year:2026 semester:1 (6 cr): AMS 301 (C), AMS 310 (C)
#   year:2026 semester:2 (15 cr): CSE 327 (C), CSE 353 (C), CSE 354 (C), CSE 356 (C), CSE 416 (C)
sem_1 = {'CHE 131', 'CSE 114', 'WRT 101'}
sem_2 = sem_1 | {'CHE 152', 'CHE 154', 'CSE 214', 'MAT 125', 'MAT 130'}
sem_3 = sem_2 | {'WRT 102'}
sem_4 = sem_3 | {'AMS 210', 'CSE 215', 'CSE 300', 'MAT 126'}
sem_5 = sem_4 | {'CSE 216', 'CSE 220', 'CSE 310', 'MAT 127'}
sem_6 = sem_5 | {'CSE 303', 'CSE 312', 'CSE 316', 'CSE 320', 'CSE 373'}
sem_7 = sem_6 | {'AMS 301', 'AMS 310'}
complete = sem_7 | {'CSE 327', 'CSE 353', 'CSE 354', 'CSE 356', 'CSE 416'}

plan_cases = {
    'empty': set(),
    'sem_1': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in sem_1},
    'sem_2': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in sem_2},
    'sem_3': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in sem_3},
    'sem_4': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in sem_4},
    'sem_5': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in sem_5},
    'sem_6': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in sem_6},
    'sem_7': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in sem_7},
    'complete': {Taken(cid, 3, 'A', (2024, 2), 'SB') for cid in complete},
}

def bm_plan(version, taken, runs = 1):
    if version not in {'clingo', 'ortools'}: return 0
    times = []
    
    for i in range(runs):
        match version:
            case 'ortools': 
                checked, _, metrics = plan_courses(taken, start_sem=(2024, 3), end_sem=(2028, 4), check=False)
                times.append(metrics['user_time_s'])
            case 'clingo':
                checked, _, metrics = run_clingo(taken_set=taken, mode='plan', main_lp=MAIN_LP, kb_lp=KB_LP)
                t = metrics.get('summary', {}).get('times', {})
                times.append(float(t.get('total', 0)))
    
    return sum(times)/runs

def write_to_file(dir_name, results, cases_in_order):
    # create filename based on datetime
    filename = datetime.now().strftime("bm_%Y%m%d_%H%M%S.txt")
    out_dir = Path(__file__).resolve().parent / dir_name
    out_dir.mkdir(exist_ok=True)

    with open(out_dir / filename, 'w') as f:
        # header
        header_check = ["case", "python", "swi", "xsb", "clingo", "ortools", "case_name"]
        header_plan = ["case", "clingo", "ortools", "case_name"]
        header = header_check if dir_name == "checking" else header_plan
        f.write("\t".join(header) + "\n")

        # rows
        for i, case in enumerate(cases_in_order):
            row = [f"{(results.get(case, {}).get(version, 0)):.9f}" for version in header if version in results.get(case, {}).keys()]
            print(row)
            row.insert(0, str(i + 1))
            row.append(str(case))
            f.write("\t".join(row) + "\n")

    print(f"Saved to {filename}")

if __name__ == '__main__':
    versions = {'python', 'swi', 'xsb', 'clingo', 'ortools'}
    
    check_results = {}

    for case, taken in plan_cases.items():
        check_results[case] = {}
        for version in versions:
            t = bm_check(version, taken, 5)
            print(version, case, t)
            check_results[case][version] = t * 1000 # convert s to ms

    # write_to_file('checking', check_results, ['passing', 'no_intro', 'no_adv', 'no_elect', 'no_mat', 'no_sci', 'no_wrt', 'no_eth'])
    write_to_file('checking', check_results, ['empty', 'sem_1', 'sem_2', 'sem_3', 'sem_4', 'sem_5', 'sem_6', 'sem_7', 'complete'])


    # plan_result = {}
    # for case, taken in plan_cases.items():
    #     plan_result[case] = {}
    #     for version in {'clingo', 'ortools'}:
    #         t = bm_plan(version, taken, 5)
    #         print(version, case, t)
    #         plan_result[case][version] = t
    #
    # write_to_file('planning', plan_result, ['empty', 'sem_1', 'sem_2', 'sem_3', 'sem_4', 'sem_5', 'sem_6', 'sem_7', 'complete'])
