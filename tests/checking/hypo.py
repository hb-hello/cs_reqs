"""
Property-based tests for cs_reqs_2024.py using Hypothesis.

DESIGN PHILOSOPHY
-----------------
We think of the system as a pure function:
    transcript (set of Taken) --> degree_reqs (dict of booleans + witnesses)

Property-based testing asks: "for ALL transcripts that look like X,
property Y must hold." This catches edge cases no human would write by hand.

Three layers of strategy (from simplest to most expressive):
  1. @given          -- "for any transcript, this invariant holds"
  2. assume()        -- "given a transcript that satisfies pre-condition P,
                         post-condition Q holds"  (conditional properties)
  3. RuleBasedStateMachine -- "as a student builds a transcript step by step,
                               these invariants hold at every step"
"""

import unittest
from hypothesis import given, assume, settings, HealthCheck
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize

from python_version.cs_reqs_2024 import (
    Taken, GPA, C_or_higher, upper_division,
    intro_req, adv_req, elect_req, elect_courses,
    calc_req, alg_req, sta_req, sci_req,
    ethics_req, writing_req, credits_at_SB_req,
    degree_reqs, w,
    grade_points,
    prog, prog2, dmath, dmath2, sys as sys_,   # avoid shadowing builtins
    theory, theory2, algo, algo2, other,
    calc1, calc2, calc3, alg1, alg2,
    fmath, sta1, sta2,
    ethics, writing,
    sci_combs, sci_more,
)

# ─────────────────────────────────────────────────────────────────────────────
# STRATEGIES
# "How do I make it pick from a set of courses?"
#
# st.sampled_from(collection) -- picks one element uniformly at random.
# st.frozensets(element_strategy, min_size, max_size) -- picks a set.
# st.builds(constructor, **field_strategies) -- assembles a namedtuple/object.
#
# The trick: we enumerate ALL known course IDs in the domain, then let
# Hypothesis pick arbitrary subsets. This is much richer than hand-writing
# test cases because Hypothesis will shrink failures to minimal examples.
# ─────────────────────────────────────────────────────────────────────────────

# Every course ID that appears anywhere in the requirements
KNOWN_IDS: list[str] = sorted({
    # intro
    *prog, *prog2, *dmath, *dmath2, *sys_,
    # adv
    *theory, *theory2, *algo, *algo2, *other,
    # electives (upper-div CSE, not excluded)
    'CSE 350', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',
    'CSE 360', 'CSE 361', 'CSE 380', 'CSE 390', 'CSE 392',
    'CSE 416', 'CSE 421', 'CSE 487', 'CSE 490', 'CSE 499',
    # excluded from electives
    'CSE 475', 'CSE 495', 'CSE 300', 'CSE 301', 'CSE 312',
    # math
    *calc1, *calc2, *calc3, *alg1, *alg2, *fmath, *sta1, *sta2,
    # science combos
    *(c for combo in sci_combs for c in combo),
    # extra science
    *sci_more,
    # ethics + writing
    *ethics, *writing,
})

# All grades that can appear on a transcript
ALL_GRADES: list[str] = list(grade_points.keys()) + ['P', 'NC', 'S', 'U', 'W', 'I']

# ── Building block: one Taken course ────────────────────────────────────────
# st.builds() maps keyword strategies onto a namedtuple constructor.
# Each field gets its own independent strategy.
taken_course = st.builds(
    Taken,
    id=st.sampled_from(KNOWN_IDS),          # picks from our catalogue
    credits=st.integers(min_value=1, max_value=4),
    grade=st.sampled_from(ALL_GRADES),
    when=st.tuples(
        st.integers(min_value=2015, max_value=2026),
        st.integers(min_value=1, max_value=4),
    ),
    where=st.sampled_from(['SB', 'transfer']),
)

# ── A full transcript: a set of Taken courses ───────────────────────────────
transcript = st.dictionaries(
    keys=st.sampled_from(KNOWN_IDS),
    values=st.fixed_dictionaries({
        'credits': st.integers(min_value=1, max_value=4),
        'grade':   st.sampled_from(ALL_GRADES),
        'when':    st.tuples(st.integers(2015, 2026), st.integers(1, 4)),
        'where':   st.sampled_from(['SB', 'transfer']),
    }),
    max_size=40,
).map(lambda d: frozenset(Taken(id=cid, **fields) for cid, fields in d.items()))

# ── A "passing" version of a specific set of course IDs ─────────────────────
# Useful when we want to FORCE a requirement to be satisfied so we can
# test something *conditional* on that. This is the assume() pattern.
def passing_taken(ids: set[str], credits: int = 3) -> frozenset[Taken]:
    """All A grades, taken at SB -- the simplest satisfying witness."""
    return frozenset(Taken(id, credits, 'A', (2024, 2), 'SB') for id in ids)


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 1: Pure math / utility invariants
# These have no pre-conditions. They hold for ALL inputs.
# ─────────────────────────────────────────────────────────────────────────────

class TestGPA(unittest.TestCase):
    """GPA is a pure function with strong mathematical invariants."""

    def test_empty_transcript_gives_zero(self):
        assert GPA([]) == 0

    @given(st.lists(
        st.tuples(st.integers(1, 4), st.sampled_from(list(grade_points))),
        min_size=1,
    ))
    def test_gpa_always_in_range(self, weighted_grades):
        """GPA must be between 0.0 (all F) and 4.0 (all A)."""
        result = GPA(weighted_grades)
        assert 0.0 <= result <= 4.0, f"GPA out of range: {result}"

    @given(st.integers(min_value=1, max_value=4))
    def test_all_A_gives_4(self, credits):
        """A transcript of all A's must have GPA exactly 4.0."""
        grades = [(credits, 'A')] * 5
        assert GPA(grades) == 4.0

    @given(st.lists(
        st.tuples(st.integers(1, 4), st.sampled_from(['P', 'S', 'NC', 'W'])),
        min_size=1,
    ))
    def test_non_gpa_grades_excluded(self, weighted_grades):
        """P/S/NC/W grades must not contribute to GPA calculation."""
        # Adding non-GPA grades to an all-A transcript shouldn't change GPA
        base = [(3, 'A')] * 3
        assert GPA(base) == GPA(base + weighted_grades)


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 2: Monotonicity properties
#
# KEY INSIGHT: adding more passing courses can only help, never hurt.
# This is the most powerful class of property for this domain because
# it lets us generate a satisfying transcript and then check that
# *supersets* of it still satisfy the requirement.
#
# Pattern:
#   1. Generate a minimal satisfying set S
#   2. Generate extra courses E (arbitrary)
#   3. Assert req(S ∪ E) is still True
# ─────────────────────────────────────────────────────────────────────────────

class TestMonotonicity(unittest.TestCase):

    @given(transcript)
    def test_intro_monotone(self, extra):
        """If intro is satisfied, adding more courses keeps it satisfied."""
        base_ids = prog | dmath | sys_          # minimal passing set
        base = passing_taken(base_ids)
        combined_ids = {c.id for c in base | extra}
        # base satisfies intro -- combined must too
        assert intro_req(combined_ids)

    @given(transcript)
    def test_calc_monotone(self, extra):
        base = passing_taken(calc1)
        combined_ids = {c.id for c in base | extra}
        assert calc_req(combined_ids)

    @given(transcript)
    def test_alg_monotone(self, extra):
        base = passing_taken(alg1)
        combined_ids = {c.id for c in base | extra}
        assert alg_req(combined_ids)

    @given(transcript)
    def test_ethics_monotone(self, extra):
        base = passing_taken(ethics)
        combined_ids = {c.id for c in base | extra}
        assert ethics_req(combined_ids)

    @given(transcript)
    def test_writing_monotone(self, extra):
        base = passing_taken(writing)
        combined_ids = {c.id for c in base | extra}
        assert writing_req(combined_ids)


GOOD_GRADES = [g for g, pts in grade_points.items() if pts >= 2.0]  # C or higher
BAD_GRADES  = [g for g, pts in grade_points.items() if pts <  2.0]  # below C
 
@st.composite
def sci_taken(draw, grade_pool, min_extra=1):
    """
    Generate a frozenset of Taken science courses:
      - one lec/lab combo (2 courses, drawn from sci_combs)
      - at least min_extra courses from sci_more
      - all at 3 credits, grades drawn from grade_pool
    """
    combo     = draw(st.sampled_from(sci_combs))
    extra_ids = draw(st.frozensets(
        st.sampled_from(sorted(sci_more)), min_size=min_extra
    ))
    return frozenset(
        Taken(cid, 3, draw(st.sampled_from(grade_pool)), (2024, 2), 'SB')
        for cid in combo | extra_ids
    )
 
 
class TestSciReq(unittest.TestCase):
 
    @given(sci_taken(GOOD_GRADES))
    def test_combo_plus_extra_good_gpa_passes(self, taken):
        """combo + >=1 sci_more course + GPA>=2.0 + >=9cr -> must pass."""
        assert sci_req(taken)
 
    @given(sci_taken(BAD_GRADES))
    def test_combo_plus_extra_bad_gpa_fails(self, taken):
        """Same structure but every grade below C -> GPA<2.0 -> must fail."""
        assert not sci_req(taken)
 
    @given(st.frozensets(
        st.sampled_from(sorted(sci_more)).map(
            lambda cid: Taken(cid, 3, 'A', (2024, 2), 'SB')
        ),
        min_size=3,   # plenty of credits, just no combo
    ))
    def test_no_combo_always_fails(self, taken):
        """sci_more courses alone, no lec/lab combo -> must always fail."""
        assert not sci_req(taken)


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 3: Conditional properties using assume()
#
# assume(condition) tells Hypothesis: "discard this example if condition is
# False." It narrows the search space to examples satisfying a pre-condition.
#
# USE SPARINGLY: if the condition is too narrow, Hypothesis has to throw away
# too many examples (health check: filter_too_much). Prefer building
# strategies that directly generate what you want.
# ─────────────────────────────────────────────────────────────────────────────

class TestConditionalProperties(unittest.TestCase):

    @given(transcript)
    def test_elect_courses_are_upper_division(self, taken):
        """Every course in elect_courses must be upper-division CSE >= 3 credits."""
        passed = {c for c in taken if C_or_higher(c.grade)}
        elects = elect_courses(passed)
        for cid in elects:
            assert cid.startswith('CSE'), f"{cid} is not a CSE course"
            assert upper_division(cid), f"{cid} is not upper division"

    @given(transcript)
    def test_elect_req_needs_four(self, taken):
        """elect_req is True iff elect_courses has >= 4 courses."""
        passed = {c for c in taken if C_or_higher(c.grade)}
        # The requirement and the count must agree
        result = elect_req(passed)
        assert result == (len(elect_courses(passed)) >= 4)

    @given(transcript)
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_sta_req_needs_fmath(self, taken):
        """sta_req can never be True without AMS 301."""
        passed_ids = {c.id for c in taken if C_or_higher(c.grade)}
        assume('AMS 301' not in passed_ids)  # pre-condition: no fmath
        # post-condition: sta_req must be False
        assert not sta_req(passed_ids)


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 4: Witness consistency
#
# The witness dictionary `w` must be internally consistent with the
# boolean result. This tests the *contract* of the witness system.
# ─────────────────────────────────────────────────────────────────────────────

class TestWitnessConsistency(unittest.TestCase):

    @given(transcript)
    def test_degree_reqs_returns_all_ten_items(self, taken):
        """degree_reqs always returns exactly the 10 required keys + 'degree'."""
        global w
        w = {}
        result = degree_reqs(taken)
        expected_keys = {'intro','adv','elect','calc','alg','sta',
                         'sci','ethics','writing','credits_at_SB','degree'}
        assert set(result.keys()) == expected_keys

    @given(transcript)
    def test_degree_true_iff_all_true(self, taken):
        """The 'degree' key must be True iff all 10 sub-requirements are True."""
        global w
        w = {}
        result = degree_reqs(taken)
        sub_results = [v for k, (v, _) in result.items() if k != 'degree']
        assert result['degree'][0] == all(sub_results)

    @given(transcript)
    def test_witness_courses_are_subset_of_taken(self, taken):
        """
        Witness course IDs must be a subset of what was actually taken.
        A witness can't reference a course you never enrolled in.
        """
        global w
        w = {}
        degree_reqs(taken)
        taken_ids = {c.id for c in taken}
        for key, val in w.items():
            if isinstance(val, (set, frozenset)):
                course_ids = {v for v in val if isinstance(v, str)
                              and v[:3].isupper()}  # looks like a course ID
                assert course_ids <= taken_ids, (
                    f"Witness '{key}' references courses not in transcript: "
                    f"{course_ids - taken_ids}"
                )


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 5: Stateful testing with RuleBasedStateMachine
#
# WHEN IS THIS RELEVANT?
# When you model a SEQUENCE OF OPERATIONS with invariants at every step.
# Here: a student adds courses one by one to their transcript.
# Invariant: "once a requirement becomes satisfied, it stays satisfied
#             (monotonicity) as long as we only ADD courses."
#
# Hypothesis will generate arbitrary sequences of rule() calls and
# check every @invariant after every step.
# ─────────────────────────────────────────────────────────────────────────────

# class StudentTranscript(RuleBasedStateMachine):
#     """
#     Model a student building up their transcript course by course.
    
#     State: self.transcript (set of Taken)
#     Rules: add a course (the only operation -- we only ever add)
#     Invariants: properties that must hold at every step
#     """
#     @settings(
#         max_examples=25,       # number of independent runs (default 100)
#         stateful_step_count=15, # max rule calls per run   (default 50)
#         suppress_health_check=[HealthCheck.too_slow],
#     )
#     def __init__(self):
#         super().__init__()
#         self.transcript: set[Taken] = set()
#         self._satisfied: dict[str, bool] = {}   # track which reqs became True

#     @initialize(course=taken_course)
#     def setup(self, course):
#         """Hypothesis calls this once at the start to set initial state."""
#         self.transcript.add(course)

#     @rule(course=taken_course)
#     def add_course(self, course):
#         """Add one course to the transcript."""
#         self.transcript.add(course)

#     # ── Invariants ────────────────────────────────────────────────────────────
#     # These run after EVERY rule() call.

#     @invariant()
#     def gpa_never_negative(self):
#         weighted = [(c.credits, c.grade) for c in self.transcript
#                     if c.grade in grade_points]
#         assert GPA(weighted) >= 0.0

#     @invariant()
#     def elect_count_is_non_negative(self):
#         passed = {c for c in self.transcript if C_or_higher(c.grade)}
#         assert len(elect_courses(passed)) >= 0  # sanity: never negative

#     @invariant()
#     def satisfied_reqs_stay_satisfied(self):
#         global w
#         w = {}
#         result = degree_reqs(self.transcript)

#         for key, (satisfied, _) in result.items():
#             if key == 'degree':
#                 continue
#             if self._satisfied.get(key) and not satisfied:
#                 raise AssertionError(
#                     f"Requirement '{key}' was True but became False "
#                     f"after adding a course! (monotonicity violated)"
#                 )
#             if satisfied:
#                 self._satisfied[key] = True

# # unittest discovers this automatically since it extends unittest.TestCase:
# TestStudentTranscript = StudentTranscript.TestCase


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY OF PATTERNS
# ─────────────────────────────────────────────────────────────────────────────
#
# st.sampled_from(list)        pick one element from a fixed collection
# st.frozensets(strategy)      pick a set of elements
# st.builds(Cls, **strategies) assemble a dataclass/namedtuple
# st.integers(min, max)        bounded integers
# st.tuples(s1, s2)            fixed-length tuple of independent strategies
#
# assume(cond)                 discard example if cond is False (use sparingly)
# @given(s)                    "for all x drawn from s, property holds"
# RuleBasedStateMachine        model sequences of operations with invariants
#
# Shrinking (free, automatic): when Hypothesis finds a failing example,
# it shrinks it to the *simplest* failing case. This is why PBT is so
# much more useful than random testing -- you get minimal counterexamples.

if __name__ == '__main__':
    unittest.main()