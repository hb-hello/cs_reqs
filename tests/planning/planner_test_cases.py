from ortools_version.planner import catalog, plan_courses
from ortools_version.course_catalog import Major, Standing, History


FULL = {
    'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',
    'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416',
    'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355',
    'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',
    'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',
    'CSE 300', 'CSE 312',
}


def history(ids, grade='A', loc='SB', when=(2024, 2)):
    return [History(cid, catalog[cid].credits, grade, when, loc) for cid in sorted(ids)]


def test_plan_no_electives():
    """Remove all 6 electives — planner must pick >= 4."""
    elects = {'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355'}
    taken = history(FULL - elects)

    def validate(checked, schedule_courses, schedule_by_course):
        assert len(schedule_courses) >= 1
        assert len(checked['elect'][1]) >= 4

    return taken, validate


# def test_plan_no_calc():
#     """Remove all science — planner picks combo + extras for >= 9 credits."""
#     ids = FULL - {'MAT 131', 'MAT 132'}
#     taken = history(ids)

#     def validate(checked, schedule_courses, schedule_by_course):
#         assert len(schedule_courses) >= 1
#         assert len(checked['calc'][1]) >= 2

#     return taken, validate


# def test_plan_no_sta():
#     """Remove calculus — planner picks a calc sequence."""
#     ids = FULL - {'AMS 301', 'AMS 310'}
#     taken = history(ids)

#     def validate(checked, schedule_courses, schedule_by_course):
#         assert len(schedule_courses) >= 1
#         sta = set(checked['sta'][1])
#         assert 'AMS 301' in sta
#         assert 'AMS 310' in sta or 'AMS 311' in sta

#     return taken, validate


# def test_plan_no_alg():
#     """Remove AMS 301 + AMS 310 — planner restores them."""
#     ids = FULL - {'AMS 210'}
#     taken = history(ids)

#     def validate(checked, schedule_courses, schedule_by_course):
#         assert len(schedule_courses) >= 1
#         alg = set(checked['alg'][1])
#         assert 'AMS 210' in alg or 'MAT 211' in alg

#     return taken, validate


# def test_plan_prereq_order_for_calc_sequence():
#     """Planner should place prereqs before dependent calc courses."""
#     ids = FULL - {'MAT 131', 'MAT 132'}
#     taken = history(ids)

#     def validate(checked, schedule_courses, schedule_by_course):
#         assert len(schedule_courses) >= 1
#         possible_pairs = [
#             ('MAT 131', 'MAT 132'),
#             ('AMS 151', 'AMS 161'),
#             ('MAT 125', 'MAT 126'),
#             ('MAT 126', 'MAT 127'),
#         ]
#         planned_pairs = [
#             (pre, req)
#             for pre, req in possible_pairs
#             if pre in schedule_by_course and req in schedule_by_course
#         ]
#         assert planned_pairs, 'no planned prereq/course pair found to validate ordering'
#         for pre, req in planned_pairs:
#             assert schedule_by_course[pre] < schedule_by_course[req], f'{pre} should be before {req} in planned schedule'

#     return taken, validate


# def test_plan_respects_course_allowed_terms():
#     """OR-Tools planner should honor per-course allowed semester names."""
#     ids = FULL - {'CSE 220'}
#     taken = history(ids)

#     def validate(checked, schedule_courses, schedule_by_course):
#         expected_sem = {'Fall': 1, 'Spring': 3}
#         for sem_name, sem_num in expected_sem.items():
#             _, direct_schedule, _ = plan_courses(
#                 taken,
#                 Major('CSE'),
#                 Standing('U4'),
#                 schedule=True,
#                 course_offered_terms={'CSE 220': {sem_name}},
#             )
#             assert 'CSE 220' in direct_schedule
#             assert direct_schedule['CSE 220'][1] == sem_num, f'CSE 220 should be planned in {sem_name}'

#     return taken, validate


# def test_plan_coreq_160_161_mutual():
#     """Mutual coreqs CSE 160 / CSE 161 should be scheduled together."""
#     ids = FULL - {'CSE 160', 'CSE 161'}
#     taken = history(ids)

#     def validate(checked, schedule_courses, schedule_by_course):
#         assert 'CSE 160' in schedule_courses
#         assert 'CSE 161' in schedule_courses
#         # mutual coreqs should end up in the same semester
#         assert schedule_by_course['CSE 160'] == schedule_by_course['CSE 161']

#     # require planner to include CSE 160 and validate its coreq is scheduled
#     return taken, validate, {'must_include': {'CSE 160'}, 'approaches': ['ortools_version']}

