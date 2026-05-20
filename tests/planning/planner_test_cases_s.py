from ortools_version.course_catalog import Taken


def _course(cid, credits, grade, when, where='SB'):
    return Taken(cid, credits, grade, when, where)


# CSE_AMS Two transcript from users2.yaml (through Spring 2024).
def _cse_ams_two_history():
    return [
        _course('WRT 102', 3, 'A', (2022, 4)),
        _course('AMS 151', 3, 'A', (2022, 4)),
        _course('POL 101', 3, 'A', (2022, 4)),
        _course('AMS 103', 3, 'A', (2022, 4)),

        _course('AMS 161', 3, 'A', (2023, 2)),
        _course('CSE 114', 4, 'A', (2023, 2)),
        _course('POL 102', 3, 'A', (2023, 2)),
        _course('POL 103', 3, 'A', (2023, 2)),

        _course('AMS 210', 3, 'A', (2023, 4)),
        _course('AMS 261', 3, 'A', (2023, 4)),
        _course('POL 201', 3, 'A', (2023, 4)),
        _course('POL 270', 3, 'A', (2023, 4)),
        _course('CSE 214', 4, 'A', (2023, 4)),

        _course('AMS 301', 3, 'A', (2024, 2)),
        _course('AMS 310', 3, 'A', (2024, 2)),
        _course('POL 323', 3, 'A', (2024, 2)),
        _course('POL 353', 3, 'A', (2024, 2)),
        _course('CSE 220', 4, 'A', (2024, 2)),
    ]


def test_plan_s_cse_ams_two_with_must_include_exclude():
    taken = _cse_ams_two_history()

    def validate(checked, schedule_courses, schedule_by_course):
        assert len(schedule_courses) >= 1
        assert checked['degree'][0]

    attrs = {
        # OR-Tools planner currently supports must_include/must_exclude directly.
        'approaches': {'ortools_version'},
        'must_include': {'CSE 360', 'CSE 353'},  # both in COURSE_OFFERED_TERMS; CSE 360 only needs CSE 220 (already taken)
        'must_exclude': {'AMS 351', 'CSE 337'},
        'skip_checker_validation': True,
    }

    return taken, validate, attrs
