from collections import namedtuple
from pprint import pprint
from ortools_version.course_catalog import catalog

# ── Full degree (all requirements satisfied) ─────────────────────────────────
# PHY 132 added vs ref tests so science reaches 9 credits:
#   PHY 131(3) + PHY 133(1) + PHY 132(3) + AST 203(3) = 10

_FULL = {
    'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',            # intro
    'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416', # adv
    'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355', # elect
    'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',            # math
    'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                        # science
    'CSE 300', 'CSE 312',                                               # ethics+writing
}

Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])

def _full_taken(grade='A', when=(2024, 2)):
    return {Taken(cid, catalog[cid].credits, grade, when, 'SB') for cid in _FULL}

_ALL_PASS = {req: (True, []) for req in
             ['intro', 'adv', 'elect', 'calc', 'alg', 'sta', 'sci',
              'ethics', 'writing', 'credits_at_SB', 'degree']}

def test_check_full():
    """Full course set — all requirements satisfied."""
    return _full_taken(), dict(_ALL_PASS)

def test_multi_attempt_passes():
    """PHY 131 taken twice (D then A). All-attempts GPA still well above 2.0."""
    taken = _full_taken()
    taken = {t for t in taken if t.id != 'PHY 131'}
    taken |= {
        Taken('PHY 131', 3, 'D',  (2023, 3), 'SB'),  # first attempt
        Taken('PHY 131', 3, 'A',  (2024, 1), 'SB'),   # retake
    }
    return taken, dict(_ALL_PASS)

def test_multi_attempt_best_only_sci_gpa():
    """PHY 131 taken twice (F then C). With best-attempt pre-processing, only C is used.
    Best-only sci GPA: (200*3 + 200*3 + 200*1 + 200*3) / (3+3+1+3) = 2000/10 = 2.0 — passes."""
    taken = _full_taken()
    taken = {t for t in taken if t.id not in {'PHY 131', 'PHY 132', 'PHY 133', 'AST 203'}}
    taken |= {
        Taken('PHY 131', 3, 'F',  (2023, 3), 'SB'),  # first attempt: F
        Taken('PHY 131', 3, 'C',  (2024, 1), 'SB'),   # retake: C
        Taken('PHY 132', 3, 'C',  (2024, 2), 'SB'),
        Taken('PHY 133', 1, 'C',  (2024, 2), 'SB'),
        Taken('AST 203', 3, 'C',  (2024, 2), 'SB'),
    }
    checked = dict(_ALL_PASS)
    checked['sci'] = (True, ['AST 203', 'PHY 131', 'PHY 132', 'PHY 133'])
    return taken, checked

if __name__ == '__main__':
    import inspect, sys
    this = sys.modules[__name__]
    for name, func in sorted(inspect.getmembers(this, inspect.isfunction)):
        if name.startswith('test_'):
            taken, checked = func()
            print(f'---- {name}')
            print(f'     taken_ids: {sorted({c.id for c in taken})}')
            pprint(checked)
            print()