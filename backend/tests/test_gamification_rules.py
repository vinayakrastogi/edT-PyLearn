"""Pure gamification rules: levels, XP formulas, the streak table, names and the badge catalogue."""
from datetime import date, timedelta

import pytest

from app.services import gamification_rules as rules
from app.services.gamification_rules import (
    BADGES,
    CORE_MODULE_IDS,
    anonymise_name,
    compute_streak,
    level_for_xp,
    level_progress,
    level_title,
    problem_xp,
    quiz_target_xp,
    xp_for_level,
)
from tools.check_content import CONTENT_DIR

D = date(2026, 3, 10)  # an arbitrary "today"


def days_ago(n: int) -> date:
    return D - timedelta(days=n)


# --------------------------------------------------------------------------------------
# Levels
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "level, xp",
    [(1, 0), (2, 100), (3, 300), (4, 600), (5, 1000), (10, 4500), (20, 19000)],
)
def test_xp_for_level_matches_the_spec(level, xp):
    assert xp_for_level(level) == xp


@pytest.mark.parametrize(
    "xp, level",
    [
        (-5, 1), (0, 1), (1, 1), (99, 1),
        (100, 2), (299, 2), (300, 3), (599, 3), (600, 4),
        (999, 4), (1000, 5), (4499, 9), (4500, 10), (18999, 19), (19000, 20),
    ],
)
def test_level_for_xp_boundaries(xp, level):
    assert level_for_xp(xp) == level


def test_level_for_xp_is_exact_for_every_level_and_capped_at_99():
    for level in range(1, 100):
        start = xp_for_level(level)
        assert level_for_xp(start) == level
        if level > 1:
            assert level_for_xp(start - 1) == level - 1
    assert level_for_xp(xp_for_level(99)) == 99
    assert level_for_xp(xp_for_level(100)) == 99
    assert level_for_xp(10**9) == 99


def test_level_progress_inside_a_level():
    p = level_progress(150)
    assert (p.level, p.title) == (2, "Sprout")
    assert p.xp_into_level == 50
    assert p.xp_for_next_level == 200  # level 2 spans 100 -> 300
    assert p.next_level_xp == 300


def test_level_progress_at_zero_and_at_a_level_start():
    p = level_progress(0)
    assert (p.level, p.xp_into_level, p.xp_for_next_level, p.next_level_xp) == (1, 0, 100, 100)
    p = level_progress(300)
    assert (p.level, p.xp_into_level, p.xp_for_next_level, p.next_level_xp) == (3, 0, 300, 600)


def test_level_progress_bar_is_full_at_the_level_cap():
    p = level_progress(10**9)
    assert p.level == 99
    assert p.xp_into_level == p.xp_for_next_level == xp_for_level(100) - xp_for_level(99)


@pytest.mark.parametrize(
    "level, title",
    [
        (1, "Hatchling"), (2, "Sprout"), (3, "Apprentice"), (4, "Bug Hunter"), (5, "Loop Rider"),
        (6, "Function Fan"), (7, "Class Act"), (8, "Data Explorer"), (9, "Automator"),
        (10, "Python Pro"), (11, "Python Pro"), (12, "Code Wizard"), (14, "Code Wizard"),
        (15, "Grand Master"), (19, "Grand Master"), (20, "Legend"), (99, "Legend"),
    ],
)
def test_level_titles_use_the_highest_threshold_reached(level, title):
    assert level_title(level) == title


# --------------------------------------------------------------------------------------
# Quiz and problem XP
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "pct, xp",
    [(0, 0), (40, 20), (70, 35), (80, 40), (100, 50), (83.3, 42), (5, 3), (25, 13)],
)
def test_quiz_target_xp(pct, xp):
    assert quiz_target_xp(pct) == xp


def test_quiz_target_xp_is_clamped_and_ignores_garbage():
    assert quiz_target_xp(-20) == 0
    assert quiz_target_xp(250) == 50
    assert quiz_target_xp(float("nan")) == 0
    assert quiz_target_xp(float("inf")) == 0


def test_problem_xp_by_difficulty():
    assert problem_xp("easy") == 20
    assert problem_xp("medium") == 35
    assert problem_xp("hard") == 60
    assert problem_xp("HARD") == 60
    assert problem_xp(" Medium ") == 35
    assert problem_xp("legendary") == 20  # unknown difficulties are treated as easy
    assert problem_xp(None) == 20


def test_constants_match_the_spec():
    assert rules.XP_LESSON == 10
    assert rules.XP_QUIZ_PERFECT == 25
    assert rules.XP_FIRST_TRY == 10
    assert rules.XP_MODULE_COMPLETE == 150
    assert rules.XP_DAILY_GOAL == 10
    assert rules.STREAK_MILESTONES == {3: 15, 7: 50, 14: 100, 30: 250, 60: 500, 100: 1000}
    assert rules.DAILY_GOAL_CHOICES == (20, 30, 50, 80)
    assert rules.DEFAULT_DAILY_GOAL == 30
    assert rules.MAX_FREEZES == 2
    assert rules.MAX_LEVEL == 99


# --------------------------------------------------------------------------------------
# Streak table
# --------------------------------------------------------------------------------------


def test_streak_first_ever_activity_starts_at_one():
    r = compute_streak(None, D, 0, 0, 0)
    assert (r.count, r.longest, r.extended) == (1, 1, True)
    assert not r.used_freeze and r.broken_from is None and not r.comeback and r.milestone is None


def test_streak_first_activity_ignores_a_stale_count():
    r = compute_streak(None, D, 9, 1, 12)
    assert r.count == 1 and r.longest == 12 and r.freezes == 1


def test_streak_same_day_is_unchanged():
    r = compute_streak(D, D, 5, 1, 8)
    assert (r.count, r.freezes, r.longest) == (5, 1, 8)
    assert not r.extended and not r.used_freeze and r.broken_from is None
    assert not r.comeback and r.milestone is None


def test_streak_same_day_never_reports_a_zero_streak():
    assert compute_streak(D, D, 0, 0, 0).count == 1


def test_streak_next_day_extends():
    r = compute_streak(days_ago(1), D, 4, 0, 4)
    assert (r.count, r.longest, r.extended) == (5, 5, True)
    assert not r.used_freeze and r.broken_from is None and r.milestone is None


def test_streak_next_day_keeps_a_longer_best():
    assert compute_streak(days_ago(1), D, 4, 0, 20).longest == 20


def test_streak_two_day_gap_with_a_freeze_spends_it():
    r = compute_streak(days_ago(2), D, 5, 1, 5)
    assert (r.count, r.freezes, r.used_freeze, r.extended) == (6, 0, True, True)
    assert r.broken_from is None and not r.comeback


def test_streak_two_day_gap_spends_only_one_of_two_freezes():
    r = compute_streak(days_ago(2), D, 5, 2, 5)
    assert (r.count, r.freezes, r.used_freeze) == (6, 1, True)


def test_streak_two_day_gap_without_a_freeze_breaks():
    r = compute_streak(days_ago(2), D, 5, 0, 5)
    assert (r.count, r.freezes, r.longest) == (1, 0, 5)
    assert r.broken_from == 5 and not r.used_freeze and not r.comeback


def test_streak_breaking_a_streak_of_one_reports_nothing_lost():
    r = compute_streak(days_ago(3), D, 1, 0, 1)
    assert r.count == 1 and r.broken_from is None


def test_streak_three_day_gap_breaks_even_with_freezes():
    r = compute_streak(days_ago(3), D, 6, 2, 6)
    assert (r.count, r.freezes, r.broken_from, r.used_freeze) == (1, 2, 6, False)


def test_streak_six_day_gap_is_not_yet_a_comeback():
    assert not compute_streak(days_ago(6), D, 3, 0, 3).comeback


@pytest.mark.parametrize("gap", [7, 8, 30, 400])
def test_streak_seven_plus_day_gap_is_a_comeback(gap):
    r = compute_streak(days_ago(gap), D, 4, 1, 9)
    assert r.comeback is True
    assert (r.count, r.broken_from, r.freezes, r.longest) == (1, 4, 1, 9)


@pytest.mark.parametrize("gap", [1, 2])
def test_streak_a_short_gap_is_never_a_comeback(gap):
    assert not compute_streak(days_ago(gap), D, 4, 1, 4).comeback


def test_streak_clock_skew_is_treated_as_the_same_day():
    r = compute_streak(D + timedelta(days=1), D, 5, 1, 5)
    assert (r.count, r.freezes, r.longest) == (5, 1, 5)
    assert not r.extended and r.broken_from is None and not r.comeback


@pytest.mark.parametrize("days", sorted(rules.STREAK_MILESTONES))
def test_streak_milestone_fires_when_the_count_reaches_it(days):
    r = compute_streak(days_ago(1), D, days - 1, 0, days - 1)
    assert r.count == days and r.milestone == days


def test_streak_milestone_is_not_repeated_on_the_same_day():
    assert compute_streak(D, D, 7, 0, 7).milestone is None


def test_streak_milestone_also_fires_on_a_day_bridged_by_a_freeze():
    r = compute_streak(days_ago(2), D, 2, 1, 2)
    assert r.count == 3 and r.milestone == 3 and r.used_freeze


def test_streak_earns_a_freeze_at_seven():
    r = compute_streak(days_ago(1), D, 6, 0, 6)
    assert r.count == 7 and r.freezes == 1


def test_streak_freeze_grant_is_capped_at_two():
    assert compute_streak(days_ago(1), D, 6, 2, 6).freezes == 2
    r = compute_streak(days_ago(1), D, 13, 1, 13)
    assert r.count == 14 and r.freezes == 2


def test_streak_a_freeze_spent_on_day_seven_is_replaced_by_the_grant():
    r = compute_streak(days_ago(2), D, 6, 1, 6)
    assert r.count == 7 and r.used_freeze and r.freezes == 1


def test_streak_no_freeze_for_a_non_multiple_of_seven():
    assert compute_streak(days_ago(1), D, 7, 0, 7).freezes == 0


def test_streak_restart_never_grants_a_freeze_or_milestone():
    r = compute_streak(days_ago(5), D, 20, 0, 20)
    assert r.freezes == 0 and r.milestone is None


# --------------------------------------------------------------------------------------
# Names
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Asha Kumar", "Asha K."),
        ("  Asha   Kumar  ", "Asha K."),
        ("asha kumar", "asha K."),
        ("Asha Devi Kumar", "Asha K."),
        ("Asha", "Asha"),
        ("Vinayak", "Vinayak"),
        ("", "Learner"),
        ("   ", "Learner"),
        (None, "Learner"),
        ("Zoë Ångström", "Zoë Å."),
        ("Åsa Öberg", "Åsa Ö."),
        ("Mary-Jane O'Brien", "Mary-Jane O."),
        ("J. Smith", "J S."),
        # Anything that is not a plain name is never echoed: e-mail addresses, phone numbers, usernames.
        ("kid.name@example.com", "Learner"),
        ("kid.name2012@gmail.com", "Learner"),
        ("9876543210", "Learner"),
        ("user_123", "Learner"),
        ("@@@", "Learner"),
        ("Ravi Kumar (ravi@school.edu)", "Ravi K."),
        ("Ravi ravi@school.edu", "Ravi"),
        ("12345 Ravi", "Ravi"),
        # Overlong names are cut to a sensible length.
        ("B" * 100_000, "B" * 15),
        ("Alexandrina-Wilhelmina Featherstonehaugh", "Alexandrina-Wil F."),
    ],
)
def test_anonymise_name(name, expected):
    assert anonymise_name(name) == expected


# --------------------------------------------------------------------------------------
# Badge catalogue
# --------------------------------------------------------------------------------------


def test_badge_ids_are_unique_and_complete():
    ids = [b.id for b in BADGES]
    assert len(ids) == len(set(ids)) == 35
    assert rules.BADGES_BY_ID.keys() == set(ids)


def test_badge_fields_are_filled_in_and_valid():
    for b in BADGES:
        assert b.name.strip() and b.description.strip(), b.id
        assert b.icon.strip(), b.id
        assert b.category in {"learning", "quizzes", "coding", "streaks", "modules", "levels"}, b.id
        assert b.rarity in {"common", "rare", "epic", "legendary"}, b.id
        assert b.target >= 1, b.id
        assert callable(b.current), b.id


def test_badge_names_are_unique():
    names = [b.name for b in BADGES]
    assert len(names) == len(set(names))


def test_badge_ids_cover_the_spec_table():
    expected = {
        "first-lesson", "lessons-10", "lessons-30", "lessons-all",
        "first-quiz", "quiz-80", "perfect-quiz", "quiz-champion",
        "first-solve", "solve-10", "solve-30", "solve-75", "first-try-5", "hard-solve", "hard-5",
        "streak-3", "streak-7", "streak-30", "comeback", "goal-getter",
        *(f"module-{n}" for n in range(1, 11)),
        "halfway-hero", "python-graduate", "level-5", "level-10", "xp-1000",
    }
    assert {b.id for b in BADGES} == expected


def test_ten_module_badges_reference_real_content_modules():
    module_badges = [b for b in BADGES if b.category == "modules" and b.id.startswith("module-")]
    assert [b.id for b in module_badges] == [f"module-{n}" for n in range(1, 11)]
    assert len(CORE_MODULE_IDS) == 10 and len(set(CORE_MODULE_IDS)) == 10
    for module_id in CORE_MODULE_IDS:
        assert (CONTENT_DIR / module_id / "module.yaml").exists(), module_id
    for badge, module_id in zip(module_badges, CORE_MODULE_IDS):
        assert badge.current({"completed_modules": {module_id}}) == 1
        other = next(m for m in CORE_MODULE_IDS if m != module_id)
        assert badge.current({"completed_modules": {other}}) == 0
        assert badge.current({}) == 0


@pytest.mark.parametrize(
    "badge_id, stats, earned",
    [
        ("first-lesson", {"lessons_read": 0}, False),
        ("first-lesson", {"lessons_read": 1}, True),
        ("lessons-10", {"lessons_read": 9}, False),
        ("lessons-10", {"lessons_read": 10}, True),
        ("lessons-all", {"lessons_read": 79}, False),
        ("lessons-all", {"lessons_read": 80}, True),
        ("first-quiz", {"quizzes_taken": 1}, True),
        ("quiz-80", {"quizzes_80": 1}, True),
        ("perfect-quiz", {"perfect_quizzes": 1}, True),
        ("quiz-champion", {"quizzes_80": 4}, False),
        ("quiz-champion", {"quizzes_80": 5}, True),
        ("first-solve", {"problems_solved": 1}, True),
        ("solve-75", {"problems_solved": 74}, False),
        ("solve-75", {"problems_solved": 75}, True),
        ("first-try-5", {"first_try_solves": 5}, True),
        ("hard-solve", {"hard_solved": 1}, True),
        ("hard-5", {"hard_solved": 4}, False),
        ("streak-3", {"longest_streak": 3}, True),
        ("streak-7", {"longest_streak": 6}, False),
        ("streak-30", {"longest_streak": 30}, True),
        ("comeback", {"comebacks": 1}, True),
        ("goal-getter", {"daily_goals_met": 6}, False),
        ("goal-getter", {"daily_goals_met": 7}, True),
        ("halfway-hero", {"modules_completed": 5}, True),
        ("python-graduate", {"modules_completed": 9}, False),
        ("python-graduate", {"modules_completed": 10}, True),
        ("level-5", {"level": 5}, True),
        ("level-10", {"level": 9}, False),
        ("xp-1000", {"xp_total": 999}, False),
        ("xp-1000", {"xp_total": 1000}, True),
    ],
)
def test_badge_conditions(badge_id, stats, earned):
    assert rules.BADGES_BY_ID[badge_id].is_earned(stats) is earned


def test_badge_current_tolerates_missing_stats():
    for b in BADGES:
        assert b.current({}) == 0
        assert not b.is_earned({})
