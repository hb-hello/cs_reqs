
##
## Test cases derived from CSE_AMS Two, Three, and Four in users2.yaml,
## plus test_check_full from planner_tests.
##
## Translation notes from users2.yaml:
##   - AP/placement transfer courses use grade='A', where='Transfer'
##     (grade T is not C_or_higher, so we use A to reflect they are treated
##      as passed; where=Transfer so they never count for credits_at_SB)
##   - AMS 161 (0-credit math placement) and CHE 133 (0-credit AP waiver)
##     appear in passed_ids but contribute 0 to credit counts
##   - CSE 114 AP credit is 3cr (not 4cr) per the yaml transfer_courses entry
##   - PHY 131 is listed as 3 credits in the yaml class schedule entries
##   - CHE 132 Spring 2025: grade D for Four, grade F for Three --
##     both fail C_or_higher; CHE 132 is in sci_more so it counts for sci_req
##     regardless of grade (sci_req uses taken, not passed)
##   - CSE 475 (teaching practica) is in elect_exclude and never counts
##   - calc is never satisfied: AMS 151 was never taken (only AMS 161
##     placement), and no MAT 125/126/127 or MAT 131/132 courses were taken

from collections import namedtuple
from pprint import pprint

Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])

# ── shared transfer block (identical for Two, Three, Four) ───────────────────
# semester codes: 1=winter, 2=spring, 3=summer, 4=fall
_transfer = {
    Taken('CSE 114', 3, 'A', (2022, 4), 'Transfer'),  # AP Computer Science A
    Taken('CHE 131', 4, 'A', (2022, 4), 'Transfer'),  # AP CHE 131
    Taken('CHE 133', 0, 'A', (2022, 4), 'Transfer'),  # AP Waiver CHE 133 (0cr)
    Taken('AMS 161', 0, 'A', (2022, 4), 'Transfer'),  # Math placement (0cr)
    Taken('WRT 101', 3, 'A', (2022, 4), 'Transfer'),  # AP English Language
}

# ── per-term course sets ─────────────────────────────────────────────────────
_f22 = {
    Taken('AMS 261', 3, 'A', (2022, 4), 'SB'),
    Taken('AMS 210', 3, 'A', (2022, 4), 'SB'),
    Taken('AMS 310', 3, 'A', (2022, 4), 'SB'),
    Taken('CSE 214', 4, 'A', (2022, 4), 'SB'),
    Taken('CSE 215', 3, 'A', (2022, 4), 'SB'),
}

_sp23 = {
    Taken('AMS 301', 3, 'A', (2023, 2), 'SB'),
    Taken('AMS 475', 3, 'A', (2023, 2), 'SB'),  # not a CSE course; ignored by elect
    Taken('CSE 216', 3, 'A', (2023, 2), 'SB'),
    Taken('WRT 102', 3, 'A', (2023, 2), 'SB'),
}

_f23 = {
    Taken('AMS 325', 3, 'A', (2023, 4), 'SB'),
    Taken('CSE 220', 4, 'A', (2023, 4), 'SB'),
    Taken('CSE 303', 3, 'A', (2023, 4), 'SB'),
    Taken('CSE 316', 3, 'A', (2023, 4), 'SB'),
    Taken('CSE 475', 3, 'A', (2023, 4), 'SB'),  # practica; excluded from elect
}

_sp24 = {
    Taken('CSE 300', 3, 'A', (2024, 2), 'SB'),
    Taken('CSE 312', 3, 'A', (2024, 2), 'SB'),
    Taken('CSE 320', 3, 'A', (2024, 2), 'SB'),
    Taken('AMS 103', 3, 'A', (2024, 2), 'SB'),
    Taken('CSE 475', 3, 'A', (2024, 2), 'SB'),  # second practica semester
    Taken('POL 101', 3, 'A', (2024, 2), 'SB'),
}

# Fall 2024 and Spring 2025 are taken only by Three and Four (not Two)
_f24 = {
    Taken('AMS 311', 3, 'A', (2024, 4), 'SB'),
    Taken('CSE 360', 3, 'A', (2024, 4), 'SB'),
    Taken('CSE 373', 3, 'A', (2024, 4), 'SB'),
    Taken('PHY 131', 3, 'A', (2024, 4), 'SB'),  # 3 credits per yaml
}

# Spring 2025 differs only in the CHE 132 grade: D (Four) vs F (Three)
# Both fail C_or_higher; CHE 132 is in sci_more so it counts for sci_req.
_sp25_four = {
    Taken('AMS 315', 3, 'A', (2025, 2), 'SB'),
    Taken('AMS 332', 3, 'A', (2025, 2), 'SB'),
    Taken('AMS 361', 3, 'A', (2025, 2), 'SB'),
    Taken('CSE 361', 3, 'A', (2025, 2), 'SB'),
    Taken('CHE 132', 4, 'D', (2025, 2), 'SB'),  # D – in taken but not passed
}

_sp25_three = {
    Taken('AMS 315', 3, 'A', (2025, 2), 'SB'),
    Taken('AMS 332', 3, 'A', (2025, 2), 'SB'),
    Taken('AMS 361', 3, 'A', (2025, 2), 'SB'),
    Taken('CSE 361', 3, 'A', (2025, 2), 'SB'),
    Taken('CHE 132', 4, 'F', (2025, 2), 'SB'),  # F – in taken but not passed
}

# ── helper ───────────────────────────────────────────────────────────────────

def _snap(*term_sets):
    """Union all term sets into one taken set."""
    result = set()
    for s in term_sets:
        result |= s
    return result

# ── CSE_AMS Two ──────────────────────────────────────────────────────────────
# Two's transcript ends at Spring 2024 in users2.yaml (no Fall 2024 data).

def test_1_two_f22():
    """CSE_AMS Two after Fall 2022.
    Has: CSE 114 (AP), CSE 214, CSE 215, AMS 210, AMS 261, AMS 310.
    Missing: CSE 216, CSE 220 (intro incomplete), all adv, calc (AMS 151 never taken),
    elect, sci, ethics, writing.  calc1 needs AMS 151 which was never taken.
    sta also fails: AMS 301 not yet taken.
    """
    taken = _snap(_transfer, _f22)
    checked = {
        'intro':   (False, []),
        'adv':     (False, []),
        'elect':   (False, ['need 4 total']),
        'calc':    (False, []),
        'alg':     (True,  ['AMS 210']),
        'sta':     (False, []),
        'sci':     (False, ['need a lec/lab combo and more, with >=9 credits and >=2.0 GPA']),
        'ethics':  (False, []),
        'writing': (False, []),
        'credits_at_SB': (False, ['items123 = 7', 'items23 = 0']),
        'degree':  (False, []),
    }
    return taken, checked


def test_1_two_sp23():
    """CSE_AMS Two after Spring 2023.
    Adds: CSE 216, AMS 301.  intro almost there (missing CSE 220).
    sta passes via AMS 301 + AMS 310 (AMS 310 was Fall 2022).
    """
    taken = _snap(_transfer, _f22, _sp23)
    checked = {
        'intro':   (False, ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216']),
        'adv':     (False, []),
        'elect':   (False, ['need 4 total']),
        'calc':    (False, []),
        'alg':     (True,  ['AMS 210']),
        'sta':     (True,  ['AMS 301', 'AMS 310']),
        'sci':     (False, ['need a lec/lab combo and more, with >=9 credits and >=2.0 GPA']),
        'ethics':  (False, []),
        'writing': (False, []),
        'credits_at_SB': (False, ['items123 = 10', 'items23 = 0']),
        'degree':  (False, []),
    }
    return taken, checked


def test_1_two_f23():
    """CSE_AMS Two after Fall 2023.
    Adds: CSE 220, CSE 303, CSE 316, CSE 475 (practica).
    intro now passes.  adv partial: theory (CSE 303) done, algo missing (CSE 373),
    other missing (none of CSE 310/316/320/416 yet... wait CSE 316 is in other!).
    adv: needs theory OR theory2, algo OR algo2, AND other (all 4 of other).
    CSE 316 is in 'other' but adv_req requires ALL of other = {CSE 310, CSE 316, CSE 320, CSE 416}.
    So adv still fails (missing CSE 310, CSE 320, CSE 416 and CSE 373).
    credits_at_SB: items123 includes intro+adv+elect at SB.
      intro at SB: CSE 214(4), CSE 215(3), CSE 216(3), CSE 220(4) = 14
      adv at SB: CSE 303(3), CSE 316(3) = 6  (but adv not satisfied; credits_at_SB
      uses elect_courses(taken) which calls passed -- CSE 475 excluded)
      elect at SB: none yet (only CSE 303, 316 in adv; CSE 475 excluded)
      items123 = 14 + 6 = 20; items23 = 6
    """
    taken = _snap(_transfer, _f22, _sp23, _f23)
    checked = {
        'intro':   (True,  ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220']),
        'adv':     (False, ['CSE 303']),
        'elect':   (False, ['need 4 total']),
        'calc':    (False, []),
        'alg':     (True,  ['AMS 210']),
        'sta':     (True,  ['AMS 301', 'AMS 310']),
        'sci':     (False, ['need a lec/lab combo and more, with >=9 credits and >=2.0 GPA']),
        'ethics':  (False, []),
        'writing': (False, []),
        'credits_at_SB': (False, ['items123 = 20', 'items23 = 6']),
        'degree':  (False, []),
    }
    return taken, checked


def test_1_two_sp24():
    """CSE_AMS Two after Spring 2024 -- end of Two's recorded transcript.
    Adds: CSE 300, CSE 312, CSE 320, AMS 103, CSE 475 (practica), POL 101.
    ethics and writing now pass.
    adv: CSE 316 + CSE 320 in other, but still missing CSE 310, CSE 416, and
         algo (CSE 373 / CSE 385).  adv fails; witness = CSE 303 only (theory).
    elect: no upper-div CSE outside adv/exclude yet.
    credits_at_SB: intro(14) + adv_SB(CSE303+316+320 = 9) + elect(0) = 23 < 24.
    """
    taken = _snap(_transfer, _f22, _sp23, _f23, _sp24)
    checked = {
        'intro':   (True,  ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220']),
        'adv':     (False, ['CSE 303']),
        'elect':   (False, ['need 4 total']),
        'calc':    (False, []),
        'alg':     (True,  ['AMS 210']),
        'sta':     (True,  ['AMS 301', 'AMS 310']),
        'sci':     (False, ['need a lec/lab combo and more, with >=9 credits and >=2.0 GPA']),
        'ethics':  (True,  ['CSE 312']),
        'writing': (True,  ['CSE 300']),
        'credits_at_SB': (False, ['items123 = 23', 'items23 = 9']),
        'degree':  (False, []),
    }
    return taken, checked


# ── CSE_AMS Four ─────────────────────────────────────────────────────────────
# Four shares all terms with Two through Spring 2024, then continues.

def test_1_four_f22():
    """CSE_AMS Four after Fall 2022.  Identical result to Two_f22."""
    taken, checked = test_1_two_f22()
    return taken, checked


def test_1_four_sp23():
    """CSE_AMS Four after Spring 2023.  Identical result to Two_sp23."""
    taken, checked = test_1_two_sp23()
    return taken, checked


def test_1_four_f23():
    """CSE_AMS Four after Fall 2023.  Identical result to Two_f23."""
    taken, checked = test_1_two_f23()
    return taken, checked


def test_1_four_sp24():
    """CSE_AMS Four after Spring 2024.  Identical result to Two_sp24."""
    taken, checked = test_1_two_sp24()
    return taken, checked


def test_1_four_f24():
    """CSE_AMS Four after Fall 2024.
    Adds: AMS 311, CSE 360, CSE 373, PHY 131 (3cr).
    algo now passes via CSE 373.  adv witness grows to include CSE 373.
    adv still fails: other still incomplete (CSE 310, CSE 416 missing).
    elect: CSE 360 qualifies (upper-div, >=3cr, not in adv/exclude).  1/4 so far.
    sci: PHY 131 alone doesn't form a valid combo (needs PHY 133 for phy2, or
         PHY 126 for phy).  Still fails.
    credits_at_SB: intro(14) + adv_SB(CSE303+316+320+373=12) + elect_SB(CSE360=3)
                 = 29; items23 = 12+3 = 15.  Both < thresholds.
    sta: AMS 311 is sta2, but AMS 301 (fmath) already satisfies; sta passes
         via fmath + sta2 now too.  Witness stays as AMS 301 (fmath triggered first).
    """
    taken = _snap(_transfer, _f22, _sp23, _f23, _sp24, _f24)
    checked = {
        'intro':   (True,  ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220']),
        'adv':     (False, ['CSE 303', 'CSE 373']),
        'elect':   (False, ['CSE 360', 'need 4 total']),
        'calc':    (False, []),
        'alg':     (True,  ['AMS 210']),
        'sta':     (True,  ['AMS 301', 'AMS 310']),
        'sci':     (False, ['need a lec/lab combo and more, with >=9 credits and >=2.0 GPA']),
        'ethics':  (True,  ['CSE 312']),
        'writing': (True,  ['CSE 300']),
        'credits_at_SB': (False, ['items123 = 29', 'items23 = 15']),
        'degree':  (False, []),
    }
    return taken, checked


def test_1_four_sp25():
    """CSE_AMS Four after Spring 2025.
    Adds: AMS 315, AMS 332, AMS 361, CSE 361 (3cr), CHE 132 (4cr, grade D).
    CHE 132 grade D: fails C_or_higher so NOT in passed; but IS in taken (sci_more).
    elect: CSE 360 + CSE 361 = 2 qualifying electives. Still < 4.
    sci: CHE 131(4cr,T,A) + CHE 133(0cr,T,A) form the 'che' combo {CHE131,CHE133}.
         Supplemented by CHE 132 (sci_more) and PHY 131 (in sci_combs union).
         Best set = {CHE131, CHE133, CHE132, PHY131}: credits = 4+0+4+3 = 11 >= 9.
         GPA over those with grade_points: CHE131(4,A=4.0), CHE133(0,A=4.0),
         CHE132(4,D=1.0), PHY131(3,A=4.0) -> (4*4+0*4+4*1+3*4)/(4+0+4+3) = 32/11 >= 2.0.
         sci passes; witness = ['CHE 131', 'CHE 132', 'CHE 133', 'PHY 131'].
    adv: still missing CSE 310 and CSE 416 (other incomplete).
    credits_at_SB: intro(14) + adv_SB(CSE303+316+320+373=12) + elect_SB(CSE360+CSE361=6)
                 = 32 >= 24; items23 = 12+6 = 18 >= 18.  credits_at_SB passes!
    """
    taken = _snap(_transfer, _f22, _sp23, _f23, _sp24, _f24, _sp25_four)
    checked = {
        'intro':   (True,  ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220']),
        'adv':     (False, ['CSE 303', 'CSE 373']),
        'elect':   (False, ['CSE 360', 'CSE 361', 'need 4 total']),
        'calc':    (False, []),
        'alg':     (True,  ['AMS 210']),
        'sta':     (True,  ['AMS 301', 'AMS 310']),
        'sci':     (True,  ['CHE 131', 'CHE 132', 'CHE 133', 'PHY 131']),
        'ethics':  (True,  ['CSE 312']),
        'writing': (True,  ['CSE 300']),
        'credits_at_SB': (True, ['items123 = 32', 'items23 = 18']),
        'degree':  (False, []),
    }
    return taken, checked


# ── CSE_AMS Three ─────────────────────────────────────────────────────────────
# Three is identical to Two through Spring 2024 (same courses, same grades).
# Fall 2024 and Spring 2025 are the same as Four except CHE 132 grade = F (not D).
# An F in CHE 132 still fails C_or_higher and still appears in taken (sci_more),
# so all outcomes are identical to Four for both these terms.

def test_1_three_f24():
    """CSE_AMS Three after Fall 2024.  Identical result to Four_f24."""
    taken, checked = test_1_four_f24()
    return taken, checked


def test_1_three_sp25():
    """CSE_AMS Three after Spring 2025.
    Same as Four_sp25 except CHE 132 is grade F instead of D.
    F is still not C_or_higher, and grade_points['F'] = 0.00.
    sci GPA recomputed: CHE132(4,F=0), others same.
    (4*4 + 0*4 + 4*0 + 3*4)/(4+0+4+3) = (16+0+0+12)/11 = 28/11 = 2.545 >= 2.0.
    sci still passes.  All other outcomes identical.
    """
    taken = _snap(_transfer, _f22, _sp23, _f23, _sp24, _f24, _sp25_three)
    checked = {
        'intro':   (True,  ['CSE 114', 'CSE 214', 'CSE 215', 'CSE 216', 'CSE 220']),
        'adv':     (False, ['CSE 303', 'CSE 373']),
        'elect':   (False, ['CSE 360', 'CSE 361', 'need 4 total']),
        'calc':    (False, []),
        'alg':     (True,  ['AMS 210']),
        'sta':     (True,  ['AMS 301', 'AMS 310']),
        'sci':     (True,  ['CHE 131', 'CHE 132', 'CHE 133', 'PHY 131']),
        'ethics':  (True,  ['CSE 312']),
        'writing': (True,  ['CSE 300']),
        'credits_at_SB': (True, ['items123 = 32', 'items23 = 18']),
        'degree':  (False, []),
    }
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
