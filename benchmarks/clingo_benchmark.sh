# benchmark for different clingo planning encodings:
## -e: what lp files to run.
## -t: timeout
## -ts: test cases to run, if not specified, runs all test cases.
## -r: number of runs for each test case.
## -n: dir name for the output, if the dir already exists, experiment will be skipped.

# 1. empty: base, min_cred, max_cred, plan, min_cred_and_plan, plan+h, min_cred_and_plan+h
python benchmarks/clingo_planning_bm.py -e exp_baseline -t 1800 -ts empty -r 2 -n baseline-empty
python benchmarks/clingo_planning_bm.py -e exp_choose_min_cred exp_choose_max_cred -t 1800 -ts empty -r 2 -n min-max-empty
python benchmarks/clingo_planning_bm.py -e exp_plan -t 1800 -ts empty -r 2 -n plan-empty
python benchmarks/clingo_planning_bm.py -e exp_min_cred_and_plan -t 1800 -ts empty -r 2 -n min-cred-and-plan-empty
python benchmarks/clingo_planning_bm.py -e exp_plan -t 1800 -ts empty -r 2 -n plan-empty-heu -heu
python benchmarks/clingo_planning_bm.py -e exp_min_cred_and_plan -t 1800 -ts empty -r 2 -n plan-min-cred-empty-heu -heu

# 2. full, sem_1 - sem_7: base, min_cred, max_cred, plan, min_cred_and_plan, plan+h, min_cred_and_plan+h
python benchmarks/clingo_planning_bm.py -e exp_baseline exp_choose_min_cred exp_choose_max_cred exp_plan exp_min_cred_and_plan -t 1800 -ts full sem_7 sem_6 sem_5 sem_4 sem_3 sem_2 sem_1 -r 3 -n all-but-empty
python benchmarks/clingo_planning_bm.py -e exp_plan exp_min_cred_and_plan -t 1800 -ts full sem_7 sem_6 sem_5 sem_4 sem_3 sem_2 sem_1 -r 3 -n all-but-empty-heu -heu